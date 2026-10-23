"""Optional local frozen representation; importing this module does not import torch."""
from __future__ import annotations

import os
import re
import importlib
from pathlib import Path
from typing import Any

import numpy as np

from .common import digest, identity, read_json, verify_files, write_json
from .models import texts_only


class FrozenEncoder:
    def __init__(self, assets: Path, *, batch_size: int = 8, device: str = "cpu"):
        assets = assets.resolve()
        self.manifest = read_json(assets / "encoder.json")
        if self.manifest["model"] != "microsoft/deberta-v3-small" or not re.fullmatch(r"[0-9a-f]{40}", self.manifest["revision"]):
            raise ValueError("One exact DeBERTa-small revision is required")
        verify_files(assets, self.manifest["files"])
        if not self.manifest["files"] or batch_size < 1:
            raise ValueError("Missing asset inventory or invalid batch")
        self.assets, self.batch_size, self.device = assets, batch_size, device
        self._model: Any = None
        self._tokenizer: Any = None

    def __getstate__(self):
        # Do not pickle the base model or tokenizer into each task-fitted probe.
        state = self.__dict__.copy()
        state["_model"], state["_tokenizer"] = None, None
        return state

    def load(self):
        if self._model is None:
            os.environ["HF_HUB_OFFLINE"] = "1"
            os.environ["TRANSFORMERS_OFFLINE"] = "1"
            torch = importlib.import_module("torch")
            transformers = importlib.import_module("transformers")
            torch.manual_seed(2027)
            torch.use_deterministic_algorithms(True)
            self._tokenizer = transformers.AutoTokenizer.from_pretrained(str(self.assets), local_files_only=True, trust_remote_code=False)
            self._model = transformers.AutoModel.from_pretrained(str(self.assets), local_files_only=True, trust_remote_code=False)
            self._model.to(device=self.device, dtype=torch.float32).eval()
            self._model.requires_grad_(False)

    def encode(self, texts) -> np.ndarray:
        texts = texts_only(texts)
        self.load()
        torch = importlib.import_module("torch")
        chunks = []
        with torch.inference_mode():
            for start in range(0, len(texts), self.batch_size):
                tokens = self._tokenizer(texts[start:start+self.batch_size], padding="max_length",
                                         truncation=True, max_length=512, return_tensors="pt")
                tokens = {k: v.to(self.device) for k, v in tokens.items()}
                hidden = self._model(**tokens).last_hidden_state
                mask = tokens["attention_mask"].unsqueeze(-1)
                pooled = (hidden * mask).sum(dim=1) / mask.sum(dim=1).clamp(min=1)
                chunks.append(pooled.cpu().numpy().astype(np.float32))
        result = np.concatenate(chunks) if chunks else np.empty((0, self._model.config.hidden_size), dtype=np.float32)
        if not np.isfinite(result).all():
            raise ValueError("Nonfinite embeddings")
        return result

    def cache(self, frame, directory: Path, *, view: str, allowed_ids: set[str]) -> np.ndarray:
        from .views import VERSION, transform
        if not set(frame.id) <= allowed_ids or frame.id.duplicated().any():
            raise ValueError("Only allowlisted development rows may enter the embedding cache")
        config = {"encoder": self.manifest, "view": view, "view_version": VERSION,
                  "max_length": 512, "pooling": "masked-mean-including-special", "dtype": "float32",
                  "implementation": "encoder-v1", "batch_size": self.batch_size}
        keys = [identity({"id": i, "text": t, "config": config}) for i, t in zip(frame.id, frame.text)]
        directory.mkdir(parents=True, exist_ok=True)
        rows = []
        for key, text in zip(keys, frame.text):
            path = directory / f"{key}.npy"
            meta = directory / f"{key}.json"
            if not path.exists():
                value = self.encode([transform(text, view)])[0]
                np.save(path, value, allow_pickle=False)
                write_json(meta, {"key": key, "sha256": digest(path)})
            if read_json(meta) != {"key": key, "sha256": digest(path)}:
                raise ValueError("Embedding cache integrity mismatch")
            rows.append(np.load(path, allow_pickle=False))
        return np.stack(rows)

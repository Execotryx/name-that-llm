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
from .environment import runtime_profile, verify_runtime_lock, package_inventory, NEURAL


class FrozenEncoder:
    def __init__(self, assets: Path, *, batch_size: int = 8, device: str = "cpu"):
        assets = assets.resolve()
        self.manifest = read_json(assets / "encoder.json")
        if self.manifest["model"] != "microsoft/deberta-v3-small" or not re.fullmatch(r"[0-9a-f]{40}", self.manifest["revision"]):
            raise ValueError("One exact DeBERTa-small revision is required")
        if batch_size < 1:
            raise ValueError("Invalid encoder batch size")
        self.assets, self.batch_size, self.device = assets, batch_size, device
        self.manifest_hash = identity(self.manifest)
        self._model: Any = None
        self._tokenizer: Any = None
        self.verify_assets()

    def verify_assets(self) -> None:
        if not hasattr(self, "manifest_hash") or identity(self.manifest) != self.manifest_hash:
            raise ValueError("Legacy or changed encoder identity; register an asset migration")
        if identity(read_json(self.assets / "encoder.json")) != self.manifest_hash:
            raise ValueError("Encoder manifest drift")
        files = self.manifest["files"]
        verify_files(self.assets, files)
        required = {"config.json", "tokenizer_config.json", "runtime-lock.json"}
        if not required <= set(files) or not ({"tokenizer.json", "spm.model", "vocab.txt"} & set(files)):
            raise ValueError("Incomplete config/tokenizer/runtime asset inventory")
        layouts = [n for n in ("model.safetensors", "pytorch_model.bin", "model.safetensors.index.json",
                               "pytorch_model.bin.index.json") if n in files]
        if len(layouts) != 1:
            raise ValueError("Exactly one checkpoint weight layout is required")
        weight = layouts[0]
        if weight.endswith(".index.json"):
            shards = set(read_json(self.assets / weight).get("weight_map", {}).values())
            if not shards or not shards <= set(files):
                raise ValueError("Missing indexed weight shards")
        for filename in ("tokenizer_config.json", "config.json"):
            config = read_json(self.assets / filename)
            for key in ("tokenizer_file", "vocab_file", "merges_file", "added_tokens_file", "special_tokens_map_file"):
                target = config.get(key)
                if target is not None and (not isinstance(target, str) or target not in files or
                                          not (self.assets / target).resolve().is_relative_to(self.assets.resolve())):
                    raise ValueError(f"Unbound loader file reference: {filename}:{key}")
        # Reject any unlisted file that a local HF loader could select.
        for path in self.assets.rglob("*"):
            if not path.is_file():
                continue
            name = path.relative_to(self.assets).as_posix()
            relevant = (path.suffix in (".bin", ".safetensors", ".model", ".json", ".py") or
                        path.name in ("vocab.txt", "merges.txt", "added_tokens.json"))
            if relevant and name != "encoder.json" and name not in files:
                raise ValueError(f"Unlisted inference asset: {name}")

    def rebind(self, assets: Path) -> None:
        self.assets = assets.resolve()
        self._model, self._tokenizer = None, None
        self.verify_assets()

    def runtime(self, *, verify_lock: bool = True) -> dict:
        self.verify_assets()
        package_inventory(NEURAL + (("sentencepiece", "protobuf") if "spm.model" in self.manifest["files"] else ()), transitive=True)
        # Optional imports live only here, after complete asset verification.
        torch = importlib.import_module("torch")
        torch.use_deterministic_algorithms(True)
        settings = {"device": self.device, "batch_size": self.batch_size, "dtype": "float32",
                    "max_length": 512, "pooling": "masked-mean-including-special",
                    "deterministic": torch.are_deterministic_algorithms_enabled(),
                    "torch_build": str(torch.__version__), "cuda_build": torch.version.cuda,
                    "cudnn": torch.backends.cudnn.version(),
                    "tf32_matmul": torch.backends.cuda.matmul.allow_tf32,
                    "tf32_cudnn": torch.backends.cudnn.allow_tf32}
        if self.device != "cpu":
            import subprocess
            device = torch.cuda.get_device_properties(self.device)
            settings["accelerator"] = {"name": device.name, "capability": [device.major, device.minor],
                "driver": subprocess.check_output(["nvidia-smi", "--query-gpu=driver_version", "--format=csv,noheader"], text=True).strip()}
        tokenizer_packages = ("sentencepiece", "protobuf") if "spm.model" in self.manifest["files"] else ()
        profile = runtime_profile(neural=True, settings=settings, tokenizer_packages=tokenizer_packages)
        if verify_lock:
            verify_runtime_lock(self.assets / "runtime-lock.json", profile)
        return profile

    def preflight(self) -> dict:
        return self.runtime()

    def __getstate__(self):
        # Do not pickle the base model or tokenizer into each task-fitted probe.
        state = self.__dict__.copy()
        state["_model"], state["_tokenizer"] = None, None
        return state

    def load(self):
        if self._model is None:
            self.verify_assets()
            profile = self.preflight()
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
            self._loaded_runtime = profile

    def encode(self, texts) -> np.ndarray:
        texts = texts_only(texts)
        self.load()
        torch = importlib.import_module("torch")
        # Warm calls must not silently adopt changed global numerical policy or
        # mutable batch/device settings. File/build inventories are cold-load checks.
        from .environment import assert_runtime
        profile = self._loaded_runtime
        settings = {**profile["settings"], "device": self.device, "batch_size": self.batch_size,
                    "deterministic": torch.are_deterministic_algorithms_enabled(),
                    "tf32_matmul": torch.backends.cuda.matmul.allow_tf32,
                    "tf32_cudnn": torch.backends.cudnn.allow_tf32}
        env = {k: os.environ.get(k) for k in profile["numerical_environment"]}
        assert_runtime(profile, {**profile, "settings": settings, "numerical_environment": env})
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
        runtime = self.runtime()
        config = {"runtime": runtime, "encoder": self.manifest, "view": view, "view_version": VERSION,
                  "max_length": 512, "pooling": "masked-mean-including-special", "dtype": "float32",
                  "implementation": "encoder-v2", "batch_size": self.batch_size}
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


def prepare_assets(assets: Path, wheels: Path, revision: str, *, batch_size: int = 8, device: str = "cpu") -> None:
    """Author a new local asset/runtime lock before G0; never download or overwrite a lock."""
    import tempfile
    import shutil
    from .environment import write_runtime_lock
    if (assets / "encoder.json").exists() or (assets / "runtime-lock.json").exists():
        raise ValueError("Preserve existing asset locks; stage a fresh asset directory")
    # Only this acquisition path permits capturing a profile before its lock exists.
    # A failed acquisition retains a non-eligible staging record for inspection.
    write_json(assets / "runtime-lock.json", {"status": "staging"}, exclusive=True)
    def inventory():
        return {"model": "microsoft/deberta-v3-small", "revision": revision,
                "files": {p.relative_to(assets).as_posix(): digest(p) for p in sorted(assets.rglob("*"))
                          if p.is_file() and p.name != "encoder.json"}}
    write_json(assets / "encoder.json", inventory(), exclusive=True)
    encoder = FrozenEncoder(assets, batch_size=batch_size, device=device)
    profile = encoder.runtime(verify_lock=False)
    with tempfile.TemporaryDirectory() as tmp:
        staged = Path(tmp) / "runtime-lock.json"
        write_runtime_lock(staged, profile, wheels)
        shutil.copy2(staged, assets / "runtime-lock.json")
    write_json(assets / "encoder.json", inventory())
    FrozenEncoder(assets, batch_size=batch_size, device=device).preflight()

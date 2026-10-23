"""Sparse feature factories; learned state lives inside fold-fitted pipelines."""
import re
import unicodedata
from typing import Any

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import FeatureUnion
from scipy.sparse import csr_matrix


class SafeTfidfVectorizer(TfidfVectorizer):
    """An all-empty/pruned diagnostic vocabulary contributes one zero column.

    This preserves rows and yields an intercept-only model if both branches
    contain no signal. The zero column carries no fitted corpus information.
    """
    def fit_transform(self, raw_documents, y=None):
        documents = list(raw_documents)
        self.empty_ = False
        try:
            return super().fit_transform(documents, y)
        except ValueError as error:
            if "empty vocabulary" not in str(error) and "After pruning, no terms remain" not in str(error):
                raise
            self.empty_ = True
            self.vocabulary_ = {}
            return csr_matrix((len(documents), 1), dtype=np.float32)

    def transform(self, raw_documents):
        documents = list(raw_documents)
        if self.empty_:
            return csr_matrix((len(documents), 1), dtype=np.float32)
        return super().transform(documents)


def sparse_features(*, word_only: bool = False):
    shared: dict[str, Any] = dict(lowercase=False, sublinear_tf=True, dtype=np.float32, min_df=2)
    branches = [("word", SafeTfidfVectorizer(ngram_range=(1, 2), max_df=.995,
                                          max_features=150000, **shared))]
    if not word_only:
        branches.append(("char", SafeTfidfVectorizer(analyzer="char", ngram_range=(3, 5),
                                                  max_features=250000, **shared)))
    return FeatureUnion(branches)


def style_features(texts, *, length_only: bool = False, no_length: bool = False):
    rows = []
    for text in texts:
        n = max(1, len(text))
        lengths = [len(text), len(text.split()), len(re.findall(r"[.!?]", text)),
                   len(text.split("\n\n")) if text else 0]
        rates = [sum(unicodedata.category(c).startswith("P") for c in text) / n,
                 sum(c.isupper() for c in text) / n,
                 sum(ord(c) > 127 for c in text) / n,
                 sum(c in "`#*_<>" for c in text) / n,
                 len(set(text.split())) / max(1, len(text.split()))]
        rows.append(lengths if length_only else rates if no_length else lengths + rates)
    width = 4 if length_only else 5 if no_length else 9
    return np.asarray(rows, dtype=np.float64).reshape(-1, width)

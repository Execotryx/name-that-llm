"""Version 1 diagnostic views: pure functions, with no corpus-fitted state."""
import re

VERSION = "views-v1"


def transform(text: str, view: str = "raw") -> str:
    if view == "raw":
        return text
    if view == "format-only":
        return re.sub(r"\w", "x", text, flags=re.UNICODE)
    if view == "format-stripped":
        text = re.sub(r"```[^\n]*\n?|```", "", text)
        text = re.sub(r"(?m)^\s*(?:#{1,6}|[-*+]|\d+[.)])\s+", "", text)
        text = re.sub(r"\[([^]]+)\]\([^)]+\)", r"\1", text)
        return re.sub(r"[*_`]+", "", text)
    if view == "lexical-only":
        return " ".join(re.findall(r"[^\W_]+", text, flags=re.UNICODE))
    sentences = re.split(r"(?<=[.!?])\s+", text, maxsplit=1)
    if view == "opening-only":
        return sentences[0]
    if view == "opening-removed":
        return sentences[1] if len(sentences) > 1 else ""
    if view in ("prefix-40", "prefix-80", "prefix-120"):
        return " ".join(text.split()[:int(view.split("-")[1])])
    raise ValueError(f"Unregistered text view: {view}")

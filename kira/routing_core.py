"""
Semantic routing engine.
Embeds trigger phrases with MiniLM, searches by cosine similarity at query time.
"""

from __future__ import annotations

import numpy as np
from pathlib import Path
from fastembed import TextEmbedding

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
THRESHOLD = 0.40  # slightly lower than production 0.44 for demo friendliness

_model: TextEmbedding | None = None
_index: list[dict] | None = None


# ─── Model ────────────────────────────────────────────────────────────────────

def _get_model() -> TextEmbedding:
    global _model
    if _model is None:
        _model = TextEmbedding(MODEL_NAME)
    return _model


def _embed(texts: list[str]) -> np.ndarray:
    """Embed a list of texts and return unit-normalized vectors."""
    model = _get_model()
    vecs = np.array(list(model.embed(texts)), dtype=np.float32)
    # Normalize each row to unit length for cosine = dot product
    norms = np.linalg.norm(vecs, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1.0, norms)
    return vecs / norms


# ─── Index build ──────────────────────────────────────────────────────────────

def _parse_routing(text: str) -> list[dict]:
    """Parse routing.md table rows into entries."""
    entries = []
    for line in text.splitlines():
        line = line.strip()
        if not line or not line.startswith("|"):
            continue
        # Skip header and separator rows
        if "Trigger" in line or line.startswith("|--") or line.startswith("| --"):
            continue
        parts = [p.strip() for p in line.split("|") if p.strip()]
        if len(parts) < 2:
            continue
        trigger_col = parts[0]
        files_col = parts[1]
        files = [f.strip() for f in files_col.split(",") if f.strip()]
        # Multi-phrase: split trigger by comma and dash to create individual phrase vectors
        phrases = [p.strip() for p in trigger_col.replace(" - ", ",").split(",") if p.strip()]
        if not phrases:
            phrases = [trigger_col]
        entries.append({
            "trigger": trigger_col,
            "phrases": phrases,
            "files": files,
        })
    return entries


def _build_index(routing_path: str = "brain/routing.md") -> list[dict]:
    text = Path(routing_path).read_text(encoding="utf-8")
    entries = _parse_routing(text)
    for entry in entries:
        # Embed full trigger + each individual phrase
        all_texts = [entry["trigger"]] + entry["phrases"]
        entry["vectors"] = _embed(all_texts)  # shape: (n_phrases+1, 384)
    return entries


def _get_index() -> list[dict]:
    global _index
    if _index is None:
        _index = _build_index()
    return _index


# ─── Search ───────────────────────────────────────────────────────────────────

def search(queries: list[str], top_k: int = 3) -> str:
    """
    Given a list of short query phrases, return the best matching knowledge cards.
    This is what search_kb exposes as an MCP tool.
    """
    index = _get_index()
    if not index:
        return "No routing index loaded."

    query_vecs = _embed(queries)  # shape: (n_queries, 384)

    scored: list[tuple[float, dict]] = []
    for entry in index:
        phrase_vecs = entry["vectors"]  # shape: (n_phrases, 384)
        # Cosine similarity matrix: (n_queries, n_phrases)
        sim_matrix = query_vecs @ phrase_vecs.T
        max_score = float(sim_matrix.max())
        if max_score >= THRESHOLD:
            scored.append((max_score, entry))

    if not scored:
        return "No relevant knowledge cards found for the given queries."

    scored.sort(reverse=True)
    scored = scored[:top_k]

    lines = ["Matched knowledge cards:\n"]
    for score, entry in scored:
        files_str = ", ".join(f"brain/{f}" for f in entry["files"])
        lines.append(f"  Score : {score:.3f}")
        lines.append(f"  Load  : {files_str}")
        lines.append(f"  Trigger: {entry['trigger']}\n")

    return "\n".join(lines)


if __name__ == "__main__":
    # Quick smoke test
    result = search(["deploy service", "kubernetes"])
    print(result)

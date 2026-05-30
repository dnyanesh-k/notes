"""
Semantic routing engine.
Embeds trigger phrases with MiniLM, searches by cosine similarity at query time.

Hot-reload: a background thread watches brain/routing.md for file changes.
When the file is modified, it rebuilds the index in the background and then
atomically swaps the reference so in-flight queries always see a complete index.
"""

from __future__ import annotations

import threading
import time as _time
import numpy as np
from pathlib import Path
from fastembed import TextEmbedding

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
THRESHOLD = 0.40  # slightly lower than production 0.44 for demo friendliness

ROUTING_FILE = "brain/routing.md"
WATCH_INTERVAL = 2.0   # seconds between mtime checks

_model: TextEmbedding | None = None
_index: list[dict] | None = None
_index_lock = threading.Lock()           # protects the atomic swap
_last_mtime: float = 0.0
_watcher_started = False


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
    import json, datetime
    text = Path(routing_path).read_text(encoding="utf-8")
    entries = _parse_routing(text)
    for entry in entries:
        # Embed full trigger + each individual phrase
        all_texts = [entry["trigger"]] + entry["phrases"]
        entry["vectors"] = _embed(all_texts)  # shape: (n_phrases+1, 384)

    # Write human-readable snapshot (no raw vectors) so the index is visible
    snapshot = {
        "built_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "model": MODEL_NAME,
        "threshold": THRESHOLD,
        "total_entries": len(entries),
        "entries": [
            {
                "trigger": e["trigger"],
                "phrases": e["phrases"],
                "phrase_count": len(e["phrases"]),
                "vector_shape": list(e["vectors"].shape),   # e.g. [3, 384]
                "files": e["files"],
            }
            for e in entries
        ],
    }
    snapshot_path = Path(routing_path).parent / "index_snapshot.json"
    snapshot_path.write_text(
        json.dumps(snapshot, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return entries


def _get_index() -> list[dict]:
    global _index, _last_mtime
    with _index_lock:
        if _index is None:
            _index = _build_index()
            try:
                _last_mtime = Path(ROUTING_FILE).stat().st_mtime
            except OSError:
                pass
    return _index


# ─── Hot-reload watcher ───────────────────────────────────────────────────────

def _watcher_loop() -> None:
    """Background thread: polls routing.md mtime, rebuilds + atomically swaps index."""
    global _index, _last_mtime
    while True:
        _time.sleep(WATCH_INTERVAL)
        try:
            mtime = Path(ROUTING_FILE).stat().st_mtime
        except OSError:
            continue
        if mtime != _last_mtime:
            print(f"\n  [HotReload] brain/routing.md changed — rebuilding index...")
            try:
                new_index = _build_index()
                with _index_lock:       # atomic swap: old index stays live until this point
                    _index = new_index
                    _last_mtime = mtime
                print(f"  [HotReload] Done — {len(new_index)} entries loaded. Snapshot updated: brain/index_snapshot.json\n")
            except Exception as exc:
                print(f"  [HotReload] Rebuild failed: {exc} — keeping old index.\n")


def start_watcher() -> None:
    """Start the hot-reload watcher thread (daemon so it dies with the main process)."""
    global _watcher_started
    if _watcher_started:
        return
    _watcher_started = True
    t = threading.Thread(target=_watcher_loop, daemon=True, name="routing-watcher")
    t.start()


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

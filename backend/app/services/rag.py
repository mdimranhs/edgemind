from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from app.core.config import settings

KNOWLEDGE_DIR = Path(__file__).resolve().parent.parent.parent / "knowledge"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
SCORE_THRESHOLD = 0.3
MMR_LAMBDA = 0.7
MMR_TOP_K = 10


class RagService:

    def __init__(self, model: SentenceTransformer | None = None) -> None:
        self.model = model or SentenceTransformer(
            EMBEDDING_MODEL, local_files_only=settings.rag_local_files_only
        )
        self.index: faiss.Index | None = None
        self.chunks: list[str] = []
        self.sources: list[str] = []
        self.chunk_embeddings: np.ndarray | None = None


    def ingest(self) -> None:
        chunks: list[str] = []
        sources: list[str] = []
        for md_path in sorted(KNOWLEDGE_DIR.rglob("*.md")):
            text = md_path.read_text()
            file_chunks = self._chunk(text)
            chunks.extend(file_chunks)
            sources.extend([md_path.stem] * len(file_chunks))
        self.chunks = chunks
        self.sources = sources
        if not chunks:
            self.index = None
            return
        embeddings = self.model.encode(chunks, show_progress_bar=False)
        embeddings = np.ascontiguousarray(embeddings, dtype=np.float32)
        faiss.normalize_L2(embeddings)
        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dim)
        self.index.add(embeddings)
        self.chunk_embeddings = embeddings

    def retrieve(self, query: str, top_k: int = 3) -> list[str]:
        if self.index is None or not self.chunks or self.chunk_embeddings is None:
            return []
        query_vec = self.model.encode([query], show_progress_bar=False)
        query_vec = np.ascontiguousarray(query_vec, dtype=np.float32)
        faiss.normalize_L2(query_vec)
        scores, indices = self.index.search(query_vec, min(MMR_TOP_K, len(self.chunks)))
        candidates = [
            (i, self.chunks[i], self.sources[i], float(scores[0][j]))
            for j, i in enumerate(indices[0]) if i >= 0
        ]
        candidates = [c for c in candidates if c[3] >= SCORE_THRESHOLD]
        selected = self._mmr(candidates, top_k)
        return [
            f"[Source: {s}]\n{c}" for _, c, s, _ in selected
        ]

    def _mmr(
        self, candidates: list[tuple[int, str, str, float]], top_k: int,
    ) -> list[tuple[int, str, str, float]]:
        if not candidates or top_k >= len(candidates) or self.chunk_embeddings is None:
            return candidates[:top_k]
        selected: list[tuple[int, str, str, float]] = [candidates[0]]
        remaining = candidates[1:]
        selected_embs = self.chunk_embeddings[[c[0] for c in selected]]
        while len(selected) < top_k and remaining:
            remaining_indices = [c[0] for c in remaining]
            remaining_embs = self.chunk_embeddings[remaining_indices]
            sim_to_query = np.array([c[3] for c in remaining])
            sim_to_selected = np.max(
                remaining_embs @ selected_embs.T, axis=1
            )
            mmr_scores = MMR_LAMBDA * sim_to_query - (1 - MMR_LAMBDA) * sim_to_selected
            best_idx = int(np.argmax(mmr_scores))
            best = remaining.pop(best_idx)
            selected.append(best)
            selected_embs = np.vstack([selected_embs, remaining_embs[best_idx:best_idx+1]])
        return selected


    def _chunk(self, text: str) -> list[str]:
        lines = text.strip().split("\n")
        title = ""
        for line in lines:
            if line.startswith("# ") and not line.startswith("## "):
                title = line
                break
        if title:
            lines = [line for line in lines if line.strip() != title]
        current: list[str] = []
        result: list[str] = []
        for line in lines:
            if line.startswith("## "):
                if current:
                    result.append("\n".join(current))
                current = [line]
            else:
                current.append(line)
        if current:
            result.append("\n".join(current))
        merged: list[str] = []
        for c in result:
            stripped = c.strip()
            if not stripped:
                continue
            if title:
                stripped = f"{title}\n{stripped}"
            if merged:
                prev_lines = merged[-1].split("\n")
                curr_lines = stripped.split("\n")
                if len(prev_lines) < 5 and len(curr_lines) < 5:
                    merged[-1] = merged[-1] + "\n" + stripped
                    continue
            merged.append(stripped)
        return merged if merged else [stripped]

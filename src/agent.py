from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        results = self.store.search(question, top_k=top_k)
        context_lines = []
        for index, result in enumerate(results, start=1):
            source = result.get("metadata", {}).get("source_url") or result.get("metadata", {}).get("source") or result.get("metadata", {}).get("doc_id") or "unknown"
            context_lines.append(f"[{index}] source={source}\n{result.get('content', '')}")

        context = "\n\n".join(context_lines) if context_lines else "No relevant context found."
        prompt = (
            "You are a retrieval-augmented assistant. Answer only using the context below. "
            "If the context is insufficient, say you do not know.\n\n"
            f"Question: {question}\n\n"
            f"Context:\n{context}\n\n"
            "Answer:"
        )
        return self.llm_fn(prompt)

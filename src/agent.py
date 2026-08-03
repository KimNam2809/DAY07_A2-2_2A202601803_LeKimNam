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
        self._store = store
        self._llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        results = self._store.search(
            query=question,
            top_k=top_k,
        )

        context_parts = []

        for index, result in enumerate(results, start=1):
            metadata = result.get("metadata", {})

            source = (
                metadata.get("source_url")
                or metadata.get("source")
                or metadata.get("doc_id")
                or result.get("id", "unknown")
            )

            score = result.get("score", 0.0)
            content = result.get("content", "")

            context_parts.append(
                f"[Chunk {index} | source={source} | score={score:.4f}]\n"
                f"{content}"
            )

        if context_parts:
            context = "\n\n".join(context_parts)
        else:
            context = "No relevant context was found."

        prompt = (
            "Answer the question using only the supplied context. "
            "If the context is insufficient, say that the information "
            "is not available.\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {question}\n\n"
            "Answer:"
        )

        return self._llm_fn(prompt)

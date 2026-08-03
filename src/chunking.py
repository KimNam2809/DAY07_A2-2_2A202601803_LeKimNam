from __future__ import annotations

import math
import re


class FixedSizeChunker:
    """
    Split text into fixed-size chunks with optional overlap.

    Rules:
        - Each chunk is at most chunk_size characters long.
        - Consecutive chunks share overlap characters.
        - The last chunk contains whatever remains.
        - If text is shorter than chunk_size, return [text].
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 50) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        if len(text) <= self.chunk_size:
            return [text]

        step = self.chunk_size - self.overlap
        chunks: list[str] = []
        for start in range(0, len(text), step):
            chunk = text[start : start + self.chunk_size]
            chunks.append(chunk)
            if start + self.chunk_size >= len(text):
                break
        return chunks


class SentenceChunker:
    """
    Split text into chunks of at most max_sentences_per_chunk sentences.

    Sentence detection: split on ". ", "! ", "? " or ".\n".
    Strip extra whitespace from each chunk.
    """

    def __init__(self, max_sentences_per_chunk: int = 3) -> None:
        self.max_sentences_per_chunk = max(1, max_sentences_per_chunk)

    def chunk(self, text: str) -> list[str]:
        text = text.strip()
        if not text:
            return []

        sentences = re.split(r"(?<=[.!?])(?:[ \t]+|\n+)", text)
        sentences = [
            sentence.strip()
            for sentence in sentences
            if sentence.strip()
        ]

        chunks = []
        for start in range(0, len(sentences), self.max_sentences_per_chunk):
            group = sentences[start : start + self.max_sentences_per_chunk]
            chunks.append(" ".join(group))

        return chunks


class RecursiveChunker:
    """
    Recursively split text using separators in priority order.

    Default separator priority:
        ["\n\n", "\n", ". ", " ", ""]
    """

    DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

    def __init__(self, separators: list[str] | None = None, chunk_size: int = 500) -> None:
        self.separators = self.DEFAULT_SEPARATORS if separators is None else list(separators)
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        text = text.strip()
        if not text:
            return []

        return self._split(text, list(self.separators))

    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        current_text = current_text.strip()
        if not current_text:
            return []

        chunk_size = max(1, self.chunk_size)

    # Văn bản đã đủ nhỏ, không cần chia tiếp.
        if len(current_text) <= chunk_size:
            return [current_text]

    # Không còn separator thì chia trực tiếp theo số ký tự.
        if not remaining_separators:
            return [
            current_text[start : start + chunk_size].strip()
            for start in range(0, len(current_text), chunk_size)
            if current_text[start : start + chunk_size].strip()
        ]

        separator = remaining_separators[0]
        next_separators = remaining_separators[1:]

    # Separator rỗng là phương án cuối: chia theo ký tự.
        if separator == "":
            return [
            current_text[start : start + chunk_size].strip()
            for start in range(0, len(current_text), chunk_size)
            if current_text[start : start + chunk_size].strip()
        ]

    # Không tìm thấy separator hiện tại thì thử separator kế tiếp.
        if separator not in current_text:
            return self._split(current_text, next_separators)

        parts = current_text.split(separator)
        chunks: list[str] = []
        current_chunk = ""

        for index, part in enumerate(parts):
        # Gắn lại separator để không làm mất cấu trúc văn bản.
            fragment = part
            if index < len(parts) - 1:
                fragment += separator

            candidate = current_chunk + fragment

            if len(candidate) <= chunk_size:
                current_chunk = candidate
                continue

            if current_chunk.strip():
                chunks.append(current_chunk.strip())

            current_chunk = ""

        # Fragment vẫn quá dài: chia tiếp bằng separator cấp thấp hơn.
            if len(fragment) > chunk_size:
                chunks.extend(
                    self._split(fragment, next_separators)
            )
            else:
                current_chunk = fragment

        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        return chunks


class BulletAwareChunker:
    """Split policy text while preserving complete bullet rules.

    Markdown headings are repeated as context in their child chunks. Short
    bullets are grouped without exceeding ``max_bullets_per_chunk`` or
    ``chunk_size``. Oversized prose or rules use RecursiveChunker as a
    fallback so every returned chunk stays bounded when possible.
    """

    HEADING_PATTERN = re.compile(r"^#{1,6}\s+.+$")
    BULLET_PATTERN = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+.+$")

    def __init__(
        self,
        chunk_size: int = 500,
        max_bullets_per_chunk: int = 3,
    ) -> None:
        self.chunk_size = max(1, chunk_size)
        self.max_bullets_per_chunk = max(1, max_bullets_per_chunk)

    def _parse_blocks(self, text: str) -> list[tuple[str, str]]:
        """Parse Markdown into heading, bullet and prose blocks."""
        blocks: list[tuple[str, str]] = []
        prose_lines: list[str] = []

        def flush_prose() -> None:
            if not prose_lines:
                return
            content = " ".join(line.strip() for line in prose_lines).strip()
            if content:
                blocks.append(("prose", content))
            prose_lines.clear()

        for raw_line in text.splitlines():
            stripped = raw_line.strip()

            if not stripped:
                flush_prose()
                continue

            if self.HEADING_PATTERN.match(stripped):
                flush_prose()
                blocks.append(("heading", stripped))
                continue

            if self.BULLET_PATTERN.match(raw_line):
                flush_prose()
                blocks.append(("bullet", stripped))
                continue

            prose_lines.append(stripped)

        flush_prose()
        return blocks

    def chunk(self, text: str) -> list[str]:
        text = text.strip()
        if not text:
            return []

        chunks: list[str] = []
        current_heading = ""
        current_parts: list[str] = []
        current_bullet_count = 0

        def candidate_text(parts: list[str]) -> str:
            values = ([current_heading] if current_heading else []) + parts
            return "\n\n".join(value for value in values if value).strip()

        def flush_current() -> None:
            nonlocal current_parts, current_bullet_count
            if current_parts:
                content = candidate_text(current_parts)
                if content:
                    chunks.append(content)
            current_parts = []
            current_bullet_count = 0

        for kind, block in self._parse_blocks(text):
            if kind == "heading":
                flush_current()
                current_heading = block
                continue

            next_bullet_count = current_bullet_count + (1 if kind == "bullet" else 0)
            candidate = candidate_text(current_parts + [block])
            exceeds_size = len(candidate) > self.chunk_size
            exceeds_bullet_limit = (
                kind == "bullet"
                and next_bullet_count > self.max_bullets_per_chunk
            )

            if current_parts and (exceeds_size or exceeds_bullet_limit):
                flush_current()
                candidate = candidate_text([block])

            if len(candidate) <= self.chunk_size:
                current_parts.append(block)
                if kind == "bullet":
                    current_bullet_count += 1
                continue

            prefix = f"{current_heading}\n\n" if current_heading else ""
            available_size = max(1, self.chunk_size - len(prefix))
            splitter = RecursiveChunker(chunk_size=available_size)
            for piece in splitter.chunk(block):
                content = f"{prefix}{piece}".strip()
                if content:
                    chunks.append(content)

        flush_current()

        if not chunks and current_heading:
            return [current_heading]
        return chunks


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    cosine_similarity = dot(a, b) / (||a|| * ||b||)

    Returns 0.0 if either vector has zero magnitude.
    """
    dot_product = _dot(vec_a, vec_b)

    magnitude_a = math.sqrt(_dot(vec_a, vec_a))
    magnitude_b = math.sqrt(_dot(vec_b, vec_b))

    if magnitude_a == 0.0 or magnitude_b == 0.0:
        return 0.0

    return dot_product / (magnitude_a * magnitude_b)


class ChunkingStrategyComparator:
    """Run all built-in chunking strategies and compare their results."""

    def compare(self, text: str, chunk_size: int = 200) -> dict:
        safe_chunk_size = max(1, chunk_size)
        safe_overlap = min(50, safe_chunk_size - 1)

        strategies = {
            "fixed_size": FixedSizeChunker(
                chunk_size=safe_chunk_size,
                overlap=safe_overlap,
            ),
            "by_sentences": SentenceChunker(
                max_sentences_per_chunk=3,
            ),
            "recursive": RecursiveChunker(
                chunk_size=safe_chunk_size,
            ),
        }

        comparison = {}

        for strategy_name, chunker in strategies.items():
            chunks = chunker.chunk(text)
            count = len(chunks)

            if count > 0:
                avg_length = sum(len(chunk) for chunk in chunks) / count
            else:
                avg_length = 0.0

            comparison[strategy_name] = {
                "count": count,
                "avg_length": avg_length,
                "chunks": chunks,
            }
        return comparison

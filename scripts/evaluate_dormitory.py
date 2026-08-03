"""Evaluate Nguyễn Duy Lâm's bullet-aware retrieval strategy.

Run from the repository root:

    python -X utf8 scripts/evaluate_dormitory.py --provider local
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from ingest import build_knowledge_base  # noqa: E402
from src import BulletAwareChunker, LocalEmbedder, _mock_embed  # noqa: E402


BENCHMARKS = [
    {
        "query": "What are the quiet hours on weekdays and weekends at VinUni?",
        "expected_doc_id": "vinuni-quiet-hours",
        "metadata_filter": None,
    },
    {
        "query": "How many guests may each resident have at the same time?",
        "expected_doc_id": "vinuni-guest-visit-policy",
        "metadata_filter": None,
    },
    {
        "query": "When must daytime guests leave the residence?",
        "expected_doc_id": "vinuni-guest-visit-policy",
        "metadata_filter": None,
    },
    {
        "query": "What steps are required during move-in and move-out?",
        "expected_doc_id": "vinuni-move-in-out",
        "metadata_filter": {"audience": "student"},
    },
    {
        "query": "What are the quiet hours at Columbia College residence halls?",
        "expected_doc_id": "columbia-residence-hall-quiet-hours",
        "metadata_filter": None,
    },
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", choices=("local", "mock"), default="local")
    parser.add_argument("--data-dir", default="data/dormitory")
    parser.add_argument("--chunk-size", type=int, default=300)
    parser.add_argument("--max-bullets", type=int, default=3)
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Load an already-downloaded Hugging Face model without network checks.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.offline:
        os.environ["HF_HUB_OFFLINE"] = "1"
        os.environ["TRANSFORMERS_OFFLINE"] = "1"
    embedder = LocalEmbedder() if args.provider == "local" else _mock_embed
    chunker = BulletAwareChunker(
        chunk_size=args.chunk_size,
        max_bullets_per_chunk=args.max_bullets,
    )
    store = build_knowledge_base(
        args.data_dir,
        embedding_fn=embedder,
        chunker=chunker,
        collection_name="nguyen_duy_lam_bullet_aware",
    )

    backend_name = getattr(embedder, "_backend_name", type(embedder).__name__)
    print(f"Backend: {backend_name}")
    print(f"Strategy: BulletAwareChunker(chunk_size={args.chunk_size}, "
          f"max_bullets_per_chunk={args.max_bullets})")
    print(f"Collection size: {store.get_collection_size()} chunks")

    total_points = 0
    for index, benchmark in enumerate(BENCHMARKS, start=1):
        metadata_filter = benchmark["metadata_filter"]
        if metadata_filter:
            results = store.search_with_filter(
                benchmark["query"],
                top_k=args.top_k,
                metadata_filter=metadata_filter,
            )
        else:
            results = store.search(benchmark["query"], top_k=args.top_k)

        expected_doc_id = benchmark["expected_doc_id"]
        relevant_rank = next(
            (
                rank
                for rank, result in enumerate(results, start=1)
                if result["metadata"].get("doc_id") == expected_doc_id
            ),
            None,
        )
        points = 2 if relevant_rank == 1 else 1 if relevant_rank else 0
        total_points += points

        print(f"\nQ{index}: {benchmark['query']}")
        print(f"Expected: {expected_doc_id}")
        print(f"Filter: {metadata_filter}")
        print(f"Relevant rank: {relevant_rank or 'not in top-k'} | retrieval points: {points}/2")
        for rank, result in enumerate(results, start=1):
            metadata = result["metadata"]
            preview = " ".join(result["content"].split())[:180]
            print(
                f"  {rank}. score={result['score']:.6f} "
                f"doc_id={metadata.get('doc_id')} "
                f"chunk={metadata.get('chunk_index')}"
            )
            print(f"     {preview}")

    print(f"\nRetrieval score: {total_points}/10")
    print("Note: this score measures relevant-document rank; verify agent answers separately.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

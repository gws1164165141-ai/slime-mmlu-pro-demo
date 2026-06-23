#!/usr/bin/env python3
"""Prepare small MMLU-Pro JSONL splits for a slime demo."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable

from datasets import load_dataset


LETTERS = "ABCDEFGHIJ"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", default="data", help="Directory for JSONL outputs.")
    parser.add_argument("--train-size", type=int, default=500)
    parser.add_argument("--dev-size", type=int, default=100)
    parser.add_argument("--train-offset", type=int, default=0)
    parser.add_argument("--dev-offset", type=int, default=500)
    return parser.parse_args()


def normalize_label(example: dict[str, Any]) -> str:
    answer = example.get("answer")
    if isinstance(answer, str):
        answer = answer.strip().upper()
        if answer in LETTERS:
            return answer

    answer_index = example.get("answer_index")
    if isinstance(answer_index, int) and 0 <= answer_index < len(LETTERS):
        return LETTERS[answer_index]

    raise ValueError(f"Cannot normalize label from example keys: {sorted(example.keys())}")


def normalize_options(options: Any) -> list[str]:
    if not isinstance(options, list):
        raise ValueError(f"Expected options to be a list, got {type(options).__name__}")
    if not 2 <= len(options) <= len(LETTERS):
        raise ValueError(f"Expected 2-{len(LETTERS)} options, got {len(options)}")
    return [str(option).strip() for option in options]


def build_prompt(example: dict[str, Any]) -> str:
    question = str(example.get("question", "")).strip()
    options = normalize_options(example.get("options"))
    option_lines = [f"{LETTERS[idx]}. {option}" for idx, option in enumerate(options)]
    return "\n".join(
        [
            "Answer the following multiple-choice question.",
            "Choose exactly one option from A through J.",
            "",
            f"Question: {question}",
            "",
            "Options:",
            *option_lines,
            "",
            "Think step by step, then put your final choice on the last line.",
            "Final answer format: Final answer: <A-J>",
        ]
    )


def convert_example(example: dict[str, Any]) -> dict[str, Any]:
    label = normalize_label(example)
    metadata = {
        "label": label,
        "question_id": example.get("question_id"),
        "category": example.get("category"),
        "src": example.get("src"),
        "answer_index": example.get("answer_index"),
    }
    return {
        "prompt": build_prompt(example),
        "label": label,
        "metadata": metadata,
    }


def select_examples(split: Any, offset: int, size: int, split_name: str) -> list[dict[str, Any]]:
    if offset < 0 or size < 0:
        raise ValueError("offset and size must be non-negative")
    if offset >= len(split):
        raise ValueError(
            f"Offset {offset} is outside split '{split_name}' with length {len(split)}"
        )
    return [convert_example(row) for row in list(split)[offset : offset + size]]


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> None:
    args = parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    dataset = load_dataset("TIGER-Lab/MMLU-Pro")
    if "test" not in dataset:
        raise ValueError("TIGER-Lab/MMLU-Pro dataset is missing required 'test' split")
    if "validation" not in dataset:
        raise ValueError("TIGER-Lab/MMLU-Pro dataset is missing required 'validation' split")

    train_rows = select_examples(dataset["test"], args.train_offset, args.train_size, "test")
    dev_rows = select_examples(dataset["test"], args.dev_offset, args.dev_size, "test")
    val_rows = [convert_example(row) for row in dataset["validation"]]

    train_path = out_dir / f"train_{len(train_rows)}.jsonl"
    dev_path = out_dir / f"dev_{len(dev_rows)}.jsonl"
    val_path = out_dir / f"val_{len(val_rows)}.jsonl"

    write_jsonl(train_path, train_rows)
    print(f"Wrote {len(train_rows)} rows to {train_path}")
    write_jsonl(dev_path, dev_rows)
    print(f"Wrote {len(dev_rows)} rows to {dev_path}")
    write_jsonl(val_path, val_rows)
    print(f"Wrote {len(val_rows)} rows to {val_path}")


if __name__ == "__main__":
    main()

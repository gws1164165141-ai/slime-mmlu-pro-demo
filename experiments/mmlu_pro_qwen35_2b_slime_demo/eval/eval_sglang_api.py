#!/usr/bin/env python3
"""Evaluate JSONL prompts against an OpenAI-compatible SGLang chat API."""

from __future__ import annotations

import argparse
import json
import re
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


VALID_LABELS = set("ABCDEFGHIJ")
FINAL_ANSWER_RE = re.compile(r"final\s+answer\s*[:：]\s*\(?\s*([A-J])\s*\)?", re.IGNORECASE)
ANSWER_RE = re.compile(
    r"(?:the\s+answer\s+is|answer)\s*[:：]?\s*\(?\s*([A-J])\s*\)?",
    re.IGNORECASE,
)
TRAILING_LETTER_RE = re.compile(r"(?:^|[\s\n])([A-J])(?:[\s\.\)]*)$", re.IGNORECASE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", required=True, help="Input JSONL with prompt, label, metadata.")
    parser.add_argument("--url", default="http://localhost:30000/v1/chat/completions")
    parser.add_argument("--model", default="Qwen/Qwen3.5-2B")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=512)
    parser.add_argument("--out", default="outputs/eval_results.jsonl")
    return parser.parse_args()


def extract_answer(text: Any) -> str | None:
    if not isinstance(text, str):
        return None
    for pattern in (FINAL_ANSWER_RE, ANSWER_RE, TRAILING_LETTER_RE):
        matches = list(pattern.finditer(text))
        if matches:
            return matches[-1].group(1).upper()
    return None


def normalize_label(row: dict[str, Any]) -> str | None:
    label = row.get("label")
    if not isinstance(label, str) and isinstance(row.get("metadata"), dict):
        label = row["metadata"].get("label")
    if not isinstance(label, str):
        return None
    label = label.strip().upper()
    return label if label in VALID_LABELS else None


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            if "prompt" not in row:
                raise ValueError(f"Missing prompt at {path}:{line_no}")
            rows.append(row)
    return rows


def call_chat_completion(
    url: str,
    model: str,
    prompt: str,
    temperature: float,
    max_tokens: int,
    timeout: float = 120.0,
) -> str:
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        data = json.loads(response.read().decode("utf-8"))
    return data["choices"][0]["message"]["content"]


def write_result(path: Path, row: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> None:
    args = parse_args()
    data_path = Path(args.data)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("", encoding="utf-8")

    rows = read_jsonl(data_path)
    correct = 0
    evaluated = 0

    for idx, row in enumerate(rows, start=1):
        label = normalize_label(row)
        started_at = time.time()
        error = None
        response_text = ""
        prediction = None
        is_correct = False

        try:
            response_text = call_chat_completion(
                args.url,
                args.model,
                row["prompt"],
                args.temperature,
                args.max_tokens,
            )
            prediction = extract_answer(response_text)
            is_correct = label is not None and prediction == label
        except (urllib.error.URLError, TimeoutError, KeyError, json.JSONDecodeError) as exc:
            error = repr(exc)

        evaluated += 1
        correct += int(is_correct)
        result = {
            "index": idx - 1,
            "prompt": row["prompt"],
            "label": label,
            "prediction": prediction,
            "correct": is_correct,
            "response": response_text,
            "metadata": row.get("metadata", {}),
            "error": error,
            "latency_sec": round(time.time() - started_at, 4),
        }
        write_result(out_path, result)

        running_accuracy = correct / evaluated if evaluated else 0.0
        print(f"[{idx}/{len(rows)}] prediction={prediction} label={label} acc={running_accuracy:.4f}")

    accuracy = correct / evaluated if evaluated else 0.0
    print(f"Accuracy: {accuracy:.4f} ({correct}/{evaluated})")
    print(f"Wrote results to {out_path}")


if __name__ == "__main__":
    main()

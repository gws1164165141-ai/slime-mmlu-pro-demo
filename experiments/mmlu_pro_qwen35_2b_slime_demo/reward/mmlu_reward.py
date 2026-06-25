"""Reward utilities for MMLU-Pro multiple-choice answers."""

from __future__ import annotations

import re
from typing import Any


VALID_LABELS = set("ABCDEFGHIJ")

FINAL_ANSWER_RE = re.compile(r"final\s+answer\s*[:：]\s*\(?\s*([A-J])\s*\)?", re.IGNORECASE)
ANSWER_RE = re.compile(
    r"(?:the\s+answer\s+is|answer)\s*[:：]?\s*\(?\s*([A-J])\s*\)?",
    re.IGNORECASE,
)
TRAILING_LETTER_RE = re.compile(r"(?:^|[\s\n])([A-J])(?:[\s\.\)]*)$", re.IGNORECASE)
LEADING_OPTION_RE = re.compile(r"^\s*([A-J])(?:[\.\)]|\s|$)", re.IGNORECASE)
ASSISTANT_BLOCK_RE = re.compile(r"<\|im_start\|>assistant\n(.*?)(?:<\|im_end\|>|$)", re.DOTALL | re.IGNORECASE)


def normalize_label(label: Any) -> str | None:
    if not isinstance(label, str):
        return None
    label = label.strip().upper()
    return label if label in VALID_LABELS else None


def _assistant_text(text: str) -> str:
    matches = list(ASSISTANT_BLOCK_RE.finditer(text))
    if matches:
        return matches[-1].group(1).strip()
    return text.strip()


def extract_answer(text: Any) -> str | None:
    """Extract an A-J answer from common final-answer formats."""
    if not isinstance(text, str):
        return None

    body = _assistant_text(text)

    for pattern in (FINAL_ANSWER_RE, ANSWER_RE, TRAILING_LETTER_RE):
        matches = list(pattern.finditer(body))
        if matches:
            return matches[-1].group(1).upper()

    leading_match = LEADING_OPTION_RE.search(body)
    if leading_match:
        return leading_match.group(1).upper()

    return None

def compute_reward(response: Any, label: Any) -> float:
    expected = normalize_label(label)
    if expected is None:
        return 0.0

    predicted = extract_answer(response)
    if predicted is None:
        return 0.0

    return 1.0 if predicted == expected else 0.0


def _get_sample_value(sample: Any, key: str) -> Any:
    if isinstance(sample, dict):
        return sample.get(key)
    return getattr(sample, key, None)


def _get_response(sample: Any) -> Any:
    for key in ("response", "output", "completion"):
        value = _get_sample_value(sample, key)
        if value is not None:
            return value
    return None


def _get_label(sample: Any) -> Any:
    direct_label = _get_sample_value(sample, "label")
    if direct_label is not None:
        return direct_label

    metadata = _get_sample_value(sample, "metadata")
    if isinstance(metadata, dict):
        return metadata.get("label")
    return None


async def reward_func(args: Any, sample: Any, **kwargs: Any) -> float:
    """slime-compatible async reward entrypoint."""
    del args, kwargs
    return compute_reward(_get_response(sample), _get_label(sample))

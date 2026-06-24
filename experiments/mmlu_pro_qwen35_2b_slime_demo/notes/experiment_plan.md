# MMLU-Pro Qwen3.5-2B slime Demo Plan

## Goal

Run a small, server-side reinforcement learning demo on MMLU-Pro to verify the data pipeline, reward function, slime wiring, and evaluation loop before scaling.

## Model

- Base model: `Qwen/Qwen3.5-2B` or the matching local checkpoint available on the server.
- Hardware target: 8x RTX 3090.
- This is a smoke/demo run, not a final training recipe.

## Data

- Source dataset: `TIGER-Lab/MMLU-Pro` from Hugging Face.
- Prepared files:
  - `data/train_500.jsonl`
  - `data/dev_100.jsonl`
  - `data/val_70.jsonl`
- Each row contains:
  - `prompt`
  - `label`
  - `metadata`
- Prompt final format requirement: `Final answer: <A-J>`.

## Reward

- Reward file: `reward/mmlu_reward.py`.
- Extraction accepts:
  - `Final answer: A`
  - `The answer is (B)`
  - `Answer: C`
  - a trailing standalone `A`-`J`
- Correct answer: `1.0`.
- Wrong answer or invalid format: `0.0`.

## Phase 1 Hyperparameters

- `rollout_batch_size=2`
- `n_samples_per_prompt=2`
- `global_batch_size=4`
- `num_steps_per_rollout=1`
- `num_rollout=5`
- `max_response_len=512`
- Temperature: start with `0.7` for rollout diversity.

## Metrics To Record

- Train reward mean and distribution.
- Dev accuracy from `eval/eval_sglang_api.py`.
- Invalid-format rate.
- Answer extraction failure count.
- Average response length.
- Rollout latency and tokens per second.
- GPU memory usage per card.
- Any OOM, timeout, or API failure details.

## Baseline eval: Qwen3.5-2B + SGLang + MMLU-Pro dev_100 direct-answer

Date: 2026-06-24

Setup:
- Model: Qwen3.5-2B
- Serving engine: SGLang
- API endpoint: http://localhost:30000/v1/chat/completions
- Dataset: MMLU-Pro dev_100
- Prompt mode: direct-answer
- Generation:
  - temperature = 0
  - max_tokens = 8

Result:
- total = 100
- errors = 0
- prediction_none = 0
- correct = 19
- accuracy = 0.19

Notes:
- The original step-by-step prompt caused long reasoning outputs and was truncated before the final answer.
- Direct-answer prompt avoids truncation and allows stable A-J answer extraction.
- This is a direct-answer baseline, not a CoT baseline.

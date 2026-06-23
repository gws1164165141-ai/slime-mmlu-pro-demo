#!/usr/bin/env bash
set -euo pipefail

# Server-side slime demo draft for 8x RTX 3090. Review paths and slime CLI flags
# against the target server before running.

PROJECT_ROOT="${PROJECT_ROOT:-/workspace/myproject1}"
EXP_DIR="${EXP_DIR:-${PROJECT_ROOT}/experiments/mmlu_pro_qwen35_2b_slime_demo}"
DATA_DIR="${DATA_DIR:-${EXP_DIR}/data}"
OUTPUT_DIR="${OUTPUT_DIR:-${EXP_DIR}/outputs/slime_qwen35_2b_mmlu_pro_demo}"
MODEL_PATH="${MODEL_PATH:-Qwen/Qwen3.5-2B}"
REWARD_FILE="${REWARD_FILE:-${EXP_DIR}/reward/mmlu_reward.py}"

TRAIN_DATA="${TRAIN_DATA:-${DATA_DIR}/train_500.jsonl}"
DEV_DATA="${DEV_DATA:-${DATA_DIR}/dev_100.jsonl}"

mkdir -p "${OUTPUT_DIR}"

export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0,1,2,3,4,5,6,7}"
export TOKENIZERS_PARALLELISM=false

# Small-batch constraints for 8x 3090:
# - rollout_batch_size=2 keeps rollout memory low.
# - n_samples_per_prompt=2 gives 4 completions per rollout batch.
# - global_batch_size=4 matches rollout_batch_size * n_samples_per_prompt.
# - num_steps_per_rollout=1 avoids building up stale rollouts.
# - num_rollout=5 is intended only as a smoke/demo run.
# - max_response_len=512 bounds generation memory and latency.

python -m slime \
  --model "${MODEL_PATH}" \
  --train-data "${TRAIN_DATA}" \
  --eval-data "${DEV_DATA}" \
  --reward-func-path "${REWARD_FILE}" \
  --output-dir "${OUTPUT_DIR}" \
  --rollout-batch-size 2 \
  --n-samples-per-prompt 2 \
  --global-batch-size 4 \
  --num-steps-per-rollout 1 \
  --num-rollout 5 \
  --max-response-len 512 \
  --temperature 0.7

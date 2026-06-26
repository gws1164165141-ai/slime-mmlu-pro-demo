#!/usr/bin/env bash
set -ex

# Minimal SLIME GRPO smoke test for Qwen2.5-1.5B-Instruct on MMLU-Pro.
# Goal: validate rollout -> reward -> ref_log_probs -> actor train -> checkpoint save.
# This is not a real training recipe.

pkill -9 sglang 2>/dev/null || true
ray stop --force 2>/dev/null || true
pkill -9 ray python 2>/dev/null || true
sleep 2

export PYTHONUNBUFFERED=1

# This script is intended to run inside the slimerl/slime Docker container.
# Required container paths:
#   /root/slime
#   /root/Megatron-LM
#   /workspace/demo
#   /models/Qwen2.5-1.5B-Instruct
#   /outputs/converted_models/qwen2.5-1.5B-Instruct_torch_dist

cd /root/slime

export PYTHONPATH="/workspace/demo/reward:/root/slime:/root/Megatron-LM:${PYTHONPATH:-}"

source /workspace/demo/slime_scripts/models/qwen2.5-1.5B.sh

CKPT_ARGS=(
   --hf-checkpoint /models/Qwen2.5-1.5B-Instruct
   --ref-load /outputs/converted_models/qwen2.5-1.5B-Instruct_torch_dist
   --save /outputs/mmlu_pro_runs/qwen2.5-1.5B-Instruct-tp2-direct-b2-r4
   --save-interval 9999
)

ROLLOUT_ARGS=(
   --prompt-data /workspace/demo/data/train_500_forced_choice.jsonl
   --input-key prompt
   --label-key label
   --apply-chat-template
   --rollout-shuffle

   --custom-rm-path mmlu_reward_partial.reward_func

   --num-rollout 4
   --rollout-batch-size 2
   --n-samples-per-prompt 1
   --num-steps-per-rollout 1
   --global-batch-size 2

   --rollout-max-response-len 8
   --rollout-temperature 0.7
)

PERF_ARGS=(
   --tensor-model-parallel-size 2
   --pipeline-model-parallel-size 1
   --context-parallel-size 1
   --expert-model-parallel-size 1
   --expert-tensor-parallel-size 1

   --seq-length 512
)

GRPO_ARGS=(
   --advantage-estimator grpo
   --use-kl-loss
   --kl-loss-coef 0.00
   --kl-loss-type low_var_kl
   --entropy-coef 0.00
   --eps-clip 0.2
   --eps-clip-high 0.28
)

OPTIMIZER_ARGS=(
   --optimizer adam
   --lr 1e-6
   --lr-decay-style constant
   --weight-decay 0.1
   --adam-beta1 0.9
   --adam-beta2 0.98
)

SGLANG_ARGS=(
   --rollout-num-gpus-per-engine 1
   --sglang-mem-fraction-static 0.20
)

MISC_ARGS=(
   --attention-dropout 0.0
   --hidden-dropout 0.0
   --accumulate-allreduce-grads-in-fp32
   --attention-softmax-in-fp32
   --attention-backend flash
)

ray start --head --node-ip-address 127.0.0.1 --num-gpus 2 --disable-usage-stats

ray job submit --address="http://127.0.0.1:8265" \
   --runtime-env-json='{
     "env_vars": {
        "PYTHONPATH": "/workspace/demo/reward:/root/slime:/root/Megatron-LM",
        "CUDA_DEVICE_MAX_CONNECTIONS": "1",
        "NVTE_FLASH_ATTN": "1",
        "NVTE_FUSED_ATTN": "0",
        "NVTE_UNFUSED_ATTN": "0",
        "NVTE_ALLOW_NONDETERMINISTIC_ALGO": "1",
        "NCCL_DEBUG": "WARN",
        "NCCL_IGNORE_DISABLED_P2P": "1"
     }
   }' \
   -- python3 train.py \
   --actor-num-nodes 1 \
   --actor-num-gpus-per-node 2 \
   --colocate \
   "${MODEL_ARGS[@]}" \
   "${CKPT_ARGS[@]}" \
   "${ROLLOUT_ARGS[@]}" \
   "${OPTIMIZER_ARGS[@]}" \
   "${GRPO_ARGS[@]}" \
   "${PERF_ARGS[@]}" \
   "${SGLANG_ARGS[@]}" \
   "${MISC_ARGS[@]}"

# myproject1

This repository is used for preparing a small RL post-training demo.

## Demo Target

- Framework: slime
- Model: Qwen3.5-2B
- Dataset: MMLU-Pro
- Goal: run a minimal rollout -> reward -> train -> eval loop

## Current Workflow

Because Codex desktop runs locally, we first prepare code locally, then copy the prepared scripts to the 8x3090 server.

## Folder Structure

```text
experiments/
└── mmlu_pro_qwen35_2b_slime_demo/
    ├── data_scripts/
    ├── reward/
    ├── eval/
    ├── slime_scripts/
    ├── notes/
    ├── data/
    └── outputs/


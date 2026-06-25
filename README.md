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

<img width="1491" height="1055" alt="image" src="https://github.com/user-attachments/assets/f5e580ed-aa1f-4716-91fa-d7396739de31" />

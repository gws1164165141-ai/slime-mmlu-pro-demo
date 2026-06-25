# Debug Log

本文档用于记录 debug（排错）历史。每条记录都要写清楚问题现象、报错信息、原因判断、解决方法、验证方法和剩余风险。以后遇到任何新问题，都应该追加到这里。

## 记录模板

### YYYY-MM-DD 问题标题

- 问题现象：
- 报错信息：
- 原因判断：
- 解决方法：
- 如何验证修复成功：
- 是否还存在风险：

## 2026-06-23 GitHub remote 指向错误仓库

- 问题现象：本地推送或拉取 GitHub 仓库时失败。
- 报错信息：`Repository not found`。
- 原因判断：Git remote（远程仓库地址）可能指向了错误仓库，或者当前账号没有权限访问该仓库。
- 解决方法：检查 `git remote -v`，确认 origin 指向正确仓库；如有错误，使用 `git remote set-url origin <正确仓库地址>` 修改。
- 如何验证修复成功：执行 `git ls-remote origin` 能列出远程引用；执行 `git push` 不再出现 `Repository not found`。
- 是否还存在风险：如果 GitHub 权限、SSH key、token 或仓库可见性配置不正确，仍然可能失败。

## 2026-06-23 服务器无法访问 huggingface.co

- 问题现象：服务器运行数据准备脚本或下载模型时，无法连接 Hugging Face。
- 报错信息：可能出现连接超时、DNS 解析失败、SSL 连接失败，或访问 `https://huggingface.co` 失败。
- 原因判断：服务器网络无法直接访问 `huggingface.co`，可能是网络出口、DNS、代理或防火墙限制。
- 解决方法：先用 `curl -I https://huggingface.co` 验证；如果不可访问，改用可访问的镜像源。
- 如何验证修复成功：服务器能成功下载 `TIGER-Lab/MMLU-Pro` 数据集，或能访问模型文件列表。
- 是否还存在风险：镜像源可能不稳定；某些模型文件可能没有同步；下载大文件仍可能中断。

## 2026-06-23 hf-mirror.com 可访问，需要设置 HF_ENDPOINT

- 问题现象：`huggingface.co` 不可访问，但 `hf-mirror.com` 可以访问。
- 报错信息：直接访问 Hugging Face 失败；访问 `https://hf-mirror.com` 成功。
- 原因判断：服务器需要通过 Hugging Face 镜像站下载数据或模型。
- 解决方法：在服务器运行相关命令前设置环境变量：

```bash
export HF_ENDPOINT=https://hf-mirror.com
```

PowerShell 本地测试时可以使用：

```powershell
$env:HF_ENDPOINT="https://hf-mirror.com"
```

- 如何验证修复成功：运行 `python data_scripts/prepare_mmlu_pro.py --out-dir data --train-size 20 --dev-size 10` 能成功下载并生成数据。
- 是否还存在风险：镜像站内容可能滞后；如果下载模型权重，还要确认模型许可和文件完整性。

## 2026-06-23 Windows/Linux 路径差异

- 问题现象：本地 Windows 命令和服务器 Linux 命令不能直接互相复制。
- 报错信息：常见错误包括路径不存在、反斜杠转义错误、脚本找不到文件。
- 原因判断：本地路径是 `D:\myproject1`，服务器路径是 `~/workspace/slime-mmlu-pro-demo`；Windows 使用反斜杠，Linux 使用正斜杠。
- 解决方法：文档中分别写 Windows 和 Linux 命令；shell 脚本中使用 Linux 路径；Python 尽量用 `pathlib.Path` 处理路径。
- 如何验证修复成功：本地能运行 reward 单测；服务器能在 `~/workspace/slime-mmlu-pro-demo` 下运行数据准备命令。
- 是否还存在风险：手动复制命令时仍可能混用路径；后续文档需要继续标明运行环境。

## 2026-06-23 data 目录不应该提交到 Git

- 问题现象：运行数据准备脚本后，`data/` 下会出现 JSONL 数据文件。
- 报错信息：没有固定报错，但 `git status` 可能显示数据文件未跟踪。
- 原因判断：`data/` 是由脚本生成的运行产物，不是源代码；提交数据会让仓库变大，也可能带来版权和同步问题。
- 解决方法：不要把 `data/` 文件加入 Git；如果需要共享数据，应该在服务器上重新生成，或使用明确的数据存储方案。
- 如何验证修复成功：提交前执行 `git status --short`，确认没有 `data/*.jsonl` 被 staged（暂存）。
- 是否还存在风险：如果 `.gitignore` 没有覆盖该目录，仍可能被误 add；提交前必须人工检查。

## 2026-06-23 dev 数据生成 0 行

- 问题现象：运行 `python prepare_mmlu_pro.py --out-dir ..\data --train-size 20 --dev-size 10` 后，train 写入 20 行，但 dev 写入 0 行。
- 报错信息：

```text
Wrote 20 rows to ..\data\train_500.jsonl
Wrote 0 rows to ..\data\dev_100.jsonl
```

- 原因判断：脚本错误地使用 `validation` split 生成 dev，并配合默认 `--dev-offset 500`，而 validation 只有约 70 行，所以切片结果为空。
- 解决方法：改为使用 `test` split 生成 train 和 dev，使用 `validation` split 生成 val；同时输出文件名改为实际行数，并在 offset 越界时抛 `ValueError`。
- 如何验证修复成功：用 mock 数据验证输出为 `train_20.jsonl`、`dev_10.jsonl`、`val_70.jsonl`，且 offset 越界会报错。
- 是否还存在风险：还需要在服务器用真实 `TIGER-Lab/MMLU-Pro` 数据集完整验证。

## 2026-06-25 Qwen3.5-2B HF to Megatron checkpoint conversion

- Goal: Convert local Qwen3.5-2B Hugging Face checkpoint into Megatron torch_dist checkpoint for later SLIME training.
- HF checkpoint on host: `/home/xudongmao/models/Qwen3.5-2B`
- HF checkpoint in container: `/models/Qwen3.5-2B`
- Model args script: `experiments/mmlu_pro_qwen35_2b_slime_demo/slime_scripts/models/qwen3.5-2B.sh`
- Output checkpoint on host: `/data1/xudongmao/slime_outputs/converted_models/qwen3.5-2B_torch_dist`
- Output checkpoint in container: `/outputs/converted_models/qwen3.5-2B_torch_dist`

Key model args:

- `num-layers = 24`
- `hidden-size = 2048`
- `ffn-hidden-size = 6144`
- `num-attention-heads = 8`
- `num-query-groups = 2`
- `kv-channels = 256`
- `vocab-size = 248320`
- `rotary-base = 10000000`
- `rotary-percent = 0.25`

Generated checkpoint files:

- `release/__0_0.distcp`
- `release/__0_1.distcp`
- `release/common.pt`
- `release/metadata.json`
- `latest_checkpointed_iteration.txt`

Validation:

- `latest_checkpointed_iteration.txt = release`
- checkpoint size: about 3.6G
- checkpoint owner on host: `xudongmao:xudongmao`
- GPU 1 was released after conversion.
- GPU 0 remained occupied by the existing SGLang service.

Result: conversion succeeded.

## 2026-06-25 Qwen3.5-2B SLIME smoke training blocked by TE attention backend on RTX 3090

### Goal

Run minimal SLIME smoke training for Qwen3.5-2B on MMLU-Pro.

Expected smoke loop:

```text
rollout -> reward -> ref_log_probs -> policy update
```

### What succeeded

- Docker GPU container started successfully on host GPU 1.
- Ray started successfully.
- SGLang rollout engine started successfully.
- Qwen3.5-2B HF checkpoint was loaded by SGLang.
- Megatron torch_dist checkpoint was loaded successfully.
- Megatron actor to SGLang engine weight update succeeded.
- Rollout generation succeeded.
- Custom reward function `mmlu_reward.reward_func` was called successfully.
- MMLU-Pro `prompt` and `label` fields were valid.

### Failure point

The job consistently failed at Megatron training-side `ref_log_probs` forward.

Main error:

```text
ValueError: No dot product attention backend is available for the provided inputs.
```

### Backend diagnostics

Tested attention backends:

- `--attention-backend flash`
- `--attention-backend fused`
- `--attention-backend unfused`
- attempted `--attention-backend local`, but Megatron only allows local backend with `--spec local`

Transformer Engine debug showed:

```text
compute_capability = sm86
qkv_layout = thd_thd_thd
head_dim_qk = 256
head_dim_v = 256

FlashAttention 3 disabled because compute capability is not sm90.
FlashAttention 2 disabled for the current head_dim / sm86 combination.
FusedAttention disabled because no backend supports the provided input.
UnfusedDotProductAttention disabled because qkv_format = thd.

Available backends = {FlashAttention=False, FusedAttention=False, UnfusedDotProductAttention=False}
Selected backend = NoBackend
```

### Conclusion

Qwen3.5-2B smoke training is blocked on the current RTX 3090 / sm86 environment due to Transformer Engine attention backend incompatibility with Qwen3.5-2B `head_dim=256` and packed THD attention layout.

This is not a data, reward, checkpoint conversion, or SGLang rollout issue.

### Next plan

Use Qwen3.5-0.8B to validate the full SLIME smoke training loop first, because it is smaller and has an official SLIME model script. Keep Qwen3.5-2B as a documented hardware and kernel compatibility issue unless a more suitable GPU, backend, or model spec is available.

## 2026-06-25 Qwen2.5-0.5B MMLU-Pro smoke and reward parser validation

### Summary

Qwen2.5-0.5B-Instruct was used as the smoke model after Qwen3.5-2B was blocked by Transformer Engine attention backend constraints on RTX 3090. The Qwen2.5-0.5B smoke run successfully exercised the full SLIME training loop: checkpoint load, SGLang rollout, custom reward, ref_log_probs forward, actor train, weight update, and checkpoint save.

### Smoke v1: step-by-step prompt

- Script: `experiments/mmlu_pro_qwen35_2b_slime_demo/slime_scripts/run_qwen25_05b_mmlu_pro_smoke.sh`
- Prompt data: `/workspace/demo/data/train_500.jsonl`
- Output: `/outputs/mmlu_pro_smoke/qwen2.5-0.5B-Instruct`
- Result: job succeeded and checkpoint was saved.
- Key finding: `rollout/truncated_ratio = 1.0`, because the prompt asked the model to think step by step while `--rollout-max-response-len` was only 128.

### Smoke v2: short-answer prompt

- Script: `experiments/mmlu_pro_qwen35_2b_slime_demo/slime_scripts/run_qwen25_05b_mmlu_pro_short_answer_smoke.sh`
- Prompt data: `/workspace/demo/data/train_500_short_answer.jsonl`
- Output: `/outputs/mmlu_pro_smoke/qwen2.5-0.5B-Instruct-short-answer`
- Result: job succeeded and checkpoint was saved.
- Key finding: response length dropped substantially and `rollout/truncated_ratio` dropped to 0.25, but raw reward remained blocked by reward parsing because model outputs such as `A. $44,100` were not accepted by the original parser.

### Reward parser fix

The reward parser was updated to extract the last assistant block before parsing, and to accept leading option formats such as `A. $44,100` or `A) ...`. This avoids matching options inside the prompt while supporting common model answer formats.

Validation command result:

- `extract = A`
- `reward_A = 1.0`
- `reward_E = 0.0`
- `final_I = 1.0`

### Smoke v3: short-answer rewardfix

- Script: `experiments/mmlu_pro_qwen35_2b_slime_demo/slime_scripts/run_qwen25_05b_mmlu_pro_short_answer_rewardfix_smoke.sh`
- Prompt data: `/workspace/demo/data/train_500_short_answer.jsonl`
- Output: `/outputs/mmlu_pro_smoke/qwen2.5-0.5B-Instruct-short-answer-rewardfix`
- Result: job succeeded and checkpoint was saved.
- Key metrics: `rollout/raw_reward = 0.25`, `rollout/truncated = 0.25`, and `train/grad_norm` became non-zero.

### Conclusion

The Qwen2.5-0.5B MMLU-Pro smoke path is now validated. The full SLIME loop runs successfully on RTX 3090, and the reward parser can now assign non-zero raw reward for realistic short-answer outputs.


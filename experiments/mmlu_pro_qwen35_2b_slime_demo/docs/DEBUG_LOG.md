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

## 2026-06-25 V6 forced-choice-16-t03 smoke

### Setup

V6 used a forced-choice prompt to suppress reasoning and require the model to output only one uppercase letter from A to J.

- Prompt data: `train_500_forced_choice.jsonl`
- Script: `run_qwen25_05b_mmlu_pro_forced_choice_16_t03_smoke.sh`
- Output: `/outputs/mmlu_pro_smoke/qwen2.5-0.5B-Instruct-forced-choice-16-t03`
- `rollout-max-response-len = 16`
- `rollout-temperature = 0.3`

### Result

The full SLIME smoke chain succeeded: checkpoint loading, SGLang rollout, ref forward, actor train, checkpoint save, and Ray job completion all passed.

Key metrics:

- `rollout/response_len/mean = 2.0`
- `rollout/response_len/max = 2`
- `rollout/truncated_ratio = 0.0`
- `rollout/raw_reward = 0.0`
- `train/grad_norm = 0.0`

### Sample analysis

The forced-choice prompt successfully controlled output format. The model generated single-letter answers instead of long reasoning text.

However, the sampled answers were wrong:

- Atlas discount problem: model output `B`, label was `A`, reward `0.0`.
- Exact-time interest problem: model output `A`, label was `E`, reward `0.0`.

### Conclusion

V6 solved the formatting and truncation problems, but did not produce a correct sampled answer in the current smoke mini-batch. The main bottleneck has moved from output format/truncation to base model option-selection accuracy. Because the smoke batch only contains 4 sampled completions, V6 does not prove that the full dataset accuracy is zero. The next step is V7, which keeps the forced-choice prompt but increases the sampled completions to 16 for a more stable estimate.

## 2026-06-25 V7 forced-choice-16-t03-b16 smoke

### Setup

V7 kept the V6 forced-choice prompt and increased the number of sampled completions from 4 to 16.

- Prompt data: `train_500_forced_choice.jsonl`
- Script: `run_qwen25_05b_mmlu_pro_forced_choice_16_t03_b16_smoke.sh`
- Output: `/outputs/mmlu_pro_smoke/qwen2.5-0.5B-Instruct-forced-choice-16-t03-b16`
- `rollout-max-response-len = 16`
- `rollout-temperature = 0.3`
- `rollout-batch-size = 8`
- `n-samples-per-prompt = 2`
- `global-batch-size = 16`

### Result

The full SLIME smoke chain succeeded: checkpoint loading, rollout, ref forward, actor train, checkpoint save, and Ray job completion all passed.

Key metrics:

- `rollout/response_len/mean = 2.0`
- `rollout/response_len/max = 2`
- `rollout/truncated_ratio = 0.0`
- `rollout/raw_reward = 0.0`
- `train/grad_norm = 0.0`
- `train/global_batch_size = 16`

### Sample analysis

The model continued to follow the forced-choice format and generated single-letter answers. However, the logged examples were still incorrect:

- Exact-time interest problem: model output `A`, label was `E`, reward `0.0`.
- Percent problem: model output `J`, label was `I`, reward `0.0`.

### Conclusion

V7 confirms that the V6 result was not only a 4-sample fluctuation. Even with 16 sampled completions, the forced-choice setting produced no correct reward. The output format and truncation issues are solved, but the base model option-selection accuracy on these MMLU-Pro samples is too low to create a useful RL signal under the current exact-match reward. The next step should be a diagnostic reasoning run to inspect visible reasoning errors, followed by partial reward design or easier warm-up data.

## 2026-06-25 V8 diagnostic-reasoning-512-t03 smoke

### Setup

V8 was designed as a diagnostic reasoning run rather than a reward-improving training run. The prompt asked the model to solve step by step, compute the numeric answer, match it to one option, and end with `Final answer: <A-J>`.

- Prompt data: `train_500_diagnostic_reasoning.jsonl`
- Script: `run_qwen25_05b_mmlu_pro_diagnostic_reasoning_512_t03_smoke.sh`
- Output: `/outputs/mmlu_pro_smoke/qwen2.5-0.5B-Instruct-diagnostic-reasoning-512-t03`
- `rollout-max-response-len = 512`
- `rollout-temperature = 0.3`
- `global-batch-size = 2`

### Result

The full SLIME smoke chain succeeded: checkpoint loading, rollout, ref forward, actor train, checkpoint save, and Ray job completion all passed.

Key metrics:

- `rollout/response_len/mean = 417.5`
- `rollout/response_len/max = 434`
- `rollout/truncated_ratio = 0.0`
- `rollout/raw_reward = 0.0`
- `train/grad_norm = 0.0`

### Visible reasoning analysis

V8 exposed the model visible reasoning errors.

1. Exact-time interest problem:
   - Label: `E = $41.52`
   - Model treated March 15 to August 12 as `1 year`.
   - It computed `1262.77 * 0.08 * 1 = 100.4136`.
   - It then incorrectly matched `$100.41` to `J = $38.70`.
   - Error type: date-span error + option-matching error.

2. Bank discount / proceeds problem:
   - Label: `A = $44,100`
   - Correct discount is `45000 * 0.06 * 120/360 = 900`; proceeds are `45000 - 900 = 44100`.
   - Model treated 120 days as approximately 1 month, then applied a full 6% discount: `45000 * 0.94 = 42300`.
   - It finally selected `F = $900`, confusing the discount amount with the proceeds.
   - Error type: time conversion error + discount formula error + target quantity confusion.

### Conclusion

V8 confirms that the current bottleneck is not only output formatting or truncation. The model can generate long visible reasoning without truncation, but its financial/math reasoning is unreliable. It makes formula, time-span, numeric, and option-matching errors. Under exact-match reward, this produces all-zero rewards and no useful RL gradient. The next step should be partial reward or easier warm-up data rather than more long-reasoning smoke runs.

## 2026-06-26 V9 partial reward parser debug

### Goal
Continue V9 partial reward experiment for Qwen2.5-0.5B-Instruct on MMLU-Pro forced-choice data.
Main question: why did the previous V9 run still show reward 0.0 even though custom-rm-path pointed to mmlu_reward_partial.reward_func.

### Starting point
Formal V9 script had these important settings:
- custom-rm-path = mmlu_reward_partial.reward_func
- global-batch-size = 32
- n-samples-per-prompt = 4
- rollout-temperature = 0.7
- rollout-max-response-len = 16

Expected partial reward behavior:
- correct parsed answer -> 1.0
- parseable but wrong A-J answer -> 0.1
- unparseable answer -> 0.0

### Previous symptom
Earlier V9 logs showed parseable-looking model outputs but reward stayed 0.0:
- assistant I, label A, reward 0.0
- assistant A, label I, reward 0.0
- rollout raw_reward = 0.0
- train grad_norm = 0.0

This was inconsistent with the intended partial reward rule because I vs A should be 0.1, not 0.0.

### Debug reward setup
Created debug reward file:
cp experiments/mmlu_pro_qwen35_2b_slime_demo/reward/mmlu_reward_partial.py experiments/mmlu_pro_qwen35_2b_slime_demo/reward/mmlu_reward_partial_debug.py

Modified mmlu_reward_partial_debug.reward_func to print:
- sample_type
- sample_keys
- kwargs_keys
- response
- label
- computed_reward

Created small batch debug script:
experiments/mmlu_pro_qwen35_2b_slime_demo/slime_scripts/run_qwen25_05b_mmlu_pro_forced_choice_partial_reward_debug_b4_t07_smoke.sh

Important debug config:
- custom-rm-path = mmlu_reward_partial_debug.reward_func
- rollout-batch-size = 2
- n-samples-per-prompt = 2
- global-batch-size = 4
- rollout-temperature = 0.7

Purpose: run a small and fast rollout to inspect reward_func input and computed reward.

### First debug finding
Debug logs showed that SLIME passed a Sample object and _get_response did receive completion strings.
Observed response format:
- F<|im_end|>
- A<|im_end|>
- I<|im_end|>

However computed_reward was still 0.0 at first.
This proved the issue was not missing response fields. The real issue was parser handling of special tokens.

### Parser bug
The parser had become too strict and did not parse bare completions with special tokens such as A<|im_end|>.
Because of this, extract_answer returned None for A<|im_end|>, so compute_reward returned 0.0.

### Parser fix
Fixed _assistant_text in experiments/mmlu_pro_qwen35_2b_slime_demo/reward/mmlu_reward_partial.py.
New behavior: after extracting the assistant body, remove special tokens before parsing.
Special tokens cleaned:
- <|im_end|>
- <|endoftext|>

Validation result after fix:
- extract_answer(A<|im_end|>) = A
- compute_reward(A<|im_end|>, A) = 1.0
- compute_reward(F<|im_end|>, A) = 0.1
- compute_reward(I do not know<|im_end|>, A) = 0.0

This confirms that A<|im_end|> is now parsed correctly and I do not know is not misparsed as option I.

### Second debug run after parser fix
After synchronizing the fixed parser into mmlu_reward_partial_debug.py, the small batch debug run showed:
- response = A<|im_end|>, label = E, computed_reward = 0.1
- response = B<|im_end|>, label = A, computed_reward = 0.1

Rollout log also showed:
- label A, reward 0.1
- label E, reward 0.1
- rollout raw_reward = 0.1

This confirms that partial reward now enters SLIME correctly.

### Remaining issue
Training metrics still showed:
- rollout raw_reward = 0.1
- rollout advantages = 0.0
- train grad_norm = 0.0

This is no longer a parser bug.
Reason: in the small debug batch, all sampled completions received the same reward 0.1. There was no within-group reward difference. For GRPO, equal rewards inside a group produce zero advantage, so policy gradient loss and grad_norm stay zero.

### Current conclusion
Parser and partial reward engineering bugs are fixed.
Confirmed:
- SLIME reward_func receives responses like A<|im_end|>
- parser strips <|im_end|> before answer extraction
- wrong but parseable A-J outputs now receive reward 0.1
- rollout raw_reward changed from 0.0 to 0.1

Still unresolved:
- small batch has no effective policy gradient because all rewards are equal
- need larger batch or easier data to create reward diversity, such as 1.0 vs 0.1 or 0.1 vs 0.0

### Next step
Rerun formal V9 b32 t0.7 with fixed parser.
Success criteria:
- raw_reward >= 0.1 means partial reward is active
- raw_reward > 0.1 means at least some samples likely got 1.0
- advantages nonzero means GRPO has usable relative signal
- grad_norm nonzero means actual policy update occurred

Failure interpretation:
- raw_reward = 0.1, advantages = 0, grad_norm = 0 means partial reward works but all samples have equal reward
- raw_reward > 0.1, advantages nonzero, grad_norm nonzero means V9 produced effective training signal
- raw_reward = 0 means formal V9 did not use the fixed parser or reward path correctly

## 2026-06-26 V9 formal b32 fixed-parser result

### Goal
Rerun formal V9 after fixing the partial reward parser.
This run uses fixed parser + partial reward + forced-choice prompt + larger batch.

### Script
experiments/mmlu_pro_qwen35_2b_slime_demo/slime_scripts/run_qwen25_05b_mmlu_pro_forced_choice_partial_reward_b32_t07_smoke.sh

Important config:
- custom-rm-path = mmlu_reward_partial.reward_func
- rollout-batch-size = 8
- n-samples-per-prompt = 4
- global-batch-size = 32
- rollout-temperature = 0.7
- rollout-max-response-len = 16

### Key rollout samples
First rollout sample:
- model output = A<|im_end|>
- label = A
- reward = 1.0

Finish rollout sample:
- model output = A<|im_end|>
- label = J
- reward = 0.1

Interpretation:
- correct parsed answer receives 1.0
- wrong but parseable A-J answer receives 0.1
- fixed parser is active in the formal V9 run

### Key metrics
Observed metrics:
- rollout/raw_reward = 0.38125
- rollout/rewards approximately 0 after normalization
- rollout/advantages approximately 0 as an averaged scalar
- train/pg_loss = 3.725290298461914e-09
- train/grad_norm = 63.101710973113676
- train/global_batch_size = 32
- Job succeeded
- checkpoint saved to /outputs/mmlu_pro_smoke/qwen2.5-0.5B-Instruct-forced-choice-partial-reward-b32-t07

### Interpretation
This is the first V9 run with effective training signal.
raw_reward = 0.38125 is much larger than 0.1, which means the batch contained some correct answers with reward 1.0 in addition to wrong-but-parseable answers with reward 0.1.
Assuming all 32 samples were parseable, raw_reward = 0.38125 corresponds approximately to 10 correct samples and 22 wrong-but-parseable samples:
0.38125 * 32 = 12.2 total reward
1.0 * 10 + 0.1 * 22 = 12.2

The averaged rollout/advantages value is close to zero because advantages are centered or averaged, but train/grad_norm = 63.1017 confirms that a real gradient update occurred.

### Conclusion
Parser bug is fixed.
Partial reward is active in formal V9.
The larger b32/t0.7 setting created reward diversity.
This run produced a nonzero grad_norm and therefore an effective policy update.

### Next decision
Keep this checkpoint for now because it is the first V9 checkpoint with effective training signal.
Next steps can be:
1. rerun with the same setting to check stability;
2. increase num-rollout or run more training steps;
3. compare fixed-parser V9 against V3 rewardfix and earlier V6/V7 runs;
4. add parser tests to the repository before committing.

## 2026-06-26 Diagnostic reasoning inspection

### Goal
Inspect whether the model is actually reasoning or only producing correct forced-choice letters by chance or option bias.
This diagnostic step uses long reasoning outputs from the existing diagnostic reasoning log.

### Key observation
The formal V9 fixed-parser run produced effective training signal, but that does not prove real reasoning ability.
The V9 forced-choice prompt only asks the model to output one uppercase letter from A to J, so the rollout logs show only the final letter, not the reasoning process.

### Diagnostic sample 1: exact-time interest problem
Question: a loan of 1262.77 is made on March 15 and repaid on August 12 at 8 percent annual interest, using exact time.
Correct label: E.

Model behavior:
- The model wrote the correct simple-interest formula.
- However, it set Time = 1 year.
- It computed 1262.77 * 0.08 * 1 = 100.4136.
- It then tried to match 100.41 to the options and ended with J.

Correct reasoning should use the exact number of days, about 150 days:
interest = 1262.77 * 0.08 * 150 / 365 ≈ 41.52, corresponding to option E.

Interpretation:
The model can imitate a formulaic solution format, but it misread the time condition. This is not reliable reasoning.

### Diagnostic sample 2: bank discount / proceeds problem
Question: a 45000 note is discounted 120 days before due at a 6 percent bank discount rate. Find the proceeds.
Correct label: A.

Model behavior:
- The model incorrectly treated 120 days as approximately 1 month.
- It applied 6 percent in an inconsistent way.
- It confused the discount amount with the proceeds.
- It selected F, which corresponds to 900, the discount amount, not the proceeds.

Correct reasoning should be:
discount = 45000 * 0.06 * 120 / 360 = 900
proceeds = 45000 - 900 = 44100, corresponding to option A.

Interpretation:
The model has weak numerical reasoning and weak financial-term grounding. It confuses discount and proceeds.

### Current conclusion
The fixed-parser V9 result should be interpreted as parser/reward/training-signal success, not as proof that the model can truly reason.
Current evidence shows:
- parser path works
- partial reward works
- formal V9 b32/t0.7 creates nonzero grad_norm
- but base-model explicit reasoning is still unreliable
- the model may produce plausible-looking explanations with wrong assumptions

### Next decision
Before extending training, run or inspect a reasoning-style evaluation on the V9 checkpoint itself.
The key comparison should be:
1. base model reasoning output
2. V9 checkpoint forced-choice output
3. V9 checkpoint reasoning output if possible

Evaluation dimensions:
- final answer correctness
- formula correctness
- unit/time handling
- option matching correctness
- whether the explanation actually supports the final answer

### Practical warning
Do not overclaim that V9 learned reasoning just because raw_reward and grad_norm improved.
The current safe claim is: V9 fixed-parser partial reward produced effective training signal under forced-choice supervision, while reasoning ability remains an open diagnostic question.

## 2026-06-26 V9 checkpoint reasoning inspect

### Goal
Inspect whether the V9 fixed-parser checkpoint improved explicit reasoning, not only forced-choice letter selection.

### Checkpoint loading
The inspect run successfully loaded the V9 checkpoint:
/outputs/mmlu_pro_smoke/qwen2.5-0.5B-Instruct-forced-choice-partial-reward-b32-t07

This confirms the reasoning inspect was run on the V9 fixed-parser checkpoint, not only on the base converted model.

### Result summary
The V9 checkpoint still shows unreliable explicit reasoning.
It can generate long step-by-step explanations, but the reasoning chain often contains wrong assumptions, wrong formulas, arithmetic errors, and wrong option matching.

### Sample 1: exact-time interest problem
Correct label: E.
The model output ended with E, but the reasoning was wrong.
Observed problems:
- it treated March 15 to August 12 as 1 year
- it also claimed the period was 10 months
- it used inconsistent arithmetic
- it said the closest option to 97.30 was 53.60
- it wrote E. 53.60 even though E is 41.52 and 53.60 is C

Interpretation:
The final letter may match the label, but the reasoning trace does not support the answer. This is not reliable mathematical reasoning.

### Sample 2: bank discount / proceeds problem
Correct label: A.
The model output was wrong and the reasoning was also wrong.
Observed problems:
- it used an incorrect formula: Principal * (1 - Discount Rate) * Number of Days
- it failed to use 120 / 360
- it confused discounted amount, discount, and proceeds
- it produced arithmetic and magnitude errors
- it matched to the wrong option

Correct reasoning should be:
discount = 45000 * 0.06 * 120 / 360 = 900
proceeds = 45000 - 900 = 44100
answer = A

### Important interpretation
The formal V9 b32/t0.7 run proved that parser, partial reward, and forced-choice training signal work.
However, the V9 reasoning inspect does not prove improved reasoning ability.
The safe claim is: V9 fixed-parser partial reward improves the forced-choice training signal, while explicit reasoning remains an open and currently weak area.

### Parser note
This reasoning inspect script still uses mmlu_reward.reward_func, not mmlu_reward_partial.reward_func.
Therefore reward = 0.0 in this inspect run should not be used as evidence against the fixed partial reward parser.
Reasoning-format outputs may require additional parser support for formats such as Final answer: A. xxx and boxed A if reasoning-style training is pursued.

### Next decision
Do not overclaim reasoning improvement.
If the next goal is engineering, clean files and commit the parser/reward/script/debug-log changes.
If the next goal is reasoning ability, design a separate reasoning evaluation or reasoning reward instead of only extending forced-choice training.

## 2026-06-26 Qwen3.5-2B attention backend triage plan

### Problem
Qwen3.5-2B SLIME smoke training is blocked by Transformer Engine DotProductAttention backend selection.
The known error is: No dot product attention backend is available for the provided inputs.

### Current evidence
- Qwen3.5-2B HF model exists at /home/xudongmao/models/Qwen3.5-2B.
- Converted Megatron checkpoint exists at /data1/xudongmao/slime_outputs/converted_models/qwen3.5-2B_torch_dist.
- SLIME smoke script exists: experiments/mmlu_pro_qwen35_2b_slime_demo/slime_scripts/run_qwen35_2b_mmlu_pro_smoke.sh.
- Previous smoke reached Megatron forward/ref_log_probs stage, so this is not a reward parser problem.
- The failure happens inside Transformer Engine DotProductAttention backend selection.

### Prior failed attempts
1. attention-backend flash/unfused still failed with No dot product attention backend available.
2. attention-backend local with transformer-impl local failed during argument validation because Megatron requires --attention-backend local only with --spec local.

### Hypotheses
H1: usable TE backend was manually disabled by NVTE_FLASH_ATTN=0 or NVTE_FUSED_ATTN=0.
H2: Qwen3.5-2B head_dim=256 is not accepted by the active backend on RTX 3090 / sm86 under current runtime conditions.
H3: packed THD qkv layout causes unfused backend to be disabled.
H4: padding_causal mask or variable-length layout makes the selected backend ineligible.
H5: GQA config with num_attention_heads=8 and num_query_groups=2 triggers backend ineligibility.
H6: local attention backend cannot be used with qwen3_5 spec and is not a valid quick fix.
H7: qwen3_5 Megatron spec is incompatible with current slime / TE / Megatron environment for this model shape.

### Triage method
Do not directly migrate 0.5B V9 reward scripts to 2B yet.
First collect environment information and run minimal backend-selection tests with NVTE_DEBUG=1 and NVTE_DEBUG_LEVEL=2.
Only change one variable per experiment.
Record every experiment as: config, expected result, actual result, interpretation, next action.

### Immediate next steps
1. Inspect current 2B smoke script and qwen3.5-2B model args.
2. Record installed versions: torch, transformer_engine, flash_attn, cuDNN, CUDA, GPU compute capability.
3. Create a minimal 2B backend reproduction script with smallest batch and response length.
4. First test: remove forced disabling of flash/fused backends and let TE auto-select.
5. If auto-selection fails, inspect NVTE debug reasons before trying another fix.

## 2026-06-26 Qwen3.5-2B attention backend evidence update

### Evidence collected
Inspected run_qwen35_2b_mmlu_pro_smoke.sh and qwen3.5-2B model args.

### Script evidence
The current 2B smoke script uses:
- attention-backend = unfused
- NVTE_FLASH_ATTN = 0
- NVTE_FUSED_ATTN = 0
- NVTE_UNFUSED_ATTN = 1
- NVTE_DEBUG = 1
- NVTE_DEBUG_LEVEL = 2

Interpretation:
The script explicitly disables FlashAttention and FusedAttention, then asks Transformer Engine to use UnfusedAttention.

### Model shape evidence
Qwen3.5-2B model args show:
- hidden-size = 2048
- num-attention-heads = 8
- num-query-groups = 2
- kv-channels = 256

Therefore:
head_dim = 2048 / 8 = 256

### Runtime environment evidence
Container environment:
- torch = 2.11.0+cu129
- CUDA = 12.9
- GPU = NVIDIA GeForce RTX 3090
- compute capability = sm86
- transformer_engine = 2.10.0
- flash_attn = 2.7.4.post1

New issue found:
torch.backends.cudnn reports a cuDNN mismatch. PyTorch was compiled against cuDNN 9.17.1 but runtime found cuDNN 9.16.0, likely due to LD_LIBRARY_PATH.

### Old NVTE debug evidence
Previous unfused debug log shows:
- qkv_layout = thd_thd_thd
- head_dim_qk = 256
- head_dim_v = 256
- attn_mask_type = padding_causal
- FlashAttention 2 disabled because NVTE_FLASH_ATTN=0
- FlashAttention 3 disabled because NVTE_FLASH_ATTN=0
- FusedAttention disabled because NVTE_FUSED_ATTN=0
- UnfusedDotProductAttention disabled because qkv_format=thd
- Available backends = all false
- Selected backend = NoBackend

### Updated hypothesis ranking
H1 confirmed: FlashAttention and FusedAttention were manually disabled by env vars.
H3 confirmed: UnfusedAttention is disabled for qkv_format=thd in this TE path.
H8 added: cuDNN runtime mismatch may affect FusedAttention, so do not rely on cuDNN attention first.
H2 still open: head_dim=256 might still be accepted by FlashAttention, because flash_attn version is 2.7.4.post1 and dropout is 0.0.

### Next experiment
Create a minimal FlashAttention-only 2B smoke script:
- use attention-backend flash
- enable NVTE_FLASH_ATTN=1
- disable NVTE_FUSED_ATTN=0 to avoid cuDNN mismatch
- disable NVTE_UNFUSED_ATTN=0 to isolate the flash path
- keep NVTE_DEBUG=1 and NVTE_DEBUG_LEVEL=2
- use smallest batch and short response length

Expected result:
If FlashAttention is eligible, TE should select FlashAttention and the smoke run should pass the ref_log_probs stage.
If it fails, inspect the new NVTE debug reason for disabling FlashAttention.

## 2026-06-26 Qwen3.5-2B flash-only backend experiment

### Goal
Test whether Qwen3.5-2B can pass SLIME smoke training by enabling only FlashAttention in Transformer Engine.

### Config
- attention-backend = flash
- NVTE_FLASH_ATTN = 1
- NVTE_FUSED_ATTN = 0
- NVTE_UNFUSED_ATTN = 0
- rollout-batch-size = 1
- n-samples-per-prompt = 1
- global-batch-size = 1
- rollout-max-response-len = 16

### Result
The run failed during Megatron ref_log_probs forward with:
No dot product attention backend is available for the provided inputs.

### NVTE debug evidence
Transformer Engine reported:
- compute capability = sm86
- qkv_layout = thd_thd_thd
- head_dim_qk = 256
- head_dim_v = 256
- attn_mask_type = padding_causal
- FlashAttention 3 disabled because compute capability is not sm90
- FlashAttention 2 disabled due to unsupported head_dim_qk and head_dim_v on sm8.6
- FusedAttention disabled because NVTE_FUSED_ATTN=0
- UnfusedDotProductAttention disabled because NVTE_UNFUSED_ATTN=0
- Available backends = all false
- Selected backend = NoBackend

### Interpretation
FlashAttention-only does not solve the Qwen3.5-2B backend issue on the current RTX 3090 / sm86 environment.
The main new evidence is that TE 2.10.0 rejects head_dim=256 for FlashAttention 2 on sm86 in this runtime path.

### Updated hypothesis status
H1 is only partially sufficient: enabling FlashAttention does not fix the issue.
H2 is now strongly supported: head_dim=256 is rejected by FlashAttention 2 in this TE path on sm86.
H3 remains confirmed: UnfusedAttention is not available for thd layout.
H8 remains open: FusedAttention may still be possible, but cuDNN runtime mismatch must be investigated.

### Next action
Test FusedAttention / cuDNN attention path separately, preferably after inspecting the cuDNN library path and LD_LIBRARY_PATH.

## 2026-06-26 cuDNN path override test result

### Goal
Test whether prepending PyTorch bundled cuDNN path to LD_LIBRARY_PATH fixes the cuDNN mismatch.

### Test
Used:
export LD_LIBRARY_PATH=/usr/local/lib/python3.12/dist-packages/nvidia/cudnn/lib:$LD_LIBRARY_PATH

### Result
The mismatch still remains.
PyTorch still reports:
compiled against cuDNN 9.17.1 but found runtime cuDNN 9.16.0.

### Interpretation
The issue is not solved by simply prepending the nvidia/cudnn/lib path.
Possible causes:
1. the installed nvidia-cudnn-cu12 package inside the container is actually cuDNN 9.16.0
2. another cuDNN 9.16.0 library is still being loaded first
3. the slimerl/slime image has an internal torch/cuDNN package mismatch

### Next action
Inspect Python package versions and the actual libcudnn.so.9 loaded by the dynamic linker before running FusedAttention-only.

## 2026-06-26 cuDNN package version evidence

### Goal
Confirm whether the cuDNN mismatch is caused by the installed Python cuDNN package version.

### Evidence
Inside slimerl/slime:latest:
- torch = 2.11.0+cu129
- nvidia-cudnn-cu12 = 9.16.0.29
- nvidia-cublas-cu12 = 12.9.1.4
- nvidia-cuda-runtime-cu12 = 12.9.79
- transformer_engine = 2.10.0
- flash-attn = 2.7.4.post1

PyTorch reports that it was compiled against cuDNN 9.17.1 but the runtime cuDNN is 9.16.0.

### Interpretation
The cuDNN mismatch is not fixed by simply prepending the bundled cuDNN path to LD_LIBRARY_PATH.
The installed nvidia-cudnn-cu12 package itself is 9.16.0.29, while torch expects cuDNN 9.17.1.
This may block the Transformer Engine FusedAttention path.

### Backend status update
UnfusedAttention is unavailable because qkv_format=thd is disabled in this TE path.
FlashAttention is unavailable because TE rejects head_dim=256 on sm86 in the flash-only experiment.
FusedAttention has not yet been validly tested because cuDNN runtime is mismatched.

### Next action
Check available nvidia-cudnn-cu12 versions and test whether upgrading cuDNN inside a temporary container resolves torch.backends.cudnn.version().
Only after cuDNN is fixed should FusedAttention-only be tested.

## 2026-06-26 available cuDNN versions check

### Goal
Check whether a cuDNN version matching torch 2.11.0+cu129 is available from pip.

### Command
python3 -m pip index versions nvidia-cudnn-cu12

### Result
pip reports available versions including 9.17.1.4 and 9.17.0.29.
The installed version inside slimerl/slime:latest is 9.16.0.29.
The latest available version is 9.23.2.1.

### Interpretation
This confirms that the current image has a cuDNN package version older than what torch expects.
PyTorch reported it was compiled against cuDNN 9.17.1, so the most conservative test target is nvidia-cudnn-cu12==9.17.1.4, not the latest 9.23.x.

### Next action
Run a one-off container test that upgrades nvidia-cudnn-cu12 to 9.17.1.4 and checks whether torch.backends.cudnn.version() succeeds.

## 2026-06-26 cuDNN upgrade validation

### Goal
Validate whether upgrading nvidia-cudnn-cu12 fixes the PyTorch cuDNN runtime mismatch inside a temporary container.

### Test
Installed nvidia-cudnn-cu12==9.17.1.4 inside a one-off slimerl/slime container.

### Result
The upgrade succeeded.
Observed:
- torch = 2.11.0+cu129
- torch cuda = 12.9
- nvidia-cudnn-cu12 = 9.17.1.4
- torch.backends.cudnn.version() = 91701

### Interpretation
The previous cuDNN mismatch was caused by the container having nvidia-cudnn-cu12 9.16.0.29 while torch expected cuDNN 9.17.1.
After upgrading to 9.17.1.4, PyTorch can load cuDNN successfully.

### Next action
Run a FusedAttention-only Qwen3.5-2B smoke experiment in the same container session after installing nvidia-cudnn-cu12==9.17.1.4.
This will test whether FusedAttention can handle Qwen3.5-2B head_dim=256 / THD layout on RTX 3090.

## 2026-06-26 Qwen3.5-2B fused-only backend experiment

### Goal
Test whether FusedAttention can solve the Qwen3.5-2B Transformer Engine attention backend blocker after fixing the cuDNN mismatch.

### Setup
Before running the smoke script, nvidia-cudnn-cu12 was upgraded inside the temporary container to 9.17.1.4.
The run confirmed cudNN version 9.17.1 in the TE debug config.

### Config
- attention-backend = fused
- NVTE_FLASH_ATTN = 0
- NVTE_FUSED_ATTN = 1
- NVTE_UNFUSED_ATTN = 0
- rollout-batch-size = 1
- n-samples-per-prompt = 1
- global-batch-size = 1
- rollout-max-response-len = 16

### Result
The run still failed during Megatron ref_log_probs forward.
Transformer Engine reported:
- compute capability = sm86
- cudnn_version = 9.17.1
- qkv_layout = thd_thd_thd
- qkv_dtype = bfloat16
- batch_size = 2
- num_heads = 8
- num_gqa_groups = 2
- max_seqlen_q = 223
- max_seqlen_kv = 223
- head_dim_qk = 256
- head_dim_v = 256
- attn_mask_type = padding_causal
- attention_dropout = 0.0
- is_training = False

Backend selection:
- FlashAttention disabled because NVTE_FLASH_ATTN=0
- UnfusedDotProductAttention disabled because NVTE_UNFUSED_ATTN=0
- FusedAttention disabled because no backend supports the provided input
- Available backends = all false
- Selected backend = NoBackend

### Interpretation
FusedAttention is not available for the Qwen3.5-2B input configuration in the current RTX 3090 / sm86 + Transformer Engine 2.10.0 path, even after fixing the cuDNN version mismatch.
This means the original 2B blocker is not only caused by the old cuDNN mismatch.

### Backend status
UnfusedAttention: unavailable because THD qkv layout is not supported in this path.
FlashAttention: unavailable because TE rejects head_dim=256 on sm86 in the flash-only experiment.
FusedAttention: unavailable because no cuDNN backend supports the provided input configuration.

### Current conclusion
Qwen3.5-2B cannot currently complete SLIME smoke training on this RTX 3090 / sm86 environment through the available TE attention backends.
Most likely blocker: head_dim=256 + GQA + THD layout + padding_causal under the qwen3_5 Megatron spec.

### Next options
Option A: test on a newer GPU such as sm90/H100 where FlashAttention 3 may be available.
Option B: use a model variant with smaller head_dim or a known compatible SLIME model script, such as Qwen3.5-0.8B or Qwen2.5-0.5B/1.5B.
Option C: change the Megatron/spec/TE stack, but this is a deeper infrastructure change rather than reward adaptation.

## 2026-06-26 Qwen3.5-2B HF reasoning probe result

### Goal
Test Qwen3.5-2B's raw HuggingFace inference ability on two MMLU-Pro-style finance/math reasoning cases, bypassing SLIME, Megatron, and Transformer Engine training backends.

### Command
Ran the HF probe with:
- model = /home/xudongmao/models/Qwen3.5-2B
- max-new-tokens = 1536
- temperature = 0.0

### Result
The probe finished successfully.

Observed:
- CASE 1 bank_discount_proceeds: correct
- CASE 2 exact_time_interest: correct
- SUMMARY: 2/2 correct

For CASE 2, the model correctly:
1. counted the exact time from March 8 to August 5 as 150 days;
2. used the formula I = P * r * days / 365;
3. computed 1262.77 * 0.08 * 150 / 365 ≈ 41.52;
4. matched the value to Option E;
5. ended with Final answer: E.

### Interpretation
Qwen3.5-2B shows much stronger raw reasoning behavior than the previous 0.5B smoke model on these hand-written probe cases.
The previous 512-token probe was misleading because generation was truncated before the model reached the final answer.
After increasing max-new-tokens to 1536, the model completed the reasoning trace and produced correct final answers.

### Current conclusion
Qwen3.5-2B is worth keeping as a capability candidate.
The current blocker is still the SLIME/Megatron/Transformer Engine attention backend incompatibility on RTX 3090 / sm86, not a lack of raw model reasoning ability.

### Next action
Expand the HF reasoning probe from 2 cases to 5-10 cases before deciding whether to invest more engineering effort into adapting a compatible training path or selecting another model.

## 2026-06-26 Qwen2.5-0.5B HF reasoning probe result

### Goal
Compare Qwen2.5-0.5B-Instruct against Qwen3.5-2B on the same two hand-written MMLU-Pro-style finance/math reasoning cases using raw HuggingFace inference.

### Command
Ran the HF probe with:
- model = /home/xudongmao/models/Qwen2.5-0.5B-Instruct
- max-new-tokens = 1536
- temperature = 0.0

### Result
The probe finished successfully.

Observed:
- CASE 1 bank_discount_proceeds: incorrect
- CASE 2 exact_time_interest: incorrect
- SUMMARY: 0/2 correct

### Error analysis

For CASE 1, the model failed in multiple places:
1. It used Interest = 45000 * 0.06 * 120 without dividing by 360.
2. It produced an unstable arithmetic result.
3. It computed proceeds as 12240 but selected option C = 44550, so the final option mapping was inconsistent with its own calculation.

For CASE 2, the model also failed in multiple places:
1. It incorrectly treated March 8 to August 5 as 10 months.
2. It used an average month length instead of exact time.
3. It failed to apply the 365-day-year denominator correctly.
4. It produced an unrealistic interest value and then selected an option inconsistent with its own calculation.

### Interpretation
Qwen2.5-0.5B-Instruct is much weaker than Qwen3.5-2B on these raw reasoning probes.
The 0.5B model can still be useful for validating the SLIME engineering smoke path, reward parser, rollout, GRPO update, and checkpoint saving.
However, it should not be treated as evidence of reliable MMLU-Pro reasoning ability.

### Current conclusion
Qwen2.5-0.5B proves that the SLIME training pipeline can run, but it is not a strong capability candidate.
Qwen3.5-2B remains a stronger capability candidate based on raw reasoning, although its current blocker is the Transformer Engine attention backend incompatibility on RTX 3090 / sm86.

## 2026-06-26 Qwen2.5-1.5B HF reasoning probe result

### Goal
Evaluate Qwen2.5-1.5B-Instruct as a candidate model between Qwen2.5-0.5B and Qwen3.5-2B.

### Config evidence
The local config shows:
- model_type = qwen2
- architectures = Qwen2ForCausalLM
- hidden_size = 1536
- num_attention_heads = 12
- num_key_value_heads = 2
- head_dim = 128
- torch_dtype = bfloat16
- attention_dropout = 0.0
- engineering_risk = LOW/MEDIUM

### Probe setup
Ran the same HF reasoning probe used for Qwen2.5-0.5B and Qwen3.5-2B:
- max-new-tokens = 1536
- temperature = 0.0
- two hand-written MMLU-Pro-style finance/math cases

### Result
Observed:
- CASE 1 bank_discount_proceeds: correct
- CASE 2 exact_time_interest: incorrect
- SUMMARY: 1/2 correct

### Error analysis
For CASE 1, the model correctly computed:
- Discount = 45000 * 0.06 * 120 / 360 = 900
- Proceeds = 45000 - 900 = 44100
- Final answer = A

For CASE 2, the model correctly identified:
- exact time = 150 days
- t = 150 / 365
- Simple Interest = 1262.77 * 0.08 * 150 / 365

However, it incorrectly computed the final value as approximately 41.00 instead of 41.52, and selected option D instead of E.

### Interpretation
Qwen2.5-1.5B-Instruct is clearly stronger than Qwen2.5-0.5B-Instruct on raw reasoning.
Its main observed failure is arithmetic precision / option matching, not complete formula misunderstanding.
It is still weaker than Qwen3.5-2B on the current two-case probe.

### Current conclusion
Qwen2.5-1.5B-Instruct is a reasonable engineering candidate because it has head_dim=128 and qwen2 architecture, but its reasoning capability may not be sufficient if Qwen3-1.7B performs better.
Next step: run the same HF reasoning probe on Qwen3-1.7B.

## 2026-06-26 Qwen3-1.7B HF reasoning probe result

### Goal
Evaluate Qwen3-1.7B as another candidate model between Qwen2.5-1.5B and Qwen3.5-2B.

### Config evidence
The local config shows:
- model_type = qwen3
- architectures = Qwen3ForCausalLM
- hidden_size = 2048
- num_attention_heads = 16
- num_key_value_heads = 8
- head_dim = 128
- torch_dtype = bfloat16
- attention_dropout = 0.0
- engineering_risk = LOW/MEDIUM

### Probe result
Using the original long reasoning probe, Qwen3-1.7B produced long thinking traces and was truncated before final answers in some cases.

Using the compact no-thinking probe:
- CASE 1 bank_discount_proceeds: correct
- CASE 2 exact_time_interest: incorrect
- SUMMARY: 1/2 correct

### Error analysis
For CASE 1, the model correctly computed:
- Discount = 45000 * 0.06 * 120 / 360 = 900
- Proceeds = 45000 - 900 = 44100
- Final answer = A

For CASE 2, the model failed in multiple places:
1. It computed exact time as 145 days instead of the expected 150 days.
2. It therefore used t = 145 / 365 instead of 150 / 365.
3. It output Interest ≈ 41.00 instead of 41.52.
4. It ended with Final answer: <I>, confusing the interest variable I with the multiple-choice final answer format.

### Interpretation
Qwen3-1.7B has better reasoning behavior than Qwen2.5-0.5B, but it does not clearly outperform Qwen2.5-1.5B on the current two-case probe.
The no-thinking prompt improves output control, but the model still makes a real date-counting and option-formatting error.

### Current conclusion
Qwen3-1.7B is a backup candidate, not the first engineering candidate.
Qwen2.5-1.5B-Instruct should be prioritized for the next SLIME smoke test because it has qwen2 architecture, head_dim=128, and is closer to the already-runnable Qwen2.5-0.5B path.

## 2026-06-26 Qwen2.5-1.5B SLIME TP2 lowmem smoke success

### Goal
Run a minimal SLIME smoke test for Qwen2.5-1.5B-Instruct after the single-GPU b1 smoke failed with optimizer-state CUDA OOM.

### Final working setup
- HF checkpoint: /home/xudongmao/models/Qwen2.5-1.5B-Instruct
- Converted checkpoint: /data1/xudongmao/slime_outputs/converted_models/qwen2.5-1.5B-Instruct_torch_dist
- Model args: experiments/mmlu_pro_qwen35_2b_slime_demo/slime_scripts/models/qwen2.5-1.5B.sh
- Smoke script: experiments/mmlu_pro_qwen35_2b_slime_demo/slime_scripts/run_qwen25_15b_mmlu_pro_b1_tp2_lowmem_smoke.sh
- Docker GPUs: device=1,2
- Docker shared memory: --shm-size=32g
- tensor-model-parallel-size = 2
- actor-num-gpus-per-node = 2
- rollout-num-gpus-per-engine = 1
- rollout-max-response-len = 8
- seq-length = 512
- sglang-mem-fraction-static = 0.20

### Previous failures and fixes
1. Single-GPU b1 smoke with default Docker shared memory failed at update_weights:
   - NCCL ncclSystemError
   - /dev/shm/nccl-* no space left on device
   Fix:
   - rerun Docker with --shm-size=16g or larger.

2. Single-GPU b1 smoke after fixing /dev/shm reached actor_train but failed during optimizer.step:
   - Transformer Engine FusedAdam initialized optimizer state.
   - CUDA OOM occurred while allocating exp_avg_sq.
   Interpretation:
   - Qwen2.5-1.5B can enter the train path, but single RTX 3090 24GB is too tight under colocated rollout + actor training + Adam optimizer state.

3. First TP2 lowmem attempt failed because:
   - PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True conflicted with SGLang TorchMemorySaver.
   Fix:
   - remove PYTORCH_CUDA_ALLOC_CONF from the Ray runtime env.

4. Second TP2 lowmem attempt with sglang-mem-fraction-static=0.10 failed during SGLang memory pool initialization:
   - RuntimeError: Not enough memory. Please try to increase --mem-fraction-static.
   Fix:
   - increase sglang-mem-fraction-static from 0.10 to 0.20.

### Success evidence
The final TP2 lowmem run succeeded.

Observed:
- update_weights reached 100%.
- SGLang accepted POST /update_weights_from_tensor with HTTP 200.
- Ray job ended with:
  Job 'raysubmit_MrwrD6TUE4h3psGT' succeeded.

### Interpretation
Qwen2.5-1.5B-Instruct is now a valid SLIME engineering candidate.
Compared with Qwen3.5-2B, it avoids the Transformer Engine attention backend blocker.
Compared with Qwen2.5-0.5B, it has stronger raw reasoning behavior, but requires TP2 on RTX 3090 24GB for this colocated SLIME smoke setup.

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

## 2026-06-26 Qwen2.5 model direct dev_100 baseline eval

### Goal
Compare Qwen2.5-1.5B-Instruct and Qwen2.5-0.5B-Instruct on the same direct forced-choice dev_100 split.

### Evaluation setup
- Data: experiments/mmlu_pro_qwen35_2b_slime_demo/data/dev_100_direct.jsonl
- Prompt style: direct forced-choice
- Output format: one letter from A to J
- max-new-tokens = 8
- temperature = 0.0

### Results
Qwen2.5-1.5B-Instruct:
- accuracy = 23/100 = 0.2300

Qwen2.5-0.5B-Instruct:
- accuracy = 12/100 = 0.1200

### Qwen2.5-1.5B prediction distribution
Gold label distribution:
- A: 6
- B: 11
- C: 7
- D: 17
- E: 8
- F: 14
- G: 13
- H: 11
- I: 10
- J: 3

Prediction distribution:
- A: 30
- B: 18
- C: 19
- D: 5
- E: 10
- F: 7
- H: 2
- J: 9

### Interpretation
Qwen2.5-1.5B is clearly stronger than Qwen2.5-0.5B on this direct forced-choice baseline.
However, the absolute accuracy is still low and the model shows a strong A/B/C option bias.
This suggests that Qwen2.5-1.5B is a better engineering candidate than 0.5B, but direct-answer behavior still needs improvement.

## 2026-06-26 Qwen2.5-1.5B dev_100 reasoning eval

### Goal
Check whether allowing step-by-step reasoning improves Qwen2.5-1.5B-Instruct accuracy compared with direct forced-choice output.

### Evaluation setup
- Model: /home/xudongmao/models/Qwen2.5-1.5B-Instruct
- Data: experiments/mmlu_pro_qwen35_2b_slime_demo/data/dev_100.jsonl
- Prompt style: Think step by step, then Final answer
- max-new-tokens = 256
- batch-size = 4
- temperature = 0.0

### Result
- accuracy = 20/100 = 0.2000

### Comparison
Previous direct forced-choice result:
- Qwen2.5-1.5B-Instruct dev_100_direct accuracy = 23/100 = 0.2300
- Qwen2.5-0.5B-Instruct dev_100_direct accuracy = 12/100 = 0.1200

### Interpretation
The reasoning prompt did not improve accuracy for Qwen2.5-1.5B on this dev_100 split.
The direct forced-choice prompt is currently better and much faster.
Next training experiments should focus on improving direct forced-choice behavior and reducing option bias rather than encouraging longer reasoning.

## 2026-06-26 Qwen2.5-1.5B short-answer eval

### Goal
Test whether a short final-answer format improves over direct single-letter forced-choice output.

### Evaluation setup
- Model: /home/xudongmao/models/Qwen2.5-1.5B-Instruct
- Data: experiments/mmlu_pro_qwen35_2b_slime_demo/data/dev_100_short_answer.jsonl
- Prompt style: no reasoning, output exactly one line: Final answer: <A-J>
- max-new-tokens = 16
- batch-size = 16
- temperature = 0.0

### Result
- short-answer accuracy = 22/100 = 0.2200

### Comparison
- direct forced-choice accuracy = 23/100 = 0.2300
- short-answer accuracy = 22/100 = 0.2200
- reasoning_512_limit20 with fixed parser = 7/20 = 0.3500

### Interpretation
Short-answer format did not improve over direct forced-choice.
The direct forced-choice prompt remains the best full dev_100 baseline and is also the fastest option.
Long reasoning has some potential, but it is much slower and currently only validated on the first 20 examples.
The next RL experiment should therefore use the direct forced-choice training data.

## 2026-06-26 End-of-day status

### Completed
- Qwen2.5-1.5B-Instruct model args were added.
- Qwen2.5-1.5B-Instruct converted checkpoint was prepared.
- Qwen2.5-1.5B TP2 lowmem smoke succeeded.
- The eval parser was improved to handle:
  - Final answer: X
  - The final answer is X
  - Answer: X
  - The answer is X
  - Therefore, the correct answer is X
  - The correct answer is X
  - fallback to the last standalone A-J letter

### Baseline evaluation results
- Qwen2.5-0.5B direct dev_100: 12/100 = 0.1200
- Qwen2.5-1.5B direct dev_100: 23/100 = 0.2300
- Qwen2.5-1.5B short-answer dev_100: 22/100 = 0.2200
- Qwen2.5-1.5B reasoning dev_100 with max-new-tokens=256: 20/100 = 0.2000
- Qwen2.5-1.5B reasoning first20 with max-new-tokens=512 and fixed parser: 7/20 = 0.3500

### Interpretation
- Qwen2.5-1.5B is clearly stronger than Qwen2.5-0.5B on the direct forced-choice baseline.
- Direct forced-choice remains the best full dev_100 baseline and is fastest.
- Long reasoning has some potential, but it is slow and sensitive to max-new-tokens truncation.
- Parser errors were confirmed to be minor, not the main cause of low reasoning_256 performance.

### Current blocker
- Attempts to scale beyond b1 smoke, such as b2/b4 direct RL, failed during SGLang memory pool initialization.
- The latest error was:
  RuntimeError: Not enough memory. Please try to increase --mem-fraction-static.
- The job did not reach rollout/reward/actor train.
- Next recommended experiment:
  1. Create and run b1_r4: keep rollout-batch-size=1 and global-batch-size=1, only increase num-rollout to 4.
  2. If b1_r4 succeeds, try b2_r4 with sglang-mem-fraction-static=0.25.

## 2026-06-29 b1_s4_r16 RL 后训练与训练后评估

### 实验目标
验证 Qwen2.5-1.5B-Instruct 在 MMLU-Pro direct forced-choice 任务上，经过 SLIME + GRPO 小规模 RL 后训练后，dev_100_direct 准确率是否相对 baseline 提升。

### 训练配置
- 模型：Qwen2.5-1.5B-Instruct
- 任务：MMLU-Pro direct forced-choice
- 框架：SLIME + Megatron actor + SGLang rollout engine
- 训练方法：GRPO
- rollout-batch-size：1
- n-samples-per-prompt：4
- global-batch-size：4
- num-rollout：16
- rollout-temperature：1.0
- rollout-max-response-len：8
- checkpoint：iter_0000015

### 训练过程结果
- b1_s4_r16 job succeeded。
- 16 个训练 step 中，有 5 个 step 的 grad_norm 非零。
- 有效梯度 step：5/16 = 31.25%。
- 说明该配置能够产生真实 RL 学习信号，但学习信号仍然偏稀疏。
- 主要时间开销仍来自 Ray/SGLang/Megatron 初始化、sleep、wake_up、update_weights 和调度等待。

### checkpoint 与格式转换
- 训练后 checkpoint：
  /data1/xudongmao/slime_outputs/mmlu_pro_runs/qwen2.5-1.5B-Instruct-tp2-direct-b1-s4-r16/iter_0000015
- checkpoint 原始格式：Megatron / torch distributed checkpoint。
- 已使用 convert_torch_dist_to_hf.py 转换为 HuggingFace 格式。
- 转换后 HF 模型：
  /data1/xudongmao/slime_outputs/hf_models/qwen2.5-1.5B-Instruct-tp2-direct-b1-s4-r16-iter15

### eval 结果
- eval 数据：dev_100_direct.jsonl
- 训练前 baseline：23/100 = 23%
- 训练后 iter15：25/100 = 25%
- 提升：+2/100，即 +2 个百分点

### 当前结论
本次实验完成了从 baseline、RL 后训练、checkpoint 保存、格式转换到训练后 eval 的完整闭环。训练后准确率从 23% 提升到 25%，说明该 RL 后训练链路没有失败，并产生了轻微正向效果。但由于训练规模较小、有效梯度 step 仅为 5/16，提升幅度仍有限，不能认为模型能力已经显著提升。

### 下一步计划
1. 做训练前后样本级对比，统计 wrong→correct 和 correct→wrong 的题。
2. 重新确认 baseline 是否为同条件 eval。
3. 根据样本对比结果决定下一步：
   - 如果提升样本合理，可以继续扩大训练；
   - 如果有效梯度仍稀疏，考虑 b1_s8_r8；
   - 或构造 reward-variance 子集，提高有效训练 step 比例。


## 2026-06-29 b1_s4_r16 RL 后训练与训练后评估

### 实验目标
验证 Qwen2.5-1.5B-Instruct 在 MMLU-Pro direct forced-choice 任务上，经过 SLIME + GRPO 小规模 RL 后训练后，dev_100_direct 准确率是否相对 baseline 提升。

### 训练配置
- 模型：Qwen2.5-1.5B-Instruct
- 任务：MMLU-Pro direct forced-choice
- 框架：SLIME + Megatron actor + SGLang rollout engine
- 训练方法：GRPO
- rollout-batch-size：1
- n-samples-per-prompt：4
- global-batch-size：4
- num-rollout：16
- rollout-temperature：1.0
- rollout-max-response-len：8
- checkpoint：iter_0000015

### 训练过程结果
- b1_s4_r16 job succeeded。
- 16 个训练 step 中，有 5 个 step 的 grad_norm 非零。
- 有效梯度 step：5/16 = 31.25%。
- 说明该配置能够产生真实 RL 学习信号，但学习信号仍然偏稀疏。
- 主要时间开销仍来自 Ray/SGLang/Megatron 初始化、sleep、wake_up、update_weights 和调度等待。

### checkpoint 与格式转换
- 训练后 checkpoint：
  /data1/xudongmao/slime_outputs/mmlu_pro_runs/qwen2.5-1.5B-Instruct-tp2-direct-b1-s4-r16/iter_0000015
- checkpoint 原始格式：Megatron / torch distributed checkpoint。
- 已使用 convert_torch_dist_to_hf.py 转换为 HuggingFace 格式。
- 转换后 HF 模型：
  /data1/xudongmao/slime_outputs/hf_models/qwen2.5-1.5B-Instruct-tp2-direct-b1-s4-r16-iter15

### eval 结果
- eval 数据：dev_100_direct.jsonl
- 训练前 baseline：23/100 = 23%
- 训练后 iter15：25/100 = 25%
- 提升：+2/100，即 +2 个百分点

### 当前结论
本次实验完成了从 baseline、RL 后训练、checkpoint 保存、格式转换到训练后 eval 的完整闭环。训练后准确率从 23% 提升到 25%，说明该 RL 后训练链路没有失败，并产生了轻微正向效果。但由于训练规模较小、有效梯度 step 仅为 5/16，提升幅度仍有限，不能认为模型能力已经显著提升。

### 下一步计划
1. 做训练前后样本级对比，统计 wrong→correct 和 correct→wrong 的题。
2. 重新确认 baseline 是否为同条件 eval。
3. 根据样本对比结果决定下一步：
   - 如果提升样本合理，可以继续扩大训练；
   - 如果有效梯度仍稀疏，考虑 b1_s8_r8；
   - 或构造 reward-variance 子集，提高有效训练 step 比例。


## 2026-06-29 b1_s4_r16 训练前后样本级对比

### 对比目标
分析 RL 后训练前后 dev_100_direct 中哪些题目发生了正确性变化，判断 23% → 25% 的提升来源。

### 输入文件
- before eval：`experiments/mmlu_pro_qwen35_2b_slime_demo/outputs/qwen25_15b_dev100_direct_eval.jsonl`
- after eval：`experiments/mmlu_pro_qwen35_2b_slime_demo/outputs/qwen25_15b_dev100_direct_eval_after_b1_s4_r16_iter15.jsonl`

### 对比结果
- before accuracy：23/100 = 0.2300
- after accuracy：25/100 = 0.2500
- delta：2
- wrong → correct：2
- correct → wrong：0
- same correct：23
- same wrong：75

### 结论
本次 RL 后训练在 dev_100_direct 上产生小幅正向变化。需要结合 wrong→correct 与 correct→wrong 样本进一步判断提升是否来自合理题型，还是小样本随机波动。

### 产物
- 样本级对比 JSONL：`experiments/mmlu_pro_qwen35_2b_slime_demo/outputs/compare_before_after_b1_s4_r16_iter15.jsonl`
- 样本级对比 Markdown：`experiments/mmlu_pro_qwen35_2b_slime_demo/outputs/compare_before_after_b1_s4_r16_iter15.md`


### 补充：b1_s4_r16 wrong→correct 两个样本的人工解释

本次训练后 eval 相比 baseline 从 23/100 提升到 25/100。样本级对比显示新增正确样本为 idx=4 和 idx=86，且 correct→wrong 为 0。

#### idx=4：Black-Scholes asset-or-nothing put option
- label：C
- before：J，错误
- after：C，正确
- 题型：金融衍生品定价 / Black-Scholes / asset-or-nothing put
- 人工判断：该样本较可靠。根据 asset-or-nothing put 公式，价格约为 3.6 million，对应选项 C。因此该样本可以视为一次较干净的 wrong→correct。

#### idx=86：markdown percent
- label：B
- before：F，错误
- after：B，按数据标签正确
- 题型：商业算术 / markdown percentage
- 人工判断：该样本需要标记为“可能存在口径歧义”。如果按常见 markdown rate = markdown / original price，则 (2.25 - 2.00) / 2.25 ≈ 11.1%，更接近 J=11%。数据标签 B=12.5% 对应的是 0.25 / 2.00，即用降价后价格作分母。因此该样本虽然按数据标签从 wrong→correct，但是否代表真实数学能力提升需要谨慎解释。

#### 更新后的实验解释
本次 b1_s4_r16 的 23% → 25% 提升来自两个新增正确样本，且没有 correct→wrong regression。其中 idx=4 是较可靠的正向样本，idx=86 按数据标签正确但存在定义口径歧义。整体结论仍是：本次小规模 RL 后训练产生了干净但幅度较小的正向效果，后续需要更多样本和更稳定的有效梯度 step 来验证趋势。


### 补充：b1_s4_r16 wrong→correct 两个样本的人工解释


本次训练后 eval 相比 baseline 从 23/100 提升到 25/100。样本级对比显示新增正确样本为 idx=4 和 idx=86，且 correct→wrong 为 0。

#### idx=4：Black-Scholes asset-or-nothing put option

- label：C
- before：J，错误
- after：C，正确
- 题型：金融衍生品定价 / Black-Scholes / asset-or-nothing put
- 人工判断：该样本较可靠。根据 asset-or-nothing put 公式，价格约为 3.6 million，对应选项 C。因此该样本可以视为一次较干净的 wrong→correct。

#### idx=86：markdown percent

- label：B
- before：F，错误
- after：B，按数据标签正确
- 题型：商业算术 / markdown percentage
- 人工判断：该样本需要标记为“可能存在口径歧义”。如果按常见 markdown rate = markdown / original price，则 (2.25 - 2.00) / 2.25 ≈ 11.1%，更接近 J=11%。数据标签 B=12.5% 对应的是 0.25 / 2.00，即用降价后价格作分母。因此该样本虽然按数据标签从 wrong→correct，但是否代表真实数学能力提升需要谨慎解释。

#### 更新后的实验解释

本次 b1_s4_r16 的 23% → 25% 提升来自两个新增正确样本，且没有 correct→wrong regression。其中 idx=4 是较可靠的正向样本，idx=86 按数据标签正确但存在定义口径歧义。整体结论仍是：本次小规模 RL 后训练产生了干净但幅度较小的正向效果，后续需要更多样本和更稳定的有效梯度 step 来验证趋势。


### 补充：b1_s4_r16 wrong→correct 两个样本的人工解释



本次训练后 eval 相比 baseline 从 23/100 提升到 25/100。样本级对比显示新增正确样本为 idx=4 和 idx=86，且 correct→wrong 为 0。

#### idx=4：Black-Scholes asset-or-nothing put option


- label：C
- before：J，错误
- after：C，正确
- 题型：金融衍生品定价 / Black-Scholes / asset-or-nothing put
- 人工判断：该样本较可靠。根据 asset-or-nothing put 公式，价格约为 3.6 million，对应选项 C。因此该样本可以视为一次较干净的 wrong→correct。

#### idx=86：markdown percent


- label：B
- before：F，错误
- after：B，按数据标签正确
- 题型：商业算术 / markdown percentage
- 人工判断：该样本需要标记为“可能存在口径歧义”。如果按常见 markdown rate = markdown / original price，则 (2.25 - 2.00) / 2.25 ≈ 11.1%，更接近 J=11%。数据标签 B=12.5% 对应的是 0.25 / 2.00，即用降价后价格作分母。因此该样本虽然按数据标签从 wrong→correct，但是否代表真实数学能力提升需要谨慎解释。

#### 更新后的实验解释


本次 b1_s4_r16 的 23% → 25% 提升来自两个新增正确样本，且没有 correct→wrong regression。其中 idx=4 是较可靠的正向样本，idx=86 按数据标签正确但存在定义口径歧义。整体结论仍是：本次小规模 RL 后训练产生了干净但幅度较小的正向效果，后续需要更多样本和更稳定的有效梯度 step 来验证趋势。


### 补充：b1_s4_r16 wrong→correct 两个样本的人工解释




本次训练后 eval 相比 baseline 从 23/100 提升到 25/100。样本级对比显示新增正确样本为 idx=4 和 idx=86，且 correct→wrong 为 0。

#### idx=4：Black-Scholes asset-or-nothing put option



- label：C
- before：J，错误
- after：C，正确
- 题型：金融衍生品定价 / Black-Scholes / asset-or-nothing put
- 人工判断：该样本较可靠。根据 asset-or-nothing put 公式，价格约为 3.6 million，对应选项 C。因此该样本可以视为一次较干净的 wrong→correct。

#### idx=86：markdown percent



- label：B
- before：F，错误
- after：B，按数据标签正确
- 题型：商业算术 / markdown percentage
- 人工判断：该样本需要标记为“可能存在口径歧义”。如果按常见 markdown rate = markdown / original price，则 (2.25 - 2.00) / 2.25 ≈ 11.1%，更接近 J=11%。数据标签 B=12.5% 对应的是 0.25 / 2.00，即用降价后价格作分母。因此该样本虽然按数据标签从 wrong→correct，但是否代表真实数学能力提升需要谨慎解释。

#### 更新后的实验解释



本次 b1_s4_r16 的 23% → 25% 提升来自两个新增正确样本，且没有 correct→wrong regression。其中 idx=4 是较可靠的正向样本，idx=86 按数据标签正确但存在定义口径歧义。整体结论仍是：本次小规模 RL 后训练产生了干净但幅度较小的正向效果，后续需要更多样本和更稳定的有效梯度 step 来验证趋势。


## 2026-06-29 b1_s8_r8 实验启动记录

### 实验目标
在 b1_s4_r16 已完成训练-转换-eval 闭环并得到 23% → 25% 小幅提升后，进一步测试将 n-samples-per-prompt 从 4 提高到 8 是否能提升 GRPO 的 reward 方差和有效梯度 step 比例。

### 实验配置
- 模型：Qwen2.5-1.5B-Instruct
- 任务：MMLU-Pro direct forced-choice
- 框架：SLIME + Megatron actor + SGLang rollout engine
- 方法：GRPO
- rollout-batch-size：1
- n-samples-per-prompt：8
- global-batch-size：8
- num-rollout：8
- rollout-temperature：1.0
- rollout-max-response-len：8
- save path：/outputs/mmlu_pro_runs/qwen2.5-1.5B-Instruct-tp2-direct-b1-s8-r8

### 预期观察指标
- train/grad_norm 非零 step 数
- zero_std 出现比例
- rollout/raw_reward 是否产生组内差异
- step_time 与 wait_time_ratio
- 是否出现 OOM / Not enough memory / Traceback

### 判断标准
如果 8 个 step 中非零 grad_norm 明显高于 b1_s4_r16 的 31.25%，说明 s8 有助于提高有效训练比例。
如果仍然稀疏，则需要考虑 reward-variance 子集或更细粒度 reward。
如果 OOM，则说明 s8 当前显存/配置压力偏高，需要回退或调整 batch/microbatch。


## 2026-06-29 b1_s8_r8 job success 确认

### 检查目标
确认 b1_s8_r8 训练任务是否完整结束，是否可以进入 checkpoint 检查、HF 转换和 eval 阶段。

### 日志检查结果
训练日志中出现：
- Job 'raysubmit_NeNFU8LeJQqEUJn4' submitted successfully
- Job 'raysubmit_NeNFU8LeJQqEUJn4' succeeded

中间出现若干 `cache_position ... not documented` 的 `[ERROR]` 信息，但最终 Ray job 明确 succeeded，因此当前判断为非致命信息，不阻塞后续 checkpoint 转换和 eval。

### 当前结论
b1_s8_r8 训练任务已成功结束，可以继续确认 latest checkpoint，并执行 Megatron checkpoint 到 HuggingFace 格式转换。

### 下一步
1. 读取 latest_checkpointed_iteration.txt。
2. 确认 iter_xxxxxxx checkpoint 文件存在。
3. 将 checkpoint 转换为 HF 格式。
4. 在 dev_100_direct 上运行 eval。


## 2026-06-29 b1_s8_r8 checkpoint 转 HF 成功

### 实验阶段
将 b1_s8_r8 的 Megatron / torch distributed checkpoint 转换为 HuggingFace 格式，供后续 eval_hf 脚本读取。

### 输入 checkpoint
/data1/xudongmao/slime_outputs/mmlu_pro_runs/qwen2.5-1.5B-Instruct-tp2-direct-b1-s8-r8/iter_0000007

### 输出 HF 模型目录
/data1/xudongmao/slime_outputs/hf_models/qwen2.5-1.5B-Instruct-tp2-direct-b1-s8-r8-iter7

### 转换日志关键信息
- 成功在 torch_dist checkpoint 中找到 embedding、attention、MLP、final_layernorm 等权重。
- model loaded in 5.72 sec.
- start saving to /outputs/hf_models/qwen2.5-1.5B-Instruct-tp2-direct-b1-s8-r8-iter7
- model-00000-of-00001.safetensors saved in 2.07 sec.
- 成功复制 config.json、tokenizer.json、tokenizer_config.json、generation_config.json、vocab.json、merges.txt 等 HF 必需文件。
- Skip .cache, not a file. 该信息为跳过缓存目录，不影响转换结果。

### 当前结论
b1_s8_r8 的 checkpoint 已成功转换为 HuggingFace 格式，可以继续执行 dev_100_direct eval。

### 下一步
运行 eval_hf_mmlu_choice_batch.py，比较 b1_s8_r8 iter7 与 baseline 23/100、b1_s4_r16 iter15 25/100 的准确率差异。


## 2026-06-29 b1_s8_r8 训练后 eval 结果

### 实验目标
评估 b1_s8_r8 训练后的 checkpoint 是否在 dev_100_direct 上优于 baseline 和 b1_s4_r16。

### 训练信号回顾
- b1_s4_r16：5/16 非零 grad step，31.25%
- b1_s8_r8：8/8 非零 grad step，100%

### eval 结果
- baseline：23/100 = 23%
- b1_s4_r16 iter15：25/100 = 25%
- b1_s8_r8 iter7：22/100 = 22%

### 当前结论
b1_s8_r8 的有效梯度比例明显高于 b1_s4_r16，但 dev_100_direct eval 准确率下降到 22/100，低于 baseline 和 b1_s4_r16。

这说明增加 n-samples-per-prompt 可以增强 GRPO 的训练信号，但当前配置下并没有带来泛化提升，反而可能因为更新过强、训练样本过少、reward 噪声或过拟合导致验证集退化。

### 下一步
1. 做样本级 before/after 对比，统计 wrong_to_correct、correct_to_wrong、same_correct、same_wrong。
2. 对比 b1_s8_r8 相比 baseline 和 b1_s4_r16 分别改对了哪些题、改错了哪些题。
3. 暂时不建议继续盲目加大 s8 训练步数。
4. 后续优先考虑更保守配置，例如降低学习率、减少 rollout 步数、检查 reward parser，或回到 b1_s4_r16 作为当前可汇报结果。


## 2026-06-29 b1_s8_r8 样本级对比分析

### 分析目标
对 b1_s8_r8 的 dev_100_direct eval 结果做样本级 before/after 对比，判断准确率下降的具体原因。

### 准确率复核
- baseline：23/100 = 0.2300
- b1_s4_r16 iter15：25/100 = 0.2500
- b1_s8_r8 iter7：22/100 = 0.2200

### baseline vs b1_s8_r8_iter7
- total_common：100
- wrong_to_correct：1
- correct_to_wrong：2
- same_correct：21
- same_wrong：76
- prediction_changed：11

结论：b1_s8_r8 相比 baseline 只新增改对 1 题，但把 2 道 baseline 原本正确的题改错，因此整体准确率从 23/100 降到 22/100。

### b1_s4_r16_iter15 vs b1_s8_r8_iter7
- total_common：100
- wrong_to_correct：0
- correct_to_wrong：3
- same_correct：22
- same_wrong：75
- prediction_changed：11

结论：b1_s8_r8 相比当前最好结果 b1_s4_r16 没有新增改对任何题，反而把 3 道原本正确的题改错，因此从 25/100 降到 22/100。

### 预测分布变化
baseline：
- A：30
- B：18
- C：19
- D：5
- E：10
- F：7
- H：2
- J：9

b1_s8_r8_iter7：
- A：34
- B：23
- C：15
- D：5
- E：9
- F：3
- H：2
- J：9

观察：b1_s8_r8 训练后预测更偏向 A 和 B，减少了 C 和 F。说明模型行为被训练推偏，但这种分布偏移没有带来准确率提升。

### 当前工程结论
b1_s8_r8 是一个负结果/消融结果。它证明增加 n-samples-per-prompt 到 8 可以提高有效梯度比例，但当前配置下没有提升泛化性能，反而导致 dev_100_direct 准确率退化。

当前最稳妥的阶段性主结果仍然是 b1_s4_r16：
- baseline：23/100
- b1_s4_r16 iter15：25/100
- 提升：+2 个百分点
- wrong_to_correct：2
- correct_to_wrong：0

### 后续建议
1. 暂时不要继续盲目加大 s8 训练步数。
2. 后续若继续优化，可尝试降低学习率、减少 rollout 步数、检查 reward parser、扩大训练样本，或重新设计更稳健的 reward。
3. 对老师/报告汇报时，应把 b1_s8_r8 写成消融实验：训练信号增强，但 eval 退化，说明有效梯度更多不等于泛化更好。


## 2026-06-29 b1_s4_r16 vs b1_s8_r8 退化样本定位

### 分析目标
进一步查看 b1_s8_r8 相比当前最好结果 b1_s4_r16 的样本级退化情况，定位准确率从 25/100 降到 22/100 的原因。

### 对比结果
b1_s4_r16_iter15 vs b1_s8_r8_iter7：

- total_common：100
- wrong_to_correct：0
- correct_to_wrong：3
- same_correct：22
- same_wrong：75
- prediction_changed：11

### 具体 correct_to_wrong 样本
1. idx=4
   - label=C
   - b1_s4_r16_iter15=C
   - b1_s8_r8_iter7=J
   - category=business
   - src=theoremQA-Finance

2. idx=19
   - label=E
   - b1_s4_r16_iter15=E
   - b1_s8_r8_iter7=A
   - category=business
   - src=stemez-Business

3. idx=41
   - label=C
   - b1_s4_r16_iter15=C
   - b1_s8_r8_iter7=B
   - category=business
   - src=stemez-Business

### 结论
b1_s8_r8 相比 b1_s4_r16 没有新增改对任何样本，反而将 3 道 b1_s4_r16 已经答对的样本改错。因此 b1_s8_r8 的准确率下降主要来自 correct_to_wrong，而不是 simply 没有提升。

其中 idx=4 是 b1_s4_r16 中较重要的正向样本，b1_s8_r8 将其从正确答案 C 改成 J，说明 s8 的更新没有稳定保留 s4 的收益。

### 当前判断
b1_s8_r8 是负结果/消融结果。它证明 n-samples-per-prompt=8 可以增强训练信号密度，但当前配置下会破坏已有正确样本，导致 dev_100_direct 泛化退化。

当前主结果仍应采用 b1_s4_r16：
- baseline：23/100
- b1_s4_r16 iter15：25/100
- b1_s8_r8 iter7：22/100

### 下一步
1. 暂停继续扩大 s8。
2. 若继续优化，可优先尝试降低学习率、减少训练步数、扩大训练数据、检查 reward parser。
3. 工程汇报中将 b1_s8_r8 作为消融实验，而不是主结果。
4. 下一阶段确认服务器是否存在老师指定的 Qwen3.5-2B，并决定是否复跑同一流程。


## 2026-06-29 Qwen3.5-2B 适配问题与当前汇报口径

### 背景
老师原始任务希望跑 SLIME 在 MMLU-Pro 上做强化学习 demo，模型使用 qwen3.5-2B。

### 当前实际完成情况
当前已先使用服务器本地可用的 Qwen2.5-1.5B-Instruct 跑通 SLIME + MMLU-Pro 强化学习 demo 闭环，包括：
- baseline eval
- reward function 接入
- SLIME rollout
- GRPO 训练
- checkpoint 保存
- Megatron / torch distributed checkpoint 转 HuggingFace
- 训练后 dev_100_direct eval
- before/after 样本级对比

### Qwen3.5-2B 未完成原因
前期尝试适配 qwen3.5-2B 时，在 Transformer Engine DotProductAttention 路径遇到：

ValueError: No dot product attention backend is available for the provided inputs.

该错误发生在 ref_log_probs forward / MegatronTrainRayActor.train() / Transformer Engine DotProductAttention 相关路径中。

### 排查结论
该问题不是 MMLU-Pro 数据、reward function 或 SLIME 主训练流程的问题，而是模型执行层的 attention backend 选择失败。

已知排查点：
- 旧脚本中曾设置 NVTE_FLASH_ATTN=0、NVTE_FUSED_ATTN=0、NVTE_UNFUSED_ATTN=1。
- 但 UnfusedDotProductAttention 因 qkv_format=thd 被禁用。
- FlashAttention 3 因当前 GPU compute capability 不是 sm90 被禁用。
- FlashAttention 2 因 head_dim_qk/head_dim_v=256 在当前 sm86 环境下不支持而被禁用。
- Fused/cuDNN 路径后续也未能选出可用 backend。
- 最终 Transformer Engine selected backend = NoBackend。

### 当前判断
Qwen3.5-2B 在当前 RTX 3090 / sm86 + Transformer Engine 路径下存在 attention backend 兼容性 blocker。为避免长期卡在模型执行层适配问题，当前先切换到 Qwen2.5-1.5B-Instruct 完成 SLIME + MMLU-Pro RL demo 工程闭环。

### 对外汇报口径
目前已用服务器本地可用的 Qwen2.5-1.5B-Instruct 跑通 SLIME + MMLU-Pro 强化学习 demo 闭环。qwen3.5-2B 严格版本尚未完成，原因是 Transformer Engine 没有为该模型在当前硬件/软件环境下选到可用的 dot product attention backend。后续如需严格复跑 qwen3.5-2B，需要进一步处理 Transformer Engine / FlashAttention / cuDNN / GPU 架构兼容性问题，或更换支持该 attention 配置的运行环境。


## 2026-06-30 PRO6000 Qwen3.5-35B-A3B 推理链路排查汇总

### 阶段
将 SLIME + MMLU-Pro demo 迁移到 PRO6000 平台，优先测试 `/models/Qwen3.5-35B-A3B`。当前目标是在进入 MMLU-Pro baseline 或 SLIME 训练前，先确认 35B-A3B 的推理链路是否可靠。

### 环境状态
- GPU：4 × NVIDIA RTX PRO 6000 Blackwell Server Edition
- 单卡显存：约 95 GiB / 96GB
- PyTorch：2.11.0+cu129
- torch CUDA：12.9
- 模型路径：`/models/Qwen3.5-35B-A3B`
- 数据集路径：`/data/MMLU-Pro`
- 代码仓库：`/workspace/slime-mmlu-pro-demo`

### 模型与数据检查
- Qwen3.5-35B-A3B 模型目录存在，约 67 GiB，包含 14 个 safetensors 权重分片。
- tokenizer/config 可读。
- model_type: `qwen3_5_moe`
- architectures: `['Qwen3_5MoeForConditionalGeneration']`
- MMLU-Pro 数据集可读：test 12032 rows，validation 70 rows。

### 模型加载检查
使用 Transformers 加载模型成功：
- `trust_remote_code=True`
- `local_files_only=True`
- `torch_dtype=torch.bfloat16`
- `device_map="auto"`
- `max_memory={i: "85GiB"}`

模型可切分加载到 4 张 GPU，显存充足，不是 OOM 或 GPU 不可见问题。

### 推理异常
普通生成与选择题 scoring 均异常：
- 裸 prompt 生成出现 `sach sach ...`
- chat template 生成出现大量 `!`
- 普通 `1+1` 中文问答生成异常重复内容
- 对 `2+2=?` 的 A/B/C/D logprob 全部相同，约为 `-12.4375`

### 权重与 loading_info 检查
模型权重加载完整：
- missing_keys count: 0
- unexpected_keys count: 0
- mismatched_keys count: 0

关键权重非零：
- `model.embed_tokens.weight std = 0.01264`
- `lm_head.weight std = 0.01880`
- `model.norm.weight std = 0.22299`
- `model.layers.0.mlp.gate.weight std = 0.02305`
- `model.layers.0.mlp.experts.gate_up_proj std = 0.00694`
- `model.layers.0.mlp.experts.down_proj std = 0.00770`

### hidden/logits 深度诊断
forward 输出异常：
- `last_hidden finite = True`
- `last_hidden min = 0.0`
- `last_hidden max = 0.0`
- `last_hidden mean = 0.0`
- `last_hidden std = 0.0`
- `out.logits finite = True`
- `out.logits std = 0.0`

当前判断：问题发生在 `lm_head` 之前。模型 backbone forward 已经产生全 0 hidden state。模型文件、lm_head、embedding 和 MoE 权重不像损坏。

### FLA / causal-conv1d 依赖排查
依赖检查结果：
- `fla OK 0.4.1`
- `causal_conv1d` 原本缺失

普通 `pip install causal-conv1d` 失败，原因是 pip build isolation 临时使用了 `torch 2.12.1+cu130`，与当前 CUDA 12.9 不匹配。

随后改用 `--no-build-isolation`，强制使用当前 torch 2.11.0+cu129 / CUDA 12.9 编译，最终成功：
- Successfully built causal-conv1d
- Successfully installed causal-conv1d-1.6.2.post1

### causal-conv1d 安装后复测
安装 `causal-conv1d` 后，重新运行 hidden/logits 诊断，结果仍异常：
- `last_hidden std = 0.0`
- `out.logits std = 0.0`

### 当前结论
`causal-conv1d` 缺失不是唯一原因，或者当前诊断脚本仍强制使用 eager 路径，未走到默认/fast attention。当前问题继续收窄到：
1. `attn_implementation="eager"` 路径问题；
2. `device_map="auto"` 多卡切分问题；
3. 当前 Transformers 5.8.1 对 Qwen3.5-35B-A3B forward 适配异常；
4. 后续可能需要转 SGLang/vLLM 后端测试。

### 下一步
1. 新建不指定 `attn_implementation` 的默认 attention 诊断脚本。
2. 如果默认 attention 仍然 `last_hidden std = 0`，做单卡加载诊断，排除 `device_map="auto"` 多卡切分问题。
3. 如果单卡仍异常，则转 SGLang/vLLM 后端继续测试 Qwen3.5-35B-A3B。

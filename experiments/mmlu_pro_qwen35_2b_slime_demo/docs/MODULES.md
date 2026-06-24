# 模块说明

本文档说明当前 demo 每个模块为什么存在、输入输出是什么、关键逻辑在哪里、当前状态如何。以后新增模块或修改模块行为时，需要同步更新这里。

## `data_scripts/prepare_mmlu_pro.py`

模块目标：

- 从 `TIGER-Lab/MMLU-Pro` 生成小规模 JSONL 数据，供 eval（评估）和 slime 训练使用。

输入：

- Hugging Face 数据集：`TIGER-Lab/MMLU-Pro`
- 命令行参数：
  - `--out-dir`
  - `--train-size`
  - `--dev-size`
  - `--train-offset`
  - `--dev-offset`

输出：

- `train_<实际行数>.jsonl`
- `dev_<实际行数>.jsonl`
- `val_<实际行数>.jsonl`
- 每行 JSON 包含 `prompt`、`label`、`metadata`。

关键函数或关键逻辑：

- `normalize_label()`：把数据集中的答案标准化成 A-J。
- `normalize_options()`：检查并清理选项列表。
- `build_prompt()`：构造要求最终输出 `Final answer: <A-J>` 的 prompt（提示词）。
- `convert_example()`：把原始样本转换成训练/eval 需要的 JSONL 行。
- `select_examples()`：按 offset（偏移量）和 size（数量）从 split 中取数据，并在 offset 越界时报错。
- `write_jsonl()`：写出 JSONL 文件。

目前状态：

- 已完成基础功能。
- 已修复 dev 误从 validation split 取数导致写 0 行的问题。
- 待在服务器上用真实 Hugging Face 或 hf-mirror 下载流程完整验证。

后续可能修改点：

- 增加 `--val-size` 或 `--val-offset`。
- 增加随机种子和 shuffle（打乱）策略。
- 增加数据去重检查，避免 train/dev 重叠。
- 增加更详细的数据统计输出。

## `reward/mmlu_reward.py`

模块目标：

- 从模型回复中抽取 A-J 答案，并根据标准答案返回 reward（奖励分数）。

输入：

- `response`、`output` 或 `completion` 字段中的模型文本。
- `label` 字段，或 `metadata["label"]` 中的标准答案。

输出：

- `1.0`：预测答案和 label 一致。
- `0.0`：答案错误、格式错误、无答案或 label 非法。

关键函数或关键逻辑：

- `extract_answer(text)`：抽取 A-J。
- `compute_reward(response, label)`：比较预测和 label。
- `reward_func(args, sample, **kwargs)`：slime 预期调用的 async（异步）reward 入口。
- 字段兼容：支持 `response`、`output`、`completion`；支持 `label` 和 `metadata["label"]`。

目前状态：

- 已完成基础功能。
- 已有 unittest 单测覆盖常见格式。
- 待在 slime 真实调用环境中验证 `reward_func` 参数结构。

后续可能修改点：

- 增加对更多模型输出格式的兼容。
- 统计格式错误率。
- 对重复答案或多个答案的情况制定更严格规则。

## `reward/test_mmlu_reward.py`

模块目标：

- 用 unittest（单元测试）验证 reward 抽取和打分逻辑，防止后续改坏。

输入：

- 手写的模型输出样例。
- 手写的 label 样例。

输出：

- 测试通过或失败。

关键函数或关键逻辑：

- 测试 `Final answer: A`。
- 测试 `The answer is (B)`。
- 测试 `Answer: C`。
- 测试尾部单独字母。
- 测试无答案。
- 测试正确 reward、错误 reward、非法 label。

目前状态：

- 已完成。
- 本地已通过 8 个测试。

后续可能修改点：

- 增加 `reward_func` 异步入口测试。
- 增加 `metadata["label"]` 兼容测试。
- 增加大小写、空格、换行、多答案输出测试。

## `eval/eval_sglang_api.py`

模块目标：

- 调用本地 SGLang OpenAI-compatible API（兼容 OpenAI 格式的接口），对 JSONL 数据做 baseline eval（基线评估）。

输入：

- `--data`：JSONL 数据文件。
- `--url`：SGLang chat completions API 地址。
- `--model`：模型名。
- `--temperature`：采样温度。
- `--max-tokens`：最大生成 token 数。
- `--out`：结果输出路径。

输出：

- 控制台打印逐条 prediction（预测）、label（标准答案）和 running accuracy（当前累计准确率）。
- JSONL 结果文件，默认 `outputs/eval_results.jsonl`。

关键函数或关键逻辑：

- `read_jsonl()`：读取输入数据。
- `call_chat_completion()`：发 HTTP POST 请求到 SGLang。
- `extract_answer()`：从回复中抽取 A-J。
- `normalize_label()`：兼容 `label` 和 `metadata["label"]`。
- `write_result()`：保存逐条结果。

目前状态：

- 已完成基础脚本。
- 待服务器启动 SGLang 后验证。

后续可能修改点：

- 增加重试机制。
- 增加请求超时参数。
- 增加并发请求。
- 复用 `reward/mmlu_reward.py` 中的答案抽取逻辑，避免重复维护。

## `slime_scripts/run_qwen35_2b_mmlu_pro_demo.sh`

模块目标：

- 提供服务器侧 slime demo 训练入口草稿。

输入：

- 环境变量：
  - `PROJECT_ROOT`
  - `EXP_DIR`
  - `DATA_DIR`
  - `OUTPUT_DIR`
  - `MODEL_PATH`
  - `REWARD_FILE`
  - `TRAIN_DATA`
  - `DEV_DATA`
  - `CUDA_VISIBLE_DEVICES`
- 数据文件：
  - `data/train_500.jsonl`
  - `data/dev_100.jsonl`

输出：

- 预期输出到 `outputs/slime_qwen35_2b_mmlu_pro_demo`。

关键函数或关键逻辑：

- 设置路径变量。
- 设置 8 卡 3090 小规模参数。
- 调用 `python -m slime`，把模型、数据、reward 和训练参数传入。

目前状态：

- 草稿。
- 未在真实 slime 环境验证。

后续可能修改点：

- 根据服务器上实际 slime CLI（命令行接口）调整参数名。
- 增加日志路径。
- 增加 checkpoint（检查点）保存和恢复参数。
- 增加 SGLang/rollout 服务连接参数。

## `notes/` 目录

模块目标：

- 存放轻量实验笔记和操作记录，偏临时、偏人类阅读。

输入：

- 实验设计、服务器检查项、手动记录的错误。

输出：

- `notes/experiment_plan.md`
- `notes/server_checklist.md`
- `notes/error_log.md`

关键文件：

- `experiment_plan.md`：实验目标、模型、数据、reward、超参和指标。
- `server_checklist.md`：服务器 GPU、Docker、数据准备、测试和 demo 命令。
- `error_log.md`：错误日志模板。

目前状态：

- 已完成初版。

后续可能修改点：

- 把确认过的服务器命令同步回 `docs/RUNBOOK.md`。
- 把真实 bug 同步到 `docs/DEBUG_LOG.md`。
- 把长期稳定说明迁移到 `docs/`。

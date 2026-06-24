# Changelog

## 2026-06-24

### Added
- 新增 `docs/` 项目记忆目录。
- 新增 `docs/README.md`，说明文档维护规则。
- 新增 `docs/ARCHITECTURE.md`，说明本地、GitHub、服务器、数据、reward、eval 和 slime 的整体关系。
- 新增 `docs/MODULES.md`，说明当前各模块职责和状态。
- 新增 `docs/INTERFACES.md`，说明 JSONL、prompt、label、metadata、reward 和 SGLang API 接口。
- 新增 `docs/CHANGELOG.md`，记录代码和文档修改历史。
- 新增 `docs/DEBUG_LOG.md`，记录已遇到和后续可能遇到的问题。
- 新增 `docs/RUNBOOK.md`，记录从零复现 demo 的操作手册。
- 新增 `docs/TODO.md`，按优先级整理后续任务。

### Changed
- 暂无代码逻辑修改。本次只创建和更新文档。

### Fixed
- 暂无新修复。本次文档补充了此前已修复的数据准备 dev 切分问题。

### Notes
- 以后新增代码、修改接口、修复 bug、调整实验流程时，必须同步更新相关文档。

## 2026-06-23

### Added
- 初始化 MMLU-Pro + Qwen3.5-2B + slime demo 目录。
- 新增 `data_scripts/prepare_mmlu_pro.py`，用于从 `TIGER-Lab/MMLU-Pro` 生成 JSONL 数据。
- 新增 `reward/mmlu_reward.py`，实现答案抽取、reward 计算和 slime 异步 reward 入口。
- 新增 `reward/test_mmlu_reward.py`，覆盖常见答案格式和奖励计算场景。
- 新增 `eval/eval_sglang_api.py`，用于调用本地 SGLang OpenAI-compatible API 计算 accuracy。
- 新增 `slime_scripts/run_qwen35_2b_mmlu_pro_demo.sh`，作为服务器侧 slime 训练脚本草稿。
- 新增 `notes/experiment_plan.md`，记录实验目标、模型、数据、reward、第一阶段超参和指标。
- 新增 `notes/server_checklist.md`，记录服务器检查命令和推荐路径。
- 新增 `notes/error_log.md`，作为错误日志模板。

### Changed
- `prepare_mmlu_pro.py` 的输出文件名改为按实际写入行数生成，例如 `train_20.jsonl`、`dev_10.jsonl`、`val_70.jsonl`。
- `prepare_mmlu_pro.py` 明确使用 `test` split 生成 train/dev，使用 `validation` split 生成 val。

### Fixed
- 修复 `prepare_mmlu_pro.py` 中 dev 数据误从 `validation` split 按默认 offset 取数，导致 `dev_100.jsonl` 写入 0 行的问题。
- 增加 offset 越界时的清晰 `ValueError`，避免静默写空文件。

### Notes
- reward 单测已在本地通过。
- slime 训练脚本仍是草稿，需要在服务器 slime 环境验证。
- 当前 `data/` 和 `outputs/` 属于运行产物，不应该提交到 Git。

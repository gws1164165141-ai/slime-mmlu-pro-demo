# TODO

本文档记录后续任务。优先级含义：

- P0：必须先做，否则后续流程可能无法继续。
- P1：跑 demo 需要做。
- P2：后续优化，可以在主流程跑通后处理。
- P3：学习和扩展，用于加深理解或扩展实验。

## P0：必须先做

- 确认 GitHub remote（远程仓库地址）指向正确仓库，避免 `Repository not found`。
- 确认 `data/`、`outputs/`、`.venv/`、`__pycache__/` 不会被提交到 Git。
- 服务器确认 GPU 和 CUDA：

```bash
nvidia-smi
nvidia-smi topo -m
```

- 服务器确认能访问 Hugging Face 或镜像：

```bash
curl -I https://huggingface.co
curl -I https://hf-mirror.com
```

- 如果服务器无法访问 Hugging Face，设置：

```bash
export HF_ENDPOINT=https://hf-mirror.com
```

## P1：跑 demo 需要做

- 服务器 clone（克隆）或 pull（拉取）最新代码到 `~/workspace/slime-mmlu-pro-demo`。
- 服务器创建 Python 环境并安装 `datasets` 等依赖。
- 服务器生成 MMLU-Pro 500/100/70 数据：

```bash
cd ~/workspace/slime-mmlu-pro-demo/experiments/mmlu_pro_qwen35_2b_slime_demo
python data_scripts/prepare_mmlu_pro.py --out-dir data --train-size 500 --dev-size 100 --train-offset 0 --dev-offset 500
```

- 服务器测试 reward：

```bash
cd ~/workspace/slime-mmlu-pro-demo/experiments/mmlu_pro_qwen35_2b_slime_demo/reward
PYTHONDONTWRITEBYTECODE=1 python -m unittest test_mmlu_reward.py
```

- 确认 slime 环境是否可用，包括 Docker 镜像、Python 包、命令行入口。
- 下载或准备 `Qwen/Qwen3.5-2B` 模型，确认路径或模型名能被 SGLang/slime 识别。
- 启动 SGLang baseline eval（基线评估）服务。
- 运行 `eval/eval_sglang_api.py`，得到 dev accuracy（开发集准确率）。
- 接入 slime RL（强化学习）训练，先做小规模 smoke test（冒烟测试）。
- 记录训练指标和 debug 日志，包括 reward 均值、accuracy、格式错误率、显存、速度和报错。

## P2：后续优化

- 给 `prepare_mmlu_pro.py` 增加 `--val-size` 和 `--val-offset`。
- 检查 train/dev 是否存在题目重叠，必要时增加去重。
- 让 `eval/eval_sglang_api.py` 复用 `reward/mmlu_reward.py` 的答案抽取逻辑，减少重复代码。
- 给 eval 脚本增加失败重试、请求超时参数和并发请求。
- 给 reward 增加 `metadata["label"]`、`output`、`completion` 的显式单测。
- 给 slime 脚本增加日志文件、checkpoint（检查点）保存和恢复配置。
- 整理一份 baseline eval 报告，记录不同 temperature（温度）和 max tokens（最大生成长度）的结果。

## P3：学习和扩展

- 学习 JSONL、prompt、label、metadata 之间的关系。
- 学习 reward（奖励函数）如何影响 RL（强化学习）训练。
- 学习 OpenAI-compatible API（兼容 OpenAI 格式接口）的请求和响应结构。
- 学习 SGLang 的模型服务启动方式。
- 学习 slime 的 rollout（采样）、global batch（全局批次）、num rollout（采样轮数）等参数含义。
- 扩展到更大的 MMLU-Pro 数据规模。
- 尝试更严格的答案格式约束和无效格式惩罚。
- 对比训练前后 dev/val accuracy（准确率）变化。

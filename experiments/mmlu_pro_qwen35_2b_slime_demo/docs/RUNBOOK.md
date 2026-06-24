# Runbook（运行手册）

这份 runbook（运行手册）用于从零复现当前 demo。命令分为本地 Windows 和服务器 Linux 两套。不要把服务器 IP、密码、token 写进文档。

## 1. 本地开发流程

本地项目路径：

```text
D:\myproject1
```

进入 demo 目录：

```powershell
cd D:\myproject1\experiments\mmlu_pro_qwen35_2b_slime_demo
```

查看当前文件：

```powershell
Get-ChildItem -Force
Get-ChildItem -Recurse -File
```

运行 reward 单测：

```powershell
cd D:\myproject1\experiments\mmlu_pro_qwen35_2b_slime_demo\reward
$env:PYTHONDONTWRITEBYTECODE="1"
python -m unittest test_mmlu_reward.py
```

注意：

- 本地主要做代码和文档编辑。
- 不建议在本地提交 `data/`、`outputs/`、`.venv/`。
- 如果在本地生成数据，只用于调试，提交前必须检查 Git 状态。

## 2. GitHub 推送流程

在本地仓库根目录检查状态：

```powershell
cd D:\myproject1
git status --short
git remote -v
```

如果 remote（远程仓库地址）错误，需要改成正确仓库：

```powershell
git remote set-url origin <你的 GitHub 仓库地址>
git ls-remote origin
```

提交前重点检查：

```powershell
git status --short
```

确认不要提交：

- `experiments/mmlu_pro_qwen35_2b_slime_demo/data/`
- `experiments/mmlu_pro_qwen35_2b_slime_demo/outputs/`
- `.venv/`
- `__pycache__/`

提交示例：

```powershell
git add experiments/mmlu_pro_qwen35_2b_slime_demo/data_scripts experiments/mmlu_pro_qwen35_2b_slime_demo/reward experiments/mmlu_pro_qwen35_2b_slime_demo/eval experiments/mmlu_pro_qwen35_2b_slime_demo/slime_scripts experiments/mmlu_pro_qwen35_2b_slime_demo/notes experiments/mmlu_pro_qwen35_2b_slime_demo/docs
git commit -m "Add MMLU-Pro slime demo docs and scripts"
git push origin main
```

## 3. 服务器 clone 流程

服务器目标路径：

```text
~/workspace/slime-mmlu-pro-demo
```

创建 workspace（工作目录）：

```bash
mkdir -p ~/workspace
cd ~/workspace
```

clone（克隆）仓库：

```bash
git clone <你的 GitHub 仓库地址> slime-mmlu-pro-demo
cd ~/workspace/slime-mmlu-pro-demo
```

如果已经 clone 过：

```bash
cd ~/workspace/slime-mmlu-pro-demo
git pull
```

进入 demo 目录：

```bash
cd ~/workspace/slime-mmlu-pro-demo/experiments/mmlu_pro_qwen35_2b_slime_demo
```

## 4. 服务器 Python 环境创建

创建虚拟环境：

```bash
cd ~/workspace/slime-mmlu-pro-demo
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

安装基础依赖：

```bash
pip install datasets requests
```

如果服务器不能访问 `huggingface.co`，先设置镜像：

```bash
export HF_ENDPOINT=https://hf-mirror.com
```

确认 Python 能运行：

```bash
python --version
python - <<'PY'
import sys
print(sys.executable)
PY
```

## 5. MMLU-Pro 数据生成

进入 demo 目录：

```bash
cd ~/workspace/slime-mmlu-pro-demo/experiments/mmlu_pro_qwen35_2b_slime_demo
```

如果需要 Hugging Face 镜像：

```bash
export HF_ENDPOINT=https://hf-mirror.com
```

生成默认 500/100/70 数据：

```bash
python data_scripts/prepare_mmlu_pro.py \
  --out-dir data \
  --train-size 500 \
  --dev-size 100 \
  --train-offset 0 \
  --dev-offset 500
```

期望输出：

```text
data/train_500.jsonl
data/dev_100.jsonl
data/val_70.jsonl
```

小规模测试可以运行：

```bash
python data_scripts/prepare_mmlu_pro.py \
  --out-dir data \
  --train-size 20 \
  --dev-size 10 \
  --train-offset 0 \
  --dev-offset 500
```

期望输出：

```text
data/train_20.jsonl
data/dev_10.jsonl
data/val_70.jsonl
```

## 6. reward 单测

进入 reward 目录：

```bash
cd ~/workspace/slime-mmlu-pro-demo/experiments/mmlu_pro_qwen35_2b_slime_demo/reward
PYTHONDONTWRITEBYTECODE=1 python -m unittest test_mmlu_reward.py
```

期望看到：

```text
Ran 8 tests
OK
```

## 7. eval 脚本检查

先确认 SGLang API 是否启动：

```bash
curl http://localhost:30000/v1/models
```

如果 SGLang 没有启动，这一步会失败。需要先按服务器上的 SGLang 环境启动模型服务。

启动后，运行 baseline eval（基线评估）：

```bash
cd ~/workspace/slime-mmlu-pro-demo/experiments/mmlu_pro_qwen35_2b_slime_demo
python eval/eval_sglang_api.py \
  --data data/dev_100.jsonl \
  --url http://localhost:30000/v1/chat/completions \
  --model Qwen/Qwen3.5-2B \
  --temperature 0.0 \
  --max-tokens 512 \
  --out outputs/eval_results.jsonl
```

检查输出：

```bash
tail -n 5 outputs/eval_results.jsonl
```

## 8. 后续 slime 训练入口

确认 GPU：

```bash
nvidia-smi
nvidia-smi topo -m
```

确认 demo 脚本：

```bash
cd ~/workspace/slime-mmlu-pro-demo/experiments/mmlu_pro_qwen35_2b_slime_demo
sed -n '1,200p' slime_scripts/run_qwen35_2b_mmlu_pro_demo.sh
```

运行草稿入口：

```bash
bash slime_scripts/run_qwen35_2b_mmlu_pro_demo.sh
```

注意：

- 这个脚本目前是草稿，需要根据服务器实际 slime CLI（命令行接口）调整。
- 第一次运行建议只做 smoke test（冒烟测试），不要直接长时间训练。
- 训练日志、模型输出、eval 结果应该写到 `outputs/`，不要提交到 Git。

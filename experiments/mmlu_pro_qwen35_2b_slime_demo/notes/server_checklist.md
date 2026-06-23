# Server Checklist

## Recommended Paths

- Project root: `/workspace/myproject1`
- Experiment dir: `/workspace/myproject1/experiments/mmlu_pro_qwen35_2b_slime_demo`
- Data dir: `/workspace/myproject1/experiments/mmlu_pro_qwen35_2b_slime_demo/data`
- Output dir: `/workspace/myproject1/experiments/mmlu_pro_qwen35_2b_slime_demo/outputs`
- Model cache: `/workspace/models` or the server's standard Hugging Face cache.

## GPU Checks

```bash
nvidia-smi
nvidia-smi topo -m
python - <<'PY'
import torch
print(torch.cuda.is_available())
print(torch.cuda.device_count())
for i in range(torch.cuda.device_count()):
    print(i, torch.cuda.get_device_name(i))
PY
```

## Docker GPU Check

```bash
docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi
```

## slime Docker Draft

Adjust image name, mount paths, shared memory, and ports for the target server.

```bash
docker run --rm -it \
  --gpus all \
  --ipc=host \
  --shm-size=64g \
  -v /workspace/myproject1:/workspace/myproject1 \
  -v /workspace/models:/workspace/models \
  -w /workspace/myproject1 \
  slime:latest \
  bash
```

## Data Preparation

```bash
cd /workspace/myproject1/experiments/mmlu_pro_qwen35_2b_slime_demo
python data_scripts/prepare_mmlu_pro.py \
  --out-dir data \
  --train-size 500 \
  --dev-size 100 \
  --train-offset 0 \
  --dev-offset 500
```

## Reward Tests

```bash
cd /workspace/myproject1/experiments/mmlu_pro_qwen35_2b_slime_demo/reward
PYTHONDONTWRITEBYTECODE=1 python -m unittest test_mmlu_reward.py
```

## SGLang API Check

```bash
curl http://localhost:30000/v1/models
```

## Demo Run

```bash
cd /workspace/myproject1/experiments/mmlu_pro_qwen35_2b_slime_demo
bash slime_scripts/run_qwen35_2b_mmlu_pro_demo.sh
```

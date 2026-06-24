# 接口说明

本文档记录模块之间的数据 interface（接口）。只要 JSONL 字段、prompt（提示词）、label（答案标签）、metadata（元数据）、reward（奖励函数）输入输出、SGLang API 参数发生变化，就必须更新本文档。

## JSONL 数据格式

JSONL 是 JSON Lines（每行一个 JSON 对象）格式。这个 demo 的每一行代表一道 MMLU-Pro 选择题。

每行必须包含：

- `prompt`：字符串，给模型看的完整题目和格式要求。
- `label`：字符串，标准答案，只能是 `A` 到 `J`。
- `metadata`：对象，保存辅助信息。

示例：

```json
{"prompt":"Answer the following multiple-choice question.\nChoose exactly one option from A through J.\n\nQuestion: Which option is correct?\n\nOptions:\nA. First choice\nB. Second choice\nC. Third choice\n\nThink step by step, then put your final choice on the last line.\nFinal answer format: Final answer: <A-J>","label":"B","metadata":{"label":"B","question_id":"demo-1","category":"example","src":"manual","answer_index":1}}
```

## `prompt` 字段格式

`prompt` 是模型输入。当前由 `data_scripts/prepare_mmlu_pro.py` 的 `build_prompt()` 生成。

当前结构：

```text
Answer the following multiple-choice question.
Choose exactly one option from A through J.

Question: <题目文本>

Options:
A. <选项 A>
B. <选项 B>
...

Think step by step, then put your final choice on the last line.
Final answer format: Final answer: <A-J>
```

关键约束：

- 选项字母范围是 A-J。
- 最后一行明确要求 `Final answer: <A-J>`。
- prompt 可以包含少于 10 个选项，但 label 必须对应实际选项。

## `label` 字段格式

`label` 是标准答案。

要求：

- 类型：字符串。
- 合法值：`A`、`B`、`C`、`D`、`E`、`F`、`G`、`H`、`I`、`J`。
- 建议使用大写。

非法示例：

- `"K"`
- `"1"`
- `""`
- `null`
- `"Answer: A"`

## `metadata` 字段格式

`metadata` 是辅助信息，不直接给模型生成答案，但用于排查、统计、兼容字段。

当前字段：

```json
{
  "label": "B",
  "question_id": "demo-1",
  "category": "example",
  "src": "manual",
  "answer_index": 1
}
```

字段说明：

- `metadata["label"]`：label 的冗余备份，便于 reward 兼容不同数据结构。
- `question_id`：原始题目 ID，可能为空。
- `category`：题目类别，可能为空。
- `src`：来源信息，可能为空。
- `answer_index`：原始答案下标，通常从 0 开始，可能为空。

## reward 函数期望输入格式

`reward/mmlu_reward.py` 需要从 sample（样本对象）中拿到模型输出和标准答案。

模型输出字段兼容：

- `sample["response"]`
- `sample["output"]`
- `sample["completion"]`

label 字段兼容：

- `sample["label"]`
- `sample["metadata"]["label"]`

reward 输入示例：

```json
{
  "response": "I compared the options.\nFinal answer: B",
  "label": "B",
  "metadata": {
    "label": "B",
    "question_id": "demo-1"
  }
}
```

也支持：

```json
{
  "completion": "The answer is (C).",
  "metadata": {
    "label": "C"
  }
}
```

## reward 函数输出格式

`compute_reward(response, label)` 输出 float（浮点数）：

- `1.0`：抽取出的答案和 label 一致。
- `0.0`：答案错误、没有抽取到答案、输出格式不支持、label 非法。

示例：

```python
compute_reward("Final answer: A", "A")  # 1.0
compute_reward("Final answer: B", "A")  # 0.0
compute_reward("I do not know.", "A")   # 0.0
compute_reward("Final answer: A", "K")  # 0.0
```

`reward_func(args, sample, **kwargs)` 是 async（异步）入口，给 slime 调用：

```python
score = await reward_func(args=None, sample={
    "output": "Answer: D",
    "metadata": {"label": "D"}
})
# score == 1.0
```

## eval 脚本调用 SGLang API 的参数格式

`eval/eval_sglang_api.py` 调用的是 OpenAI-compatible（兼容 OpenAI 格式）chat completions 接口。

默认 URL：

```text
http://localhost:30000/v1/chat/completions
```

请求体示例：

```json
{
  "model": "Qwen/Qwen3.5-2B",
  "messages": [
    {
      "role": "user",
      "content": "<prompt>"
    }
  ],
  "temperature": 0.0,
  "max_tokens": 512
}
```

期望响应关键字段：

```json
{
  "choices": [
    {
      "message": {
        "content": "Reasoning...\nFinal answer: B"
      }
    }
  ]
}
```

eval 输出每行结果包含：

- `index`
- `prompt`
- `label`
- `prediction`
- `correct`
- `response`
- `metadata`
- `error`
- `latency_sec`

## 常见字段兼容策略

为了降低不同训练/推理框架之间的接入成本，当前采用以下兼容策略：

- 模型输出字段优先级：`response` -> `output` -> `completion`。
- 标准答案优先级：`label` -> `metadata["label"]`。
- 答案抽取支持：
  - `Final answer: A`
  - `The answer is (B)`
  - `Answer: C`
  - 结尾单独字母，例如最后一行是 `D`
- 非法 label 不抛异常，reward 返回 `0.0`。
- 数据准备时 offset（偏移量）越界会抛 `ValueError`，避免静默生成空文件。

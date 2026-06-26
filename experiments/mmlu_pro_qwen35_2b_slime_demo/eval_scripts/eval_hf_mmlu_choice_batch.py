#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


def extract_choice(text: str):
    text = text.strip()

    # 1. Direct single-letter output, used by direct forced-choice prompts.
    if re.fullmatch(r"\(?[A-J]\)?[\s\.]*", text, flags=re.IGNORECASE):
        m = re.search(r"([A-J])", text, flags=re.IGNORECASE)
        return m.group(1).upper() if m else None

    # 2. Prefer explicit final-answer patterns. Use the last match if multiple appear.
    patterns = [
        r"Final answer\s*[:：]?\s*\(?([A-J])\)?\b",
        r"The final answer is\s*\(?([A-J])\)?\b",
        r"Answer\s*[:：]?\s*\(?([A-J])\)?\b",
        r"The answer is\s*\(?([A-J])\)?\b",
        r"Therefore,?\s*the correct answer is\s*\(?([A-J])\)?\b",
        r"[Tt]he correct answer is\s*\(?([A-J])\)?\b",
    ]

    for pat in patterns:
        matches = list(re.finditer(pat, text, flags=re.IGNORECASE))
        if matches:
            return matches[-1].group(1).upper()

    # 3. Conservative fallback: only use the last standalone letter.
    # This is safer than taking the first letter in reasoning text,
    # because the first letter often belongs to option enumeration.
    letters = re.findall(r"\b([A-J])\b", text)
    if letters:
        return letters[-1].upper()

    return None


def load_jsonl(path: Path, limit: int | None):
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            rows.append(json.loads(line))
            if limit is not None and len(rows) >= limit:
                break
    return rows


def build_input(tokenizer, prompt: str):
    messages = [{"role": "user", "content": prompt}]
    if getattr(tokenizer, "chat_template", None):
        return tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )
    return prompt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--data", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--max-new-tokens", type=int, default=8)
    parser.add_argument("--temperature", type=float, default=0.0)
    args = parser.parse_args()

    data_path = Path(args.data)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    rows = load_jsonl(data_path, args.limit)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.bfloat16 if device == "cuda" else torch.float32

    print(f"model={args.model}")
    print(f"data={data_path}")
    print(f"num_examples={len(rows)}")
    print(f"device={device}")
    print(f"dtype={dtype}")
    print(f"batch_size={args.batch_size}")

    tokenizer = AutoTokenizer.from_pretrained(args.model, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        args.model,
        torch_dtype=dtype,
        trust_remote_code=True,
    ).to(device)
    model.eval()

    if tokenizer.pad_token_id is None:
        tokenizer.pad_token_id = tokenizer.eos_token_id
    tokenizer.padding_side = "left"

    correct = 0
    total = 0

    with out_path.open("w", encoding="utf-8") as fout:
        for start in range(0, len(rows), args.batch_size):
            batch = rows[start : start + args.batch_size]
            prompts = [build_input(tokenizer, row["prompt"]) for row in batch]

            inputs = tokenizer(
                prompts,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=2048,
            ).to(device)

            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=args.max_new_tokens,
                    do_sample=args.temperature > 0,
                    temperature=args.temperature,
                    pad_token_id=tokenizer.pad_token_id,
                    eos_token_id=tokenizer.eos_token_id,
                )

            input_len = inputs["input_ids"].shape[1]

            for i, row in enumerate(batch):
                new_tokens = outputs[i][input_len:]
                response = tokenizer.decode(new_tokens, skip_special_tokens=True)
                pred = extract_choice(response)
                label = row["label"]
                ok = pred == label

                correct += int(ok)
                total += 1

                record = {
                    "index": start + i,
                    "label": label,
                    "prediction": pred,
                    "correct": ok,
                    "response": response,
                    "metadata": row.get("metadata", {}),
                }
                fout.write(json.dumps(record, ensure_ascii=False) + "\n")

            acc = correct / total if total else 0.0
            print(f"progress {total}/{len(rows)} acc={acc:.4f}")

    acc = correct / total if total else 0.0
    print("=" * 80)
    print(f"FINAL accuracy: {correct}/{total} = {acc:.4f}")
    print(f"output={out_path}")
    print("=" * 80)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import argparse
import inspect
import re
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


CASES = [
    {
        "name": "bank_discount_proceeds",
        "label": "A",
        "question": """A customer borrowed $45,000 on a 120-day, 6% note. The bank discounted the note. What are the proceeds?

Options:
A. $44,100
B. $44,280
C. $44,550
D. $45,000
E. $45,900
F. $46,200
G. $43,900
H. $44,000
I. $45,100
J. $44,820""",
    },
    {
        "name": "exact_time_interest",
        "label": "E",
        "question": """Find the exact simple interest on $1,262.77 at 8% from March 8 to August 5, using exact time and a 365-day year. What is the interest?

Options:
A. $39.80
B. $40.00
C. $40.55
D. $41.00
E. $41.52
F. $42.10
G. $42.75
H. $43.20
I. $44.00
J. $45.52""",
    },
]


def extract_final_answer(text: str):
    patterns = [
        r"Final answer\s*[:：]\s*([A-J])\b",
        r"\\boxed\{([A-J])\}",
        r"Answer\s*[:：]\s*([A-J])\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return match.group(1).upper()
    return None


def build_prompt(question: str) -> str:
    return f"""/no_think

Solve the multiple-choice problem using the required compact format.

Rules:
- Do not use hidden thinking or <think> tags.
- Show only the essential calculation.
- For exact time interest, do not count the starting date unless the problem explicitly says to include it.
- End with exactly: Final answer: <A-J>

Format:
Formula:
Substitution:
Calculation:
Option match:
Final answer:

Question:
{question}
"""


def apply_chat_template_safely(tokenizer, messages):
    kwargs = dict(
        tokenize=False,
        add_generation_prompt=True,
    )

    try:
        sig = inspect.signature(tokenizer.apply_chat_template)
        if "enable_thinking" in sig.parameters:
            kwargs["enable_thinking"] = False
    except Exception:
        pass

    try:
        return tokenizer.apply_chat_template(messages, **kwargs)
    except TypeError:
        kwargs.pop("enable_thinking", None)
        return tokenizer.apply_chat_template(messages, **kwargs)


def make_input_text(tokenizer, prompt: str) -> str:
    messages = [
        {
            "role": "system",
            "content": "You are a precise exam solver. /no_think Use compact calculation only. Do not output <think> tags.",
        },
        {
            "role": "user",
            "content": prompt,
        },
    ]

    if getattr(tokenizer, "chat_template", None):
        return apply_chat_template_safely(tokenizer, messages)

    return "System: You are a precise exam solver. /no_think\n\nUser: " + prompt + "\n\nAssistant:"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--max-new-tokens", type=int, default=512)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--top-p", type=float, default=0.9)
    args = parser.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.bfloat16 if device == "cuda" else torch.float32

    print("=" * 100)
    print(f"model: {args.model}")
    print(f"device: {device}")
    print(f"dtype: {dtype}")
    print("=" * 100)

    tokenizer = AutoTokenizer.from_pretrained(args.model, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        args.model,
        torch_dtype=dtype,
        trust_remote_code=True,
    )
    model.to(device)
    model.eval()

    if tokenizer.pad_token_id is None:
        tokenizer.pad_token_id = tokenizer.eos_token_id

    correct = 0

    for idx, case in enumerate(CASES, start=1):
        prompt = build_prompt(case["question"])
        input_text = make_input_text(tokenizer, prompt)
        inputs = tokenizer(input_text, return_tensors="pt").to(device)

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=args.max_new_tokens,
                do_sample=args.temperature > 0,
                temperature=args.temperature,
                top_p=args.top_p,
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id,
            )

        new_tokens = outputs[0][inputs["input_ids"].shape[-1]:]
        response = tokenizer.decode(new_tokens, skip_special_tokens=False)
        pred = extract_final_answer(response)
        ok = pred == case["label"]
        correct += int(ok)

        print("\n" + "=" * 100)
        print(f"CASE {idx}: {case['name']}")
        print(f"gold label: {case['label']}")
        print("-" * 100)
        print("MODEL RESPONSE:")
        print(response)
        print("-" * 100)
        print(f"parsed final answer: {pred}")
        print(f"correct: {ok}")

    print("\n" + "=" * 100)
    print(f"SUMMARY: {correct}/{len(CASES)} correct")
    print("=" * 100)


if __name__ == "__main__":
    main()

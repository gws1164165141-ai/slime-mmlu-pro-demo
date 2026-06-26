#!/usr/bin/env python3
import argparse
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
        "expected_reasoning": "discount = 45000 * 0.06 * 120 / 360 = 900; proceeds = 45000 - 900 = 44100; Final answer: A",
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
        "expected_reasoning": "days ≈ 150; interest = 1262.77 * 0.08 * 150 / 365 ≈ 41.52; Final answer: E",
    },
]


def extract_final_answer(text: str):
    patterns = [
        r"Final answer\s*[:：]\s*([A-J])\b",
        r"final answer\s*[:：]\s*([A-J])\b",
        r"Answer\s*[:：]\s*([A-J])\b",
        r"answer\s*[:：]\s*([A-J])\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return match.group(1).upper()

    letters = re.findall(r"\b([A-J])\b", text.upper())
    if letters:
        return letters[-1]

    return None


def build_prompt(question: str) -> str:
    return f"""Solve the following multiple-choice question step by step.

First compute the numeric answer.
Then match it to one option.
End with exactly one line:
Final answer: <A-J>

Question:
{question}
"""


def make_input_text(tokenizer, prompt: str) -> str:
    messages = [
        {
            "role": "system",
            "content": "You are a careful math and exam reasoning assistant.",
        },
        {
            "role": "user",
            "content": prompt,
        },
    ]

    if getattr(tokenizer, "chat_template", None):
        return tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )

    return (
        "System: You are a careful math and exam reasoning assistant.\n\n"
        f"User: {prompt}\n\n"
        "Assistant:"
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, help="HF model path")
    parser.add_argument("--max-new-tokens", type=int, default=512)
    parser.add_argument("--temperature", type=float, default=0.3)
    parser.add_argument("--top-p", type=float, default=0.9)
    args = parser.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.bfloat16 if device == "cuda" else torch.float32

    print("=" * 100)
    print(f"model: {args.model}")
    print(f"device: {device}")
    print(f"dtype: {dtype}")
    print("=" * 100)

    tokenizer = AutoTokenizer.from_pretrained(
        args.model,
        trust_remote_code=True,
    )

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

        inputs = tokenizer(
            input_text,
            return_tensors="pt",
        ).to(device)

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
        print(f"expected reasoning: {case['expected_reasoning']}")
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

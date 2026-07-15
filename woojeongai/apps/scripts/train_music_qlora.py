# ruff: noqa: E402
"""EXAONE-3.5-2.4B-Instruct에 음악 추천 대화 데이터로 QLoRA(PEFT) 파인튜닝을 적용한다.

python3 train_music_qlora.py

전제: qlora_data/music_mood_recommendations.jsonl (messages: [user, assistant] 쌍)
결과: qlora_output/ 에 LoRA 어댑터(가중치)만 저장 (베이스 모델은 그대로 둠)
"""

import os
from pathlib import Path

import torch
from datasets import load_dataset
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    Trainer,
    TrainingArguments,
)

_SCRIPTS_DIR = Path(__file__).resolve().parent

MODEL_PATH = os.path.expanduser(
    os.getenv("QLORA_BASE_MODEL", "~/models/EXAONE-3.5-2.4B-Instruct")
)
DATA_PATH = _SCRIPTS_DIR / "qlora_data" / "music_mood_recommendations.jsonl"
OUTPUT_DIR = _SCRIPTS_DIR / "qlora_output"

# EXAONE 아키텍처의 실제 서브모듈 이름 (LLaMA류 q/k/v/o_proj·gate/up/down_proj와 다름).
# modeling_exaone.py의 ExaoneAttention/ExaoneMLP 정의를 그대로 따른다.
LORA_TARGET_MODULES = ["q_proj", "k_proj", "v_proj", "out_proj", "c_fc_0", "c_fc_1", "c_proj"]


def build_example(tokenizer, messages: list[dict[str, str]]) -> dict[str, list[int]]:
    prompt_text = tokenizer.apply_chat_template(
        messages[:-1], tokenize=False, add_generation_prompt=True
    )
    full_text = tokenizer.apply_chat_template(messages, tokenize=False)

    prompt_ids = tokenizer(prompt_text, add_special_tokens=False)["input_ids"]
    full_ids = tokenizer(full_text, add_special_tokens=False)["input_ids"]

    labels = [-100] * len(prompt_ids) + full_ids[len(prompt_ids) :]
    return {"input_ids": full_ids, "attention_mask": [1] * len(full_ids), "labels": labels}


def collate(tokenizer, batch: list[dict[str, list[int]]]) -> dict[str, torch.Tensor]:
    max_len = max(len(item["input_ids"]) for item in batch)
    pad_id = tokenizer.pad_token_id

    input_ids, attention_mask, labels = [], [], []
    for item in batch:
        pad_len = max_len - len(item["input_ids"])
        input_ids.append(item["input_ids"] + [pad_id] * pad_len)
        attention_mask.append(item["attention_mask"] + [0] * pad_len)
        labels.append(item["labels"] + [-100] * pad_len)

    return {
        "input_ids": torch.tensor(input_ids, dtype=torch.long),
        "attention_mask": torch.tensor(attention_mask, dtype=torch.long),
        "labels": torch.tensor(labels, dtype=torch.long),
    }


def main() -> int:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
    )
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_PATH,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
    )
    model = prepare_model_for_kbit_training(model)

    lora_config = LoraConfig(
        r=16,
        lora_alpha=32,
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=LORA_TARGET_MODULES,
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    dataset = load_dataset("json", data_files=str(DATA_PATH))["train"]
    dataset = dataset.map(
        lambda ex: build_example(tokenizer, ex["messages"]),
        remove_columns=dataset.column_names,
    )

    training_args = TrainingArguments(
        output_dir=str(OUTPUT_DIR),
        per_device_train_batch_size=1,
        gradient_accumulation_steps=8,
        num_train_epochs=5,
        learning_rate=2e-4,
        bf16=True,
        logging_steps=5,
        save_strategy="no",
        report_to=[],
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        data_collator=lambda batch: collate(tokenizer, batch),
    )
    trainer.train()

    model.save_pretrained(str(OUTPUT_DIR))
    tokenizer.save_pretrained(str(OUTPUT_DIR))
    print(f"LoRA 어댑터 저장 완료: {OUTPUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

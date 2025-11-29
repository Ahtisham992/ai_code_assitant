"""
Model architecture and training utilities
Fine-tunes CodeT5 for multiple code assistance tasks
"""

import torch
from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    Seq2SeqTrainingArguments,
    Seq2SeqTrainer,
    DataCollatorForSeq2Seq
)
from typing import Dict, List
import numpy as np
from datasets import Dataset

from config import config


class CodeAssistantModel:
    """Wrapper class for code assistance model"""

    def __init__(self, model_config=config):
        self.config = model_config
        self.tokenizer = None
        self.model = None

    def load_model(self, model_name: str = None):
        """Load pretrained model and tokenizer"""
        model_name = model_name or self.config.base_model

        print(f"Loading model: {model_name}")

        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            cache_dir=self.config.cache_dir
        )

        self.model = AutoModelForSeq2SeqLM.from_pretrained(
            model_name,
            cache_dir=self.config.cache_dir
        )

        # Enable gradient checkpointing for memory efficiency
        if self.config.gradient_checkpointing:
            self.model.gradient_checkpointing_enable()

        print(f"Model loaded with {self.model.num_parameters():,} parameters")

        return self.model, self.tokenizer

    def preprocess_function(self, examples: Dict) -> Dict:
        """Preprocess data for training"""
        # Add task prefix to input
        inputs = []
        for input_text, task in zip(examples["input"], examples["task"]):
            prefix = self.config.task_prefix.get(task, "")
            inputs.append(prefix + input_text)

        # Tokenize inputs
        model_inputs = self.tokenizer(
            inputs,
            max_length=self.config.max_source_length,
            padding="max_length",
            truncation=True,
        )

        # Tokenize targets
        labels = self.tokenizer(
            text_target=examples["output"],
            max_length=self.config.max_target_length,
            padding="max_length",
            truncation=True,
        )

        model_inputs["labels"] = labels["input_ids"]

        return model_inputs

    def prepare_datasets(self, train_dataset: Dataset, val_dataset: Dataset):
        """Prepare datasets for training"""
        print("Preprocessing datasets...")

        # Process datasets
        train_dataset = train_dataset.map(
            self.preprocess_function,
            batched=True,
            remove_columns=train_dataset.column_names,
            desc="Processing train dataset"
        )

        val_dataset = val_dataset.map(
            self.preprocess_function,
            batched=True,
            remove_columns=val_dataset.column_names,
            desc="Processing validation dataset"
        )

        return train_dataset, val_dataset

    def get_training_args(self) -> Seq2SeqTrainingArguments:
        """Get training arguments"""
        return Seq2SeqTrainingArguments(
            output_dir=self.config.output_dir,
            eval_strategy="steps",
            eval_steps=500,
            logging_dir=self.config.logging_dir,
            logging_steps=100,
            save_strategy="steps",
            save_steps=500,
            save_total_limit=3,
            learning_rate=self.config.learning_rate,
            per_device_train_batch_size=self.config.batch_size,
            per_device_eval_batch_size=self.config.batch_size,
            gradient_accumulation_steps=self.config.gradient_accumulation_steps,
            weight_decay=self.config.weight_decay,
            num_train_epochs=self.config.num_epochs,
            warmup_steps=self.config.warmup_steps,
            predict_with_generate=True,
            fp16=self.config.fp16,
            load_best_model_at_end=True,
            metric_for_best_model="eval_loss",
            report_to=["tensorboard"],
            push_to_hub=False,
        )

    def compute_metrics(self, eval_preds):
        """Compute evaluation metrics"""
        predictions, labels = eval_preds

        # Decode predictions and labels
        if isinstance(predictions, tuple):
            predictions = predictions[0]

        # Replace -100 in labels (used for padding)
        labels = np.where(labels != -100, labels, self.tokenizer.pad_token_id)

        decoded_preds = self.tokenizer.batch_decode(
            predictions, skip_special_tokens=True
        )
        decoded_labels = self.tokenizer.batch_decode(
            labels, skip_special_tokens=True
        )

        # Simple metrics - can be extended with BLEU, ROUGE, etc.
        # For now, calculate average length
        pred_lens = [len(pred.split()) for pred in decoded_preds]

        return {
            "avg_pred_length": np.mean(pred_lens),
        }

    def train(self, train_dataset: Dataset, val_dataset: Dataset):
        """Train the model"""
        print("Starting training...")

        # Prepare datasets
        train_dataset, val_dataset = self.prepare_datasets(
            train_dataset, val_dataset
        )

        # Data collator
        data_collator = DataCollatorForSeq2Seq(
            self.tokenizer,
            model=self.model,
            padding=True
        )

        # Training arguments
        training_args = self.get_training_args()

        # Initialize trainer
        trainer = Seq2SeqTrainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            tokenizer=self.tokenizer,
            data_collator=data_collator,
            compute_metrics=self.compute_metrics,
        )

        # Train
        train_result = trainer.train()

        # Save model
        trainer.save_model()
        self.tokenizer.save_pretrained(self.config.output_dir)

        # Save metrics
        metrics = train_result.metrics
        trainer.log_metrics("train", metrics)
        trainer.save_metrics("train", metrics)

        print(f"Training completed! Model saved to {self.config.output_dir}")

        return trainer, metrics

    def load_finetuned_model(self, model_path: str = None):
        """Load fine-tuned model"""
        model_path = model_path or self.config.output_dir

        print(f"Loading fine-tuned model from {model_path}")

        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_path)

        # Move to GPU if available
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(device)

        return self.model, self.tokenizer


class ModelEvaluator:
    """Evaluate model performance"""

    def __init__(self, model, tokenizer, config=config):
        self.model = model
        self.tokenizer = tokenizer
        self.config = config
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)

    def generate_output(self, input_text: str, task: str = "explain") -> str:
        """Generate output for given input"""
        # Add task prefix
        prefix = self.config.task_prefix.get(task, "")
        full_input = prefix + input_text

        # Tokenize
        inputs = self.tokenizer(
            full_input,
            max_length=self.config.max_source_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        ).to(self.device)

        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=self.config.max_target_length,
                num_beams=self.config.num_beams,
                temperature=self.config.temperature,
                top_p=self.config.top_p,
                early_stopping=True
            )

        # Decode
        generated_text = self.tokenizer.decode(
            outputs[0], skip_special_tokens=True
        )

        return generated_text

    def evaluate_on_dataset(self, test_dataset: Dataset) -> Dict:
        """Evaluate model on test dataset"""
        print("Evaluating model...")

        predictions = []
        references = []

        for example in test_dataset:
            pred = self.generate_output(example["input"], example["task"])
            predictions.append(pred)
            references.append(example["output"])

        # Calculate metrics (can be extended)
        results = {
            "num_samples": len(predictions),
            "avg_pred_length": np.mean([len(p.split()) for p in predictions]),
            "avg_ref_length": np.mean([len(r.split()) for r in references]),
        }

        return results
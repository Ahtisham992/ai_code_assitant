"""
Configuration file for AI Code Assistant
Manages all hyperparameters and paths
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class ModelConfig:
    """Model architecture and training configuration"""

    # Base model selection
    base_model: str = "Salesforce/codet5-small"  # Optimized for Colab free tier
    # Alternative: "microsoft/codebert-base" or "Salesforce/codet5-base"

    # Model parameters
    max_source_length: int = 512
    max_target_length: int = 128

    # Training hyperparameters
    batch_size: int = 4  # Small for free Colab
    gradient_accumulation_steps: int = 4  # Effective batch size = 16
    learning_rate: float = 5e-5
    num_epochs: int = 3
    warmup_steps: int = 500
    weight_decay: float = 0.01

    # Optimization
    fp16: bool = True  # Mixed precision training
    gradient_checkpointing: bool = True  # Memory efficient

    # Paths
    output_dir: str = "./models/finetuned_model"
    cache_dir: str = "./cache"
    logging_dir: str = "./logs"

    # Data
    train_data_path: str = "./data/train.jsonl"
    val_data_path: str = "./data/val.jsonl"
    test_data_path: str = "./data/test.jsonl"

    # Inference
    temperature: float = 0.7
    top_p: float = 0.95
    num_beams: int = 5

    # Task-specific settings
    task_prefix: dict = None

    def __post_init__(self):
        """Initialize task prefixes"""
        self.task_prefix = {
            "explain": "explain python code: ",
            "document": "generate documentation for: ",
            "fix_bug": "fix bug in python code: ",
            "optimize": "optimize python code: ",
            "generate_tests": "generate unit tests for: "
        }

        # Create directories
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.cache_dir, exist_ok=True)
        os.makedirs(self.logging_dir, exist_ok=True)


@dataclass
class DataConfig:
    """Data processing configuration"""

    # Dataset URLs (for automatic download)
    dataset_name: str = "code_x_glue_cc_code_to_code_trans"  # HuggingFace dataset

    # Processing
    validation_split: float = 0.1
    test_split: float = 0.1
    max_samples: Optional[int] = None  # None for full dataset, set to limit for testing

    # Filtering
    min_code_length: int = 50
    max_code_length: int = 2000

    # Augmentation
    use_augmentation: bool = True


# Global config instance
config = ModelConfig()
data_config = DataConfig()
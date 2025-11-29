"""
Main training script for AI Code Assistant
Single file for Google Colab execution
"""

import os
import sys
import argparse
import torch
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from config import config, data_config
from src.data_preprocessing import CodeDataProcessor
from src.model import CodeAssistantModel


def check_gpu():
    """Check GPU availability"""
    if torch.cuda.is_available():
        print(f"✓ GPU is available: {torch.cuda.get_device_name(0)}")
        print(f"  Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
    else:
        print("⚠ GPU not available, using CPU (training will be slow)")


def prepare_data():
    """Prepare training data"""
    print("\n" + "="*60)
    print("STEP 1: DATA PREPARATION")
    print("="*60)

    processor = CodeDataProcessor(config, data_config)

    # Check if data already exists
    if (Path(config.train_data_path).exists() and
        Path(config.val_data_path).exists()):
        print("Data files already exist. Loading...")
        train_dataset = processor.load_dataset_for_training("train")
        val_dataset = processor.load_dataset_for_training("validation")
    else:
        print("Preparing new data...")
        train_data, val_data, test_data = processor.prepare_training_data()
        train_dataset = processor.load_dataset_for_training("train")
        val_dataset = processor.load_dataset_for_training("validation")

    print(f"\nDataset sizes:")
    print(f"  Training: {len(train_dataset)} samples")
    print(f"  Validation: {len(val_dataset)} samples")

    return train_dataset, val_dataset


def train_model(train_dataset, val_dataset):
    """Train the model"""
    print("\n" + "="*60)
    print("STEP 2: MODEL TRAINING")
    print("="*60)

    # Initialize model
    model_wrapper = CodeAssistantModel(config)
    model, tokenizer = model_wrapper.load_model()

    print(f"\nTraining configuration:")
    print(f"  Base model: {config.base_model}")
    print(f"  Batch size: {config.batch_size}")
    print(f"  Gradient accumulation: {config.gradient_accumulation_steps}")
    print(f"  Effective batch size: {config.batch_size * config.gradient_accumulation_steps}")
    print(f"  Learning rate: {config.learning_rate}")
    print(f"  Epochs: {config.num_epochs}")
    print(f"  FP16: {config.fp16}")

    # Train
    trainer, metrics = model_wrapper.train(train_dataset, val_dataset)

    print("\n" + "="*60)
    print("TRAINING COMPLETED!")
    print("="*60)
    print(f"Model saved to: {config.output_dir}")
    print("\nTraining metrics:")
    for key, value in metrics.items():
        print(f"  {key}: {value}")

    return model_wrapper, trainer


def quick_test(model_wrapper):
    """Quick test of the trained model"""
    print("\n" + "="*60)
    print("STEP 3: QUICK MODEL TEST")
    print("="*60)

    # Load the fine-tuned model
    model_wrapper.load_finetuned_model()

    # Test cases
    test_cases = [
        {
            "task": "explain",
            "code": """def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)"""
        },
        {
            "task": "document",
            "code": """def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1"""
        },
        {
            "task": "fix_bug",
            "code": """def calculate_average(numbers):
    total = 0
    for num in numbers:
        total += num
    return total / len(numbers)"""  # Missing empty list check
        }
    ]

    from src.model import ModelEvaluator
    evaluator = ModelEvaluator(model_wrapper.model, model_wrapper.tokenizer)

    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i} - Task: {test['task']}")
        print(f"Input code:\n{test['code']}")
        print(f"\nGenerated output:")

        output = evaluator.generate_output(test['code'], test['task'])
        print(output)
        print("-" * 60)


def main():
    """Main training pipeline"""
    parser = argparse.ArgumentParser(description='Train AI Code Assistant')
    parser.add_argument('--skip-data', action='store_true',
                        help='Skip data preparation if data already exists')
    parser.add_argument('--test-only', action='store_true',
                        help='Only run model testing (requires trained model)')
    parser.add_argument('--epochs', type=int, default=None,
                        help='Number of training epochs')
    parser.add_argument('--batch-size', type=int, default=None,
                        help='Training batch size')

    args = parser.parse_args()

    # Update config if arguments provided
    if args.epochs:
        config.num_epochs = args.epochs
    if args.batch_size:
        config.batch_size = args.batch_size

    print("="*60)
    print("AI CODE ASSISTANT - TRAINING PIPELINE")
    print("="*60)

    # Check GPU
    check_gpu()

    if args.test_only:
        # Only test existing model
        print("\nTesting existing model...")
        model_wrapper = CodeAssistantModel(config)
        quick_test(model_wrapper)
        return

    # Step 1: Prepare data
    if not args.skip_data:
        train_dataset, val_dataset = prepare_data()
    else:
        print("\nSkipping data preparation, loading existing data...")
        processor = CodeDataProcessor(config, data_config)
        train_dataset = processor.load_dataset_for_training("train")
        val_dataset = processor.load_dataset_for_training("validation")

    # Step 2: Train model
    model_wrapper, trainer = train_model(train_dataset, val_dataset)

    # Step 3: Quick test
    quick_test(model_wrapper)

    print("\n" + "="*60)
    print("ALL STEPS COMPLETED SUCCESSFULLY!")
    print("="*60)
    print(f"\nYou can now use the model for inference:")
    print(f"  python inference_demo.py")
    print(f"\nOr run evaluation:")
    print(f"  python evaluate.py")


if __name__ == "__main__":
    main()
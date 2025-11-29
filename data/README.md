# Data Directory

This directory contains the training, validation, and test datasets for the AI Code Assistant.

## Data Files

- `train.jsonl` - Training dataset
- `val.jsonl` - Validation dataset  
- `test.jsonl` - Test dataset

## Data Format

Each line in the JSONL files contains a JSON object with the following structure:

```json
{
  "input": "Python code string",
  "output": "Expected output (explanation, documentation, or fixed code)",
  "task": "Task type (explain, document, fix_bug, optimize, generate_tests)"
}
```

## Data Preparation

The data is automatically prepared when you run:

```bash
python train.py
```

Or manually:

```bash
python -c "from src.data_preprocessing import CodeDataProcessor; CodeDataProcessor().prepare_training_data()"
```

## Data Sources

1. **CodeSearchNet**: Python subset from GitHub repositories
2. **Synthetic Data**: Generated examples for demonstration
3. **Augmented Data**: Code samples with introduced bugs for bug-fixing task

## Dataset Statistics

- Training samples: ~1000-2000 (configurable)
- Validation samples: ~100-200 (10% of total)
- Test samples: ~100-200 (10% of total)

## Custom Data

To add your own data, create JSONL files following the format above and place them in this directory. Update the paths in `config.py`:

```python
config.train_data_path = "./data/custom_train.jsonl"
config.val_data_path = "./data/custom_val.jsonl"
config.test_data_path = "./data/custom_test.jsonl"
```
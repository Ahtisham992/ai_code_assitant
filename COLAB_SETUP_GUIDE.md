# Google Colab Setup Guide 🚀

Complete guide to train your AI Code Assistant on Google Colab free tier.

## Prerequisites

- Google account
- Basic understanding of Python
- ~2-3 hours for training

## Step-by-Step Setup

### Option 1: Quick Setup (Recommended)

1. **Open Google Colab**
   - Go to [colab.research.google.com](https://colab.research.google.com)
   - Create a new notebook

2. **Connect to GPU Runtime**
   ```
   Runtime → Change runtime type → GPU (T4)
   ```

3. **Clone Repository**
   ```python
   !git clone https://github.com/yourusername/ai-code-assistant.git
   %cd ai-code-assistant
   ```

4. **Install Dependencies**
   ```python
   !pip install -q transformers datasets accelerate torch jsonlines tqdm
   !pip install -q tensorboard wandb
   ```

5. **Start Training**
   ```python
   !python train.py --epochs 3 --batch-size 4
   ```

6. **Monitor Progress**
   ```python
   %load_ext tensorboard
   %tensorboard --logdir logs/
   ```

### Option 2: Manual Setup

#### 1. Upload Files to Colab

```python
from google.colab import files
import os

# Create directory structure
!mkdir -p src data models logs

# Upload required files
print("Upload train.py")
uploaded = files.upload()

print("Upload config.py")
uploaded = files.upload()

print("Upload requirements.txt")
uploaded = files.upload()

# Upload src files
print("Upload all files from src/ directory")
uploaded = files.upload()
```

#### 2. Install Dependencies

```python
!pip install -r requirements.txt
```

#### 3. Verify GPU

```python
import torch
print(f"GPU Available: {torch.cuda.is_available()}")
print(f"GPU Name: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None'}")
```

#### 4. Prepare Data

```python
# Option A: Use pre-prepared data (upload train.jsonl, val.jsonl, test.jsonl to data/)

# Option B: Generate data automatically
!python -c "from src.data_preprocessing import CodeDataProcessor; CodeDataProcessor().prepare_training_data()"
```

#### 5. Configure Training (Optional)

```python
# Edit config.py for custom settings
# Or use command line arguments
```

#### 6. Train Model

```python
# Full training
!python train.py

# Or with custom parameters
!python train.py --epochs 5 --batch-size 8
```

## Training Configuration for Colab Free Tier

### Recommended Settings

```python
# config.py
base_model = "Salesforce/codet5-small"  # 60M parameters
batch_size = 4
gradient_accumulation_steps = 4  # Effective batch = 16
num_epochs = 3
fp16 = True  # Mixed precision
gradient_checkpointing = True
```

### Memory Management Tips

1. **Use Small Model**: `codet5-small` instead of `codet5-base`
2. **Enable FP16**: Reduces memory usage by ~50%
3. **Gradient Checkpointing**: Trades compute for memory
4. **Small Batch Size**: Use 2-4 with gradient accumulation
5. **Clear Cache**: Run `torch.cuda.empty_cache()` if needed

### Expected Training Time

- **codet5-small**: 2-3 hours for 3 epochs
- **codet5-base**: 5-6 hours for 3 epochs (may hit memory limits)

## Monitoring Training

### TensorBoard

```python
%load_ext tensorboard
%tensorboard --logdir logs/
```

### Manual Monitoring

```python
# Check GPU memory
!nvidia-smi

# View training logs
!tail -f logs/training.log
```

### WandB Integration (Optional)

```python
!pip install wandb
!wandb login

# Enable in training
# Logs will be sent to wandb.ai
```

## After Training

### 1. Test the Model

```python
!python inference_demo.py --demo all
```

### 2. Run Evaluation

```python
!python evaluate.py --test-samples 50
```

### 3. Try Interactive Mode

```python
!python inference_demo.py --interactive
```

### 4. Download Trained Model

```python
# Zip the model
!zip -r finetuned_model.zip models/finetuned_model/

# Download
from google.colab import files
files.download('finetuned_model.zip')
```

## Troubleshooting

### Out of Memory (OOM) Error

```python
# Reduce batch size
!python train.py --batch-size 2

# Or use even smaller model
# Change in config.py: base_model = "Salesforce/codet5-small"

# Clear GPU cache
import torch
torch.cuda.empty_cache()
```

### Runtime Disconnects

```python
# Colab free tier has time limits (~12 hours)
# To resume training:

# 1. Re-upload your files
# 2. The training script will resume from last checkpoint automatically
!python train.py --skip-data  # Skip data preparation
```

### Slow Training

```python
# Verify GPU is enabled
import torch
assert torch.cuda.is_available(), "GPU not available! Change runtime type."

# Check if FP16 is enabled
# In config.py: fp16 = True

# Increase gradient accumulation
!python train.py --batch-size 4  # Adjust as needed
```

### Import Errors

```python
# Reinstall dependencies
!pip install --upgrade transformers datasets torch

# Or install specific versions
!pip install transformers==4.30.0 torch==2.0.0
```

## Advanced Configuration

### Custom Dataset

```python
# Upload your custom data files
from google.colab import files

print("Upload train.jsonl")
uploaded = files.upload()
!mv train.jsonl data/

print("Upload val.jsonl")
uploaded = files.upload()
!mv val.jsonl data/

print("Upload test.jsonl")
uploaded = files.upload()
!mv test.jsonl data/

# Train with custom data
!python train.py --skip-data
```

### Multiple Training Runs

```python
# Run 1: Small model, quick test
!python train.py --epochs 1 --batch-size 4

# Run 2: Full training
!python train.py --epochs 3 --batch-size 4

# Run 3: Extended training
!python train.py --epochs 5 --batch-size 8
```

### Hyperparameter Tuning

```python
# Try different learning rates
learning_rates = [3e-5, 5e-5, 1e-4]

for lr in learning_rates:
    # Update config
    !sed -i 's/learning_rate: float = .*/learning_rate: float = {lr}/' config.py
    
    # Train
    !python train.py --epochs 2
    
    # Save results
    !mv models/finetuned_model models/model_lr_{lr}
```

## Colab Pro Benefits

If you upgrade to Colab Pro:

- **Longer runtime**: Up to 24 hours
- **Better GPUs**: A100, V100 access
- **More RAM**: 25-50GB system RAM
- **Faster training**: 2-3x speedup

Recommended settings for Colab Pro:

```python
base_model = "Salesforce/codet5-base"  # Use larger model
batch_size = 8
gradient_accumulation_steps = 2
num_epochs = 5
```

## Tips for Success

1. **Start Small**: Test with 1 epoch first
2. **Save Frequently**: Models auto-save every 500 steps
3. **Monitor Memory**: Check `nvidia-smi` regularly
4. **Use Checkpoints**: Training resumes from last checkpoint
5. **Download Models**: Always download after training
6. **Keep Colab Active**: Move mouse occasionally to prevent disconnect

## Resources

- [Google Colab FAQ](https://research.google.com/colaboratory/faq.html)
- [Colab Resource Limits](https://research.google.com/colaboratory/faq.html#resource-limits)
- [HuggingFace Training Tips](https://huggingface.co/docs/transformers/performance)

## Complete Colab Notebook Template

```python
# ===== SETUP =====
# 1. Change runtime to GPU
# Runtime → Change runtime type → GPU

# 2. Clone repository
!git clone https://github.com/yourusername/ai-code-assistant.git
%cd ai-code-assistant

# 3. Install dependencies
!pip install -q transformers datasets accelerate torch jsonlines tqdm

# 4. Verify GPU
import torch
print(f"GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None'}")

# ===== TRAINING =====
# 5. Train model
!python train.py --epochs 3 --batch-size 4

# ===== TESTING =====
# 6. Run demos
!python inference_demo.py --demo all

# 7. Evaluate
!python evaluate.py --examples-only

# ===== DOWNLOAD =====
# 8. Download trained model
!zip -r model.zip models/finetuned_model/
from google.colab import files
files.download('model.zip')
```

Save this as a notebook and you're ready to train! 🎉
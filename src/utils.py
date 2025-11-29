"""
Utility functions for AI Code Assistant
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Any
import torch


def setup_logging(log_file: str = "training.log", level=logging.INFO):
    """Setup logging configuration"""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


def save_json(data: Dict, filepath: str):
    """Save dictionary to JSON file"""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)


def load_json(filepath: str) -> Dict:
    """Load JSON file into dictionary"""
    with open(filepath, 'r') as f:
        return json.load(f)


def count_parameters(model: torch.nn.Module) -> int:
    """Count trainable parameters in model"""
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


def get_device() -> torch.device:
    """Get available device (CUDA or CPU)"""
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def create_dirs(dirs: List[str]):
    """Create directories if they don't exist"""
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)


def format_time(seconds: float) -> str:
    """Format seconds into readable time string"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"


def print_gpu_memory():
    """Print current GPU memory usage"""
    if torch.cuda.is_available():
        allocated = torch.cuda.memory_allocated() / 1e9
        reserved = torch.cuda.memory_reserved() / 1e9
        print(f"GPU Memory - Allocated: {allocated:.2f}GB, Reserved: {reserved:.2f}GB")


class MetricsTracker:
    """Track and save training metrics"""

    def __init__(self, save_dir: str = "./logs"):
        self.save_dir = save_dir
        self.metrics = {
            "train_loss": [],
            "val_loss": [],
            "learning_rate": [],
            "epoch": []
        }
        create_dirs([save_dir])

    def add_metric(self, name: str, value: float, step: int):
        """Add a metric value"""
        if name not in self.metrics:
            self.metrics[name] = []
        self.metrics[name].append({"step": step, "value": value})

    def save_metrics(self, filename: str = "metrics.json"):
        """Save metrics to file"""
        filepath = os.path.join(self.save_dir, filename)
        save_json(self.metrics, filepath)

    def load_metrics(self, filename: str = "metrics.json"):
        """Load metrics from file"""
        filepath = os.path.join(self.save_dir, filename)
        if os.path.exists(filepath):
            self.metrics = load_json(filepath)


def truncate_code(code: str, max_lines: int = 50) -> str:
    """Truncate code to maximum number of lines"""
    lines = code.split('\n')
    if len(lines) > max_lines:
        return '\n'.join(lines[:max_lines]) + f"\n... ({len(lines) - max_lines} more lines)"
    return code


def validate_python_code(code: str) -> bool:
    """Check if code is valid Python syntax"""
    import ast
    try:
        ast.parse(code)
        return True
    except SyntaxError:
        return False


def extract_code_blocks(text: str) -> List[str]:
    """Extract code blocks from markdown text"""
    import re
    pattern = r'```python\n(.*?)```'
    matches = re.findall(pattern, text, re.DOTALL)
    return matches


def calculate_code_complexity(code: str) -> Dict[str, int]:
    """Calculate basic code complexity metrics"""
    lines = code.split('\n')

    metrics = {
        "total_lines": len(lines),
        "code_lines": len([l for l in lines if l.strip() and not l.strip().startswith('#')]),
        "comment_lines": len([l for l in lines if l.strip().startswith('#')]),
        "blank_lines": len([l for l in lines if not l.strip()]),
        "functions": code.count('def '),
        "classes": code.count('class '),
        "imports": code.count('import ') + code.count('from ')
    }

    return metrics


class ProgressPrinter:
    """Simple progress printer for training"""

    def __init__(self, total_steps: int):
        self.total_steps = total_steps
        self.current_step = 0

    def update(self, loss: float = None):
        """Update progress"""
        self.current_step += 1
        progress = (self.current_step / self.total_steps) * 100

        msg = f"Progress: {self.current_step}/{self.total_steps} ({progress:.1f}%)"
        if loss is not None:
            msg += f" - Loss: {loss:.4f}"

        print(msg, end='\r')

        if self.current_step >= self.total_steps:
            print()  # New line at end
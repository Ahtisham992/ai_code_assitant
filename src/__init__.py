# src/__init__.py
"""
AI Code Assistant - Source Package
"""

from .model import CodeAssistantModel, ModelEvaluator
from .inference import CodeAssistant, InteractiveAssistant
from .data_preprocessing import CodeDataProcessor

__version__ = "1.0.0"
__author__ = "Your Name"

__all__ = [
    "CodeAssistantModel",
    "ModelEvaluator",
    "CodeAssistant",
    "InteractiveAssistant",
    "CodeDataProcessor"
]
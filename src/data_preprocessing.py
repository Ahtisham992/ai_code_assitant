"""
Data preprocessing module for Python code dataset
Handles data loading, cleaning, and augmentation
"""

import json
import random
import re
import ast
from typing import List, Dict, Tuple, Optional
from pathlib import Path
import jsonlines
from datasets import load_dataset, Dataset
from tqdm import tqdm

from config import config, data_config


class CodeDataProcessor:
    """Processes and prepares Python code data for training"""

    def __init__(self, config=config, data_config=data_config):
        self.config = config
        self.data_config = data_config

    def load_raw_data(self) -> Dict[str, List[Dict]]:
        """Load raw Python code data from multiple sources"""
        print("Loading raw data...")

        # Option 1: Use HuggingFace CodeSearchNet dataset
        try:
            dataset = load_dataset("code_search_net", "python", split="train")
            print(f"Loaded {len(dataset)} samples from CodeSearchNet")
            return self._process_codesearchnet(dataset)
        except:
            print("Could not load from HuggingFace, using synthetic data generation...")
            return self._generate_synthetic_data()

    def _process_codesearchnet(self, dataset) -> Dict[str, List[Dict]]:
        """Process CodeSearchNet dataset into training format"""
        processed_data = {
            "explain": [],
            "document": [],
            "fix_bug": []
        }

        for item in tqdm(dataset, desc="Processing samples"):
            code = item.get("func_code_string", "")
            docstring = item.get("func_documentation_string", "")

            if not code or len(code) < self.data_config.min_code_length:
                continue

            # Clean code
            code = self._clean_code(code)

            # Create multiple task formats from same code
            if docstring:
                # Documentation task
                processed_data["document"].append({
                    "input": code,
                    "output": docstring,
                    "task": "document"
                })

                # Explanation task
                explanation = f"This function {docstring}"
                processed_data["explain"].append({
                    "input": code,
                    "output": explanation,
                    "task": "explain"
                })

            # Bug fix task (create synthetic bugs)
            if self.data_config.use_augmentation and random.random() < 0.3:
                buggy_code, fix_desc = self._introduce_bug(code)
                if buggy_code:
                    processed_data["fix_bug"].append({
                        "input": buggy_code,
                        "output": code,
                        "task": "fix_bug",
                        "bug_description": fix_desc
                    })

            # Limit samples if specified
            total_samples = sum(len(v) for v in processed_data.values())
            if self.data_config.max_samples and total_samples >= self.data_config.max_samples:
                break

        return processed_data

    def _generate_synthetic_data(self) -> Dict[str, List[Dict]]:
        """Generate synthetic training data for demonstration"""
        print("Generating synthetic training data...")

        synthetic_samples = [
            {
                "code": """def calculate_sum(numbers):
    total = 0
    for num in numbers:
        total += num
    return total""",
                "doc": "Calculates the sum of all numbers in the input list.",
                "explanation": "This function takes a list of numbers and returns their sum by iterating through each number and accumulating the total."
            },
            {
                "code": """def find_max(arr):
    if not arr:
        return None
    max_val = arr[0]
    for item in arr:
        if item > max_val:
            max_val = item
    return max_val""",
                "doc": "Finds and returns the maximum value in an array. Returns None for empty arrays.",
                "explanation": "This function finds the maximum value in an array by iterating through all elements and keeping track of the largest value found."
            },
            {
                "code": """def reverse_string(s):
    return s[::-1]""",
                "doc": "Reverses the input string using Python slicing.",
                "explanation": "This function reverses a string by using Python's slice notation with a step of -1, which traverses the string backwards."
            },
            {
                "code": """def is_palindrome(text):
    text = text.lower().replace(' ', '')
    return text == text[::-1]""",
                "doc": "Checks if a string is a palindrome, ignoring case and spaces.",
                "explanation": "This function determines if a string is a palindrome by converting it to lowercase, removing spaces, and comparing it with its reverse."
            },
            {
                "code": """def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)""",
                "doc": "Calculates the factorial of n using recursion.",
                "explanation": "This recursive function calculates the factorial of a number by multiplying n with the factorial of n-1, with base case returning 1 for n <= 1."
            }
        ]

        # Expand with variations
        data = {"explain": [], "document": [], "fix_bug": []}

        for sample in synthetic_samples * 200:  # Repeat to create larger dataset
            code = sample["code"]

            data["document"].append({
                "input": code,
                "output": sample["doc"],
                "task": "document"
            })

            data["explain"].append({
                "input": code,
                "output": sample["explanation"],
                "task": "explain"
            })

            # Create buggy versions
            buggy_code, fix = self._introduce_bug(code)
            if buggy_code:
                data["fix_bug"].append({
                    "input": buggy_code,
                    "output": code,
                    "task": "fix_bug"
                })

        return data

    def _clean_code(self, code: str) -> str:
        """Clean and normalize code"""
        # Remove excessive whitespace
        code = re.sub(r'\n\s*\n', '\n\n', code)
        # Remove trailing whitespace
        code = '\n'.join(line.rstrip() for line in code.split('\n'))
        return code.strip()

    def _introduce_bug(self, code: str) -> Tuple[Optional[str], str]:
        """Introduce common Python bugs for training bug-fix task"""
        bug_types = [
            self._bug_indentation,
            self._bug_variable_name,
            self._bug_operator,
            self._bug_comparison,
        ]

        bug_func = random.choice(bug_types)
        return bug_func(code)

    def _bug_indentation(self, code: str) -> Tuple[Optional[str], str]:
        """Introduce indentation error"""
        lines = code.split('\n')
        if len(lines) < 3:
            return None, ""

        # Add extra indent to a random line
        idx = random.randint(1, len(lines) - 1)
        if lines[idx].strip():
            lines[idx] = "    " + lines[idx]
            return '\n'.join(lines), "Fixed indentation error"
        return None, ""

    def _bug_variable_name(self, code: str) -> Tuple[Optional[str], str]:
        """Introduce undefined variable"""
        # Change variable name in one place
        matches = re.findall(r'\b([a-z_][a-z0-9_]*)\b', code)
        if len(matches) > 2:
            var = matches[random.randint(0, len(matches) - 1)]
            buggy = code.replace(var, var + "_typo", 1)
            return buggy, f"Fixed undefined variable '{var}_typo'"
        return None, ""

    def _bug_operator(self, code: str) -> Tuple[Optional[str], str]:
        """Introduce operator error"""
        replacements = [('+', '-'), ('*', '/'), ('==', '='), ('>', '<')]
        for old, new in replacements:
            if old in code:
                buggy = code.replace(old, new, 1)
                return buggy, f"Fixed operator from '{new}' to '{old}'"
        return None, ""

    def _bug_comparison(self, code: str) -> Tuple[Optional[str], str]:
        """Introduce comparison error"""
        if '==' in code:
            buggy = code.replace('==', '=', 1)
            return buggy, "Fixed comparison operator from '=' to '=='"
        return None, ""

    def prepare_training_data(self, output_dir: str = "./data"):
        """Prepare and split data into train/val/test sets"""
        print("Preparing training data...")

        # Load raw data
        raw_data = self.load_raw_data()

        # Combine all tasks
        all_samples = []
        for task_type, samples in raw_data.items():
            all_samples.extend(samples)

        # Shuffle
        random.shuffle(all_samples)

        # Split
        n = len(all_samples)
        n_val = int(n * self.data_config.validation_split)
        n_test = int(n * self.data_config.test_split)
        n_train = n - n_val - n_test

        train_data = all_samples[:n_train]
        val_data = all_samples[n_train:n_train + n_val]
        test_data = all_samples[n_train + n_val:]

        print(f"Train: {len(train_data)}, Val: {len(val_data)}, Test: {len(test_data)}")

        # Save to files
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        self._save_jsonl(train_data, f"{output_dir}/train.jsonl")
        self._save_jsonl(val_data, f"{output_dir}/val.jsonl")
        self._save_jsonl(test_data, f"{output_dir}/test.jsonl")

        print(f"Data saved to {output_dir}/")

        return train_data, val_data, test_data

    def _save_jsonl(self, data: List[Dict], filepath: str):
        """Save data in JSONL format"""
        with jsonlines.open(filepath, mode='w') as writer:
            writer.write_all(data)

    def load_dataset_for_training(self, split: str) -> Dataset:
        """Load preprocessed dataset for training"""
        filepath = {
            "train": self.config.train_data_path,
            "validation": self.config.val_data_path,
            "test": self.config.test_data_path
        }[split]

        data = []
        with jsonlines.open(filepath) as reader:
            for item in reader:
                data.append(item)

        return Dataset.from_list(data)


if __name__ == "__main__":
    # Test data preprocessing
    processor = CodeDataProcessor()
    processor.prepare_training_data()
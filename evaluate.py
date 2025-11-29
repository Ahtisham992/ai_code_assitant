"""
Evaluation script for AI Code Assistant
Evaluates model performance on test set with multiple metrics
"""

import sys
import json
from pathlib import Path
from typing import Dict, List
import numpy as np

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.inference import CodeAssistant
from src.data_preprocessing import CodeDataProcessor
from src.model import ModelEvaluator
from config import config


class ComprehensiveEvaluator:
    """Comprehensive evaluation with multiple metrics"""

    def __init__(self, assistant: CodeAssistant):
        self.assistant = assistant

    def evaluate_on_test_set(self, test_data: List[Dict]) -> Dict:
        """Evaluate model on test set"""
        print("\n" + "="*60)
        print("EVALUATING MODEL ON TEST SET")
        print("="*60)

        results_by_task = {
            "explain": [],
            "document": [],
            "fix_bug": []
        }

        all_predictions = []
        all_references = []

        print(f"\nProcessing {len(test_data)} test samples...")

        for i, sample in enumerate(test_data):
            if i % 10 == 0:
                print(f"Progress: {i}/{len(test_data)}")

            task = sample.get("task", "explain")
            code = sample["input"]
            reference = sample["output"]

            # Generate prediction
            if task == "explain":
                prediction = self.assistant.explain_code(code)
            elif task == "document":
                prediction = self.assistant.generate_documentation(code)
            elif task == "fix_bug":
                result = self.assistant.fix_bug(code)
                prediction = result["fixed_code"]
            else:
                prediction = self.assistant.explain_code(code)

            all_predictions.append(prediction)
            all_references.append(reference)

            # Store by task
            results_by_task[task].append({
                "input": code,
                "prediction": prediction,
                "reference": reference
            })

        # Calculate metrics
        metrics = self._calculate_metrics(all_predictions, all_references)

        # Task-specific metrics
        task_metrics = {}
        for task, results in results_by_task.items():
            if results:
                preds = [r["prediction"] for r in results]
                refs = [r["reference"] for r in results]
                task_metrics[task] = self._calculate_metrics(preds, refs)

        return {
            "overall_metrics": metrics,
            "task_metrics": task_metrics,
            "num_samples": len(test_data)
        }

    def _calculate_metrics(self, predictions: List[str], references: List[str]) -> Dict:
        """Calculate evaluation metrics"""
        metrics = {}

        # Length metrics
        pred_lengths = [len(p.split()) for p in predictions]
        ref_lengths = [len(r.split()) for r in references]

        metrics["avg_prediction_length"] = np.mean(pred_lengths)
        metrics["avg_reference_length"] = np.mean(ref_lengths)
        metrics["length_ratio"] = np.mean(pred_lengths) / np.mean(ref_lengths)

        # Token overlap (simple measure)
        overlaps = []
        for pred, ref in zip(predictions, references):
            pred_tokens = set(pred.lower().split())
            ref_tokens = set(ref.lower().split())
            if ref_tokens:
                overlap = len(pred_tokens & ref_tokens) / len(ref_tokens)
                overlaps.append(overlap)

        metrics["avg_token_overlap"] = np.mean(overlaps) if overlaps else 0

        # Try to calculate BLEU if available
        try:
            from sacrebleu import corpus_bleu
            bleu = corpus_bleu(predictions, [references])
            metrics["bleu_score"] = bleu.score
        except:
            metrics["bleu_score"] = None

        # Try to calculate ROUGE if available
        try:
            from rouge_score import rouge_scorer
            scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)

            rouge_scores = {'rouge1': [], 'rouge2': [], 'rougeL': []}
            for pred, ref in zip(predictions, references):
                scores = scorer.score(ref, pred)
                for key in rouge_scores:
                    rouge_scores[key].append(scores[key].fmeasure)

            for key in rouge_scores:
                metrics[f"{key}_f1"] = np.mean(rouge_scores[key])
        except:
            metrics["rouge1_f1"] = None
            metrics["rouge2_f1"] = None
            metrics["rougeL_f1"] = None

        return metrics

    def evaluate_specific_examples(self) -> Dict:
        """Evaluate on specific hand-crafted examples"""
        print("\n" + "="*60)
        print("EVALUATING ON SPECIFIC EXAMPLES")
        print("="*60)

        examples = [
            {
                "task": "explain",
                "code": """def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr""",
                "expected_keywords": ["sort", "bubble", "compare", "swap"]
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
    return -1""",
                "expected_keywords": ["binary", "search", "sorted", "target"]
            }
        ]

        results = []

        for i, example in enumerate(examples, 1):
            print(f"\nExample {i} - Task: {example['task']}")
            print(f"Code:\n{example['code']}")

            if example['task'] == 'explain':
                output = self.assistant.explain_code(example['code'])
            elif example['task'] == 'document':
                output = self.assistant.generate_documentation(example['code'])

            print(f"\nGenerated Output:\n{output}")

            # Check for expected keywords
            output_lower = output.lower()
            found_keywords = [kw for kw in example['expected_keywords']
                            if kw in output_lower]

            print(f"\nExpected Keywords: {example['expected_keywords']}")
            print(f"Found Keywords: {found_keywords}")
            print(f"Coverage: {len(found_keywords)}/{len(example['expected_keywords'])}")

            results.append({
                "example": i,
                "task": example['task'],
                "keyword_coverage": len(found_keywords) / len(example['expected_keywords']),
                "output": output
            })

            print("-" * 60)

        return results


def print_evaluation_report(results: Dict):
    """Print formatted evaluation report"""
    print("\n" + "="*60)
    print("EVALUATION REPORT")
    print("="*60)

    if "overall_metrics" in results:
        print("\nOverall Metrics:")
        for metric, value in results["overall_metrics"].items():
            if value is not None:
                if isinstance(value, float):
                    print(f"  {metric}: {value:.4f}")
                else:
                    print(f"  {metric}: {value}")

        print(f"\nTotal samples evaluated: {results['num_samples']}")

    if "task_metrics" in results:
        print("\nTask-Specific Metrics:")
        for task, metrics in results["task_metrics"].items():
            print(f"\n  {task.upper()}:")
            for metric, value in metrics.items():
                if value is not None:
                    if isinstance(value, float):
                        print(f"    {metric}: {value:.4f}")
                    else:
                        print(f"    {metric}: {value}")


def save_evaluation_results(results: Dict, output_file: str = "evaluation_results.json"):
    """Save evaluation results to JSON file"""
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {output_file}")


def main():
    """Main evaluation pipeline"""
    import argparse

    parser = argparse.ArgumentParser(description='Evaluate AI Code Assistant')
    parser.add_argument('--model-path', type=str, default=None,
                        help='Path to fine-tuned model')
    parser.add_argument('--test-samples', type=int, default=100,
                        help='Number of test samples to use')
    parser.add_argument('--examples-only', action='store_true',
                        help='Only evaluate on specific examples')

    args = parser.parse_args()

    print("\n" + "="*60)
    print("AI CODE ASSISTANT - EVALUATION")
    print("="*60)

    # Load model
    print("\nLoading model...")
    assistant = CodeAssistant(args.model_path)

    evaluator = ComprehensiveEvaluator(assistant)

    all_results = {}

    # Evaluate on specific examples
    example_results = evaluator.evaluate_specific_examples()
    all_results["specific_examples"] = example_results

    if not args.examples_only:
        # Load test data
        try:
            processor = CodeDataProcessor()
            test_dataset = processor.load_dataset_for_training("test")

            # Limit samples if specified
            if args.test_samples:
                test_data = [test_dataset[i] for i in range(min(args.test_samples, len(test_dataset)))]
            else:
                test_data = list(test_dataset)

            # Evaluate on test set
            test_results = evaluator.evaluate_on_test_set(test_data)
            all_results.update(test_results)

        except Exception as e:
            print(f"\nWarning: Could not evaluate on test set: {e}")
            print("Continuing with example-based evaluation only...")

    # Print report
    print_evaluation_report(all_results)

    # Save results
    save_evaluation_results(all_results)

    print("\n" + "="*60)
    print("EVALUATION COMPLETED!")
    print("="*60)


if __name__ == "__main__":
    main()
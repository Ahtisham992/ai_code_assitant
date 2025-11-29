"""
Inference module for AI Code Assistant
Provides interface for code explanation, documentation, and bug fixing
"""

import torch
import ast
import re
from typing import Dict, List, Optional, Tuple
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

from config import config


class CodeAssistant:
    """Main inference class for code assistance tasks"""

    def __init__(self, model_path: str = None):
        """Initialize the code assistant"""
        self.model_path = model_path or config.output_dir
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        print(f"Loading model from {self.model_path}...")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_path)
        self.model.to(self.device)
        self.model.eval()

        print(f"Model loaded on {self.device}")

    def _generate(self, input_text: str, task: str,
                  max_length: int = None,
                  temperature: float = None,
                  num_beams: int = None) -> str:
        """Generate output for given input"""
        # Add task prefix
        prefix = config.task_prefix.get(task, "")
        full_input = prefix + input_text

        # Use config defaults if not specified
        max_length = max_length or config.max_target_length
        temperature = temperature or config.temperature
        num_beams = num_beams or config.num_beams

        # Tokenize
        inputs = self.tokenizer(
            full_input,
            max_length=config.max_source_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        ).to(self.device)

        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=max_length,
                num_beams=num_beams,
                temperature=temperature,
                top_p=config.top_p,
                early_stopping=True,
                no_repeat_ngram_size=3
            )

        # Decode
        generated_text = self.tokenizer.decode(
            outputs[0], skip_special_tokens=True
        )

        return generated_text

    def explain_code(self, code: str, detailed: bool = False) -> str:
        """
        Generate natural language explanation of code

        Args:
            code: Python code to explain
            detailed: If True, generate more detailed explanation

        Returns:
            Natural language explanation
        """
        max_length = 256 if detailed else 128
        explanation = self._generate(code, "explain", max_length=max_length)
        return explanation

    def generate_documentation(self, code: str, style: str = "google") -> str:
        """
        Generate docstring for code

        Args:
            code: Python code to document
            style: Documentation style (google, numpy, sphinx)

        Returns:
            Generated docstring
        """
        doc = self._generate(code, "document")

        # Format according to style
        if style == "google":
            doc = self._format_google_docstring(code, doc)
        elif style == "numpy":
            doc = self._format_numpy_docstring(code, doc)

        return doc

    def fix_bug(self, code: str, error_msg: str = None) -> Dict[str, str]:
        """
        Suggest bug fixes for code

        Args:
            code: Python code with potential bugs
            error_msg: Optional error message to help diagnose

        Returns:
            Dictionary with fixed code and explanation
        """
        # Analyze code for common issues
        issues = self._detect_issues(code)

        # Generate fix
        fixed_code = self._generate(code, "fix_bug")

        # Generate explanation
        explanation = f"Detected issues: {', '.join(issues)}" if issues else "No obvious issues detected."

        if error_msg:
            explanation += f"\nError message: {error_msg}"

        return {
            "fixed_code": fixed_code,
            "explanation": explanation,
            "detected_issues": issues
        }

    def optimize_code(self, code: str) -> Dict[str, str]:
        """
        Suggest code optimizations

        Args:
            code: Python code to optimize

        Returns:
            Dictionary with optimized code and suggestions
        """
        optimized = self._generate(code, "optimize")

        suggestions = self._get_optimization_suggestions(code)

        return {
            "optimized_code": optimized,
            "suggestions": suggestions
        }

    def generate_tests(self, code: str, num_tests: int = 3) -> List[str]:
        """
        Generate unit tests for code

        Args:
            code: Python code to test
            num_tests: Number of test cases to generate

        Returns:
            List of test cases
        """
        tests = []

        # Extract function name
        func_name = self._extract_function_name(code)

        if func_name:
            test_code = self._generate(code, "generate_tests", max_length=256)
            tests.append(test_code)

        return tests

    def _format_google_docstring(self, code: str, doc: str) -> str:
        """Format docstring in Google style"""
        # Extract function signature
        lines = code.split('\n')
        func_line = lines[0] if lines else ""

        # Parse parameters
        params = self._extract_parameters(func_line)

        formatted = f'"""{doc}\n\n'

        if params:
            formatted += "Args:\n"
            for param in params:
                formatted += f"    {param}: Description\n"

        formatted += "\nReturns:\n    Description of return value\n"
        formatted += '"""'

        return formatted

    def _format_numpy_docstring(self, code: str, doc: str) -> str:
        """Format docstring in NumPy style"""
        params = self._extract_parameters(code)

        formatted = f'"""{doc}\n\n'

        if params:
            formatted += "Parameters\n----------\n"
            for param in params:
                formatted += f"{param} : type\n    Description\n"

        formatted += "\nReturns\n-------\ntype\n    Description\n"
        formatted += '"""'

        return formatted

    def _detect_issues(self, code: str) -> List[str]:
        """Detect common code issues"""
        issues = []

        # Check for common patterns
        if '=' in code and '==' not in code:
            if 'if' in code or 'while' in code:
                issues.append("Possible assignment instead of comparison")

        # Check indentation
        lines = code.split('\n')
        indents = [len(line) - len(line.lstrip()) for line in lines if line.strip()]
        if indents and any(indent % 4 != 0 for indent in indents):
            issues.append("Inconsistent indentation")

        # Check for undefined variables (basic)
        try:
            ast.parse(code)
        except SyntaxError as e:
            issues.append(f"Syntax error: {str(e)}")

        return issues

    def _get_optimization_suggestions(self, code: str) -> List[str]:
        """Get optimization suggestions"""
        suggestions = []

        # Check for list comprehensions
        if 'for' in code and 'append' in code:
            suggestions.append("Consider using list comprehension")

        # Check for repeated computations in loops
        if 'for' in code or 'while' in code:
            if 'len(' in code:
                suggestions.append("Move len() call outside loop")

        # Check for dictionary/set membership
        if 'in' in code and '[' in code:
            suggestions.append("Consider using set for O(1) membership testing")

        return suggestions

    def _extract_function_name(self, code: str) -> Optional[str]:
        """Extract function name from code"""
        match = re.search(r'def\s+(\w+)\s*\(', code)
        return match.group(1) if match else None

    def _extract_parameters(self, func_signature: str) -> List[str]:
        """Extract parameter names from function signature"""
        match = re.search(r'\((.*?)\)', func_signature)
        if not match:
            return []

        params_str = match.group(1)
        params = [p.strip().split('=')[0].split(':')[0].strip()
                  for p in params_str.split(',') if p.strip()]

        # Remove 'self' for methods
        params = [p for p in params if p != 'self']

        return params


class InteractiveAssistant:
    """Interactive CLI for code assistant"""

    def __init__(self, model_path: str = None):
        self.assistant = CodeAssistant(model_path)

    def run(self):
        """Run interactive session"""
        print("\n" + "="*60)
        print("AI CODE ASSISTANT - Interactive Mode")
        print("="*60)
        print("\nAvailable commands:")
        print("  1. explain   - Explain code")
        print("  2. document  - Generate documentation")
        print("  3. fix       - Fix bugs")
        print("  4. optimize  - Optimize code")
        print("  5. test      - Generate tests")
        print("  6. quit      - Exit")
        print("\n" + "="*60)

        while True:
            print("\nEnter command (or 'quit' to exit):")
            command = input("> ").strip().lower()

            if command in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break

            if command not in ['explain', 'document', 'fix', 'optimize', 'test', '1', '2', '3', '4', '5']:
                print("Invalid command. Try again.")
                continue

            # Map numbers to commands
            command_map = {'1': 'explain', '2': 'document', '3': 'fix', '4': 'optimize', '5': 'test'}
            command = command_map.get(command, command)

            print("\nEnter your Python code (press Enter twice to finish):")
            code_lines = []
            empty_count = 0

            while empty_count < 2:
                line = input()
                if line == "":
                    empty_count += 1
                else:
                    empty_count = 0
                code_lines.append(line)

            code = '\n'.join(code_lines).strip()

            if not code:
                print("No code provided.")
                continue

            print("\nProcessing...")

            # Execute command
            if command == 'explain':
                result = self.assistant.explain_code(code, detailed=True)
                print(f"\nExplanation:\n{result}")

            elif command == 'document':
                result = self.assistant.generate_documentation(code)
                print(f"\nGenerated Documentation:\n{result}")

            elif command == 'fix':
                result = self.assistant.fix_bug(code)
                print(f"\nFixed Code:\n{result['fixed_code']}")
                print(f"\nExplanation:\n{result['explanation']}")

            elif command == 'optimize':
                result = self.assistant.optimize_code(code)
                print(f"\nOptimized Code:\n{result['optimized_code']}")
                if result['suggestions']:
                    print(f"\nSuggestions:")
                    for suggestion in result['suggestions']:
                        print(f"  - {suggestion}")

            elif command == 'test':
                result = self.assistant.generate_tests(code)
                print(f"\nGenerated Tests:")
                for i, test in enumerate(result, 1):
                    print(f"\nTest {i}:\n{test}")

            print("\n" + "-"*60)


if __name__ == "__main__":
    # Run interactive mode
    interactive = InteractiveAssistant()
    interactive.run()
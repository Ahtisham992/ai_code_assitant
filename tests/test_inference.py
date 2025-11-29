"""
Unit tests for inference module
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from src.inference import CodeAssistant
from config import config


# Test data
SAMPLE_CODE = """def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)"""


@pytest.fixture
def assistant():
    """Create CodeAssistant instance for testing"""
    try:
        return CodeAssistant()
    except:
        pytest.skip("Model not available for testing")


def test_code_explanation(assistant):
    """Test code explanation functionality"""
    explanation = assistant.explain_code(SAMPLE_CODE)

    assert isinstance(explanation, str)
    assert len(explanation) > 0
    assert any(word in explanation.lower() for word in ['factorial', 'recursive', 'function'])


def test_documentation_generation(assistant):
    """Test documentation generation"""
    doc = assistant.generate_documentation(SAMPLE_CODE)

    assert isinstance(doc, str)
    assert len(doc) > 0


def test_bug_fixing(assistant):
    """Test bug fixing functionality"""
    buggy_code = """def divide(a, b):
    return a / b"""

    result = assistant.fix_bug(buggy_code)

    assert "fixed_code" in result
    assert "explanation" in result
    assert isinstance(result["fixed_code"], str)


def test_code_optimization(assistant):
    """Test code optimization"""
    result = assistant.optimize_code(SAMPLE_CODE)

    assert "optimized_code" in result
    assert "suggestions" in result
    assert isinstance(result["suggestions"], list)


def test_test_generation(assistant):
    """Test unit test generation"""
    tests = assistant.generate_tests(SAMPLE_CODE)

    assert isinstance(tests, list)


def test_extract_function_name(assistant):
    """Test function name extraction"""
    func_name = assistant._extract_function_name(SAMPLE_CODE)
    assert func_name == "factorial"


def test_extract_parameters(assistant):
    """Test parameter extraction"""
    params = assistant._extract_parameters("def test(a, b, c=5):")
    assert "a" in params
    assert "b" in params
    assert "c" in params
    assert "self" not in params


def test_detect_issues(assistant):
    """Test issue detection"""
    code_with_issues = """def test():
    x = 5
    if x = 5:
        print(x)"""

    issues = assistant._detect_issues(code_with_issues)
    assert isinstance(issues, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
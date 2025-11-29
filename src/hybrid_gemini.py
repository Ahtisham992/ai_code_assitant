"""
Improved Hybrid AI Code Assistant
Fixed prompts for better output quality
"""

import torch
import os
import sys
from pathlib import Path
from typing import Dict, List
from transformers import AutoTokenizer, T5ForConditionalGeneration
import warnings
warnings.filterwarnings('ignore')

# Add root directory to path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

try:
    from google import genai
    from google.genai import types
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Import config
try:
    from config import config
except ImportError:
    class MinimalConfig:
        output_dir = "./models/finetuned_model"
        max_source_length = 512
        num_beams = 5
        task_prefix = {
            "explain": "explain python code: ",
            "document": "generate documentation for: ",
            "fix_bug": "fix bug in python code: ",
            "optimize": "optimize python code: ",
            "generate_tests": "generate unit tests for: "
        }
    config = MinimalConfig()


class HybridGeminiAssistant:
    """Hybrid AI Assistant with improved prompts"""
    
    def __init__(self, model_path: str = None):
        """Initialize hybrid assistant"""
        self.model_path = model_path or config.output_dir
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Load fine-tuned model
        print(f"Loading fine-tuned model from {self.model_path}...")
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_path,
                local_files_only=True,
                trust_remote_code=True
            )
            self.model = T5ForConditionalGeneration.from_pretrained(
                self.model_path,
                local_files_only=True,
                trust_remote_code=True
            )
            self.model.to(self.device)
            self.model.eval()
            print(f"✅ Fine-tuned model loaded on {self.device}")
        except Exception as e:
            checkpoint_path = os.path.join(self.model_path, "checkpoint-24390")
            if os.path.exists(checkpoint_path):
                self.tokenizer = AutoTokenizer.from_pretrained(checkpoint_path)
                self.model = T5ForConditionalGeneration.from_pretrained(checkpoint_path)
                self.model.to(self.device)
                self.model.eval()
                print(f"✅ Model loaded from checkpoint on {self.device}")
            else:
                raise Exception(f"Could not load model from {self.model_path}")
        
        # Initialize Gemini
        self.gemini_client = None
        self.gemini_model = None
        self.use_gemini = False
        
        if GEMINI_AVAILABLE:
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key:
                try:
                    print(f"🔑 API Key detected: {api_key[:10]}...{api_key[-5:]}")
                    self.gemini_client = genai.Client(api_key=api_key)
                    
                    model_names = ["gemini-2.0-flash", "gemini-2.5-flash-lite", "gemini-2.5-flash"]
                    
                    print("🔍 Testing Gemini models...")
                    for model_name in model_names:
                        try:
                            print(f"   Trying {model_name}...", end=" ")
                            response = self.gemini_client.models.generate_content(
                                model=model_name,
                                contents="Hello"
                            )
                            
                            if hasattr(response, 'text') and response.text:
                                text = response.text
                            elif hasattr(response, 'candidates') and response.candidates:
                                text = response.candidates[0].content.parts[0].text
                            else:
                                text = str(response)
                            
                            self.gemini_model = model_name
                            self.use_gemini = True
                            print(f"✅ WORKS!")
                            print(f"✅ Google Gemini initialized - Using {model_name}")
                            break
                            
                        except Exception as e:
                            print(f"❌ {str(e)[:50]}...")
                            continue
                    
                    if not self.use_gemini:
                        print("⚠️ Could not initialize any Gemini model")
                        
                except Exception as e:
                    print(f"⚠️ Gemini initialization error: {e}")
                    self.use_gemini = False
            else:
                print("⚠️ GEMINI_API_KEY not found")
                self.use_gemini = False
    
    def _generate_finetuned(self, input_text: str, task: str, max_length: int = 128) -> str:
        """Generate using fine-tuned model"""
        prefix = config.task_prefix.get(task, "")
        full_input = prefix + input_text
        
        inputs = self.tokenizer(
            full_input,
            max_length=config.max_source_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        ).to(self.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=max_length,
                num_beams=config.num_beams,
                early_stopping=True,
                no_repeat_ngram_size=3
            )
        
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    def _generate_gemini(self, prompt: str, max_retries: int = 2) -> str:
        """Generate using Google Gemini"""
        if not self.use_gemini or not self.gemini_client:
            return "AI unavailable. Set GEMINI_API_KEY."
        
        for attempt in range(max_retries):
            try:
                response = self.gemini_client.models.generate_content(
                    model=self.gemini_model,
                    contents=prompt
                )
                
                if hasattr(response, 'text') and response.text:
                    return response.text.strip()
                elif hasattr(response, 'candidates') and response.candidates:
                    return response.candidates[0].content.parts[0].text.strip()
                
                return str(response).strip()
                    
            except Exception as e:
                if attempt < max_retries - 1:
                    continue
                return f"Error: {str(e)[:100]}"
        
        return "Failed after retries."
    
    def explain_code(self, code: str, detailed: bool = False) -> str:
        """
        Explain code - First use fine-tuned model, then enhance with Gemini
        Returns comprehensive explanation with both basic and enhanced insights
        """
        # Step 1: Get basic explanation from fine-tuned model
        print("🤖 Step 1: Getting basic explanation from fine-tuned model...")
        basic_explanation = self._generate_finetuned(code, "explain", max_length=256)
        
        if self.use_gemini:
            # Step 2: Enhance with Gemini
            print("✨ Step 2: Enhancing explanation with Gemini AI...")
            
            prompt = f"""You are enhancing a code explanation. Here's what we have:

Code:
```python
{code}
```

Basic Explanation (from fine-tuned model):
{basic_explanation}

Your task: Enhance this explanation by:
1. Expanding on the logic and flow
2. Identifying any bugs or logical errors (like unreachable conditions)
3. Explaining edge cases and potential issues
4. Making it more comprehensive and detailed

Provide an enhanced 4-6 sentence explanation that builds upon the basic one.

Enhanced Explanation:"""
            
            enhanced = self._generate_gemini(prompt)
            return f"""💡 Code Explanation

📝 Basic Explanation :
{basic_explanation}

✨ Enhanced Explanation :
{enhanced}"""
        else:
            # Only fine-tuned model available
            return f"💡 Code Explanation\n\n{basic_explanation}"
    
    def generate_documentation(self, code: str, style: str = "google") -> str:
        """
        Generate documentation - First use fine-tuned model, then enhance with Gemini
        Returns comprehensive documentation with both basic and enhanced versions
        """
        # Step 1: Get basic documentation from fine-tuned model
        print("🤖 Step 1: Generating basic documentation from fine-tuned model...")
        basic_docs = self._generate_finetuned(code, "document", max_length=256)
        
        if self.use_gemini:
            # Step 2: Enhance with Gemini
            print("✨ Step 2: Enhancing documentation with Gemini AI...")
            
            prompt = f"""You are enhancing code documentation. Here's what we have:

Code:
```python
{code}
```

Basic Documentation (from fine-tuned model):
{basic_docs}

Your task: Create a professional, comprehensive Google-style docstring that MUST include:
1. Brief one-line description of what the function does
2. Detailed explanation of the functionality
3. Args section listing ALL parameters with their types and descriptions
4. Returns section describing the return value and its type
5. Any edge cases or important details

Return ONLY the docstring in this EXACT format:

\"\"\"
Brief one-line description of what the function does.

Detailed explanation of the functionality, how it works, and what it accomplishes.

Args:
    param_name (type): Clear description of what this parameter is and how it's used
    another_param (type): Description

Returns:
    type: Description of what is returned and what it represents

Raises:
    ExceptionType: When this exception occurs (if applicable)
\"\"\"

Enhanced docstring:"""
            
            enhanced = self._generate_gemini(prompt)
            
            # Clean up if Gemini adds extra stuff
            if '"""' in enhanced:
                # Extract just the docstring
                parts = enhanced.split('"""')
                if len(parts) >= 3:
                    enhanced = '"""' + parts[1] + '"""'
            
            return f"""📚 Documentation

📝 Basic Documentation :
{basic_docs}

✨ Enhanced Documentation :
{enhanced}"""
        else:
            # Only fine-tuned model available
            return f"📚 Documentation\n\n{basic_docs}"
    
    def fix_bug(self, code: str, error_msg: str = None) -> Dict[str, str]:
        """Fix bugs in code"""
        if self.use_gemini:
            print("✨ Using Gemini for bug fixing...")

            error_context = f"\n\nError message: {error_msg}" if error_msg else ""
            
            prompt = f"""Fix the bugs in this Python code. Pay special attention to logical errors like unreachable conditions.{error_context}

Buggy Code:
```python
{code}
```

Provide your response in this EXACT format with PROFESSIONAL HEADINGS:

FIXED_CODE:
```python
[corrected code here - properly indented]
```

EXPLANATION:
Write a professional explanation using proper section headings (not bullet points or informal lists).

Use this structure:
## Bug Analysis
[Describe what was wrong]

## Solution Implemented
[Describe the fix applied]

## Key Improvements
[List specific improvements in paragraph form]

Response:"""
            
            result = self._generate_gemini(prompt)
            
            # Parse response
            if "FIXED_CODE:" in result and "EXPLANATION:" in result:
                parts = result.split("EXPLANATION:")
                fixed_code = parts[0].replace("FIXED_CODE:", "").strip()
                explanation = parts[1].strip()
                
                # Clean markdown
                if "```python" in fixed_code:
                    fixed_code = fixed_code.split("```python")[1].split("```")[0].strip()
                elif "```" in fixed_code:
                    code_parts = fixed_code.split("```")
                    if len(code_parts) >= 2:
                        fixed_code = code_parts[1].strip()
                
                return {
                    "fixed_code": fixed_code,
                    "explanation": explanation,
                    "method": f"Google Gemini ({self.gemini_model})"
                }
            else:
                # Try to extract code
                if "```python" in result:
                    fixed_code = result.split("```python")[1].split("```")[0].strip()
                elif "```" in result:
                    parts = result.split("```")
                    fixed_code = parts[1].strip() if len(parts) >= 2 else result
                else:
                    fixed_code = result
                
                return {
                    "fixed_code": fixed_code,
                    "explanation": "Code analyzed and corrected",
                    "method": f"Google Gemini ({self.gemini_model})"
                }
        else:
            print("🤖 Using fine-tuned model...")
            fixed = self._generate_finetuned(code, "fix_bug", max_length=512)
            return {
                "fixed_code": fixed,
                "explanation": "Fixed using fine-tuned model",
                "method": "Fine-tuned CodeT5"
            }
    
    def optimize_code(self, code: str) -> Dict[str, str]:
        """Optimize code"""
        if self.use_gemini:
            print("✨ Using Gemini for optimization...")
            
            prompt = f"""Optimize this Python code for better performance, readability, and best practices.

Code:
```python
{code}
```

Provide your response in this EXACT format with PROFESSIONAL HEADINGS:

OPTIMIZED_CODE:
```python
[optimized code]
```

IMPROVEMENTS:
Write a professional explanation using proper section headings (NO bullet points, NO asterisks, NO numbered lists).

Use this structure:
## Performance Optimizations
Describe performance improvements in paragraph form, explaining time/space complexity changes.

## Code Quality Improvements
Describe readability and maintainability improvements in paragraph form.

## Best Practices Applied
Describe any design patterns or best practices implemented in paragraph form.

Response:"""
            
            result = self._generate_gemini(prompt)
            
            # Parse
            if "OPTIMIZED_CODE:" in result and "IMPROVEMENTS:" in result:
                parts = result.split("IMPROVEMENTS:")
                opt_code = parts[0].replace("OPTIMIZED_CODE:", "").strip()
                improvements = parts[1].strip()
                
                # Clean markdown
                if "```python" in opt_code:
                    opt_code = opt_code.split("```python")[1].split("```")[0].strip()
                elif "```" in opt_code:
                    code_parts = opt_code.split("```")
                    if len(code_parts) >= 2:
                        opt_code = code_parts[1].strip()
                
                return {
                    "optimized_code": opt_code,
                    "suggestions": [improvements],
                    "method": f"Google Gemini ({self.gemini_model})"
                }
            else:
                if "```python" in result:
                    opt_code = result.split("```python")[1].split("```")[0].strip()
                elif "```" in result:
                    parts = result.split("```")
                    opt_code = parts[1].strip() if len(parts) >= 2 else result
                else:
                    opt_code = result
                
                return {
                    "optimized_code": opt_code,
                    "suggestions": ["Code optimized"],
                    "method": f"Google Gemini ({self.gemini_model})"
                }
        else:
            return {
                "optimized_code": "AI optimization unavailable.",
                "suggestions": [],
                "method": "N/A"
            }
    
    def generate_tests(self, code: str, num_tests: int = 3) -> List[str]:
        """Generate unit tests"""
        if self.use_gemini:
            print("✨ Using Gemini for test generation...")
            
            prompt = f"""Generate comprehensive pytest unit tests for this Python code.

Code:
```python
{code}
```

Include:
- Test normal/expected cases
- Test edge cases (boundary values)
- Test error cases

Return ONLY the complete test code (imports + test functions).

Test code:"""
            
            result = self._generate_gemini(prompt)
            
            # Clean markdown
            if "```python" in result:
                result = result.split("```python")[1].split("```")[0].strip()
            elif "```" in result:
                parts = result.split("```")
                if len(parts) >= 2:
                    result = parts[1].strip()
            
            return [result]
        else:
            return ["AI test generation unavailable."]
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
        basic_explanation = self._generate_finetuned(code, "explain", max_length=512)
        
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
        Generate documentation - Hybrid approach using fine-tuned model + Gemini
        Returns professional documentation with Args, Returns, and proper structure
        """
        # Step 1: Get basic documentation from fine-tuned model
        print("🤖 Step 1: Generating basic documentation from fine-tuned model...")
        basic_docs = self._generate_finetuned(code, "document", max_length=1024)
        
        if self.use_gemini:
            # Step 2: Enhance with Gemini for professional format
            print("✨ Step 2: Formatting professional documentation with Gemini AI...")
            
            prompt = f"""Generate a professional Google-style docstring for this code.

Code:
```python
{code}
```

Basic analysis from fine-tuned model:
{basic_docs}

IMPORTANT REQUIREMENTS:
- ONE-LINE summary (concise, no fluff)
- Brief description (2-3 sentences max)
- Args section with parameter types and descriptions
- Returns section with return type and description
- NO code examples
- NO lengthy explanations
- Professional, concise format

Format EXACTLY as:

\"\"\"
One-line summary of function purpose.

Brief 2-3 sentence description of what it does and how.

Args:
    param_name (type): Concise description
    another_param (type): Concise description

Returns:
    type: What is returned

Raises:
    ExceptionType: When raised (only if applicable)
\"\"\"

Docstring:"""
            
            enhanced = self._generate_gemini(prompt)
            
            # Clean up the response
            if '"""' in enhanced:
                parts = enhanced.split('"""')
                if len(parts) >= 3:
                    enhanced = '"""' + parts[1] + '"""'
                elif len(parts) == 2:
                    enhanced = '"""' + parts[1].strip()
            
            return f"""📚 Professional Documentation

🤖 Fine-tuned Model Analysis:
{basic_docs}

✨ Enhanced:
{enhanced}"""
        else:
            # Only fine-tuned model available
            return f"📚 Documentation\n\n{basic_docs}"
    
    def fix_bug(self, code: str, error_msg: str = None) -> Dict[str, str]:
        """Fix bugs using hybrid approach - fine-tuned model analysis + Gemini correction"""
        # Step 1: Analyze with fine-tuned model
        print("🤖 Step 1: Analyzing code with fine-tuned model...")
        finetuned_analysis = self._generate_finetuned(code, "fix_bug", max_length=512)
        
        if self.use_gemini:
            # Step 2: Use Gemini to fix based on fine-tuned analysis
            print("✨ Step 2: Generating fix with Gemini AI...")
            error_context = f"\n\nError message: {error_msg}" if error_msg else ""
            
            prompt = f"""Fix bugs in this Python code using the initial analysis provided.

Buggy Code:
```python
{code}
```

Initial Analysis (from fine-tuned CodeT5 model):
{finetuned_analysis}{error_context}

Provide your response in this EXACT format:

FIXED_CODE:
```python
[corrected code - properly indented]
```

EXPLANATION:
## Bug Analysis
[What was wrong with the code]

## Solution Implemented
[How the fix addresses the issue]

## Key Improvements
[Specific improvements made]

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
                    "explanation": f"🤖 Fine-tuned Model Analysis:\n{finetuned_analysis}\n\n✨ Gemini Fix:\n{explanation}",
                    "method": f"Hybrid (CodeT5 + Gemini {self.gemini_model})"
                }
            else:
                # Fallback parsing
                if "```python" in result:
                    fixed_code = result.split("```python")[1].split("```")[0].strip()
                elif "```" in result:
                    parts = result.split("```")
                    fixed_code = parts[1].strip() if len(parts) >= 2 else result
                else:
                    fixed_code = result
                
                return {
                    "fixed_code": fixed_code,
                    "explanation": f"🤖 Analysis: {finetuned_analysis}\n\n✨ Fix applied",
                    "method": f"Hybrid (CodeT5 + Gemini {self.gemini_model})"
                }
        else:
            # Only fine-tuned model available
            print("🤖 Using fine-tuned model only...")
            return {
                "fixed_code": finetuned_analysis,
                "explanation": "Fixed using fine-tuned CodeT5 model",
                "method": "Fine-tuned CodeT5"
            }
    
    def optimize_code(self, code: str) -> Dict[str, str]:
        """Optimize code using hybrid approach - fine-tuned model + Gemini"""
        # Step 1: Get optimization suggestions from fine-tuned model
        print("🤖 Step 1: Getting optimization suggestions from fine-tuned model...")
        finetuned_suggestions = self._generate_finetuned(code, "optimize", max_length=512)
        
        if self.use_gemini:
            # Step 2: Apply optimizations with Gemini
            print("✨ Step 2: Applying optimizations with Gemini AI...")
            
            prompt = f"""Optimize this Python code using the initial suggestions provided.

Original Code:
```python
{code}
```

Optimization Suggestions (from fine-tuned CodeT5 model):
{finetuned_suggestions}

Provide your response in this EXACT format with PROFESSIONAL HEADINGS:

OPTIMIZED_CODE:
```python
[optimized code]
```

IMPROVEMENTS:
## Performance Optimizations
Describe performance improvements in paragraph form.

## Code Quality Improvements
Describe readability improvements in paragraph form.

## Best Practices Applied
Describe best practices in paragraph form.

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
                    "suggestions": [f"🤖 CodeT5 Suggestions:\n{finetuned_suggestions}\n\n✨ Gemini Improvements:\n{improvements}"],
                    "method": f"Hybrid (CodeT5 + Gemini {self.gemini_model})"
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
                    "suggestions": [f"🤖 CodeT5: {finetuned_suggestions}\n\n✨ Optimized"],
                    "method": f"Hybrid (CodeT5 + Gemini {self.gemini_model})"
                }
        else:
            # Only fine-tuned model available
            print("🤖 Using fine-tuned model only...")
            return {
                "optimized_code": finetuned_suggestions,
                "suggestions": ["Optimized using fine-tuned CodeT5 model"],
                "method": "Fine-tuned CodeT5"
            }
    
    def generate_tests(self, code: str, num_tests: int = 3) -> List[str]:
        """Generate unit tests using hybrid approach - fine-tuned model + Gemini"""
        # Step 1: Get test outline from fine-tuned model
        print("🤖 Step 1: Generating test outline from fine-tuned model...")
        finetuned_tests = self._generate_finetuned(code, "generate_tests", max_length=512)
        
        if self.use_gemini:
            # Step 2: Generate comprehensive tests with Gemini
            print("✨ Step 2: Generating comprehensive tests with Gemini AI...")
            
            prompt = f"""Generate comprehensive pytest unit tests for this Python code.

Code:
```python
{code}
```

Test Outline (from fine-tuned CodeT5 model):
{finetuned_tests}

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
            
            # Add header showing hybrid approach
            result = f"# Generated using Hybrid Approach (CodeT5 + Gemini {self.gemini_model})\n# CodeT5 Outline: {finetuned_tests[:100]}...\n\n{result}"
            return [result]
        else:
            # Only fine-tuned model available
            print("🤖 Using fine-tuned model only...")
            return [f"# Generated using Fine-tuned CodeT5\n\n{finetuned_tests}"]
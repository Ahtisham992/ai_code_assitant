"""
Improved Hybrid RAG Assistant
Only adds codebase context when actually helpful
"""

from src.hybrid_gemini import HybridGeminiAssistant
from src.codebase_retrieval import CodebaseRetrieval
from typing import Dict, List


class HybridRAGAssistant(HybridGeminiAssistant):
    """RAG Assistant that only adds context when relevant"""
    
    def __init__(self, model_path: str = None, codebase_dir: str = "./user_codebase"):
        super().__init__(model_path)
        
        print("Initializing codebase retrieval...")
        try:
            self.retriever = CodebaseRetrieval(codebase_dir=codebase_dir)
            self.retrieval_enabled = True
            print("✅ Codebase retrieval ready")
        except Exception as e:
            print(f"⚠️ Retrieval initialization failed: {e}")
            self.retriever = None
            self.retrieval_enabled = False
    
    def index_codebase(self, force_reindex: bool = False):
        """Index user's codebase"""
        if self.retrieval_enabled:
            self.retriever.index_codebase(force_reindex=force_reindex)
        else:
            print("⚠️ Retrieval not enabled")
    
    def explain_code_with_context(self, code: str, detailed: bool = False, use_retrieval: bool = True) -> str:
        """
        Explain code - NO codebase context (just use Gemini directly)
        The codebase context was adding confusion
        """
        # Just use the base explain_code - don't add confusing context
        return self.explain_code(code, detailed=detailed)
    
    def fix_bug_with_context(self, code: str, error_msg: str = None) -> Dict[str, str]:
        """
        Fix bugs - optionally use similar code from codebase for reference
        """
        # Check if we have similar working code
        similar_code = []
        if self.retrieval_enabled and self.use_gemini:
            try:
                print("🔍 Looking for similar working code patterns...")
                similar_code = self.retriever.retrieve_similar_code(code, top_k=2)
            except:
                pass
        
        # If we have very similar working code (similarity > 0.7), use it for context
        if similar_code and similar_code[0]['similarity_score'] > 0.7:
            examples = "\n\nSimilar working code from your codebase for reference:\n"
            for result in similar_code[:1]:  # Just use best match
                examples += f"```python\n{result['code'][:300]}\n```\n"
            
            if self.use_gemini:
                error_context = f"\nError: {error_msg}" if error_msg else ""
                
                prompt = f"""Fix bugs in this code. Here's a similar working pattern from the codebase for reference.{error_context}

Buggy Code:
```python
{code}
```

{examples}

Provide:
FIXED_CODE:
```python
[corrected code]
```

EXPLANATION:
[What was wrong and how you fixed it]

Response:"""
                
                result = self._generate_gemini(prompt)
                
                if "FIXED_CODE:" in result and "EXPLANATION:" in result:
                    parts = result.split("EXPLANATION:")
                    fixed_code = parts[0].replace("FIXED_CODE:", "").strip()
                    explanation = parts[1].strip()
                    
                    if "```python" in fixed_code:
                        fixed_code = fixed_code.split("```python")[1].split("```")[0].strip()
                    elif "```" in fixed_code:
                        code_parts = fixed_code.split("```")
                        if len(code_parts) >= 2:
                            fixed_code = code_parts[1].strip()
                    
                    return {
                        "fixed_code": fixed_code,
                        "explanation": explanation + "\n\n✨ Referenced similar working code from your codebase",
                        "method": "Gemini with Codebase Context"
                    }
        
        # Otherwise just use base fix_bug
        return self.fix_bug(code, error_msg)
    
    def optimize_code_with_context(self, code: str) -> Dict[str, str]:
        """
        Optimize code - look for better patterns in codebase
        """
        similar_code = []
        if self.retrieval_enabled and self.use_gemini:
            try:
                print("🔍 Looking for optimization patterns...")
                similar_code = self.retriever.retrieve_similar_code(code, top_k=2)
            except:
                pass
        
        # If we have similar code with good patterns
        if similar_code and similar_code[0]['similarity_score'] > 0.6:
            patterns = "\n\nOptimization patterns from your codebase:\n"
            for result in similar_code[:1]:
                patterns += f"```python\n{result['code'][:300]}\n```\n"
            
            if self.use_gemini:
                prompt = f"""Optimize this code. Here are similar patterns from the codebase showing good practices.

Code to optimize:
```python
{code}
```

{patterns}

Provide:
OPTIMIZED_CODE:
```python
[optimized code]
```

IMPROVEMENTS:
[What you improved]

Response:"""
                
                result = self._generate_gemini(prompt)
                
                if "OPTIMIZED_CODE:" in result and "IMPROVEMENTS:" in result:
                    parts = result.split("IMPROVEMENTS:")
                    opt_code = parts[0].replace("OPTIMIZED_CODE:", "").strip()
                    improvements = parts[1].strip()
                    
                    if "```python" in opt_code:
                        opt_code = opt_code.split("```python")[1].split("```")[0].strip()
                    elif "```" in opt_code:
                        code_parts = opt_code.split("```")
                        if len(code_parts) >= 2:
                            opt_code = code_parts[1].strip()
                    
                    return {
                        "optimized_code": opt_code,
                        "suggestions": [improvements + "\n\n✨ Applied patterns from your codebase"],
                        "method": "Gemini with Codebase Context"
                    }
        
        # Otherwise use base optimize
        return self.optimize_code(code)
    
    def get_codebase_stats(self) -> Dict:
        """Get codebase statistics"""
        if self.retrieval_enabled and self.retriever.metadata:
            files = set(m['file'] for m in self.retriever.metadata)
            return {
                'total_snippets': len(self.retriever.metadata),
                'total_files': len(files),
                'indexed': True
            }
        return {
            'total_snippets': 0,
            'total_files': 0,
            'indexed': False
        }
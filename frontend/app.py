"""
Flask Backend for AI Code Assistant
With hardcoded API key
"""

from flask import Flask, render_template, request, jsonify
import sys
import os
from pathlib import Path

# ============================================================
# HARDCODE YOUR API KEY HERE
# ============================================================
os.environ["GEMINI_API_KEY"] = "AIzaSyCE7DgKDeujj4iM_O6h0dRdz9FnESVW7UM"
# ============================================================

# Add parent directory to path
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

# Verify API key is set
gemini_key = os.getenv("GEMINI_API_KEY")
print(f"✅ API Key hardcoded: {gemini_key[:10]}...{gemini_key[-5:]}")
print(f"   Length: {len(gemini_key)} characters")

# Now import project modules
from src.hybrid_gemini_rag import HybridRAGAssistant
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)

# Global variable to store the assistant
assistant = None
model_loaded = False
loading_error = None


def load_model():
    """Load the AI model on startup"""
    global assistant, model_loaded, loading_error
    try:
        print("Loading AI Code Assistant with RAG...")
        print("This may take 10-15 seconds...")
        
        # Set paths explicitly
        model_path = str(root_dir / "models" / "finetuned_model")
        codebase_path = str(root_dir / "user_codebase")
        
        # Create codebase directory if it doesn't exist
        os.makedirs(codebase_path, exist_ok=True)
        
        assistant = HybridRAGAssistant(
            model_path=model_path,
            codebase_dir=codebase_path
        )
        
        model_loaded = True
        print("✅ Model loaded successfully!")
        print(f"✅ Gemini available: {assistant.use_gemini}")
        print(f"✅ RAG enabled: {assistant.retrieval_enabled}")
        return True
    except Exception as e:
        loading_error = str(e)
        print(f"❌ Error loading model: {e}")
        import traceback
        traceback.print_exc()
        return False


@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')


@app.route('/pricing')
def pricing():
    """Serve the pricing page"""
    return render_template('pricing.html')


@app.route('/api/status')
def get_status():
    """Get model loading status"""
    return jsonify({
        'loaded': model_loaded,
        'error': loading_error,
        'gemini_available': assistant.use_gemini if assistant else False,
        'rag_enabled': assistant.retrieval_enabled if assistant else False
    })


@app.route('/api/codebase-stats')
def get_codebase_stats():
    """Get codebase indexing statistics"""
    if not model_loaded or not assistant:
        return jsonify({'indexed': False})
    
    try:
        stats = assistant.get_codebase_stats()
        return jsonify(stats)
    except Exception as e:
        print(f"Error getting codebase stats: {e}")
        return jsonify({'indexed': False, 'error': str(e)})


@app.route('/api/index-codebase', methods=['POST'])
def index_codebase():
    """Index user's codebase for RAG"""
    if not model_loaded:
        return jsonify({
            'success': False,
            'error': 'Model not loaded yet'
        }), 503
    
    try:
        # Get code from request if provided
        data = request.json
        code = data.get('code', '') if data else ''
        
        # If code is provided, save it to user_codebase directory
        if code:
            print("💾 Saving provided code to codebase...")
            codebase_path = Path(__file__).parent.parent / "user_codebase"
            codebase_path.mkdir(exist_ok=True)
            
            # Save to user_code.py (overwrite if exists)
            user_code_file = codebase_path / "user_code.py"
            with open(user_code_file, 'w', encoding='utf-8') as f:
                f.write(code)
            print(f"✅ Code saved to {user_code_file}")
        
        print("🔍 Indexing codebase...")
        assistant.index_codebase(force_reindex=True)
        
        stats = assistant.get_codebase_stats()
        
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        print(f"Error indexing codebase: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/process', methods=['POST'])
def process_code():
    """Process code with selected feature"""
    if not model_loaded:
        return jsonify({
            'success': False,
            'error': 'Model not loaded yet. Please wait.'
        }), 503
    
    try:
        data = request.json
        code = data.get('code', '')
        feature = data.get('feature', '')
        use_context = data.get('use_context', True)
        
        if not code:
            return jsonify({
                'success': False,
                'error': 'No code provided'
            }), 400
        
        result = {}
        
        if feature == 'explain':
            if assistant.retrieval_enabled and use_context:
                result['output'] = assistant.explain_code_with_context(code, detailed=True)
            else:
                result['output'] = assistant.explain_code(code, detailed=True)
            result['type'] = 'text'
            
        elif feature == 'document':
            if assistant.retrieval_enabled and use_context:
                result['output'] = assistant.explain_code_with_context(code, detailed=False)
            else:
                result['output'] = assistant.generate_documentation(code)
            result['type'] = 'text'
            
        elif feature == 'fix':
            if assistant.retrieval_enabled and use_context:
                fix_result = assistant.fix_bug_with_context(code)
            else:
                fix_result = assistant.fix_bug(code)
            
            result['output'] = fix_result['fixed_code']
            result['explanation'] = fix_result.get('explanation', '')
            result['method'] = fix_result.get('method', '')
            result['type'] = 'code'
            
        elif feature == 'optimize':
            if assistant.retrieval_enabled and use_context:
                opt_result = assistant.optimize_code_with_context(code)
            else:
                opt_result = assistant.optimize_code(code)
            
            result['output'] = opt_result['optimized_code']
            result['suggestions'] = opt_result.get('suggestions', [])
            result['method'] = opt_result.get('method', '')
            result['type'] = 'code'
            
        elif feature == 'test':
            tests = assistant.generate_tests(code)
            result['output'] = tests[0] if tests else 'No tests generated'
            result['type'] = 'code'
            
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid feature selected'
            }), 400
        
        return jsonify({
            'success': True,
            'result': result
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 AI CODE ASSISTANT - WEB INTERFACE")
    print("="*60 + "\n")
    
    load_model()
    
    print("\n" + "="*60)
    print("🌐 Starting web server...")
    print("🔗 Open: http://localhost:5000")
    print("💰 Pricing: http://localhost:5000/pricing")
    print("="*60 + "\n")
    
    app.run(debug=False, host='0.0.0.0', port=5000)
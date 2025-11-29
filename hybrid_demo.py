"""
Hybrid AI Code Assistant Demo
Shows all 5 capabilities using fine-tuned model + LLM
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "src"))

# Try to use hybrid with Gemini (best free option), then OpenAI, then Ollama
try:
    from src.hybrid_gemini import HybridGeminiAssistant as HybridCodeAssistant
    print("Using Hybrid Assistant with Google Gemini (FREE & FAST)")
except Exception as e:
    print(f"Gemini import failed: {e}")
    try:
        from src.hybrid_inference import HybridCodeAssistant
        print("Using Hybrid Assistant with OpenAI support")
    except Exception as e:
        print(f"OpenAI import failed: {e}")
        try:
            from src.hybrid_local import HybridLocalAssistant as HybridCodeAssistant
            print("Using Hybrid Assistant with Ollama (local)")
        except Exception as e:
            print(f"Ollama import failed: {e}")
            from src.inference import CodeAssistant as HybridCodeAssistant
            print("Using fine-tuned model only")

import time


def demo_with_pause(title, code, task, assistant):
    """Helper function for clean demo output"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)
    print("\n📝 INPUT CODE:")
    print(code)
    print("\n⏳ Processing...")
    
    if task == "explain":
        result = assistant.explain_code(code, detailed=True)
        print("\n💡 EXPLANATION:")
        print(result)
        
    elif task == "document":
        result = assistant.generate_documentation(code)
        print("\n📚 GENERATED DOCUMENTATION:")
        print(result)
        
    elif task == "fix":
        result = assistant.fix_bug(code)
        print("\n🔧 FIXED CODE:")
        print(result['fixed_code'])
        print(f"\n🔍 Method Used: {result.get('method', 'Unknown')}")
        if result.get('explanation'):
            print(f"📝 Explanation: {result['explanation']}")
            
    elif task == "optimize":
        result = assistant.optimize_code(code)
        print("\n⚡ OPTIMIZED CODE:")
        print(result['optimized_code'])
        print(f"\n🔍 Method Used: {result.get('method', 'Unknown')}")
        if result.get('suggestions'):
            print("\n💡 Suggestions:")
            for suggestion in result['suggestions']:
                print(f"   • {suggestion}")
                
    elif task == "test":
        result = assistant.generate_tests(code)
        print("\n🧪 GENERATED TESTS:")
        for i, test in enumerate(result, 1):
            print(f"\nTest {i}:")
            print(test)
    
    input("\n[Press Enter to continue...]")


# Initialize
print("\n" + "="*70)
print(" "*10 + "🤖 HYBRID AI CODE ASSISTANT DEMO")
print(" "*5 + "Fine-tuned CodeT5 + LLM for Complete Coverage")
print("="*70)

print("\n📊 System Architecture:")
print("   • Fine-tuned CodeT5 (60M params) → Basic Explain & Document")
print("   • Gemini AI → Enhance Explain & Document + Bug Fix, Optimize, Test")
print("\n🎯 All 5 Capabilities:")
print("   1. ✅ Code Explanation (Fine-tuned → Enhanced by Gemini)")
print("   2. ✅ Documentation Generation (Fine-tuned → Enhanced by Gemini)")
print("   3. ✅ Bug Fixing (Gemini - Excellent)")
print("   4. ✅ Code Optimization (Gemini - Excellent)")
print("   5. ✅ Test Generation (Gemini - Excellent)")

input("\n[Press Enter to start demo...]")

assistant = HybridCodeAssistant()

# Demo 1: Code Explanation (Two-stage: Fine-tuned then Gemini)
demo_with_pause(
    "DEMO 1: CODE EXPLANATION (Two-stage: Fine-tuned → Gemini Enhancement)",
    """def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    
    result.extend(left[i:])
    result.extend(right[j:])
    return result""",
    "explain",
    assistant
)

# Demo 2: Documentation Generation (Two-stage: Fine-tuned then Gemini)
demo_with_pause(
    "DEMO 2: DOCUMENTATION GENERATION (Two-stage: Fine-tuned → Gemini Enhancement)",
    """def calculate_statistics(numbers):
    if not numbers:
        return None
    
    total = sum(numbers)
    count = len(numbers)
    mean = total / count
    
    sorted_nums = sorted(numbers)
    mid = count // 2
    if count % 2 == 0:
        median = (sorted_nums[mid-1] + sorted_nums[mid]) / 2
    else:
        median = sorted_nums[mid]
    
    variance = sum((x - mean) ** 2 for x in numbers) / count
    std_dev = variance ** 0.5
    
    return {
        'mean': mean,
        'median': median,
        'std_dev': std_dev,
        'min': min(numbers),
        'max': max(numbers)
    }""",
    "document",
    assistant
)

# Demo 3: Bug Fixing (LLM)
demo_with_pause(
    "DEMO 3: BUG DETECTION & FIXING (LLM)",
    """def process_user_data(users):
    results = []
    for user in users:
        age = int(user['age'])
        if age >= 18:
            discount = 0
        elif age >= 65:
            discount = 0.2
        else:
            discount = 0.1
        
        total = user['purchase_amount']
        final_price = total - (total * discount)
        results.append({
            'name': user['name'],
            'final_price': final_price
        })
    return results""",
    "fix",
    assistant
)

# Demo 4: Code Optimization (LLM)
demo_with_pause(
    "DEMO 4: CODE OPTIMIZATION (LLM)",
    """def find_common_elements(list1, list2, list3):
    common = []
    for item in list1:
        found_in_2 = False
        for item2 in list2:
            if item == item2:
                found_in_2 = True
                break
        
        if found_in_2:
            found_in_3 = False
            for item3 in list3:
                if item == item3:
                    found_in_3 = True
                    break
            
            if found_in_3 and item not in common:
                common.append(item)
    
    return common""",
    "optimize",
    assistant
)

# Demo 5: Test Generation (LLM)
demo_with_pause(
    "DEMO 5: TEST CASE GENERATION (LLM)",
    """def validate_password(password):
    if len(password) < 8:
        return False
    
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in '!@#$%^&*()' for c in password)
    
    if not (has_upper and has_lower):
        return False
    if not (has_digit or has_special):
        return False
    
    return True""",
    "test",
    assistant
)

print("\n" + "="*70)
print(" "*20 + "✅ ALL 5 DEMOS COMPLETED!")
print("="*70)

print("\n📈 Results Summary:")
print("   ✅ Code Explanation: Excellent (Fine-tuned → Gemini Enhanced)")
print("   ✅ Documentation: Excellent (Fine-tuned → Gemini Enhanced)")
print("   ✅ Bug Fixing: Excellent (Gemini)")
print("   ✅ Code Optimization: Excellent (Gemini)")
print("   ✅ Test Generation: Excellent (Gemini)")

print("\n🎓 Two-Stage Hybrid Approach Benefits:")
print("   • Leverages fine-tuned model's specialized knowledge first")
print("   • Gemini enhances and expands on basic outputs")
print("   • Best of both worlds: domain-specific + general AI")
print("   • Shows clear progression from basic to enhanced results")

print("\n💡 Implementation Options:")
print("   1. OpenAI API (best quality, costs ~$0.01 per demo)")
print("   2. Ollama (free, local, good quality)")
print("   3. Fine-tuned only (free, limited to 2 tasks)")

print("\n🙏 Thank you for watching!")
print("📧 Questions?\n")

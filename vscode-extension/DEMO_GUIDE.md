# Visual Demo Guide - VS Code Extension

## 🎯 What You'll Build

A VS Code extension that adds **AI-powered code assistance** directly to your right-click context menu!

## 📸 User Experience Flow

### Step 1: Select Code
```python
# User selects this buggy function
def find_max(numbers):
    max_val = 0  # Bug: doesn't handle negative numbers
    for num in numbers:
        if num > max_val:
            max_val = num
    return max_val
```

### Step 2: Right-Click Context Menu

When you right-click on selected code, you see:

```
┌─────────────────────────────────┐
│ Cut                             │
│ Copy                            │
│ Paste                           │
├─────────────────────────────────┤
│ 🤖 AI Code Assistant        ▶   │  ← NEW MENU!
├─────────────────────────────────┤
│ Format Document                 │
│ ...                             │
└─────────────────────────────────┘
```

### Step 3: Submenu Opens

Hover over "🤖 AI Code Assistant" to see options:

```
┌─────────────────────────────────┐
│ 🤖 AI Code Assistant        ▶   │
│                                 │ ┌──────────────────────────┐
│                                 │ │ 💡 Explain Code          │
│                                 │ │ 📚 Generate Documentation│
│                                 │ ├──────────────────────────┤
│                                 │ │ 🔧 Fix Bugs              │
│                                 │ │ ⚡ Optimize Code         │
│                                 │ ├──────────────────────────┤
│                                 │ │ 🧪 Generate Tests        │
│                                 │ └──────────────────────────┘
└─────────────────────────────────┘
```

### Step 4: Click "Fix Bugs"

**Progress Notification:**
```
┌────────────────────────────────┐
│ ⏳ AI Assistant: Fixing bugs...│
└────────────────────────────────┘
```

### Step 5: Code is Automatically Fixed!

**Before:**
```python
def find_max(numbers):
    max_val = 0  # Bug!
    for num in numbers:
        if num > max_val:
            max_val = num
    return max_val
```

**After (automatically replaced):**
```python
def find_max(numbers):
    """Find the maximum value in a list of numbers.
    
    Args:
        numbers (list): List of numbers to search
        
    Returns:
        int/float: Maximum value, or None if list is empty
    """
    if not numbers:
        return None
    max_val = numbers[0]
    for num in numbers:
        if num > max_val:
            max_val = num
    return max_val
```

**Success Message:**
```
┌────────────────────────────────┐
│ ✅ Code fixed successfully!    │
└────────────────────────────────┘
```

## 🎬 Feature Demonstrations

### Demo 1: Explain Code

**Input:** Select complex code
```python
def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)
```

**Action:** Right-click → AI Assistant → Explain Code

**Result:** Opens new tab with explanation:
```markdown
# 💡 Code Explanation

## Basic Explanation (Fine-tuned Model):
This function implements the quicksort algorithm using list comprehensions...

## Enhanced Explanation (Gemini AI):
The quicksort function is a divide-and-conquer sorting algorithm. It works by:
1. Selecting a pivot element (middle element in this case)
2. Partitioning the array into three parts: elements less than, equal to, and greater than the pivot
3. Recursively sorting the left and right partitions
4. Concatenating the results

Time Complexity: O(n log n) average case, O(n²) worst case
Space Complexity: O(n) due to list comprehensions creating new lists
```

### Demo 2: Generate Documentation

**Input:** Select undocumented function
```python
def calculate_discount(price, discount_percent, is_member):
    if is_member:
        discount_percent += 5
    discount = price * (discount_percent / 100)
    return price - discount
```

**Action:** Right-click → AI Assistant → Generate Documentation

**Result:** Opens new tab with docstring:
```python
"""
Calculate the final price after applying a discount.

This function computes the discounted price for a product, with an additional
5% discount for members. The discount is calculated as a percentage of the
original price and subtracted from it.

Args:
    price (float): The original price of the product before any discounts
    discount_percent (float): The base discount percentage to apply (0-100)
    is_member (bool): Whether the customer is a member (gets extra 5% off)

Returns:
    float: The final price after applying all applicable discounts

Example:
    >>> calculate_discount(100, 10, True)
    85.0  # 10% + 5% member discount = 15% off
"""
```

### Demo 3: Optimize Code

**Input:** Select inefficient code
```python
def find_duplicates(list1, list2):
    duplicates = []
    for item1 in list1:
        for item2 in list2:
            if item1 == item2 and item1 not in duplicates:
                duplicates.append(item1)
    return duplicates
```

**Action:** Right-click → AI Assistant → Optimize Code

**Result:** Code replaced with:
```python
def find_duplicates(list1, list2):
    """Find duplicate elements between two lists efficiently.
    
    Args:
        list1 (list): First list to compare
        list2 (list): Second list to compare
        
    Returns:
        list: List of unique elements present in both lists
    """
    return list(set(list1) & set(list2))
```

**Explanation in Output Panel:**
```
=============================================================
⚡ Optimization Details
=============================================================

## Performance Optimizations
The original implementation used nested loops resulting in O(n*m) time 
complexity. By converting both lists to sets and using set intersection, 
we achieve O(n+m) time complexity. This is significantly faster for large 
lists.

## Code Quality Improvements
The optimized version is more concise and Pythonic. Using set operations 
makes the intent clearer and reduces the code from 6 lines to 1 line.

## Best Practices Applied
Added a comprehensive docstring following Google style conventions. Used 
built-in set operations which are implemented in C and highly optimized.
```

### Demo 4: Generate Tests

**Input:** Select function
```python
def divide_numbers(a, b):
    return a / b
```

**Action:** Right-click → AI Assistant → Generate Tests

**Result:** Opens new file with tests:
```python
import pytest

def divide_numbers(a, b):
    return a / b

def test_divide_positive_numbers():
    """Test division of two positive numbers"""
    assert divide_numbers(10, 2) == 5.0
    assert divide_numbers(9, 3) == 3.0

def test_divide_negative_numbers():
    """Test division with negative numbers"""
    assert divide_numbers(-10, 2) == -5.0
    assert divide_numbers(10, -2) == -5.0
    assert divide_numbers(-10, -2) == 5.0

def test_divide_by_zero():
    """Test that division by zero raises ZeroDivisionError"""
    with pytest.raises(ZeroDivisionError):
        divide_numbers(10, 0)

def test_divide_zero_by_number():
    """Test dividing zero by a number"""
    assert divide_numbers(0, 5) == 0.0

def test_divide_floats():
    """Test division with floating point numbers"""
    assert abs(divide_numbers(7.5, 2.5) - 3.0) < 0.001
```

## 🎨 UI Elements

### Status Bar Indicator
Bottom right of VS Code:
```
┌──────────────────────────────────────────────┐
│                           🤖 AI Assistant    │
└──────────────────────────────────────────────┘
```
Hover shows: "AI Code Assistant is ready"

### Progress Notifications
```
┌────────────────────────────────────┐
│ ⏳ AI Assistant: Processing...     │
└────────────────────────────────────┘
```

### Success Messages
```
┌────────────────────────────────────┐
│ ✅ Code optimized successfully!    │
└────────────────────────────────────┘
```

### Error Messages
```
┌─────────────────────────────────────────────────┐
│ ❌ Cannot connect to AI Assistant server at     │
│    http://localhost:5000. Please start server.  │
└─────────────────────────────────────────────────┘
```

## 🔧 Settings Panel

Access via: `File > Preferences > Settings > AI Code Assistant`

```
┌─────────────────────────────────────────────┐
│ AI Code Assistant                           │
├─────────────────────────────────────────────┤
│                                             │
│ Server URL                                  │
│ ┌─────────────────────────────────────┐   │
│ │ http://localhost:5000               │   │
│ └─────────────────────────────────────┘   │
│ URL of the AI Code Assistant backend       │
│                                             │
│ ☐ Show In New Editor                       │
│ Show results in a new editor tab instead    │
│ of replacing selection                      │
│                                             │
└─────────────────────────────────────────────┘
```

## 📊 Comparison: Web vs Extension

| Feature | Web Interface | VS Code Extension |
|---------|--------------|-------------------|
| Access | Browser | Right-click menu |
| Code Input | Copy-paste | Auto-selected |
| Result | Separate window | Inline/side-by-side |
| Workflow | Switch windows | Stay in editor |
| Speed | Slower | Faster |
| Convenience | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

## 🚀 Quick Start Commands

```bash
# 1. Install dependencies
cd vscode-extension
npm install

# 2. Start backend (new terminal)
cd ..
python frontend/app.py

# 3. Test extension
# Press F5 in VS Code
```

## 💡 Pro Tips

1. **Select entire functions** for best results
2. **Use "Show in New Editor"** to compare before/after
3. **Add keyboard shortcuts** for faster access
4. **Index your codebase** first for context-aware suggestions
5. **Keep backend running** in background while coding

## 🎓 Learning Path

1. ✅ Install and test basic features
2. ✅ Try all 5 AI capabilities
3. ✅ Configure settings to your preference
4. ✅ Add custom keyboard shortcuts
5. ✅ Package and share with team

---

**Ready to boost your coding productivity? Press F5 and start using AI assistance!** 🚀

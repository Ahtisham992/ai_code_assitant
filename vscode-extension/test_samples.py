# Test Samples for VS Code Extension
# Use these code snippets to test each feature

# ============================================
# TEST 1: EXPLAIN CODE
# Select this function and use "Explain Code"
# ============================================
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)


# ============================================
# TEST 2: GENERATE DOCUMENTATION
# Select this function and use "Generate Documentation"
# ============================================
def calculate_discount(price, discount_percent, is_member):
    if is_member:
        discount_percent += 5
    discount = price * (discount_percent / 100)
    return price - discount


# ============================================
# TEST 3: FIX BUGS
# This has bugs! Select and use "Fix Bugs"
# ============================================
def find_max(numbers):
    max_val = 0  # Bug: doesn't work for negative numbers
    for num in numbers:
        if num > max_val:
            max_val = num
    return max_val


# ============================================
# TEST 4: OPTIMIZE CODE
# Inefficient code - Select and use "Optimize Code"
# ============================================
def find_common_elements(list1, list2, list3):
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
    
    return common


# ============================================
# TEST 5: GENERATE TESTS
# Select this function and use "Generate Tests"
# ============================================
def divide_numbers(a, b):
    return a / b


# ============================================
# TESTING INSTRUCTIONS
# ============================================
# 1. Make sure backend is running: python frontend/app.py
# 2. Press F5 in VS Code to launch Extension Development Host
# 3. Open this file in the new window
# 4. For each test:
#    - Select the function
#    - Right-click
#    - Choose "🤖 AI Code Assistant"
#    - Select the appropriate action
# 5. Verify the results!

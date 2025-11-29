def calculate_total(items):
    """Calculate total price of items"""
    return sum(item['price'] for item in items)

def process_order(order):
    """Process customer order"""
    total = calculate_total(order['items'])
    return {'total': total, 'status': 'processed'}
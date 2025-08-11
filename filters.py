from datetime import datetime

def format_currency(value):
    """Format number as currency (₹)"""
    try: 
        value = float(value)
        return f"₹{value:,.2f}"
    except (ValueError, TypeError):
        return value
    
def format_date(value):
    """Format date to 'DD Mon YYYY'"""
    try:
        dt = datetime.strptime(str(value), "%Y-%m-%d")
        return dt.strftime("%d %b %Y")
    except (ValueError, TypeError):
        return value

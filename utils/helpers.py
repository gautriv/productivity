"""
Utility helper functions
Common utilities used across the application
"""
from datetime import datetime, date, timedelta
from functools import wraps
from flask import jsonify

def format_date(date_obj):
    """Format date object to ISO string"""
    if isinstance(date_obj, str):
        return date_obj
    return date_obj.isoformat()

def parse_date(date_str):
    """Parse ISO date string to date object"""
    if isinstance(date_str, date):
        return date_str
    return datetime.fromisoformat(date_str).date()

def format_time_minutes(minutes):
    """Format minutes to human-readable string"""
    if minutes < 60:
        return f"{minutes}m"
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours}h {mins}m" if mins > 0 else f"{hours}h"

def handle_errors(f):
    """Decorator to handle errors in routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    return decorated_function

def validate_task_data(data):
    """Validate task data"""
    errors = []
    
    if not data.get('title'):
        errors.append('Title is required')
    
    complexity = data.get('complexity', 3)
    if not isinstance(complexity, int) or complexity < 1 or complexity > 5:
        errors.append('Complexity must be between 1 and 5')
    
    cognitive_load = data.get('cognitive_load', 'active_work')
    valid_loads = ['deep_work', 'active_work', 'admin', 'learning']
    if cognitive_load not in valid_loads:
        errors.append(f'Cognitive load must be one of: {", ".join(valid_loads)}')
    
    time_estimate = data.get('time_estimate', 30)
    if not isinstance(time_estimate, int) or time_estimate < 0:
        errors.append('Time estimate must be a positive number')
    
    return errors

def calculate_date_range(days=30):
    """Calculate date range for queries"""
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    return start_date, end_date


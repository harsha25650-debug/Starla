# Simple in-memory warning system (upgrade later to database)

warnings = {}

def add_warning(user_id, reason):
    if user_id not in warnings:
        warnings[user_id] = []
    warnings[user_id].append(reason)

def get_warnings(user_id):
    return warnings.get(user_id, [])

def clear_warnings(user_id):
    warnings[user_id] = []

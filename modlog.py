from utils.db import add_log

def log_action(user, moderator, action, reason):
    add_log(str(user), str(moderator), action, reason)

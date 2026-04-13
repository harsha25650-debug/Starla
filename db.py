import sqlite3

conn = sqlite3.connect("bot.db", check_same_thread=False)
cursor = conn.cursor()

# Table for moderation logs
cursor.execute("""
CREATE TABLE IF NOT EXISTS modlogs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT,
    moderator TEXT,
    action TEXT,
    reason TEXT,
    time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()

def add_log(user, moderator, action, reason):
    cursor.execute(
        "INSERT INTO modlogs (user, moderator, action, reason) VALUES (?, ?, ?, ?)",
        (user, moderator, action, reason)
    )
    conn.commit()

def get_logs(limit=20):
    cursor.execute("SELECT * FROM modlogs ORDER BY id DESC LIMIT ?", (limit,))
    return cursor.fetchall()

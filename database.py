import sqlite3

conn = sqlite3.connect("workhours.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS shifts(
id INTEGER PRIMARY KEY AUTOINCREMENT,
date TEXT,
shift_type TEXT,
clock_in TEXT,
clock_out TEXT,
break_start TEXT,
break_end TEXT
)
""")

conn.commit()
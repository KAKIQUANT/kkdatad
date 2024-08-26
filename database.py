# database.py
import sqlite3

def get_db_connection():
    conn = sqlite3.connect('tokens.db')
    conn.row_factory = sqlite3.Row
    return conn

def setup_database():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS tokens (
            token TEXT PRIMARY KEY,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            usage INTEGER DEFAULT 0,
            limit INTEGER DEFAULT 1073741824  -- 1GB limit
        )
    ''')
    conn.commit()
    conn.close()

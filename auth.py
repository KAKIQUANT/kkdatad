# auth.py
import secrets
from database import get_db_connection

def generate_token():
    token = secrets.token_hex(16)
    conn = get_db_connection()
    conn.execute('INSERT INTO tokens (token) VALUES (?)', (token,))
    conn.commit()
    conn.close()
    return token

def is_authorized(token):
    conn = get_db_connection()
    result = conn.execute('SELECT * FROM tokens WHERE token = ?', (token,)).fetchone()
    conn.close()
    return result is not None

def check_traffic_limit(token, data_size):
    conn = get_db_connection()
    token_data = conn.execute('SELECT usage, limit FROM tokens WHERE token = ?', (token,)).fetchone()

    if token_data:
        new_usage = token_data['usage'] + data_size
        if new_usage > token_data['limit']:
            conn.close()
            return False
        conn.execute('UPDATE tokens SET usage = ? WHERE token = ?', (new_usage, token))
        conn.commit()
        conn.close()
        return True
    conn.close()
    return False

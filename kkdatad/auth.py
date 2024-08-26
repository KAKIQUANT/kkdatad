# auth.py
import secrets
from database import get_client
from datetime import datetime
from uuid import uuid4

async def generate_api_key(username: str, email: str):
    api_key = secrets.token_hex(16)
    query = f"""
    INSERT INTO users (id, username, email, api_key) 
    VALUES ('{uuid4()}', '{username}', '{email}', '{api_key}')
    """
    client = await get_client()
    await client.execute(query)
    return api_key

async def is_authorized(api_key: str):
    query = f"SELECT 1 FROM users WHERE api_key = '{api_key}' LIMIT 1"
    client = await get_client()

    async with client.cursor() as cursor:
        await cursor.execute(query)
        result = await cursor.fetchone()

    # Check if any rows were returned
    return result is not None



async def check_traffic_limit(api_key: str, data_size: int):
    # Define the data limit in bytes (1GB in this case)
    DATA_LIMIT = 1 * 1024 * 1024 * 1024  # 1GB

    client = await get_client()

    # Check if the API key exists in the usage table
    usage_query = f"SELECT usage_bytes FROM api_usage WHERE api_key = '{api_key}' LIMIT 1"
    usage_record = await client.fetchrow(usage_query)

    if usage_record:
        # Calculate new usage
        new_usage = usage_record['usage_bytes'] + data_size

        # Check if the new usage exceeds the limit
        if new_usage > DATA_LIMIT:
            return False

        # Update the usage in the database
        update_query = f"""
        UPDATE api_usage 
        SET usage_bytes = {new_usage}, last_updated = '{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}'
        WHERE api_key = '{api_key}'
        """
        await client.execute(update_query)
    else:
        # If no record exists for this API key, insert a new one
        insert_query = f"""
        INSERT INTO api_usage (api_key, usage_bytes, last_updated)
        VALUES ('{api_key}', {data_size}, '{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}')
        """
        await client.execute(insert_query)

    return True

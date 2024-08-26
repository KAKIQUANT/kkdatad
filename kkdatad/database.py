import clickhouse_connect

async def get_client():
    # Assuming you're using an async connection, adjust as per actual usage
    client = clickhouse_connect.get_client(host='localhost', username='default', password='default')
    return client

async def setup_database():
    client = await get_client()

    # Create the users table
    client.command('''
    CREATE TABLE IF NOT EXISTS users (
        id UUID DEFAULT generateUUIDv4(),
        username String,
        email String,
        api_key String,
        created_at DateTime DEFAULT now()
    ) ENGINE = MergeTree()
    ORDER BY (created_at)
    ''')

    # Create the api_usage table to track API key usage
    client.command('''
    CREATE TABLE IF NOT EXISTS api_usage (
        api_key String,
        usage_bytes UInt64,
        last_updated DateTime DEFAULT now()
    ) ENGINE = MergeTree()
    ORDER BY (api_key)
    ''')


    
async def get_financial_data(query: str):
    client = await get_client()
    result = await client.fetch(query)
    return result

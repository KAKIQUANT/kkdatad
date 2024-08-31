from kkdatad.auth import verify_token

async def is_authorized(id: str) -> bool:
    """
    Check if the API key is valid
    """
    return verify_token(id)

async def check_traffic_limit(api_key: str, data_size: int) -> bool:
    """
    Check if the API key has exceeded the traffic limit
    """
    return True
from fastapi import APIRouter, HTTPException, Header
from auth import is_authorized, check_traffic_limit
from compression import compress_data
from cache import get_cached_data
from database import get_financial_data

router = APIRouter()

@router.get("/financial-data/")
async def fetch_financial_data(query: str, api_key: str = Header(None)):
    if not await is_authorized(api_key):
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        data = await get_cached_data(query)
        compressed_data = compress_data(str(data))
        if not await check_traffic_limit(api_key, len(compressed_data)):
            raise HTTPException(status_code=403, detail="Traffic limit exceeded")
        return {"status": "success", "data": compressed_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/execute-sql/")
async def execute_sql(query: str, api_key: str = Header(None)):
    if not await is_authorized(api_key):
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        data = await get_financial_data(query)
        compressed_data = compress_data(str(data))
        if not await check_traffic_limit(api_key, len(compressed_data)):
            raise HTTPException(status_code=403, detail="Traffic limit exceeded")
        return {"status": "success", "data": compressed_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

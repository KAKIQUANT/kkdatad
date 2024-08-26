from fastapi import APIRouter, HTTPException, Header
from auth import is_authorized, check_traffic_limit
from compression import compress_data
from cache import get_cached_data
from database import get_financial_data

router = APIRouter()

@router.get("/financial-data/")
async def fetch_financial_data(query: str, token: str = Header(None)):
    if not is_authorized(token):
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        data = await get_cached_data(query)
        compressed_data = compress_data(str(data))
        if not check_traffic_limit(token, len(compressed_data)):
            raise HTTPException(status_code=403, detail="Traffic limit exceeded")
        return {"status": "success", "data": compressed_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/execute-sql/")
async def execute_sql(query: str, token: str = Header(None)):
    if not is_authorized(token):
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        data = await get_financial_data(query)
        compressed_data = compress_data(str(data))
        if not check_traffic_limit(token, len(compressed_data)):
            raise HTTPException(status_code=403, detail="Traffic limit exceeded")
        return {"status": "success", "data": compressed_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

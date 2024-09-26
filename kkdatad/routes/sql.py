from fastapi import APIRouter, HTTPException, Header
from kkdatad.utils.compression import compress_data
from kkdatad.utils.database import get_cc_client
from kkdatad.utils.verify import is_authorized, check_traffic_limit
import pickle

data_router = APIRouter()


@data_router.post("/sql/")
async def sql(query: str, api_key: str = Header(None)):
    if not await is_authorized(api_key):
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        client = await get_cc_client()
        df = await client.query_df(query)

        # Serialize the DataFrame to a binary format using pickle
        serialized_df = pickle.dumps(df)

        # Compress the serialized DataFrame using lz4
        compressed_data = compress_data(serialized_df)

        if not await check_traffic_limit(api_key, len(compressed_data)):
            raise HTTPException(status_code=403, detail="Traffic limit exceeded")

        return {
            "status": "success",
            "data": compressed_data.hex()  # Convert compressed data to hex for transmission
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


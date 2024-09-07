import httpx  # Use aiohttp as an alternative
import asyncio
import pandas as pd
from fastapi import APIRouter, HTTPException
from kkdatad.compression import compress_data
import pickle

proxy_router = APIRouter()

TUSHARE_URL = "http://api.tushare.pro"
AKSHARE_URL = "http://localhost:8501/api/public"  # Placeholder, replace with actual Akshare URL


# Helper function to send POST request to Tushare Pro API
async def fetch_tushare_data(api_name: str, token: str, params: dict, fields: str):
    request_data = {
        "api_name": api_name,
        "token": token,
        "params": params,
        "fields": fields
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(TUSHARE_URL, json=request_data)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Tushare API Error: " + response.text)
        return response.json()


async def fetch_akshare_data(api_name: str, params: dict = None):
    request_data = {
        "api_name": api_name,
        "params": params or {}  # Send empty params if none provided
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(AKSHARE_URL, json=request_data)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Akshare API Error: " + response.text)
        return response.json()

# Proxy endpoint to Tushare Pro
@proxy_router.post("/tushare/")
async def tushare_proxy(api_name: str, token: str, params: dict, fields: str):
    try:
        # Fetch data from Tushare
        response_data = await fetch_tushare_data(api_name, token, params, fields)
        
        # Optionally, convert response to a DataFrame
        df = pd.DataFrame(response_data['data']['items'], columns=response_data['data']['fields'])
        
        # Serialize and compress data
        serialized_df = pickle.dumps(df)
        compressed_data = compress_data(serialized_df)

        return {
            "status": "success",
            "data": compressed_data.hex()  # Convert compressed data to hex for transmission
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Generic proxy endpoint for Akshare API
@proxy_router.post("/akshare/")
async def akshare_proxy(api_name: str, params: dict = None):

    try:
        # Fetch data from Akshare with or without parameters
        response_data = await fetch_akshare_data(api_name, params)

        # Convert the response to a DataFrame if needed
        df = pd.DataFrame(response_data['data']['items'], columns=response_data['data']['fields'])
        
        # Serialize and compress data
        serialized_df = pickle.dumps(df)
        compressed_data = compress_data(serialized_df)

        return {
            "status": "success",
            "data": compressed_data.hex()  # Convert compressed data to hex for transmission
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
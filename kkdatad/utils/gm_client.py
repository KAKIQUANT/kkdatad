from typing import Optional, Dict, List
import pandas as pd
from gm.api import *
from .config import settings

class GMClient:
    """Client for accessing data through GoldMiner API"""
    
    def __init__(self):
        if settings.GM_TOKEN:
            set_token(settings.GM_TOKEN)
        else:
            raise ValueError("GM_TOKEN not set in environment variables")
        
    def history(self, symbols: List[str], frequency: str = '1d',
                start_date: str = None, end_date: str = None,
                fields: List[str] = None, adjust: str = None) -> pd.DataFrame:
        """Get historical price data"""
        dfs = []
        for symbol in symbols:
            df = history(symbol=symbol, 
                        frequency=frequency,
                        start_time=start_date,
                        end_time=end_date,
                        fields=fields or ['open', 'high', 'low', 'close', 'volume'],
                        adjust=adjust or 'none')
            dfs.append(df)
        return pd.concat(dfs) if dfs else pd.DataFrame()

    def get_fundamentals(self, table: str, symbols: List[str], 
                        start_date: str, end_date: str, fields: List[str] = None) -> pd.DataFrame:
        """Get fundamental data from GM"""
        return get_fundamentals(table=table,
                              symbols=symbols,
                              start_date=start_date,
                              end_date=end_date,
                              fields=fields)

    def get_instruments(self, symbols: List[str] = None, 
                       types: List[str] = None) -> pd.DataFrame:
        """Get instrument information"""
        return get_instruments(symbols=symbols, types=types)

# Initialize singleton client
gm_client = GMClient()
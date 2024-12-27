from typing import List
import pandas as pd
from gm.api import *
from kkdatad.utils.config import settings

class GMClient:
    def __init__(self):
        if settings.LOCAL_MODE:
            return
        if not settings.GM_TOKEN:
            raise ValueError("GM_TOKEN not set in settings")
        set_token(settings.GM_TOKEN)

    def get_history_data(self, symbols: List[str], start_date: str, end_date: str) -> pd.DataFrame:
        if settings.LOCAL_MODE:
            return pd.DataFrame()
        return history(symbols=symbols, start_time=start_date, end_time=end_date, df=True)

    def get_industry_data(self, symbols: List[str]) -> pd.DataFrame:
        if settings.LOCAL_MODE:
            return pd.DataFrame()
        return get_industry(symbols=symbols, df=True)

gm_client = GMClient()

import requests
import pandas as pd
import streamlit as st
from src.config import API_URL, API_KEY

class LiquidityAPIClient:
    """
    Client for interacting with the Liquidity Stress API.
    """
    def __init__(self):
        self.base_url = API_URL
        self.api_key = API_KEY

    def _get(self, endpoint, params=None):
        headers = {"X-API-Key": self.api_key}
        try:
            response = requests.get(f"{self.base_url}/api/v1{endpoint}", headers=headers, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"API Request failed: {e}")
            return None

    def get_onrrp(self, last_n=30):
        data = self._get("/onrrp/", params={"last_n": last_n})
        return pd.DataFrame(data) if data else None

    def get_sofr(self, days=30):
        data = self._get("/sofr/", params={"days": days})
        return pd.DataFrame(data) if data else None

    def get_reserves(self, days=90):
        data = self._get("/reserves/", params={"days": days})
        return pd.DataFrame(data) if data else None

    def get_treasury(self, days=30):
        data = self._get("/treasury/", params={"days": days})
        return pd.DataFrame(data) if data else None

    def get_srf(self, days=30):
        data = self._get("/srf/", params={"days": days})
        return pd.DataFrame(data) if data else None

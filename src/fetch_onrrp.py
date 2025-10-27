import pandas as pd
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging

from bs4 import BeautifulSoup

from .config import DATA_SOURCES, DATA_FILES, THRESHOLDS
from .utils import safe_request, save_data, load_data, format_date, suppress_warnings

"""
Fetch Overnight Reverse Repo (ON RRP) data from NY Fed
"""

def fetch_onrrp_data(mode: str = "latest", start_date: Optional[datetime] = None, end_date: Optional[datetime] = None, last_n: Optional[int] = None) -> Optional[pd.DataFrame]:
    """
    Convenience function to fetch ON RRP data using ONRRPFetcher.
    """
    fetcher = ONRRPFetcher()
    return fetcher.fetch_data(mode=mode, start_date=start_date, end_date=end_date, last_n=last_n)
"""
Fetch Overnight Reverse Repo (ON RRP) data from NY Fed
"""
from typing import Optional, Dict, Any
import logging

from bs4 import BeautifulSoup

from .config import DATA_SOURCES, DATA_FILES, THRESHOLDS
from .utils import safe_request, save_data, load_data, format_date, suppress_warnings

logger = logging.getLogger(__name__)

class ONRRPFetcher:
    """Fetcher for NY Fed ON RRP data"""
    
    def __init__(self):
        self.base_url = DATA_SOURCES['NY_FED_ONRRP']
        self.data_file = DATA_FILES['onrrp']
        suppress_warnings()
    
    def fetch_data(self, mode: str = "latest", start_date: Optional[datetime] = None, end_date: Optional[datetime] = None, last_n: Optional[int] = None, operation_type: str = "Reverse Repo") -> Optional[pd.DataFrame]:
        """
        Fetch ON RRP data from NY Fed API only. No mock or fallback data.
        Uses the correct endpoint for latest Reverse Repo operation results.
        """
        def parse_response(data):
            if isinstance(data, dict) and "repo" in data and "operations" in data["repo"]:
                return data["repo"]["operations"]
            elif isinstance(data, dict) and "operations" in data:
                return data["operations"]
            elif isinstance(data, list):
                return data
            else:
                logger.error("Unexpected ON RRP API response structure.")
                return []

        df = pd.DataFrame()
        headers = {
            "User-Agent": "Mozilla/5.0 (liquidity-dashboard/1.0)",
            "Accept": "application/json"
        }
        if mode == "latest":
            try:
                url_latest = "https://markets.newyorkfed.org/api/rp/reverserepo/all/results/latest.json"
                logger.info(f"Attempting to fetch latest Reverse Repo operation: {url_latest}")
                response = requests.get(url_latest, timeout=15, headers=headers)
                logger.info(f"API status code: {response.status_code}")
                logger.info(f"API raw response: {response.text}")
                response.raise_for_status()
                data = response.json()
                operations = parse_response(data)
                if operations:
                    logger.info("Successfully fetched latest Reverse Repo operation.")
                    df = pd.DataFrame(operations)
                else:
                    logger.warning("No results from latest Reverse Repo operation endpoint.")
            except Exception as e:
                logger.error(f"Error fetching latest Reverse Repo operation: {e}")

        elif mode == "last_n":
            try:
                n = last_n if last_n else 10
                url_last_n = f"https://markets.newyorkfed.org/api/rp/reverserepo/all/results/last/{n}.json"
                logger.info(f"Attempting to fetch last {n} Reverse Repo operations: {url_last_n}")
                response = requests.get(url_last_n, timeout=15, headers=headers)
                logger.info(f"API status code: {response.status_code}")
                logger.info(f"API raw response: {response.text}")
                response.raise_for_status()
                data = response.json()
                operations = parse_response(data)
                if operations:
                    logger.info(f"Successfully fetched last {n} Reverse Repo operations.")
                    df = pd.DataFrame(operations)
                else:
                    logger.warning(f"No results from last {n} Reverse Repo operations endpoint.")
            except Exception as e:
                logger.error(f"Error fetching last {n} Reverse Repo operations: {e}")

        elif mode == "date_range" and start_date:
            try:
                start_str = start_date.strftime('%Y-%m-%d')
                end_str = (end_date or start_date).strftime('%Y-%m-%d')
                # Use NY Fed API for date range queries
                # operation_type can be "Repo" or "Reverse Repo"
                op_type_param = requests.utils.quote(operation_type)
                url_date_range = (
                    f"https://markets.newyorkfed.org/api/rp/results/search.json?"
                    f"startDate={start_str}&endDate={end_str}"
                    f"&operationTypes={op_type_param}&method=multiple"
                )
                logger.info(f"Attempting to fetch {operation_type} data for date range: {url_date_range}")
                response = requests.get(url_date_range, timeout=15, headers=headers)
                logger.info(f"API status code: {response.status_code}")
                logger.info(f"API raw response: {response.text}")
                response.raise_for_status()
                data = response.json()
                operations = parse_response(data)
                if operations:
                    logger.info(f"Successfully fetched {operation_type} data for date range.")
                    df = pd.DataFrame(operations)
                else:
                    logger.warning(f"No results from {operation_type} date range endpoint.")
            except Exception as e:
                logger.error(f"Error fetching {operation_type} data for range: {e}")

        # Map correct NY Fed API fields to dashboard columns
        if not df.empty:
            # Extract and transform fields
            df["Date"] = pd.to_datetime(df["operationDate"]) if "operationDate" in df.columns else pd.NaT
            df["Accepted_Billions"] = df["totalAmtAccepted"].astype(float) / 1e9 if "totalAmtAccepted" in df.columns else pd.NA
            df["Counterparties"] = df["acceptedCpty"] if "acceptedCpty" in df.columns else pd.NA
            
            # Extract Rate from details list (NY Fed API structure)
            if "details" in df.columns:
                def get_rate(details):
                    if isinstance(details, list) and len(details) > 0:
                        return details[0].get("percentAwardRate")
                    return None
                df["Rate"] = df["details"].apply(get_rate).astype(float)
            elif "rate" in df.columns:
                df["Rate"] = df["rate"].astype(float)
            else:
                df["Rate"] = pd.NA
                
            df["Operation_Type"] = df["operationType"] if "operationType" in df.columns else pd.NA
            df["_data_source"] = "live"
        else:
            # Create empty DataFrame with required columns
            df = pd.DataFrame(columns=["Date", "Accepted_Billions", "Counterparties", "Rate", "Operation_Type", "_data_source"])
            df["_data_source"] = "live_empty"
        return df
    
    # _generate_mock_data removed. Only real API data is used.
    
    def save_data(self, df: pd.DataFrame) -> bool:
        """Save ON RRP data to CSV"""
        return save_data(df, self.data_file)
    
    def load_data(self) -> Optional[pd.DataFrame]:
        """Load ON RRP data from CSV"""
        return load_data(self.data_file)

    def check_stress_level(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Check ON RRP stress indicators"""
        if df.empty:
            return {'stress_detected': False, 'message': 'No data available'}

        latest_amount = df['amount_billions'].iloc[-1]
        stress_threshold = THRESHOLDS['onrrp_stress']

        is_stress = latest_amount > stress_threshold

        return {
            'stress_detected': is_stress,
            'latest_amount': latest_amount,
            'threshold': stress_threshold,
            'message': f"ON RRP at ${latest_amount:.1f}B ({'ABOVE' if is_stress else 'below'} stress threshold of ${stress_threshold}B)"
        }
    
    # ...existing code...
        print(df.head())
        print(f"Latest amount: ${df['amount_billions'].iloc[-1]:.1f}B")
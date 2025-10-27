"""
Fetch Overnight Reverse Repo (ON RRP) data from NY Fed
"""

import pandas as pd
import requests
from datetime import datetime, timedelta
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
    
    def fetch_data(self, mode: str = "latest", start_date: Optional[datetime] = None, end_date: Optional[datetime] = None, last_n: Optional[int] = None) -> Optional[pd.DataFrame]:
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
                url_last_n = f"https://markets.newyorkfed.org/api/rp/overnightreverse-repo/operation-results/results/last/{n}.json"
                logger.info(f"Attempting to fetch last {n} ON RRP operations: {url_last_n}")
                response = requests.get(url_last_n, timeout=15, headers=headers)
                logger.info(f"API status code: {response.status_code}")
                logger.info(f"API raw response: {response.text}")
                response.raise_for_status()
                data = response.json()
                operations = parse_response(data)
                if operations:
                    logger.info(f"Successfully fetched last {n} ON RRP operations.")
                    df = pd.DataFrame(operations)
                else:
                    logger.warning(f"No results from last {n} ON RRP operations endpoint.")
            except Exception as e:
                logger.error(f"Error fetching last {n} ON RRP operations: {e}")

        elif mode == "date_range" and start_date:
            try:
                date_list = pd.date_range(start=start_date, end=end_date or start_date, freq='D')
                all_ops = []
                for d in date_list:
                    date_str = d.strftime('%Y%m%d')
                    url_date = f"https://markets.newyorkfed.org/api/rp/overnightreverse-repo/operation-results/results/date/{date_str}.json"
                    logger.info(f"Attempting to fetch ON RRP data for date: {url_date}")
                    try:
                        response = requests.get(url_date, timeout=15, headers=headers)
                        logger.info(f"API status code: {response.status_code}")
                        logger.info(f"API raw response: {response.text}")
                        response.raise_for_status()
                        data = response.json()
                        ops = parse_response(data)
                        if ops:
                            all_ops.extend(ops)
                    except Exception as e:
                        logger.error(f"Error fetching ON RRP data for {date_str}: {e}")
                if all_ops:
                    logger.info(f"Successfully fetched ON RRP data for date range.")
                    df = pd.DataFrame(all_ops)
                else:
                    logger.warning("No results from ON RRP date range endpoint.")
            except Exception as e:
                logger.error(f"Error fetching ON RRP data for range: {e}")

        # Mark data source as live only
        if not df.empty:
            df["_data_source"] = "live"
        else:
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

def fetch_onrrp_data(start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Optional[pd.DataFrame]:
    """Convenience function to fetch ON RRP data"""
    if start_date is None:
        start_date = datetime.now() - timedelta(days=365)
    if end_date is None:
        end_date = datetime.now()
    
    fetcher = ONRRPFetcher()
    df = fetcher.fetch_data(start_date, end_date)
    
    if df is not None and not df.empty:
        fetcher.save_data(df)
        stress_info = fetcher.check_stress_level(df)
        logger.info(stress_info['message'])
    
    return df

if __name__ == "__main__":
    # Test the fetcher
    df = fetch_onrrp_data()
    if df is not None:
        print(f"Fetched {len(df)} ON RRP records")
        print(df.head())
        print(f"Latest amount: ${df['amount_billions'].iloc[-1]:.1f}B")
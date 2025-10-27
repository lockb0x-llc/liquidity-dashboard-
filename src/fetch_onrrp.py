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
        Robustly fetch ON RRP data from NY Fed API.
        Tries latest, then last N, then date range if no results. Documents all steps.

        Parameters:
            mode: "latest", "last_n", "date_range"
            start_date, end_date: for custom range
            last_n: for last N operations

        Returns:
            pd.DataFrame or None
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

        # 1. Try latest operation
        try:
            url_latest = "https://markets.newyorkfed.org/api/rp/overnightreverse-repo/operation-results/results/last/1.json"
            logger.info(f"Attempting to fetch latest ON RRP operation: {url_latest}")
            response = requests.get(url_latest, timeout=15)
            response.raise_for_status()
            data = response.json()
            operations = parse_response(data)
            if operations:
                logger.info("Successfully fetched latest ON RRP operation.")
                df = pd.DataFrame(operations)
            else:
                logger.warning("No results from latest ON RRP operation endpoint.")
                df = pd.DataFrame()
        except Exception as e:
            logger.error(f"Error fetching latest ON RRP operation: {e}")
            df = pd.DataFrame()

        # 2. If empty, try last N operations (default N=10)
        if df.empty:
            try:
                n = last_n if last_n else 10
                url_last_n = f"https://markets.newyorkfed.org/api/rp/overnightreverse-repo/operation-results/results/last/{n}.json"
                logger.info(f"Attempting to fetch last {n} ON RRP operations: {url_last_n}")
                response = requests.get(url_last_n, timeout=15)
                response.raise_for_status()
                data = response.json()
                operations = parse_response(data)
                if operations:
                    logger.info(f"Successfully fetched last {n} ON RRP operations.")
                    df = pd.DataFrame(operations)
                else:
                    logger.warning(f"No results from last {n} ON RRP operations endpoint.")
                    df = pd.DataFrame()
            except Exception as e:
                logger.error(f"Error fetching last {n} ON RRP operations: {e}")
                df = pd.DataFrame()

        # 3. If still empty, try date range (default: last 90 days)
        if df.empty:

            import requests
            import pandas as pd
            import logging
            from datetime import datetime, timedelta

            logger = logging.getLogger(__name__)

            class ONRRPFetcher:
                """
                Fetches ON RRP (Overnight Reverse Repo) data from the NY Fed API.
                Provides robust fallback logic for missing fields and handles errors gracefully.
                """
                BASE_URL = "https://markets.newyorkfed.org/api/rp/overnightreverse/search.json"

                @staticmethod
                def fetch_data(mode="live", start_date=None, end_date=None, last_n=30):
                    """
                    Fetch ON RRP data from NY Fed API or demo file.
                    Args:
                        mode (str): 'live' or 'demo'.
                        start_date (str): 'YYYY-MM-DD'.
                        end_date (str): 'YYYY-MM-DD'.
                        last_n (int): Number of most recent records if no date range provided.
                    Returns:
                        pd.DataFrame or None: ON RRP data, or None if unavailable.
                    """
                    if mode == "demo":
                        try:
                            return pd.read_csv("data/onrrp_sample.csv")
                        except Exception as e:
                            logger.error(f"Demo ON RRP data not available: {e}")
                            return None

                    params = {"format": "json"}
                    if start_date and end_date:
                        params["startDate"] = start_date
                        params["endDate"] = end_date
                    else:
                        today = datetime.today()
                        params["startDate"] = (today - timedelta(days=60)).strftime("%Y-%m-%d")
                        params["endDate"] = today.strftime("%Y-%m-%d")

                    try:
                        response = requests.get(ONRRPFetcher.BASE_URL, params=params, timeout=10)
                        response.raise_for_status()
                        data = response.json()
                        records = data.get("repoOperations", [])
                        if not records:
                            logger.warning("No ON RRP records found in API response.")
                            return None
                        df = pd.DataFrame(records)
                    except Exception as e:
                        logger.error(f"ON RRP API fetch failed: {e}")
                        return None

                    # Ensure required columns
                    for col in ["operationDate", "acceptedAmount", "note"]:
                        if col not in df.columns:
                            df[col] = pd.NA

                    # Convert acceptedAmount to float (billions)
                    df["acceptedAmount"] = pd.to_numeric(df["acceptedAmount"], errors="coerce") / 1e9
                    # Parse operationDate to datetime
                    df["operationDate"] = pd.to_datetime(df["operationDate"], errors="coerce")

                    # Sort and trim
                    df = df.sort_values("operationDate", ascending=False)
                    if last_n:
                        df = df.head(last_n)
                    return df.reset_index(drop=True)
    
    def _generate_mock_data(self, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Generate mock ON RRP data for testing"""
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Generate realistic ON RRP amounts (typically $1.5-2.5 trillion)
        base_amount = 2000  # $2 trillion baseline
        amounts = []
        
        for i, date in enumerate(date_range):
            # Add weekly patterns (lower on weekends)
            weekly_factor = 0.9 if date.weekday() >= 5 else 1.0
            
            # Add some trend and randomness
            trend = (i / len(date_range)) * 200  # Gradual increase
            random_factor = (i % 17) * 30 - 150  # Pseudo-random variation
            
            amount = base_amount + trend + random_factor
            amount *= weekly_factor
            amounts.append(max(amount, 1000))  # Minimum floor
        
        df = pd.DataFrame({
            'date': date_range,
            'amount_billions': amounts,
            'participants': [75 + (i % 25) for i in range(len(date_range))],
            'rate': [5.25 + (i % 10) * 0.01 for i in range(len(date_range))]
        })
        
        logger.info(f"Generated mock ON RRP data with {len(df)} records")
        return df
    
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
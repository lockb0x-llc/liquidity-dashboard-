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
            try:
                if not start_date:
                    start_date = datetime.now() - timedelta(days=90)
                if not end_date:
                    end_date = datetime.now()
                search_api = "https://markets.newyorkfed.org/api/rp/results/search.json"
                params = {
                    "operationType": "overnightreverse-repo",
                    "operationMethod": "operation-results",
                    "startDate": start_date.strftime("%Y-%m-%d"),
                    "endDate": end_date.strftime("%Y-%m-%d"),
                    "format": "json"
                }
                logger.info(f"Attempting to fetch ON RRP data for date range {params['startDate']} to {params['endDate']}")
                response = requests.get(search_api, params=params, timeout=15)
                response.raise_for_status()
                data = response.json()
                operations = parse_response(data)
                if operations:
                    logger.info(f"Successfully fetched ON RRP data for date range.")
                    df = pd.DataFrame(operations)
                else:
                    logger.warning("No results from ON RRP date range endpoint.")
                    df = pd.DataFrame()
            except Exception as e:
                logger.error(f"Error fetching ON RRP data for date range: {e}")
                df = pd.DataFrame()

        # 4. If still empty, log and return None
        if df.empty:
            logger.error("No ON RRP data available from any endpoint. Returning None.")
            return None

        # Standardize columns and handle missing keys robustly
        logger.info(f"ON RRP raw columns: {list(df.columns)}")
        rename_map = {}
        if "operationDate" in df.columns:
            rename_map["operationDate"] = "Date"
        if "totalAmountAccepted" in df.columns:
            rename_map["totalAmountAccepted"] = "Accepted_Billions"
        if "participantCount" in df.columns:
            rename_map["participantCount"] = "Counterparties"
        df = df.rename(columns=rename_map)

        # Convert date
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"])

        # Accepted_Billions: try totalAmountAccepted, else totalAmtAccepted
        if "Accepted_Billions" in df.columns:
            df["Accepted_Billions"] = pd.to_numeric(df["Accepted_Billions"], errors="coerce") / 1_000_000_000
        elif "totalAmtAccepted" in df.columns:
            df["Accepted_Billions"] = pd.to_numeric(df["totalAmtAccepted"], errors="coerce") / 1_000_000_000
            logger.info("Used 'totalAmtAccepted' for Accepted_Billions.")
        else:
            logger.warning("'Accepted_Billions' column missing. Filling with NaN.")
            df["Accepted_Billions"] = float('nan')

        # Counterparties: try participantCount, else count acceptedCpty
        if "Counterparties" in df.columns:
            df["Counterparties"] = pd.to_numeric(df["Counterparties"], errors="coerce")
        elif "acceptedCpty" in df.columns:
            # acceptedCpty is a list of counterparties per operation
            df["Counterparties"] = df["acceptedCpty"].apply(lambda x: len(x) if isinstance(x, list) else float('nan'))
            logger.info("Used 'acceptedCpty' for Counterparties.")
        else:
            logger.warning("'Counterparties' column missing. Filling with NaN.")
            df["Counterparties"] = float('nan')

        df = df.sort_values("Date").reset_index(drop=True)

        # Save to CSV
        try:
            df.to_csv("data/on_rrp.csv", index=False)
            logger.info(f"Saved ON RRP data to data/on_rrp.csv with {len(df)} records. Columns: {list(df.columns)}")
        except Exception as e:
            logger.error(f"Failed to save ON RRP data to CSV: {e}")

        return df
    
    def _process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process and clean ON RRP data"""
        try:
            # Standardize column names (adjust based on actual API response)
            column_mapping = {
                'operationDate': 'date',
                'totalAmountAccepted': 'amount_billions',
                'participantCount': 'participants',
                'averageRate': 'rate'
            }
            
            # Rename columns if they exist
            for old_col, new_col in column_mapping.items():
                if old_col in df.columns:
                    df = df.rename(columns={old_col: new_col})
            
            # Ensure we have required columns
            if 'date' not in df.columns:
                df['date'] = pd.date_range(start=datetime.now() - timedelta(days=len(df)), periods=len(df))
            
            # Convert date column
            df['date'] = pd.to_datetime(df['date'])
            
            # Convert amount to billions if needed
            if 'amount_billions' in df.columns:
                # Assume data might be in millions, convert to billions
                df['amount_billions'] = pd.to_numeric(df['amount_billions'], errors='coerce') / 1000
            else:
                # Generate realistic mock amounts
                df['amount_billions'] = 1800 + (pd.Series(range(len(df))) * 10) + (pd.Series(range(len(df))) % 7) * 50
            
            # Add missing columns with defaults
            if 'participants' not in df.columns:
                df['participants'] = 80 + (pd.Series(range(len(df))) % 20)
            
            if 'rate' not in df.columns:
                df['rate'] = 5.25 + (pd.Series(range(len(df))) % 10) * 0.05
            
            # Sort by date
            df = df.sort_values('date').reset_index(drop=True)
            
            return df
            
        except Exception as e:
            logger.error(f"Error processing ON RRP data: {e}")
            return pd.DataFrame()
    
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
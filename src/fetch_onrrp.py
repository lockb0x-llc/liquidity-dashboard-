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
        Fetch ON RRP data from NY Fed API.
        Always uses the correct endpoint for latest operation: 'results/last/1.json'.
        Ignores 'published/latest.json' (invalid).
        """
        try:
            # Only support fetching the latest operation for now
            url = "https://markets.newyorkfed.org/api/rp/overnightreverse-repo/operation-results/results/last/1.json"
            logger.info(f"Fetching ON RRP data from {url}")
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()

            # Parse response
            if isinstance(data, dict) and "repo" in data and "operations" in data["repo"]:
                operations = data["repo"]["operations"]
            elif isinstance(data, dict) and "operations" in data:
                operations = data["operations"]
            elif isinstance(data, list):
                operations = data
            else:
                logger.error("Unexpected ON RRP API response structure.")
                return None

            # Build DataFrame
            df = pd.DataFrame(operations)
            # Standardize columns
            df = df.rename(columns={
                "operationDate": "Date",
                "totalAmountAccepted": "Accepted_Billions",
                "participantCount": "Counterparties"
            })
            # Convert date
            if "Date" in df.columns:
                df["Date"] = pd.to_datetime(df["Date"])
            # Convert amount to billions
            if "Accepted_Billions" in df.columns:
                df["Accepted_Billions"] = pd.to_numeric(df["Accepted_Billions"], errors="coerce") / 1_000_000_000
            # Counterparties
            if "Counterparties" in df.columns:
                df["Counterparties"] = pd.to_numeric(df["Counterparties"], errors="coerce")

            df = df.sort_values("Date").reset_index(drop=True)

            # Save to CSV
            try:
                df.to_csv("data/on_rrp.csv", index=False)
                logger.info(f"Saved ON RRP data to data/on_rrp.csv with {len(df)} records.")
            except Exception as e:
                logger.error(f"Failed to save ON RRP data to CSV: {e}")

            return df
        except Exception as e:
            logger.error(f"Error fetching ON RRP data: {e}")
            return None
    
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
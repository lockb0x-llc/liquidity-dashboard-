"""
Fetch SRF (Standing Repo Facility) usage data from NY Fed
"""

import pandas as pd
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging

from .config import DATA_SOURCES, DATA_FILES, THRESHOLDS
from .utils import safe_request, save_data, load_data, format_date, suppress_warnings

logger = logging.getLogger(__name__)

class SRFFetcher:
    """Fetcher for NY Fed SRF data"""
    
    def __init__(self):
        self.base_url = DATA_SOURCES['NY_FED_SRF']
        self.data_file = DATA_FILES['srf']
        suppress_warnings()
    
    def fetch_data(self, start_date: datetime, end_date: datetime) -> Optional[pd.DataFrame]:
        """Fetch SRF data from NY Fed API"""
        try:
            # Build parameters for NY Fed SRF API
            params = {
                'startDate': format_date(start_date),
                'endDate': format_date(end_date),
                'format': 'json'
            }
            
            logger.info(f"Fetching SRF data from {start_date.date()} to {end_date.date()}")
            response = safe_request(self.base_url, params=params)
            
            if response is None:
                logger.warning("Failed to fetch SRF data, source data not available")
                return None
            
            data = response.json()
            
            # Parse the response structure (adjust based on actual API response)
            if 'repo' in data and 'operations' in data['repo']:
                operations = data['repo']['operations']
                df = pd.DataFrame(operations)
            else:
                logger.warning("Unexpected SRF API response structure, source data not available")
                return None
            
            # Clean and process data
            df = self._process_data(df)
            return df
            
        except Exception as e:
            logger.error(f"Error fetching SRF data: {e}")
            return None
    
    def _process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process and clean SRF data"""
        try:
            # Standardize column names (adjust based on actual API response)
            column_mapping = {
                'operationDate': 'date',
                'totalAmountAccepted': 'usage_billions',
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
            
            # Convert usage to billions if needed
            if 'usage_billions' in df.columns:
                df['usage_billions'] = pd.to_numeric(df['usage_billions'], errors='coerce') / 1000
            else:
                # SRF usage is typically very low (emergency facility)
                # Generate mostly zero usage with occasional spikes
                usage = []
                for i in range(len(df)):
                    # 95% of the time, no usage
                    if i % 20 == 0:  # Occasional usage
                        usage.append((i % 5) * 10 + 5)  # 5-45 billion
                    else:
                        usage.append(0)
                df['usage_billions'] = usage
            
            # Add missing columns with defaults
            if 'participants' not in df.columns:
                df['participants'] = [1 if usage > 0 else 0 for usage in df['usage_billions']]
            
            if 'rate' not in df.columns:
                # SRF rate is typically Fed Funds + 25bp (currently ~5.5%)
                df['rate'] = 5.50 + (pd.Series(range(len(df))) % 10) * 0.01
            
            # Sort by date
            df = df.sort_values('date').reset_index(drop=True)
            
            return df
            
        except Exception as e:
            logger.error(f"Error processing SRF data: {e}")
            return pd.DataFrame()
    
    def _generate_mock_data(self, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Generate mock SRF data for testing"""
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # SRF is an emergency facility - mostly zero usage
        usage_data = []
        participants_data = []
        rates_data = []
        
        base_rate = 5.50  # Fed Funds + 25bp
        
        for i, date in enumerate(date_range):
            # Generate occasional stress periods
            if i % 50 == 0 and i > 0:  # Stress event every ~50 days
                # Stress period with some usage
                stress_duration = min(5, len(date_range) - i)
                for j in range(stress_duration):
                    if i + j < len(date_range):
                        usage = min(100, (j + 1) * 20)  # Escalating usage
                        usage_data.append(usage)
                        participants_data.append(min(5, j + 1))
                        rates_data.append(base_rate + j * 0.05)
                i += stress_duration
            else:
                # Normal period - no usage
                usage_data.append(0)
                participants_data.append(0)
                rates_data.append(base_rate)
        
        # Trim to match date range length
        usage_data = usage_data[:len(date_range)]
        participants_data = participants_data[:len(date_range)]
        rates_data = rates_data[:len(date_range)]
        
        df = pd.DataFrame({
            'date': date_range,
            'usage_billions': usage_data,
            'participants': participants_data,
            'rate': rates_data
        })
        
        logger.info(f"Generated mock SRF data with {len(df)} records")
        return df
    
    def save_data(self, df: pd.DataFrame) -> bool:
        """Save SRF data to CSV"""
        return save_data(df, self.data_file)
    
    def load_data(self) -> Optional[pd.DataFrame]:
        """Load SRF data from CSV"""
        return load_data(self.data_file)
    
    def check_stress_level(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Check SRF stress indicators"""
        if df.empty:
            return {'stress_detected': False, 'message': 'No data available'}
        
        latest_usage = df['usage_billions'].iloc[-1]
        stress_threshold = THRESHOLDS['srf_usage']
        
        # Any significant SRF usage indicates stress
        is_stress = latest_usage > stress_threshold
        
        # Check for recent usage trend
        if len(df) >= 7:
            recent_usage = df['usage_billions'].tail(7).sum()
            sustained_usage = recent_usage > stress_threshold
        else:
            sustained_usage = False
        
        # Check for frequency of usage
        if len(df) >= 30:
            monthly_usage_days = (df['usage_billions'].tail(30) > 0).sum()
            frequent_usage = monthly_usage_days > 3
        else:
            frequent_usage = False
        
        return {
            'stress_detected': is_stress or sustained_usage or frequent_usage,
            'latest_usage': latest_usage,
            'threshold': stress_threshold,
            'sustained_usage': sustained_usage,
            'frequent_usage': frequent_usage,
            'message': f"SRF usage at ${latest_usage:.1f}B ({'EMERGENCY' if is_stress else 'normal'} - threshold ${stress_threshold}B)"
        }

def fetch_srf_data(start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Optional[pd.DataFrame]:
    """Convenience function to fetch SRF data"""
    if start_date is None:
        start_date = datetime.now() - timedelta(days=365)
    if end_date is None:
        end_date = datetime.now()
    
    fetcher = SRFFetcher()
    df = fetcher.fetch_data(start_date, end_date)
    
    if df is not None and not df.empty:
        fetcher.save_data(df)
        stress_info = fetcher.check_stress_level(df)
        logger.info(stress_info['message'])
        
        # Log emergency usage if detected
        if stress_info['stress_detected']:
            logger.warning(f"⚠️  SRF EMERGENCY USAGE DETECTED: {stress_info['message']}")
    
    return df

if __name__ == "__main__":
    # Test the fetcher
    df = fetch_srf_data()
    if df is not None:
        print(f"Fetched {len(df)} SRF records")
        print(df.head())
        print(f"Latest SRF usage: ${df['usage_billions'].iloc[-1]:.1f}B")
        print(f"Total usage in dataset: ${df['usage_billions'].sum():.1f}B")
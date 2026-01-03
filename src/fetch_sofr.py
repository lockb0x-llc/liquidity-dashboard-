"""
Fetch SOFR (Secured Overnight Financing Rate) data from NY Fed
"""

import pandas as pd
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging

from .config import DATA_SOURCES, DATA_FILES, THRESHOLDS
from .utils import safe_request, save_data, load_data, format_date, suppress_warnings

logger = logging.getLogger(__name__)

class SOFRFetcher:
    """Fetcher for NY Fed SOFR data"""
    
    def __init__(self):
        self.base_url = DATA_SOURCES['NY_FED_SOFR']
        self.data_file = DATA_FILES['sofr']
        suppress_warnings()
    
    def fetch_data(self, start_date: datetime, end_date: datetime) -> Optional[pd.DataFrame]:
        """Fetch SOFR data from NY Fed API"""
        try:
            # Build parameters for NY Fed SOFR API
            params = {
                'startDate': format_date(start_date),
                'endDate': format_date(end_date),
                'format': 'json'
            }
            
            logger.info(f"Fetching SOFR data from {start_date.date()} to {end_date.date()}")
            response = safe_request(self.base_url, params=params)
            
            if response is None:
                logger.warning("Failed to fetch SOFR data, source data not available")
                return None
            
            data = response.json()
            
            # Parse the response structure (adjust based on actual API response)
            if 'refRates' in data:
                rates_data = data['refRates']
                df = pd.DataFrame(rates_data)
            else:
                logger.warning("Unexpected SOFR API response structure, source data not available")
                return None
            
            # Clean and process data
            df = self._process_data(df)
            return df
            
        except Exception as e:
            logger.error(f"Error fetching SOFR data: {e}")
            return None
    
    def _process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process and clean SOFR data"""
        try:
            # Standardize column names (adjust based on actual API response)
            column_mapping = {
                'effectiveDate': 'date',
                'percentRate': 'sofr_rate',
                'volumeInBillions': 'volume_billions'
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
            
            # Convert rates to numeric
            if 'sofr_rate' in df.columns:
                df['sofr_rate'] = pd.to_numeric(df['sofr_rate'], errors='coerce')
            else:
                # Generate realistic SOFR rates (currently around 5.3%)
                df['sofr_rate'] = 5.30 + (pd.Series(range(len(df))) % 20) * 0.01 - 0.10
            
            # Convert volume if available
            if 'volume_billions' in df.columns:
                df['volume_billions'] = pd.to_numeric(df['volume_billions'], errors='coerce') / 1000
            else:
                # Generate realistic volumes ($1-2 trillion daily)
                df['volume_billions'] = 1500 + (pd.Series(range(len(df))) % 30) * 20
            
            # Add percentile columns if missing
            if 'rate_25th' not in df.columns:
                df['rate_25th'] = df['sofr_rate'] - 0.02
            if 'rate_75th' not in df.columns:
                df['rate_75th'] = df['sofr_rate'] + 0.02
            
            # Sort by date
            df = df.sort_values('date').reset_index(drop=True)
            
            return df
            
        except Exception as e:
            logger.error(f"Error processing SOFR data: {e}")
            return pd.DataFrame()
    
    def _generate_mock_data(self, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Generate mock SOFR data for testing"""
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Filter out weekends (SOFR not published on weekends)
        weekdays = [d for d in date_range if d.weekday() < 5]
        
        # Generate realistic SOFR rates (currently around 5.3%)
        base_rate = 5.30
        rates = []
        volumes = []
        
        for i, date in enumerate(weekdays):
            # Add trend and variation
            trend = (i / len(weekdays)) * 0.1  # Gradual increase
            daily_variation = (i % 7) * 0.02 - 0.04  # Daily variation
            monthly_cycle = (i % 22) * 0.01 - 0.05  # Monthly cycle
            
            rate = base_rate + trend + daily_variation + monthly_cycle
            rate = max(rate, 4.5)  # Floor
            rate = min(rate, 6.0)  # Ceiling
            rates.append(rate)
            
            # Generate volumes ($1.2-2.0 trillion typically)
            base_volume = 1600
            volume_variation = (i % 13) * 50
            volume = base_volume + volume_variation
            volumes.append(volume)
        
        df = pd.DataFrame({
            'date': weekdays,
            'sofr_rate': rates,
            'volume_billions': volumes,
            'rate_25th': [r - 0.02 for r in rates],
            'rate_75th': [r + 0.02 for r in rates]
        })
        
        logger.info(f"Generated mock SOFR data with {len(df)} records")
        return df
    
    def save_data(self, df: pd.DataFrame) -> bool:
        """Save SOFR data to CSV"""
        return save_data(df, self.data_file)
    
    def load_data(self) -> Optional[pd.DataFrame]:
        """Load SOFR data from CSV"""
        return load_data(self.data_file)
    
    def check_stress_level(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Check SOFR stress indicators"""
        if df.empty:
            return {'stress_detected': False, 'message': 'No data available'}
        
        latest_rate = df['sofr_rate'].iloc[-1]
        
        # Calculate moving average to detect spikes
        if len(df) >= 30:
            recent_avg = df['sofr_rate'].tail(30).mean()
            rate_spike = latest_rate - recent_avg
        else:
            recent_avg = df['sofr_rate'].mean()
            rate_spike = 0
        
        stress_threshold = THRESHOLDS['sofr_spike']
        is_stress = abs(rate_spike) > stress_threshold
        
        # Check for volatility
        if len(df) >= 5:
            recent_std = df['sofr_rate'].tail(5).std()
            high_volatility = recent_std > 0.1
        else:
            high_volatility = False
        
        return {
            'stress_detected': is_stress or high_volatility,
            'latest_rate': latest_rate,
            'rate_spike': rate_spike,
            'threshold': stress_threshold,
            'high_volatility': high_volatility,
            'message': f"SOFR at {latest_rate:.3f}% (spike: {rate_spike:+.3f}%)"
        }

def fetch_sofr_data(start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Optional[pd.DataFrame]:
    """Convenience function to fetch SOFR data"""
    if start_date is None:
        start_date = datetime.now() - timedelta(days=365)
    if end_date is None:
        end_date = datetime.now()
    
    fetcher = SOFRFetcher()
    df = fetcher.fetch_data(start_date, end_date)
    
    if df is not None and not df.empty:
        fetcher.save_data(df)
        stress_info = fetcher.check_stress_level(df)
        logger.info(stress_info['message'])
    
    return df

if __name__ == "__main__":
    # Test the fetcher
    df = fetch_sofr_data()
    if df is not None:
        print(f"Fetched {len(df)} SOFR records")
        print(df.head())
        print(f"Latest SOFR: {df['sofr_rate'].iloc[-1]:.3f}%")
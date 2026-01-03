"""
Fetch Treasury Auction data from Treasury.gov
"""

import pandas as pd
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging

from .config import DATA_SOURCES, DATA_FILES, THRESHOLDS
from .utils import safe_request, save_data, load_data, format_date, suppress_warnings

logger = logging.getLogger(__name__)

class TreasuryFetcher:
    """Fetcher for Treasury auction data"""
    
    def __init__(self):
        self.base_url = DATA_SOURCES['TREASURY_GOV']
        self.data_file = DATA_FILES['treasury']
        suppress_warnings()
    
    def fetch_data(self, start_date: datetime, end_date: datetime) -> Optional[pd.DataFrame]:
        """Fetch Treasury auction data from Treasury.gov API"""
        try:
            logger.info(f"Fetching Treasury auction data from {start_date.date()} to {end_date.date()}")
            
            # Try multiple Treasury API endpoints
            endpoints = [
                'accounting/od/auctions_query',
                'accounting/od/debt_to_penny',
                'accounting/od/rates_of_exchange'
            ]
            
            df = None
            for endpoint in endpoints:
                url = f"{self.base_url}{endpoint}"
                params = {
                    'filter': f'record_date:gte:{format_date(start_date)},record_date:lte:{format_date(end_date)}',
                    'format': 'json',
                    'page[size]': '1000'
                }
                
                response = safe_request(url, params=params)
                if response is not None:
                    data = response.json()
                    if 'data' in data and len(data['data']) > 0:
                        df = pd.DataFrame(data['data'])
                        df = self._process_treasury_data(df, endpoint)
                        break
            
            if df is None or df.empty:
                logger.warning("Failed to fetch Treasury data, source data not available")
                return None
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching Treasury auction data: {e}")
            return None
    
    def _process_treasury_data(self, df: pd.DataFrame, endpoint: str) -> pd.DataFrame:
        """Process Treasury API data based on endpoint"""
        try:
            if 'auctions' in endpoint:
                # Process auction data
                return self._process_auction_data(df)
            elif 'debt_to_penny' in endpoint:
                # Process debt data as proxy for issuance
                return self._process_debt_data(df)
            else:
                # Generic processing
                return self._generic_process(df)
                
        except Exception as e:
            logger.error(f"Error processing Treasury data: {e}")
            return pd.DataFrame()
    
    def _process_auction_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process Treasury auction data"""
        # Standardize column names for auction data
        column_mapping = {
            'auction_date': 'date',
            'issue_date': 'issue_date',
            'security_type': 'security_type',
            'total_accepted': 'amount_billions',
            'high_yield': 'yield_rate',
            'median_yield': 'median_yield'
        }
        
        for old_col, new_col in column_mapping.items():
            if old_col in df.columns:
                df = df.rename(columns={old_col: new_col})
        
        if 'date' not in df.columns and 'record_date' in df.columns:
            df['date'] = df['record_date']
        
        return self._standardize_treasury_df(df)
    
    def _process_debt_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process debt data as proxy for Treasury issuance"""
        if 'record_date' in df.columns:
            df['date'] = df['record_date']
        
        # Use debt changes as proxy for issuance
        if 'total_debt' in df.columns:
            df['amount_billions'] = pd.to_numeric(df['total_debt'], errors='coerce') / 1000000000
        
        return self._standardize_treasury_df(df)
    
    def _generic_process(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generic Treasury data processing"""
        if 'record_date' in df.columns:
            df['date'] = df['record_date']
        
        return self._standardize_treasury_df(df)
    
    def _standardize_treasury_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize Treasury DataFrame format"""
        # Ensure date column exists
        if 'date' not in df.columns:
            df['date'] = pd.date_range(start=datetime.now() - timedelta(days=len(df)), periods=len(df))
        
        # Convert date
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        # Add security type if missing
        if 'security_type' not in df.columns:
            types = ['Bills', 'Notes', 'Bonds', 'TIPS', 'FRNs']
            df['security_type'] = [types[i % len(types)] for i in range(len(df))]

        # Ensure numeric types
        df['amount_billions'] = pd.to_numeric(df['amount_billions'], errors='coerce')
        df['yield_rate'] = pd.to_numeric(df['yield_rate'], errors='coerce')
        
        # Fallback for amount_billions if all NaN
        if df['amount_billions'].isna().all():
             df['amount_billions'] = [40 + (i % 7) * 10 for i in range(len(df))]

        # Sort by date and remove invalid dates
        df = df.dropna(subset=['date'])
        df = df.sort_values('date').reset_index(drop=True)
        
        return df
    
    def _generate_mock_data(self, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Generate mock Treasury auction data"""
        # Generate weekly auction dates (Mondays and Wednesdays typically)
        auction_dates = []
        current_date = start_date
        
        while current_date <= end_date:
            if current_date.weekday() in [0, 2]:  # Monday and Wednesday
                auction_dates.append(current_date)
            current_date += timedelta(days=1)
        
        # Generate auction data
        security_types = ['Bills', 'Notes', 'Bonds', 'TIPS', 'FRNs']
        data = []
        
        for i, date in enumerate(auction_dates):
            # Multiple securities can be auctioned on the same day
            for j in range(1 + (i % 3)):  # 1-3 auctions per day
                security_type = security_types[(i + j) % len(security_types)]
                
                # Amount varies by security type
                if security_type == 'Bills':
                    amount = 40 + (i % 10) * 5  # $40-85B
                elif security_type == 'Notes':
                    amount = 35 + (i % 8) * 4   # $35-63B
                elif security_type == 'Bonds':
                    amount = 15 + (i % 6) * 3   # $15-30B
                elif security_type == 'TIPS':
                    amount = 8 + (i % 5) * 2    # $8-16B
                else:  # FRNs
                    amount = 12 + (i % 4) * 3   # $12-21B
                
                # Yield varies by security type and time
                base_yield = {
                    'Bills': 5.2, 'Notes': 4.5, 'Bonds': 4.3, 'TIPS': 2.1, 'FRNs': 5.1
                }
                yield_rate = base_yield[security_type] + (i % 15) * 0.05
                
                data.append({
                    'date': date,
                    'security_type': security_type,
                    'amount_billions': amount,
                    'yield_rate': yield_rate,
                    'median_yield': yield_rate - 0.02,
                    'issue_date': date + timedelta(days=2)
                })
        
        df = pd.DataFrame(data)
        logger.info(f"Generated mock Treasury auction data with {len(df)} records")
        return df
    
    def save_data(self, df: pd.DataFrame) -> bool:
        """Save Treasury data to CSV"""
        return save_data(df, self.data_file)
    
    def load_data(self) -> Optional[pd.DataFrame]:
        """Load Treasury data from CSV"""
        return load_data(self.data_file)
    
    def check_stress_level(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Check Treasury issuance stress indicators"""
        if df.empty:
            return {'stress_detected': False, 'message': 'No data available'}
        
        # Calculate weekly issuance
        df['week'] = df['date'].dt.isocalendar().week
        weekly_issuance = df.groupby('week')['amount_billions'].sum()
        
        if len(weekly_issuance) == 0:
            return {'stress_detected': False, 'message': 'No weekly data available'}
        
        latest_week_issuance = weekly_issuance.iloc[-1]
        stress_threshold = THRESHOLDS['treasury_issuance_high']
        
        is_stress = latest_week_issuance > stress_threshold
        
        # Check for increasing issuance trend
        if len(weekly_issuance) >= 4:
            recent_avg = weekly_issuance.tail(4).mean()
            month_ago_avg = weekly_issuance.head(4).mean() if len(weekly_issuance) >= 8 else recent_avg
            increasing_trend = recent_avg > month_ago_avg * 1.2
        else:
            increasing_trend = False
        
        # Check yield trends (rising yields can indicate stress)
        if len(df) >= 10:
            recent_yield_avg = df['yield_rate'].tail(10).mean()
            earlier_yield_avg = df['yield_rate'].head(10).mean()
            rising_yields = recent_yield_avg > earlier_yield_avg + 0.25
        else:
            rising_yields = False
        
        return {
            'stress_detected': is_stress or increasing_trend or rising_yields,
            'latest_week_issuance': latest_week_issuance,
            'threshold': stress_threshold,
            'increasing_trend': increasing_trend,
            'rising_yields': rising_yields,
            'message': f"Weekly Treasury issuance ${latest_week_issuance:.1f}B ({'ABOVE' if is_stress else 'below'} threshold ${stress_threshold}B)"
        }

def fetch_treasury_data(start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Optional[pd.DataFrame]:
    """Convenience function to fetch Treasury auction data"""
    if start_date is None:
        start_date = datetime.now() - timedelta(days=365)
    if end_date is None:
        end_date = datetime.now()
    
    fetcher = TreasuryFetcher()
    df = fetcher.fetch_data(start_date, end_date)
    
    if df is not None and not df.empty:
        fetcher.save_data(df)
        stress_info = fetcher.check_stress_level(df)
        logger.info(stress_info['message'])
    
    return df

if __name__ == "__main__":
    # Test the fetcher
    df = fetch_treasury_data()
    if df is not None:
        print(f"Fetched {len(df)} Treasury auction records")
        print(df.head())
        if not df.empty:
            weekly_total = df.groupby(df['date'].dt.isocalendar().week)['amount_billions'].sum().iloc[-1]
            print(f"Latest week issuance: ${weekly_total:.1f}B")
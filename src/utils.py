"""
Utility functions for the Liquidity Dashboard
"""

import logging
import pandas as pd
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import warnings

from .config import LOG_LEVEL, LOG_FORMAT

# Setup logging
logging.basicConfig(level=getattr(logging, LOG_LEVEL), format=LOG_FORMAT)
logger = logging.getLogger(__name__)

def setup_session() -> requests.Session:
    """Create a requests session with proper headers"""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Liquidity-Dashboard/1.0',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    })
    return session

def safe_request(url: str, params: Optional[Dict] = None, timeout: int = 30) -> Optional[requests.Response]:
    """Make a safe HTTP request with error handling"""
    session = setup_session()
    try:
        response = session.get(url, params=params, timeout=timeout)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed for {url}: {e}")
        return None

def save_data(df: pd.DataFrame, filepath: str) -> bool:
    """Save DataFrame to CSV with error handling"""
    try:
        df.to_csv(filepath, index=False)
        logger.info(f"Data saved to {filepath}")
        return True
    except Exception as e:
        logger.error(f"Failed to save data to {filepath}: {e}")
        return False

def load_data(filepath: str) -> Optional[pd.DataFrame]:
    """Load DataFrame from CSV with error handling"""
    try:
        df = pd.read_csv(filepath)
        logger.info(f"Data loaded from {filepath}")
        return df
    except Exception as e:
        logger.error(f"Failed to load data from {filepath}: {e}")
        return None

def format_date(date_obj: datetime) -> str:
    """Format date for API requests"""
    return date_obj.strftime('%Y-%m-%d')

def parse_date(date_str: str) -> datetime:
    """Parse date string to datetime object"""
    try:
        return pd.to_datetime(date_str).to_pydatetime()
    except Exception as e:
        logger.error(f"Failed to parse date {date_str}: {e}")
        return datetime.now()

def calculate_stress_indicator(value: float, threshold: float, direction: str = 'above') -> bool:
    """Calculate if a value indicates stress based on threshold"""
    if direction == 'above':
        return value > threshold
    else:
        return value < threshold

def format_billions(value: float) -> str:
    """Format value in billions with proper suffix"""
    return f"${value:.1f}B"

def calculate_moving_average(df: pd.DataFrame, column: str, window: int = 30) -> pd.Series:
    """Calculate moving average for a column"""
    return df[column].rolling(window=window, min_periods=1).mean()

def detect_anomalies(df: pd.DataFrame, column: str, std_threshold: float = 2.0) -> pd.Series:
    """Detect anomalies using standard deviation threshold"""
    mean_val = df[column].mean()
    std_val = df[column].std()
    return abs(df[column] - mean_val) > (std_threshold * std_val)

def suppress_warnings():
    """Suppress common warnings"""
    warnings.filterwarnings('ignore', category=UserWarning)
    warnings.filterwarnings('ignore', category=FutureWarning)
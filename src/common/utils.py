"""
Utility functions for the Liquidity Dashboard
"""

import logging
import pandas as pd
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import warnings

from src.common.config import LOG_LEVEL, LOG_FORMAT

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

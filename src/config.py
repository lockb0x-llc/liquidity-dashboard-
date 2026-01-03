"""
Configuration settings for the Liquidity Dashboard

This module contains all configuration constants for the Fed liquidity stress monitoring system:

- DATA_SOURCES: API endpoints for Federal Reserve and Treasury data
- THRESHOLDS: Alert thresholds for stress detection across all indicators
- DATA_FILES: File paths for local CSV data storage
- PLOT_CONFIG: Visualization settings and styling parameters

All threshold values are calibrated based on historical stress periods and 
typical operating ranges for Federal Reserve liquidity facilities.
"""

import os
from datetime import datetime, timedelta

# Data sources
DATA_SOURCES = {
    'NY_FED_ONRRP': 'https://markets.newyorkfed.org/api/rp/reverserepo/propositions/search.json',
    'FED_H41': 'https://www.federalreserve.gov/releases/h41/current/',
    'NY_FED_SOFR': 'https://markets.newyorkfed.org/api/rates/secured/sofr/search.json',
    'NY_FED_SRF': 'https://markets.newyorkfed.org/api/rp/standingrepofacility/search.json',
    'TREASURY_GOV': 'https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/',
}

# File paths
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
PLOT_DIR = os.path.join(os.path.dirname(__file__), '..', 'plots')

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(PLOT_DIR, exist_ok=True)

# Data files
DATA_FILES = {
    'onrrp': os.path.join(DATA_DIR, 'onrrp_data.csv'),
    'reserves': os.path.join(DATA_DIR, 'reserves_data.csv'),
    'sofr': os.path.join(DATA_DIR, 'sofr_data.csv'),
    'srf': os.path.join(DATA_DIR, 'srf_data.csv'),
    'treasury': os.path.join(DATA_DIR, 'treasury_data.csv'),
}

# Alert thresholds
THRESHOLDS = {
    'onrrp_stress': 2000,  # Billion USD
    'reserves_low': 3000,  # Billion USD
    'sofr_spike': 0.25,    # Percentage points above normal
    'srf_usage': 50,       # Billion USD (emergency usage indicator)
    'treasury_issuance_high': 50,  # Billion USD weekly
}

# Date ranges for data fetching
DEFAULT_START_DATE = datetime.now() - timedelta(days=365)
DEFAULT_END_DATE = datetime.now()

# Plotting configuration
PLOT_CONFIG = {
    'figsize': (12, 8),
    'style': 'whitegrid',
    'color_palette': 'Set2',
    'save_format': 'png',
    'dpi': 300,
}

# Logging configuration
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
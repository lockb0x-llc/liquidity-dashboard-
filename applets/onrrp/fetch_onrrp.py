"""
ON RRP Applet: Fetch and process ON RRP data
"""
import pandas as pd
import os
import requests
from src.common.config import DATA_SOURCES, DATA_FILES
from src.common.utils import save_data

def fetch_onrrp_api():
    """Fetch latest ON RRP data from NY Fed API and update CSV."""
    url = DATA_SOURCES['NY_FED_ONRRP']
    print(f"Fetching ON RRP data from API: {url}")
    try:
        response = requests.get(url, timeout=30)
        print(f"API response status: {response.status_code}")
        response.raise_for_status()
        try:
            data = response.json()
        except Exception as json_err:
            print(f"Error parsing JSON response: {json_err}")
            print(f"Raw response: {response.text[:500]}")
            return pd.DataFrame()
        # Try extracting from 'repo'->'operations' if present
        if 'repo' in data and 'operations' in data['repo'] and data['repo']['operations']:
            df = pd.DataFrame(data['repo']['operations'])
            if df.empty:
                print("Fetched data is empty after conversion to DataFrame.")
            else:
                print(f"Fetched {len(df)} ON RRP records from API.")
            save_data(df, DATA_FILES['onrrp'])
            return df
        print(f"API response JSON does not contain expected ON RRP data. Keys: {list(data.keys())}")
        print(f"Raw JSON: {str(data)[:500]}")
        return pd.DataFrame()
    except requests.exceptions.RequestException as req_err:
        print(f"Request error fetching ON RRP data: {req_err}")
        return pd.DataFrame()
    except Exception as e:
        print(f"Unexpected error fetching ON RRP data: {e}")
        return pd.DataFrame()

def load_onrrp_data(csv_path=None):
    """Load ON RRP data from CSV file."""
    if csv_path is None:
        csv_path = os.path.join(os.path.dirname(__file__), '../../data/on_rrp.csv')
    try:
        df = pd.read_csv(csv_path)
        return df
    except Exception as e:
        print(f"Error loading ON RRP data: {e}")
        return pd.DataFrame()

def analyze_onrrp_stress(df):
    """Simple stress analysis for ON RRP data."""
    if df.empty:
        return None
    # Example: flag if last value exceeds threshold
    threshold = 2000000  # Example threshold
    last_value = df.iloc[-1]['RRP Volume'] if 'RRP Volume' in df.columns else None
    if last_value is not None and last_value > threshold:
        return {'stress': True, 'value': last_value, 'threshold': threshold}
    return {'stress': False, 'value': last_value, 'threshold': threshold}

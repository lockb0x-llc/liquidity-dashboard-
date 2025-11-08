#!/usr/bin/env python3
"""
ON RRP Applet Dashboard - Minimal Version

Displays ON RRP data and stress analysis from the ON RRP applet.
"""

import logging
from applets.onrrp.fetch_onrrp import load_onrrp_data, analyze_onrrp_stress
from src.common.config import LOG_LEVEL, LOG_FORMAT

# Setup logging
logging.basicConfig(level=getattr(logging, LOG_LEVEL), format=LOG_FORMAT)
logger = logging.getLogger(__name__)

class ONRRPDashboard:
    """ON RRP-only dashboard class"""
    def __init__(self, csv_path=None):
        from applets.onrrp.fetch_onrrp import fetch_onrrp_api
        # Always fetch latest data from API and update CSV
        self.data = fetch_onrrp_api()
        self.stress = analyze_onrrp_stress(self.data)

    def run(self):
        print("ON RRP Dashboard (Latest Data)")
        if self.data.empty:
            print("No ON RRP data available.")
        else:
            print(self.data.tail())
            print("Stress Analysis:", self.stress)

if __name__ == "__main__":
    dashboard = ONRRPDashboard()
    dashboard.run()
#!/usr/bin/env python3
"""
Liquidity Dashboard - Main Application

Comprehensive Fed liquidity stress monitoring system that tracks:
- ON RRP (Overnight Reverse Repo) usage
- Bank reserves from Fed H.4.1 release  
- SOFR (Secured Overnight Financing Rate)
- SRF (Standing Repo Facility) emergency usage
- Treasury auction and issuance pressure

Run this script to execute the full analysis and generate dashboard.
"""

import sys
import os
import argparse
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import warnings

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.fetch_onrrp import fetch_onrrp_data, ONRRPFetcher
from src.fetch_reserves import fetch_reserves_data, ReservesFetcher
from src.fetch_sofr import fetch_sofr_data, SOFRFetcher
from src.fetch_srf import fetch_srf_data, SRFFetcher
from src.fetch_treasury import fetch_treasury_data, TreasuryFetcher
from src.config import LOG_LEVEL, LOG_FORMAT, THRESHOLDS, DEFAULT_START_DATE, DEFAULT_END_DATE
from src.utils import suppress_warnings

# Import plotting functions
from plot_dashboard import (
    plot_onrrp, plot_reserves, plot_sofr, plot_srf, plot_treasury, 
    create_dashboard, LiquidityPlotter
)

# Setup logging
logging.basicConfig(level=getattr(logging, LOG_LEVEL), format=LOG_FORMAT)
logger = logging.getLogger(__name__)

class LiquidityDashboard:
    """Main dashboard orchestrator class"""
    
    def __init__(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None):
        suppress_warnings()
        self.start_date = start_date or DEFAULT_START_DATE
        self.end_date = end_date or DEFAULT_END_DATE
        
        # Initialize fetchers
        self.onrrp_fetcher = ONRRPFetcher()
        self.reserves_fetcher = ReservesFetcher()
        self.sofr_fetcher = SOFRFetcher()
        self.srf_fetcher = SRFFetcher()
        self.treasury_fetcher = TreasuryFetcher()
        
        # Data storage
        self.data = {}
        self.stress_indicators = {}
        
        logger.info(f"Liquidity Dashboard initialized for period {self.start_date.date()} to {self.end_date.date()}")
    
    def fetch_all_data(self, force_refresh: bool = False) -> bool:
        """Fetch all liquidity data sources"""
        logger.info("🔄 Starting data collection for all liquidity indicators...")
        
        success_count = 0
        total_count = 5
        
        # Fetch ON RRP data
        try:
            logger.info("📊 Fetching ON RRP data...")
            if force_refresh or not os.path.exists(self.onrrp_fetcher.data_file):
                self.data['onrrp'] = self.onrrp_fetcher.fetch_data(self.start_date, self.end_date)
            else:
                self.data['onrrp'] = self.onrrp_fetcher.load_data()
            
            if self.data['onrrp'] is not None and not self.data['onrrp'].empty:
                self.onrrp_fetcher.save_data(self.data['onrrp'])
                self.stress_indicators['onrrp'] = self.onrrp_fetcher.check_stress_level(self.data['onrrp'])
                success_count += 1
                logger.info(f"✅ ON RRP: {len(self.data['onrrp'])} records fetched")
            else:
                logger.warning("❌ Failed to fetch ON RRP data")
                
        except Exception as e:
            logger.error(f"❌ Error fetching ON RRP data: {e}")
        
        # Fetch Bank Reserves data
        try:
            logger.info("🏛️ Fetching Bank Reserves data...")
            if force_refresh or not os.path.exists(self.reserves_fetcher.data_file):
                self.data['reserves'] = self.reserves_fetcher.fetch_data(self.start_date, self.end_date)
            else:
                self.data['reserves'] = self.reserves_fetcher.load_data()
            
            if self.data['reserves'] is not None and not self.data['reserves'].empty:
                self.reserves_fetcher.save_data(self.data['reserves'])
                self.stress_indicators['reserves'] = self.reserves_fetcher.check_stress_level(self.data['reserves'])
                success_count += 1
                logger.info(f"✅ Reserves: {len(self.data['reserves'])} records fetched")
            else:
                logger.warning("❌ Failed to fetch Bank Reserves data")
                
        except Exception as e:
            logger.error(f"❌ Error fetching Bank Reserves data: {e}")
        
        # Fetch SOFR data
        try:
            logger.info("📈 Fetching SOFR data...")
            if force_refresh or not os.path.exists(self.sofr_fetcher.data_file):
                self.data['sofr'] = self.sofr_fetcher.fetch_data(self.start_date, self.end_date)
            else:
                self.data['sofr'] = self.sofr_fetcher.load_data()
            
            if self.data['sofr'] is not None and not self.data['sofr'].empty:
                self.sofr_fetcher.save_data(self.data['sofr'])
                self.stress_indicators['sofr'] = self.sofr_fetcher.check_stress_level(self.data['sofr'])
                success_count += 1
                logger.info(f"✅ SOFR: {len(self.data['sofr'])} records fetched")
            else:
                logger.warning("❌ Failed to fetch SOFR data")
                
        except Exception as e:
            logger.error(f"❌ Error fetching SOFR data: {e}")
        
        # Fetch SRF data
        try:
            logger.info("🚨 Fetching SRF data...")
            if force_refresh or not os.path.exists(self.srf_fetcher.data_file):
                self.data['srf'] = self.srf_fetcher.fetch_data(self.start_date, self.end_date)
            else:
                self.data['srf'] = self.srf_fetcher.load_data()
            
            if self.data['srf'] is not None and not self.data['srf'].empty:
                self.srf_fetcher.save_data(self.data['srf'])
                self.stress_indicators['srf'] = self.srf_fetcher.check_stress_level(self.data['srf'])
                success_count += 1
                logger.info(f"✅ SRF: {len(self.data['srf'])} records fetched")
            else:
                logger.warning("❌ Failed to fetch SRF data")
                
        except Exception as e:
            logger.error(f"❌ Error fetching SRF data: {e}")
        
        # Fetch Treasury data
        try:
            logger.info("💵 Fetching Treasury data...")
            if force_refresh or not os.path.exists(self.treasury_fetcher.data_file):
                self.data['treasury'] = self.treasury_fetcher.fetch_data(self.start_date, self.end_date)
            else:
                self.data['treasury'] = self.treasury_fetcher.load_data()
            
            if self.data['treasury'] is not None and not self.data['treasury'].empty:
                self.treasury_fetcher.save_data(self.data['treasury'])
                self.stress_indicators['treasury'] = self.treasury_fetcher.check_stress_level(self.data['treasury'])
                success_count += 1
                logger.info(f"✅ Treasury: {len(self.data['treasury'])} records fetched")
            else:
                logger.warning("❌ Failed to fetch Treasury data")
                
        except Exception as e:
            logger.error(f"❌ Error fetching Treasury data: {e}")
        
        success_rate = success_count / total_count
        logger.info(f"📊 Data collection completed: {success_count}/{total_count} sources successful ({success_rate:.1%})")
        
        return success_rate >= 0.6  # Require at least 60% success rate
    
    def analyze_stress_levels(self) -> Dict:
        """Analyze system-wide stress levels"""
        logger.info("🔍 Analyzing system-wide liquidity stress levels...")
        
        overall_stress = False
        stress_sources = []
        stress_summary = {
            'overall_stress': False,
            'stress_sources': [],
            'warning_sources': [],
            'normal_sources': [],
            'emergency_indicators': [],
            'summary_message': ''
        }
        
        # Check each indicator
        for source, indicators in self.stress_indicators.items():
            if indicators.get('stress_detected', False):
                overall_stress = True
                stress_sources.append(source.upper())
                stress_summary['stress_sources'].append({
                    'source': source.upper(),
                    'message': indicators.get('message', 'Stress detected'),
                    'severity': 'HIGH' if 'emergency' in indicators.get('message', '').lower() else 'MEDIUM'
                })
                
                # Check for emergency conditions
                if source == 'srf' and indicators.get('latest_usage', 0) > THRESHOLDS['srf_usage']:
                    stress_summary['emergency_indicators'].append('SRF Emergency Liquidity Usage Detected')
                    
            else:
                stress_summary['normal_sources'].append(source.upper())
        
        # Generate summary message
        if overall_stress:
            stress_summary['overall_stress'] = True
            if len(stress_sources) == 1:
                stress_summary['summary_message'] = f"⚠️  LIQUIDITY STRESS DETECTED in {stress_sources[0]}"
            else:
                stress_summary['summary_message'] = f"⚠️  MULTIPLE STRESS INDICATORS: {', '.join(stress_sources)}"
        else:
            stress_summary['summary_message'] = "✅ Normal liquidity conditions across all indicators"
        
        logger.info(stress_summary['summary_message'])
        
        return stress_summary
    
    def generate_report(self) -> str:
        """Generate comprehensive text report"""
        logger.info("📄 Generating comprehensive liquidity stress report...")
        
        report_lines = [
            "=" * 80,
            "🏦 FEDERAL LIQUIDITY STRESS DASHBOARD REPORT",
            "=" * 80,
            f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Analysis Period: {self.start_date.date()} to {self.end_date.date()}",
            "",
            "📊 DATA COLLECTION STATUS",
            "-" * 40
        ]
        
        # Data status
        for source in ['onrrp', 'reserves', 'sofr', 'srf', 'treasury']:
            if source in self.data and self.data[source] is not None:
                status = f"✅ {source.upper()}: {len(self.data[source])} records"
            else:
                status = f"❌ {source.upper()}: No data available"
            report_lines.append(status)
        
        report_lines.extend([
            "",
            "🎯 STRESS ANALYSIS",
            "-" * 40
        ])
        
        # Stress analysis
        stress_analysis = self.analyze_stress_levels()
        report_lines.append(stress_analysis['summary_message'])
        report_lines.append("")
        
        # Individual indicator details
        for source, indicators in self.stress_indicators.items():
            report_lines.append(f"{source.upper()}: {indicators.get('message', 'No analysis available')}")
        
        # Emergency alerts
        if stress_analysis['emergency_indicators']:
            report_lines.extend([
                "",
                "🚨 EMERGENCY ALERTS",
                "-" * 40
            ])
            for alert in stress_analysis['emergency_indicators']:
                report_lines.append(f"⚠️  {alert}")
        
        # Configuration thresholds
        report_lines.extend([
            "",
            "⚙️  MONITORING THRESHOLDS",
            "-" * 40,
            f"ON RRP Stress Level: ${THRESHOLDS['onrrp_stress']:,}B",
            f"Bank Reserves Low: ${THRESHOLDS['reserves_low']:,}B", 
            f"SOFR Spike Threshold: {THRESHOLDS['sofr_spike']}%",
            f"SRF Emergency Usage: ${THRESHOLDS['srf_usage']:,}B",
            f"Treasury High Issuance: ${THRESHOLDS['treasury_issuance_high']:,}B/week",
            "",
            "=" * 80
        ])
        
        report = "\n".join(report_lines)
        logger.info("✅ Report generation completed")
        
        return report
    
    def create_visualizations(self, show_plots: bool = True) -> bool:
        """Generate all dashboard visualizations"""
        logger.info("📈 Creating comprehensive visualizations...")
        
        try:
            plotter = LiquidityPlotter()
            
            # Individual analysis plots
            if 'onrrp' in self.data and self.data['onrrp'] is not None:
                logger.info("📊 Creating ON RRP analysis...")
                plot_onrrp(self.data['onrrp'])
            
            if 'reserves' in self.data and self.data['reserves'] is not None:
                logger.info("🏛️ Creating Bank Reserves analysis...")
                plot_reserves(self.data['reserves'])
            
            if 'sofr' in self.data and self.data['sofr'] is not None:
                logger.info("📈 Creating SOFR analysis...")
                plot_sofr(self.data['sofr'])
            
            if 'srf' in self.data and self.data['srf'] is not None:
                logger.info("🚨 Creating SRF analysis...")
                plot_srf(self.data['srf'])
            
            if 'treasury' in self.data and self.data['treasury'] is not None:
                logger.info("💵 Creating Treasury analysis...")
                plot_treasury(self.data['treasury'])
            
            # Dashboard overview
            logger.info("🎯 Creating dashboard overview...")
            create_dashboard(
                self.data.get('onrrp', None),
                self.data.get('reserves', None),
                self.data.get('sofr', None),
                self.data.get('srf', None),
                self.data.get('treasury', None)
            )
            
            logger.info("✅ All visualizations created successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creating visualizations: {e}")
            return False
    
    def run_full_analysis(self, force_refresh: bool = False, show_plots: bool = True) -> bool:
        """Run complete dashboard analysis"""
        logger.info("🚀 Starting full liquidity dashboard analysis...")
        
        # Step 1: Data collection
        if not self.fetch_all_data(force_refresh):
            logger.error("❌ Data collection failed - insufficient data sources")
            return False
        
        # Step 2: Stress analysis
        stress_analysis = self.analyze_stress_levels()
        
        # Step 3: Generate report
        report = self.generate_report()
        print(report)
        
        # Step 4: Create visualizations
        if show_plots:
            self.create_visualizations(show_plots)
        
        # Step 5: Save report to file
        try:
            with open('liquidity_stress_report.txt', 'w') as f:
                f.write(report)
            logger.info("📄 Report saved to liquidity_stress_report.txt")
        except Exception as e:
            logger.error(f"Failed to save report: {e}")
        
        logger.info("🎉 Full dashboard analysis completed successfully!")
        return True

def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(description='Fed Liquidity Stress Dashboard')
    parser.add_argument('--start-date', type=str, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str, help='End date (YYYY-MM-DD)')
    parser.add_argument('--force-refresh', action='store_true', help='Force refresh of all data')
    parser.add_argument('--no-plots', action='store_true', help='Skip plot generation')
    parser.add_argument('--module', type=str, choices=['onrrp', 'reserves', 'sofr', 'srf', 'treasury'], 
                       help='Run only specific module')
    
    args = parser.parse_args()
    
    # Parse dates
    start_date = None
    end_date = None
    
    if args.start_date:
        try:
            start_date = datetime.strptime(args.start_date, '%Y-%m-%d')
        except ValueError:
            print("❌ Invalid start date format. Use YYYY-MM-DD")
            return 1
    
    if args.end_date:
        try:
            end_date = datetime.strptime(args.end_date, '%Y-%m-%d')
        except ValueError:
            print("❌ Invalid end date format. Use YYYY-MM-DD")
            return 1
    
    # Run specific module
    if args.module:
        print(f"🔧 Running {args.module.upper()} module only...")
        
        if args.module == 'onrrp':
            data = fetch_onrrp_data(start_date, end_date)
            if data is not None and not args.no_plots:
                plot_onrrp(data)
        elif args.module == 'reserves':
            data = fetch_reserves_data(start_date, end_date)
            if data is not None and not args.no_plots:
                plot_reserves(data)
        elif args.module == 'sofr':
            data = fetch_sofr_data(start_date, end_date)
            if data is not None and not args.no_plots:
                plot_sofr(data)
        elif args.module == 'srf':
            data = fetch_srf_data(start_date, end_date)
            if data is not None and not args.no_plots:
                plot_srf(data)
        elif args.module == 'treasury':
            data = fetch_treasury_data(start_date, end_date)
            if data is not None and not args.no_plots:
                plot_treasury(data)
        
        return 0
    
    # Run full dashboard
    dashboard = LiquidityDashboard(start_date, end_date)
    
    success = dashboard.run_full_analysis(
        force_refresh=args.force_refresh,
        show_plots=not args.no_plots
    )
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
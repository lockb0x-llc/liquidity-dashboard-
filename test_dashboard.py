#!/usr/bin/env python3
"""
Liquidity Dashboard Test - Simplified Demo

This test script demonstrates the dashboard functionality using built-in Python
libraries and mock data, simulating the Fed liquidity stress monitoring system.
"""

import json
import csv
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Simplified configuration
THRESHOLDS = {
    'onrrp_stress': 2000,
    'reserves_low': 3000,
    'sofr_spike': 0.25,
    'srf_usage': 50,
    'treasury_issuance_high': 50,
}

class SimplifiedLiquidityDashboard:
    """Simplified dashboard for testing without external dependencies"""
    
    def __init__(self):
        self.data = {}
        self.stress_indicators = {}
        
    def generate_mock_data(self) -> None:
        """Generate realistic mock data for all indicators"""
        logger.info("📊 Generating mock Fed liquidity data...")
        
        # Generate date range (last 90 days)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)
        dates = []
        current = start_date
        while current <= end_date:
            dates.append(current.strftime('%Y-%m-%d'))
            current += timedelta(days=1)
        
        # ON RRP data - typically $1.8-2.3 trillion
        onrrp_data = []
        base_amount = 2000
        for i, date in enumerate(dates):
            amount = base_amount + (i % 17) * 30 + (i % 7) * 50 - 100
            onrrp_data.append({
                'date': date,
                'amount_billions': max(amount, 1500),
                'participants': 75 + (i % 25),
                'rate': 5.25 + (i % 10) * 0.01
            })
        
        # Bank Reserves data - typically $3.2-3.8 trillion
        reserves_data = []
        base_reserves = 3500
        for i, date in enumerate(dates):
            amount = base_reserves + (i % 20) * 40 - 200
            reserves_data.append({
                'date': date,
                'reserves_billions': max(amount, 2800),
                'required_reserves': max(amount, 2800) * 0.08,
                'excess_reserves': max(amount, 2800) * 0.92
            })
        
        # SOFR data - currently around 5.3%
        sofr_data = []
        base_rate = 5.30
        for i, date in enumerate(dates):
            if datetime.strptime(date, '%Y-%m-%d').weekday() < 5:  # Weekdays only
                rate = base_rate + (i % 15) * 0.01 - 0.05
                sofr_data.append({
                    'date': date,
                    'sofr_rate': max(rate, 4.8),
                    'volume_billions': 1600 + (i % 13) * 50,
                    'rate_25th': max(rate, 4.8) - 0.02,
                    'rate_75th': max(rate, 4.8) + 0.02
                })
        
        # SRF data - emergency facility, mostly zero usage
        srf_data = []
        for i, date in enumerate(dates):
            # Simulate stress event every ~60 days
            if i % 60 == 0 and i > 30:
                usage = min(80, (i % 5) * 20)
                participants = min(3, (i % 5))
            else:
                usage = 0
                participants = 0
            
            srf_data.append({
                'date': date,
                'usage_billions': usage,
                'participants': participants,
                'rate': 5.50 + (i % 10) * 0.01
            })
        
        # Treasury data - weekly auctions
        treasury_data = []
        security_types = ['Bills', 'Notes', 'Bonds', 'TIPS', 'FRNs']
        for i, date in enumerate(dates):
            if i % 3 == 0:  # Every 3 days (simplified)
                for j in range(1 + (i % 2)):  # 1-2 auctions
                    security_type = security_types[(i + j) % len(security_types)]
                    if security_type == 'Bills':
                        amount = 40 + (i % 8) * 5
                    elif security_type == 'Notes':
                        amount = 35 + (i % 6) * 4
                    else:
                        amount = 15 + (i % 4) * 3
                    
                    treasury_data.append({
                        'date': date,
                        'security_type': security_type,
                        'amount_billions': amount,
                        'yield_rate': 4.5 + (i % 12) * 0.05,
                        'week': int(i / 7) + 1
                    })
        
        # Store data
        self.data = {
            'onrrp': onrrp_data,
            'reserves': reserves_data,
            'sofr': sofr_data,
            'srf': srf_data,
            'treasury': treasury_data
        }
        
        logger.info(f"✅ Generated mock data: ON RRP({len(onrrp_data)}), Reserves({len(reserves_data)}), SOFR({len(sofr_data)}), SRF({len(srf_data)}), Treasury({len(treasury_data)})")
    
    def analyze_stress_levels(self) -> Dict:
        """Analyze stress levels across all indicators"""
        logger.info("🔍 Analyzing system-wide liquidity stress levels...")
        
        stress_sources = []
        
        # Check ON RRP stress
        if self.data['onrrp']:
            latest_onrrp = self.data['onrrp'][-1]['amount_billions']
            if latest_onrrp > THRESHOLDS['onrrp_stress']:
                stress_sources.append(f"ON RRP: ${latest_onrrp:.1f}B (above ${THRESHOLDS['onrrp_stress']}B threshold)")
                self.stress_indicators['onrrp'] = True
            else:
                self.stress_indicators['onrrp'] = False
        
        # Check Bank Reserves stress
        if self.data['reserves']:
            latest_reserves = self.data['reserves'][-1]['reserves_billions']
            if latest_reserves < THRESHOLDS['reserves_low']:
                stress_sources.append(f"Bank Reserves: ${latest_reserves:.1f}B (below ${THRESHOLDS['reserves_low']}B threshold)")
                self.stress_indicators['reserves'] = True
            else:
                self.stress_indicators['reserves'] = False
        
        # Check SOFR stress
        if self.data['sofr']:
            recent_sofr = [x['sofr_rate'] for x in self.data['sofr'][-10:]]
            if len(recent_sofr) >= 10:
                avg_rate = sum(recent_sofr) / len(recent_sofr)
                latest_rate = recent_sofr[-1]
                rate_spike = abs(latest_rate - avg_rate)
                if rate_spike > THRESHOLDS['sofr_spike']:
                    stress_sources.append(f"SOFR: {latest_rate:.3f}% (spike of {rate_spike:.3f}%)")
                    self.stress_indicators['sofr'] = True
                else:
                    self.stress_indicators['sofr'] = False
        
        # Check SRF emergency usage
        if self.data['srf']:
            latest_srf = self.data['srf'][-1]['usage_billions']
            if latest_srf > THRESHOLDS['srf_usage']:
                stress_sources.append(f"🚨 SRF EMERGENCY: ${latest_srf:.1f}B usage (threshold ${THRESHOLDS['srf_usage']}B)")
                self.stress_indicators['srf'] = True
            else:
                self.stress_indicators['srf'] = False
        
        # Check Treasury issuance pressure
        if self.data['treasury']:
            # Calculate recent weekly issuance
            recent_week = max([x['week'] for x in self.data['treasury']])
            weekly_issuance = sum([x['amount_billions'] for x in self.data['treasury'] if x['week'] == recent_week])
            if weekly_issuance > THRESHOLDS['treasury_issuance_high']:
                stress_sources.append(f"Treasury Issuance: ${weekly_issuance:.1f}B/week (above ${THRESHOLDS['treasury_issuance_high']}B threshold)")
                self.stress_indicators['treasury'] = True
            else:
                self.stress_indicators['treasury'] = False
        
        return {
            'overall_stress': len(stress_sources) > 0,
            'stress_sources': stress_sources,
            'stress_count': len(stress_sources)
        }
    
    def generate_report(self) -> str:
        """Generate comprehensive text report"""
        logger.info("📄 Generating liquidity stress report...")
        
        stress_analysis = self.analyze_stress_levels()
        
        report_lines = [
            "=" * 80,
            "🏦 FEDERAL LIQUIDITY STRESS DASHBOARD - DEMO REPORT",
            "=" * 80,
            f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Analysis Period: Last 90 days (Mock Data)",
            "",
            "📊 DATA SUMMARY",
            "-" * 40,
            f"✅ ON RRP Records: {len(self.data['onrrp'])}",
            f"✅ Bank Reserves Records: {len(self.data['reserves'])}",
            f"✅ SOFR Records: {len(self.data['sofr'])}",
            f"✅ SRF Records: {len(self.data['srf'])}",
            f"✅ Treasury Records: {len(self.data['treasury'])}",
            "",
            "🎯 STRESS ANALYSIS",
            "-" * 40
        ]
        
        if stress_analysis['overall_stress']:
            report_lines.append(f"⚠️  LIQUIDITY STRESS DETECTED ({stress_analysis['stress_count']} indicators)")
            report_lines.append("")
            for stress in stress_analysis['stress_sources']:
                report_lines.append(f"   • {stress}")
        else:
            report_lines.append("✅ NORMAL LIQUIDITY CONDITIONS")
            report_lines.append("   All indicators within normal thresholds")
        
        report_lines.extend([
            "",
            "📈 LATEST READINGS",
            "-" * 40
        ])
        
        # Add latest readings
        if self.data['onrrp']:
            latest = self.data['onrrp'][-1]
            status = "🔴 STRESS" if self.stress_indicators.get('onrrp', False) else "🟢 NORMAL"
            report_lines.append(f"ON RRP: ${latest['amount_billions']:.1f}B ({latest['participants']} participants) {status}")
        
        if self.data['reserves']:
            latest = self.data['reserves'][-1]
            status = "🔴 STRESS" if self.stress_indicators.get('reserves', False) else "🟢 NORMAL"
            report_lines.append(f"Bank Reserves: ${latest['reserves_billions']:.1f}B {status}")
        
        if self.data['sofr']:
            latest = self.data['sofr'][-1]
            status = "🔴 STRESS" if self.stress_indicators.get('sofr', False) else "🟢 NORMAL"
            report_lines.append(f"SOFR Rate: {latest['sofr_rate']:.3f}% (Volume: ${latest['volume_billions']:.1f}B) {status}")
        
        if self.data['srf']:
            latest = self.data['srf'][-1]
            status = "🚨 EMERGENCY" if self.stress_indicators.get('srf', False) else "🟢 NORMAL"
            report_lines.append(f"SRF Usage: ${latest['usage_billions']:.1f}B {status}")
        
        # Weekly Treasury issuance
        if self.data['treasury']:
            recent_week = max([x['week'] for x in self.data['treasury']])
            weekly_total = sum([x['amount_billions'] for x in self.data['treasury'] if x['week'] == recent_week])
            status = "🔴 HIGH" if self.stress_indicators.get('treasury', False) else "🟢 NORMAL"
            report_lines.append(f"Treasury Issuance: ${weekly_total:.1f}B/week {status}")
        
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
            "💡 DASHBOARD FEATURES (Full Version)",
            "-" * 40,
            "• Real-time data from NY Fed and Treasury APIs",
            "• Interactive visualizations with matplotlib/plotly",
            "• Historical trend analysis and volatility monitoring", 
            "• Automated threshold alerts and stress detection",
            "• Comprehensive liquidity risk assessment",
            "• Export functionality for further analysis",
            "",
            "=" * 80
        ])
        
        return "\n".join(report_lines)
    
    def save_data_samples(self) -> None:
        """Save sample data to CSV files"""
        logger.info("💾 Saving sample data to CSV files...")
        
        # Ensure data directory exists
        os.makedirs('data', exist_ok=True)
        
        # Save each dataset
        for name, dataset in self.data.items():
            filename = f"data/{name}_sample.csv"
            
            if dataset and len(dataset) > 0:
                # Get field names from first record
                fieldnames = dataset[0].keys()
                
                with open(filename, 'w', newline='') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(dataset)
                
                logger.info(f"✅ Saved {len(dataset)} records to {filename}")
        
        logger.info("📁 Sample data files created in ./data/ directory")
    
    def run_demo(self) -> None:
        """Run the complete dashboard demo"""
        logger.info("🚀 Starting Fed Liquidity Dashboard Demo...")
        
        # Generate mock data
        self.generate_mock_data()
        
        # Save sample data
        self.save_data_samples()
        
        # Generate and display report
        report = self.generate_report()
        print(report)
        
        # Save report
        with open('liquidity_stress_demo_report.txt', 'w') as f:
            f.write(report)
        
        logger.info("📄 Demo report saved to liquidity_stress_demo_report.txt")
        logger.info("🎉 Dashboard demo completed successfully!")
        
        return True

def main():
    """Main demo function"""
    print("🏦 Fed Liquidity Stress Dashboard - Demo Version")
    print("=" * 60)
    print("This demo simulates the full dashboard functionality using mock data.")
    print("The production version fetches real-time data from Fed and Treasury APIs.")
    print("=" * 60)
    print()
    
    dashboard = SimplifiedLiquidityDashboard()
    dashboard.run_demo()
    
    return 0

if __name__ == "__main__":
    exit(main())
"""
Plotting and Visualization Module for Liquidity Dashboard

Creates comprehensive visualizations for Fed liquidity stress indicators
"""

import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
import logging
import warnings

from src.config import PLOT_CONFIG, THRESHOLDS, PLOT_DIR
from src.utils import suppress_warnings, format_billions

logger = logging.getLogger(__name__)

class LiquidityPlotter:
    """Main plotting class for liquidity dashboard visualizations"""
    
    def __init__(self, style: str = 'whitegrid'):
        suppress_warnings()
        plt.style.use('default')
        sns.set_style(style)
        sns.set_palette(PLOT_CONFIG['color_palette'])
        self.figsize = PLOT_CONFIG['figsize']
        self.dpi = PLOT_CONFIG['dpi']
        
    def plot_onrrp_analysis(self, df: pd.DataFrame, save_path: Optional[str] = None) -> None:
        """Create comprehensive ON RRP analysis plots"""
        if df.empty:
            logger.warning("No ON RRP data to plot")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('ON RRP Analysis - Fed Liquidity Stress Monitor', fontsize=16, fontweight='bold')
        
        # Plot 1: ON RRP Amount over time
        axes[0, 0].plot(df['date'], df['amount_billions'], linewidth=2, color='darkblue')
        axes[0, 0].axhline(y=THRESHOLDS['onrrp_stress'], color='red', linestyle='--', alpha=0.7, label=f'Stress Threshold ({format_billions(THRESHOLDS["onrrp_stress"])})')
        axes[0, 0].set_title('ON RRP Usage Over Time', fontweight='bold')
        axes[0, 0].set_ylabel('Amount (Billions USD)')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # Plot 2: Participant count
        if 'participants' in df.columns:
            axes[0, 1].plot(df['date'], df['participants'], linewidth=2, color='green')
            axes[0, 1].set_title('ON RRP Participant Count', fontweight='bold')
            axes[0, 1].set_ylabel('Number of Participants')
            axes[0, 1].grid(True, alpha=0.3)
        
        # Plot 3: Rate analysis
        if 'rate' in df.columns:
            axes[1, 0].plot(df['date'], df['rate'], linewidth=2, color='orange')
            axes[1, 0].set_title('ON RRP Rate', fontweight='bold')
            axes[1, 0].set_ylabel('Rate (%)')
            axes[1, 0].grid(True, alpha=0.3)
        
        # Plot 4: Stress indicator
        if len(df) >= 30:
            df['stress_level'] = df['amount_billions'] / THRESHOLDS['onrrp_stress']
            axes[1, 1].plot(df['date'], df['stress_level'], linewidth=2, color='purple')
            axes[1, 1].axhline(y=1.0, color='red', linestyle='--', alpha=0.7, label='Stress Level')
            axes[1, 1].set_title('Stress Level (Ratio to Threshold)', fontweight='bold')
            axes[1, 1].set_ylabel('Stress Ratio')
            axes[1, 1].legend()
            axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
            logger.info(f"ON RRP analysis saved to {save_path}")
        else:
            plt.savefig(f"{PLOT_DIR}/onrrp_analysis.png", dpi=self.dpi, bbox_inches='tight')
        
        plt.show()
    
    def plot_reserves_analysis(self, df: pd.DataFrame, save_path: Optional[str] = None) -> None:
        """Create bank reserves analysis plots"""
        if df.empty:
            logger.warning("No reserves data to plot")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Bank Reserves Analysis - Fed H.4.1', fontsize=16, fontweight='bold')
        
        # Plot 1: Total reserves
        axes[0, 0].plot(df['date'], df['reserves_billions'], linewidth=2, color='darkgreen')
        axes[0, 0].axhline(y=THRESHOLDS['reserves_low'], color='red', linestyle='--', alpha=0.7, 
                          label=f'Low Threshold ({format_billions(THRESHOLDS["reserves_low"])})')
        axes[0, 0].set_title('Total Bank Reserves', fontweight='bold')
        axes[0, 0].set_ylabel('Reserves (Billions USD)')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # Plot 2: Required vs Excess reserves
        if 'required_reserves' in df.columns and 'excess_reserves' in df.columns:
            axes[0, 1].plot(df['date'], df['required_reserves'], linewidth=2, label='Required', color='blue')
            axes[0, 1].plot(df['date'], df['excess_reserves'], linewidth=2, label='Excess', color='cyan')
            axes[0, 1].set_title('Required vs Excess Reserves', fontweight='bold')
            axes[0, 1].set_ylabel('Amount (Billions USD)')
            axes[0, 1].legend()
            axes[0, 1].grid(True, alpha=0.3)
        
        # Plot 3: 30-day moving average
        if len(df) >= 30:
            df['ma_30'] = df['reserves_billions'].rolling(window=30).mean()
            axes[1, 0].plot(df['date'], df['reserves_billions'], linewidth=1, alpha=0.5, label='Daily', color='lightgreen')
            axes[1, 0].plot(df['date'], df['ma_30'], linewidth=2, label='30-day MA', color='darkgreen')
            axes[1, 0].set_title('Reserves with Moving Average', fontweight='bold')
            axes[1, 0].set_ylabel('Reserves (Billions USD)')
            axes[1, 0].legend()
            axes[1, 0].grid(True, alpha=0.3)
        
        # Plot 4: Change analysis
        df['daily_change'] = df['reserves_billions'].diff()
        axes[1, 1].bar(df['date'], df['daily_change'], alpha=0.7, color='steelblue')
        axes[1, 1].axhline(y=0, color='black', linestyle='-', alpha=0.5)
        axes[1, 1].set_title('Daily Change in Reserves', fontweight='bold')
        axes[1, 1].set_ylabel('Change (Billions USD)')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
            logger.info(f"Reserves analysis saved to {save_path}")
        else:
            plt.savefig(f"{PLOT_DIR}/reserves_analysis.png", dpi=self.dpi, bbox_inches='tight')
        
        plt.show()
    
    def plot_sofr_analysis(self, df: pd.DataFrame, save_path: Optional[str] = None) -> None:
        """Create SOFR analysis plots"""
        if df.empty:
            logger.warning("No SOFR data to plot")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('SOFR Analysis - Secured Overnight Financing Rate', fontsize=16, fontweight='bold')
        
        # Plot 1: SOFR rate over time
        axes[0, 0].plot(df['date'], df['sofr_rate'], linewidth=2, color='navy')
        if 'rate_25th' in df.columns and 'rate_75th' in df.columns:
            axes[0, 0].fill_between(df['date'], df['rate_25th'], df['rate_75th'], alpha=0.3, color='lightblue', label='25th-75th Percentile')
        axes[0, 0].set_title('SOFR Rate Evolution', fontweight='bold')
        axes[0, 0].set_ylabel('Rate (%)')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # Plot 2: Volume analysis
        if 'volume_billions' in df.columns:
            axes[0, 1].plot(df['date'], df['volume_billions'], linewidth=2, color='darkred')
            axes[0, 1].set_title('SOFR Transaction Volume', fontweight='bold')
            axes[0, 1].set_ylabel('Volume (Billions USD)')
            axes[0, 1].grid(True, alpha=0.3)
        
        # Plot 3: Rate volatility
        if len(df) >= 10:
            df['rate_volatility'] = df['sofr_rate'].rolling(window=10).std()
            axes[1, 0].plot(df['date'], df['rate_volatility'], linewidth=2, color='orange')
            axes[1, 0].axhline(y=0.1, color='red', linestyle='--', alpha=0.7, label='High Volatility Threshold')
            axes[1, 0].set_title('SOFR Rate Volatility (10-day rolling std)', fontweight='bold')
            axes[1, 0].set_ylabel('Standard Deviation')
            axes[1, 0].legend()
            axes[1, 0].grid(True, alpha=0.3)
        
        # Plot 4: Rate distribution
        axes[1, 1].hist(df['sofr_rate'], bins=30, alpha=0.7, color='purple', edgecolor='black')
        axes[1, 1].axvline(x=df['sofr_rate'].mean(), color='red', linestyle='--', alpha=0.7, label=f'Mean: {df["sofr_rate"].mean():.3f}%')
        axes[1, 1].set_title('SOFR Rate Distribution', fontweight='bold')
        axes[1, 1].set_xlabel('Rate (%)')
        axes[1, 1].set_ylabel('Frequency')
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
            logger.info(f"SOFR analysis saved to {save_path}")
        else:
            plt.savefig(f"{PLOT_DIR}/sofr_analysis.png", dpi=self.dpi, bbox_inches='tight')
        
        plt.show()
    
    def plot_srf_analysis(self, df: pd.DataFrame, save_path: Optional[str] = None) -> None:
        """Create SRF emergency usage analysis plots"""
        if df.empty:
            logger.warning("No SRF data to plot")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('SRF Analysis - Emergency Liquidity Facility Usage', fontsize=16, fontweight='bold')
        
        # Plot 1: SRF usage over time
        usage_color = ['red' if x > THRESHOLDS['srf_usage'] else 'green' for x in df['usage_billions']]
        axes[0, 0].bar(df['date'], df['usage_billions'], color=usage_color, alpha=0.7)
        axes[0, 0].axhline(y=THRESHOLDS['srf_usage'], color='red', linestyle='--', alpha=0.7, 
                          label=f'Emergency Threshold ({format_billions(THRESHOLDS["srf_usage"])})')
        axes[0, 0].set_title('SRF Usage - Emergency Liquidity Injections', fontweight='bold')
        axes[0, 0].set_ylabel('Usage (Billions USD)')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # Plot 2: Usage frequency
        usage_days = (df['usage_billions'] > 0).sum()
        no_usage_days = len(df) - usage_days
        
        labels = ['No Usage', 'Usage Days']
        sizes = [no_usage_days, usage_days]
        colors = ['lightgreen', 'lightcoral']
        
        axes[0, 1].pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        axes[0, 1].set_title('SRF Usage Frequency', fontweight='bold')
        
        # Plot 3: Participants during usage
        if 'participants' in df.columns:
            usage_mask = df['usage_billions'] > 0
            if usage_mask.any():
                axes[1, 0].scatter(df.loc[usage_mask, 'usage_billions'], df.loc[usage_mask, 'participants'], 
                                 alpha=0.7, color='red', s=60)
                axes[1, 0].set_title('Participants vs Usage Amount', fontweight='bold')
                axes[1, 0].set_xlabel('Usage (Billions USD)')
                axes[1, 0].set_ylabel('Number of Participants')
                axes[1, 0].grid(True, alpha=0.3)
        
        # Plot 4: Emergency events timeline
        emergency_events = df[df['usage_billions'] > THRESHOLDS['srf_usage']]
        if not emergency_events.empty:
            axes[1, 1].bar(emergency_events['date'], emergency_events['usage_billions'], 
                          color='darkred', alpha=0.8, width=2)
            axes[1, 1].set_title('⚠️ Emergency Usage Events', fontweight='bold', color='darkred')
            axes[1, 1].set_ylabel('Emergency Usage (Billions USD)')
            axes[1, 1].grid(True, alpha=0.3)
        else:
            axes[1, 1].text(0.5, 0.5, '✅ No Emergency Events\nDetected in Dataset', 
                           ha='center', va='center', transform=axes[1, 1].transAxes,
                           fontsize=14, color='green', fontweight='bold')
            axes[1, 1].set_title('Emergency Status', fontweight='bold')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
            logger.info(f"SRF analysis saved to {save_path}")
        else:
            plt.savefig(f"{PLOT_DIR}/srf_analysis.png", dpi=self.dpi, bbox_inches='tight')
        
        plt.show()
    
    def plot_treasury_analysis(self, df: pd.DataFrame, save_path: Optional[str] = None) -> None:
        """Create Treasury auction and issuance analysis plots"""
        if df.empty:
            logger.warning("No Treasury data to plot")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Treasury Analysis - Issuance Pressure & Yield Trends', fontsize=16, fontweight='bold')
        
        # Plot 1: Weekly issuance amounts
        df['week'] = df['date'].dt.isocalendar().week
        weekly_issuance = df.groupby('week')['amount_billions'].sum().reset_index()
        
        issuance_colors = ['red' if x > THRESHOLDS['treasury_issuance_high'] else 'blue' for x in weekly_issuance['amount_billions']]
        axes[0, 0].bar(weekly_issuance['week'], weekly_issuance['amount_billions'], 
                      color=issuance_colors, alpha=0.7)
        axes[0, 0].axhline(y=THRESHOLDS['treasury_issuance_high'], color='red', linestyle='--', alpha=0.7,
                          label=f'High Issuance Threshold ({format_billions(THRESHOLDS["treasury_issuance_high"])})')
        axes[0, 0].set_title('Weekly Treasury Issuance', fontweight='bold')
        axes[0, 0].set_ylabel('Issuance (Billions USD)')
        axes[0, 0].set_xlabel('Week of Year')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # Plot 2: Issuance by security type
        if 'security_type' in df.columns:
            type_issuance = df.groupby('security_type')['amount_billions'].sum().sort_values(ascending=False)
            axes[0, 1].pie(type_issuance.values, labels=type_issuance.index, autopct='%1.1f%%', startangle=90)
            axes[0, 1].set_title('Issuance by Security Type', fontweight='bold')
        
        # Plot 3: Yield trends
        if 'yield_rate' in df.columns:
            axes[1, 0].plot(df['date'], df['yield_rate'], linewidth=2, color='darkgreen')
            if len(df) >= 30:
                df['yield_ma'] = df['yield_rate'].rolling(window=30).mean()
                axes[1, 0].plot(df['date'], df['yield_ma'], linewidth=2, color='lightgreen', 
                               linestyle='--', label='30-day MA')
                axes[1, 0].legend()
            axes[1, 0].set_title('Treasury Yield Trends', fontweight='bold')
            axes[1, 0].set_ylabel('Yield (%)')
            axes[1, 0].grid(True, alpha=0.3)
        
        # Plot 4: Issuance pressure indicator
        if len(weekly_issuance) >= 4:
            weekly_issuance['pressure_ratio'] = weekly_issuance['amount_billions'] / THRESHOLDS['treasury_issuance_high']
            pressure_colors = ['red' if x > 1.0 else 'orange' if x > 0.8 else 'green' for x in weekly_issuance['pressure_ratio']]
            
            axes[1, 1].bar(weekly_issuance['week'], weekly_issuance['pressure_ratio'], 
                          color=pressure_colors, alpha=0.7)
            axes[1, 1].axhline(y=1.0, color='red', linestyle='--', alpha=0.7, label='Pressure Threshold')
            axes[1, 1].set_title('Issuance Pressure Ratio', fontweight='bold')
            axes[1, 1].set_ylabel('Pressure Ratio')
            axes[1, 1].set_xlabel('Week of Year')
            axes[1, 1].legend()
            axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
            logger.info(f"Treasury analysis saved to {save_path}")
        else:
            plt.savefig(f"{PLOT_DIR}/treasury_analysis.png", dpi=self.dpi, bbox_inches='tight')
        
        plt.show()
    
    def create_dashboard_overview(self, onrrp_df: pd.DataFrame, reserves_df: pd.DataFrame, 
                                sofr_df: pd.DataFrame, srf_df: pd.DataFrame, 
                                treasury_df: pd.DataFrame, save_path: Optional[str] = None) -> None:
        """Create comprehensive dashboard overview"""
        fig, axes = plt.subplots(2, 3, figsize=(20, 12))
        fig.suptitle('🏦 Fed Liquidity Stress Dashboard - System Overview', fontsize=18, fontweight='bold')
        
        # ON RRP overview
        if not onrrp_df.empty:
            axes[0, 0].plot(onrrp_df['date'], onrrp_df['amount_billions'], linewidth=2, color='darkblue')
            axes[0, 0].axhline(y=THRESHOLDS['onrrp_stress'], color='red', linestyle='--', alpha=0.7)
            axes[0, 0].set_title('💰 ON RRP Usage', fontweight='bold')
            axes[0, 0].set_ylabel('Billions USD')
            axes[0, 0].grid(True, alpha=0.3)
        
        # Bank Reserves overview
        if not reserves_df.empty:
            axes[0, 1].plot(reserves_df['date'], reserves_df['reserves_billions'], linewidth=2, color='darkgreen')
            axes[0, 1].axhline(y=THRESHOLDS['reserves_low'], color='red', linestyle='--', alpha=0.7)
            axes[0, 1].set_title('🏛️ Bank Reserves', fontweight='bold')
            axes[0, 1].set_ylabel('Billions USD')
            axes[0, 1].grid(True, alpha=0.3)
        
        # SOFR overview
        if not sofr_df.empty:
            axes[0, 2].plot(sofr_df['date'], sofr_df['sofr_rate'], linewidth=2, color='navy')
            axes[0, 2].set_title('📊 SOFR Rate', fontweight='bold')
            axes[0, 2].set_ylabel('Rate (%)')
            axes[0, 2].grid(True, alpha=0.3)
        
        # SRF emergency usage
        if not srf_df.empty:
            emergency_mask = srf_df['usage_billions'] > THRESHOLDS['srf_usage']
            axes[1, 0].bar(srf_df['date'], srf_df['usage_billions'], 
                          color=['red' if x else 'green' for x in emergency_mask], alpha=0.7)
            axes[1, 0].axhline(y=THRESHOLDS['srf_usage'], color='red', linestyle='--', alpha=0.7)
            axes[1, 0].set_title('🚨 SRF Emergency Usage', fontweight='bold')
            axes[1, 0].set_ylabel('Billions USD')
            axes[1, 0].grid(True, alpha=0.3)
        
        # Treasury issuance
        if not treasury_df.empty:
            treasury_df['week'] = treasury_df['date'].dt.isocalendar().week
            weekly_issuance = treasury_df.groupby('week')['amount_billions'].sum().reset_index()
            pressure_mask = weekly_issuance['amount_billions'] > THRESHOLDS['treasury_issuance_high']
            
            axes[1, 1].bar(weekly_issuance['week'], weekly_issuance['amount_billions'],
                          color=['red' if x else 'blue' for x in pressure_mask], alpha=0.7)
            axes[1, 1].axhline(y=THRESHOLDS['treasury_issuance_high'], color='red', linestyle='--', alpha=0.7)
            axes[1, 1].set_title('💵 Treasury Issuance', fontweight='bold')
            axes[1, 1].set_ylabel('Billions USD/Week')
            axes[1, 1].grid(True, alpha=0.3)
        
        # Stress summary
        stress_indicators = []
        if not onrrp_df.empty:
            stress_indicators.append('ON RRP' if onrrp_df['amount_billions'].iloc[-1] > THRESHOLDS['onrrp_stress'] else None)
        if not reserves_df.empty:
            stress_indicators.append('Reserves' if reserves_df['reserves_billions'].iloc[-1] < THRESHOLDS['reserves_low'] else None)
        if not srf_df.empty:
            stress_indicators.append('SRF Emergency' if srf_df['usage_billions'].iloc[-1] > THRESHOLDS['srf_usage'] else None)
        
        stress_indicators = [x for x in stress_indicators if x is not None]
        
        if stress_indicators:
            axes[1, 2].text(0.5, 0.7, '⚠️ STRESS DETECTED', ha='center', va='center', 
                           transform=axes[1, 2].transAxes, fontsize=16, color='red', fontweight='bold')
            axes[1, 2].text(0.5, 0.3, '\n'.join(stress_indicators), ha='center', va='center',
                           transform=axes[1, 2].transAxes, fontsize=12, color='darkred')
        else:
            axes[1, 2].text(0.5, 0.5, '✅ NORMAL\nLIQUIDITY\nCONDITIONS', ha='center', va='center',
                           transform=axes[1, 2].transAxes, fontsize=16, color='green', fontweight='bold')
        
        axes[1, 2].set_title('🎯 Stress Status', fontweight='bold')
        axes[1, 2].set_xticks([])
        axes[1, 2].set_yticks([])
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
            logger.info(f"Dashboard overview saved to {save_path}")
        else:
            plt.savefig(f"{PLOT_DIR}/dashboard_overview.png", dpi=self.dpi, bbox_inches='tight')
        
        plt.show()

# Convenience functions for individual plotting
def plot_onrrp(df: pd.DataFrame, save_path: Optional[str] = None) -> None:
    """Plot ON RRP analysis"""
    plotter = LiquidityPlotter()
    plotter.plot_onrrp_analysis(df, save_path)

def plot_reserves(df: pd.DataFrame, save_path: Optional[str] = None) -> None:
    """Plot bank reserves analysis"""
    plotter = LiquidityPlotter()
    plotter.plot_reserves_analysis(df, save_path)

def plot_sofr(df: pd.DataFrame, save_path: Optional[str] = None) -> None:
    """Plot SOFR analysis"""
    plotter = LiquidityPlotter()
    plotter.plot_sofr_analysis(df, save_path)

def plot_srf(df: pd.DataFrame, save_path: Optional[str] = None) -> None:
    """Plot SRF analysis"""
    plotter = LiquidityPlotter()
    plotter.plot_srf_analysis(df, save_path)

def plot_treasury(df: pd.DataFrame, save_path: Optional[str] = None) -> None:
    """Plot Treasury analysis"""
    plotter = LiquidityPlotter()
    plotter.plot_treasury_analysis(df, save_path)

def create_dashboard(onrrp_df: pd.DataFrame, reserves_df: pd.DataFrame, 
                    sofr_df: pd.DataFrame, srf_df: pd.DataFrame, 
                    treasury_df: pd.DataFrame, save_path: Optional[str] = None) -> None:
    """Create complete dashboard overview"""
    plotter = LiquidityPlotter()
    plotter.create_dashboard_overview(onrrp_df, reserves_df, sofr_df, srf_df, treasury_df, save_path)

if __name__ == "__main__":
    # Test plotting with mock data
    from datetime import datetime, timedelta
    import pandas as pd
    
    # Create test data
    dates = pd.date_range(start=datetime.now() - timedelta(days=90), periods=90)
    test_onrrp = pd.DataFrame({
        'date': dates,
        'amount_billions': 2000 + np.random.randn(90) * 100,
        'participants': 80 + np.random.randn(90) * 10,
        'rate': 5.3 + np.random.randn(90) * 0.1
    })
    
    print("Testing plot functionality...")
    plot_onrrp(test_onrrp)
    print("Plot test completed!")
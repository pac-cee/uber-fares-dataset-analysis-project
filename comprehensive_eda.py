#!/usr/bin/env python3
"""
Comprehensive Exploratory Data Analysis for Uber Fares Dataset
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# Set style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class UberEDA:
    """
    Comprehensive EDA class for Uber Fares dataset
    """
    
    def __init__(self, data_path='uber_enhanced.csv'):
        """Initialize the EDA analyzer"""
        self.data_path = data_path
        self.df = None
        
    def load_data(self):
        """Load the enhanced dataset"""
        print("=" * 80)
        print("UBER FARES DATASET - COMPREHENSIVE EXPLORATORY DATA ANALYSIS")
        print("=" * 80)
        
        self.df = pd.read_csv(self.data_path)
        # Convert pickup_datetime back to datetime if needed
        if self.df['pickup_datetime'].dtype == 'object':
            self.df['pickup_datetime'] = pd.to_datetime(self.df['pickup_datetime'])
        
        print(f"\n📊 Enhanced dataset loaded:")
        print(f"   • Shape: {self.df.shape}")
        print(f"   • Features: {len(self.df.columns)}")
        print(f"   • Memory usage: {self.df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        
        return True
    
    def fare_distribution_analysis(self):
        """Analyze fare amount distributions"""
        print("\n" + "=" * 60)
        print("1. FARE DISTRIBUTION ANALYSIS")
        print("=" * 60)
        
        # Create comprehensive fare analysis plots
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('Uber Fare Distribution Analysis', fontsize=16, fontweight='bold')
        
        # 1. Histogram of fare amounts
        axes[0, 0].hist(self.df['fare_amount'], bins=50, alpha=0.7, color='skyblue', edgecolor='black')
        axes[0, 0].set_title('Distribution of Fare Amounts')
        axes[0, 0].set_xlabel('Fare Amount ($)')
        axes[0, 0].set_ylabel('Frequency')
        axes[0, 0].axvline(self.df['fare_amount'].mean(), color='red', linestyle='--', label=f'Mean: ${self.df["fare_amount"].mean():.2f}')
        axes[0, 0].axvline(self.df['fare_amount'].median(), color='green', linestyle='--', label=f'Median: ${self.df["fare_amount"].median():.2f}')
        axes[0, 0].legend()
        
        # 2. Box plot of fare amounts
        axes[0, 1].boxplot(self.df['fare_amount'])
        axes[0, 1].set_title('Fare Amount Box Plot')
        axes[0, 1].set_ylabel('Fare Amount ($)')
        
        # 3. Fare by time period
        fare_by_period = self.df.groupby('time_period')['fare_amount'].mean().sort_values(ascending=False)
        axes[0, 2].bar(fare_by_period.index, fare_by_period.values, color='lightcoral')
        axes[0, 2].set_title('Average Fare by Time Period')
        axes[0, 2].set_xlabel('Time Period')
        axes[0, 2].set_ylabel('Average Fare ($)')
        axes[0, 2].tick_params(axis='x', rotation=45)
        
        # 4. Fare by day of week
        fare_by_day = self.df.groupby('day_of_week')['fare_amount'].mean()
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        fare_by_day = fare_by_day.reindex(day_order)
        axes[1, 0].bar(fare_by_day.index, fare_by_day.values, color='lightgreen')
        axes[1, 0].set_title('Average Fare by Day of Week')
        axes[1, 0].set_xlabel('Day of Week')
        axes[1, 0].set_ylabel('Average Fare ($)')
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        # 5. Fare by passenger count
        fare_by_passengers = self.df.groupby('passenger_count')['fare_amount'].mean()
        axes[1, 1].bar(fare_by_passengers.index, fare_by_passengers.values, color='gold')
        axes[1, 1].set_title('Average Fare by Passenger Count')
        axes[1, 1].set_xlabel('Passenger Count')
        axes[1, 1].set_ylabel('Average Fare ($)')
        
        # 6. Fare by distance category
        fare_by_distance = self.df.groupby('distance_category')['fare_amount'].mean()
        distance_order = ['Very Short', 'Short', 'Medium', 'Long', 'Very Long']
        fare_by_distance = fare_by_distance.reindex(distance_order)
        axes[1, 2].bar(fare_by_distance.index, fare_by_distance.values, color='plum')
        axes[1, 2].set_title('Average Fare by Distance Category')
        axes[1, 2].set_xlabel('Distance Category')
        axes[1, 2].set_ylabel('Average Fare ($)')
        axes[1, 2].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig('fare_distribution_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # Print key statistics
        print(f"\n📊 Fare Statistics:")
        print(f"   • Mean: ${self.df['fare_amount'].mean():.2f}")
        print(f"   • Median: ${self.df['fare_amount'].median():.2f}")
        print(f"   • Standard Deviation: ${self.df['fare_amount'].std():.2f}")
        print(f"   • Min: ${self.df['fare_amount'].min():.2f}")
        print(f"   • Max: ${self.df['fare_amount'].max():.2f}")
        
        print(f"\n📈 Highest average fares:")
        print(f"   • Time period: {fare_by_period.index[0]} (${fare_by_period.iloc[0]:.2f})")
        print(f"   • Day of week: {fare_by_day.idxmax()} (${fare_by_day.max():.2f})")
        print(f"   • Distance category: {fare_by_distance.idxmax()} (${fare_by_distance.max():.2f})")
    
    def temporal_analysis(self):
        """Analyze temporal patterns"""
        print("\n" + "=" * 60)
        print("2. TEMPORAL PATTERN ANALYSIS")
        print("=" * 60)
        
        # Create temporal analysis plots
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Temporal Pattern Analysis', fontsize=16, fontweight='bold')
        
        # 1. Rides by hour of day
        rides_by_hour = self.df.groupby('pickup_hour').size()
        axes[0, 0].plot(rides_by_hour.index, rides_by_hour.values, marker='o', linewidth=2, markersize=6)
        axes[0, 0].set_title('Number of Rides by Hour of Day')
        axes[0, 0].set_xlabel('Hour of Day')
        axes[0, 0].set_ylabel('Number of Rides')
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. Rides by day of week
        rides_by_day = self.df.groupby('day_of_week').size()
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        rides_by_day = rides_by_day.reindex(day_order)
        axes[0, 1].bar(rides_by_day.index, rides_by_day.values, color='skyblue')
        axes[0, 1].set_title('Number of Rides by Day of Week')
        axes[0, 1].set_xlabel('Day of Week')
        axes[0, 1].set_ylabel('Number of Rides')
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # 3. Peak vs Off-peak comparison
        peak_comparison = self.df.groupby('is_peak_hour').agg({
            'fare_amount': 'mean',
            'trip_distance_km': 'mean'
        })
        peak_labels = ['Off-Peak', 'Peak']
        
        x = np.arange(len(peak_labels))
        width = 0.35
        
        axes[1, 0].bar(x - width/2, peak_comparison['fare_amount'], width, label='Avg Fare ($)', color='lightcoral')
        axes[1, 0].set_xlabel('Time Period')
        axes[1, 0].set_ylabel('Average Fare ($)', color='lightcoral')
        axes[1, 0].set_title('Peak vs Off-Peak Comparison')
        axes[1, 0].set_xticks(x)
        axes[1, 0].set_xticklabels(peak_labels)
        
        ax2 = axes[1, 0].twinx()
        ax2.bar(x + width/2, peak_comparison['trip_distance_km'], width, label='Avg Distance (km)', color='lightblue')
        ax2.set_ylabel('Average Distance (km)', color='lightblue')
        
        # 4. Monthly trends
        monthly_trends = self.df.groupby('pickup_month').agg({
            'fare_amount': 'mean',
            'trip_distance_km': 'mean'
        })
        
        axes[1, 1].plot(monthly_trends.index, monthly_trends['fare_amount'], marker='o', label='Avg Fare', color='red')
        axes[1, 1].set_xlabel('Month')
        axes[1, 1].set_ylabel('Average Fare ($)', color='red')
        axes[1, 1].set_title('Monthly Trends')
        
        ax3 = axes[1, 1].twinx()
        ax3.plot(monthly_trends.index, monthly_trends['trip_distance_km'], marker='s', label='Avg Distance', color='blue')
        ax3.set_ylabel('Average Distance (km)', color='blue')
        
        plt.tight_layout()
        plt.savefig('temporal_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # Print key insights
        print(f"\n📊 Temporal Insights:")
        print(f"   • Busiest hour: {rides_by_hour.idxmax()}:00 ({rides_by_hour.max():,} rides)")
        print(f"   • Busiest day: {rides_by_day.idxmax()} ({rides_by_day.max():,} rides)")
        print(f"   • Peak hour avg fare: ${peak_comparison.loc[1, 'fare_amount']:.2f}")
        print(f"   • Off-peak avg fare: ${peak_comparison.loc[0, 'fare_amount']:.2f}")
    
    def geographical_analysis(self):
        """Analyze geographical patterns"""
        print("\n" + "=" * 60)
        print("3. GEOGRAPHICAL PATTERN ANALYSIS")
        print("=" * 60)
        
        # Create geographical analysis plots
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Geographical Pattern Analysis', fontsize=16, fontweight='bold')
        
        # 1. Pickup locations scatter plot
        sample_size = min(5000, len(self.df))  # Sample for performance
        sample_df = self.df.sample(n=sample_size, random_state=42)
        
        scatter = axes[0, 0].scatter(sample_df['pickup_longitude'], sample_df['pickup_latitude'], 
                                   c=sample_df['fare_amount'], cmap='viridis', alpha=0.6, s=1)
        axes[0, 0].set_title('Pickup Locations (colored by fare)')
        axes[0, 0].set_xlabel('Longitude')
        axes[0, 0].set_ylabel('Latitude')
        plt.colorbar(scatter, ax=axes[0, 0], label='Fare Amount ($)')
        
        # 2. Borough analysis
        borough_stats = self.df.groupby('pickup_borough').agg({
            'fare_amount': 'mean',
            'trip_distance_km': 'mean',
            'pickup_borough': 'count'
        }).rename(columns={'pickup_borough': 'ride_count'})
        
        axes[0, 1].bar(borough_stats.index, borough_stats['ride_count'], color='lightblue')
        axes[0, 1].set_title('Rides by Pickup Borough')
        axes[0, 1].set_xlabel('Borough')
        axes[0, 1].set_ylabel('Number of Rides')
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # 3. Inter-borough vs Intra-borough
        inter_borough_stats = self.df.groupby('is_inter_borough').agg({
            'fare_amount': 'mean',
            'trip_distance_km': 'mean'
        })
        
        labels = ['Intra-borough', 'Inter-borough']
        x = np.arange(len(labels))
        width = 0.35
        
        axes[1, 0].bar(x - width/2, inter_borough_stats['fare_amount'], width, 
                      label='Avg Fare ($)', color='lightcoral')
        axes[1, 0].set_xlabel('Trip Type')
        axes[1, 0].set_ylabel('Average Fare ($)')
        axes[1, 0].set_title('Intra vs Inter-borough Trips')
        axes[1, 0].set_xticks(x)
        axes[1, 0].set_xticklabels(labels)
        
        ax4 = axes[1, 0].twinx()
        ax4.bar(x + width/2, inter_borough_stats['trip_distance_km'], width, 
               label='Avg Distance (km)', color='lightgreen')
        ax4.set_ylabel('Average Distance (km)')
        
        # 4. Distance from center analysis
        distance_bins = pd.cut(self.df['pickup_distance_from_center'], bins=5)
        distance_stats = self.df.groupby(distance_bins)['fare_amount'].mean()
        
        axes[1, 1].bar(range(len(distance_stats)), distance_stats.values, color='gold')
        axes[1, 1].set_title('Fare by Distance from City Center')
        axes[1, 1].set_xlabel('Distance from Center (binned)')
        axes[1, 1].set_ylabel('Average Fare ($)')
        axes[1, 1].set_xticks(range(len(distance_stats)))
        axes[1, 1].set_xticklabels([f'{interval.left:.1f}-{interval.right:.1f}' for interval in distance_stats.index], rotation=45)
        
        plt.tight_layout()
        plt.savefig('geographical_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # Print key insights
        print(f"\n📊 Geographical Insights:")
        print(f"   • Most popular pickup borough: {borough_stats['ride_count'].idxmax()} ({borough_stats['ride_count'].max():,} rides)")
        print(f"   • Highest avg fare borough: {borough_stats['fare_amount'].idxmax()} (${borough_stats['fare_amount'].max():.2f})")
        print(f"   • Inter-borough avg fare: ${inter_borough_stats.loc[1, 'fare_amount']:.2f}")
        print(f"   • Intra-borough avg fare: ${inter_borough_stats.loc[0, 'fare_amount']:.2f}")

def main():
    """Main function to run comprehensive EDA"""
    eda = UberEDA('uber_enhanced.csv')
    eda.load_data()
    eda.fare_distribution_analysis()
    eda.temporal_analysis()
    eda.geographical_analysis()
    
    print(f"\n🎯 Comprehensive EDA completed successfully!")
    print(f"📊 Generated visualizations:")
    print(f"   • fare_distribution_analysis.png")
    print(f"   • temporal_analysis.png")
    print(f"   • geographical_analysis.png")

if __name__ == "__main__":
    main()

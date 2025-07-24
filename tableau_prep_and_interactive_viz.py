#!/usr/bin/env python3
"""
Tableau Data Preparation and Interactive Visualizations
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.offline as pyo
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class TableauDataPrep:
    """
    Prepare data for Tableau and create interactive visualizations
    """
    
    def __init__(self, data_path='uber_enhanced.csv'):
        """Initialize the Tableau data prep"""
        self.data_path = data_path
        self.df = None
        
    def load_and_prepare_data(self):
        """Load and prepare data for Tableau"""
        print("=" * 80)
        print("TABLEAU DATA PREPARATION & INTERACTIVE VISUALIZATIONS")
        print("=" * 80)
        
        self.df = pd.read_csv(self.data_path)
        
        # Convert pickup_datetime back to datetime if needed
        if self.df['pickup_datetime'].dtype == 'object':
            self.df['pickup_datetime'] = pd.to_datetime(self.df['pickup_datetime'])
        
        print(f"\n📊 Dataset loaded for Tableau preparation:")
        print(f"   • Shape: {self.df.shape}")
        print(f"   • Features: {len(self.df.columns)}")
        
        return True
    
    def create_tableau_optimized_dataset(self):
        """Create an optimized dataset for Tableau"""
        print("\n" + "=" * 60)
        print("1. CREATING TABLEAU-OPTIMIZED DATASET")
        print("=" * 60)
        
        # Create a subset with key features for Tableau
        tableau_df = self.df.copy()
        
        # Add additional calculated fields that are useful for Tableau
        tableau_df['pickup_date'] = tableau_df['pickup_datetime'].dt.date
        tableau_df['pickup_time'] = tableau_df['pickup_datetime'].dt.time
        tableau_df['year_month'] = tableau_df['pickup_datetime'].dt.to_period('M').astype(str)
        tableau_df['hour_minute'] = tableau_df['pickup_datetime'].dt.strftime('%H:%M')
        
        # Create revenue metrics
        tableau_df['total_revenue'] = tableau_df['fare_amount']
        tableau_df['revenue_per_km'] = tableau_df['fare_amount'] / (tableau_df['trip_distance_km'] + 0.001)
        
        # Create efficiency metrics
        tableau_df['trips_per_hour'] = 1  # Will be aggregated in Tableau
        
        # Round coordinates for better performance in Tableau
        tableau_df['pickup_lat_rounded'] = tableau_df['pickup_latitude'].round(4)
        tableau_df['pickup_lon_rounded'] = tableau_df['pickup_longitude'].round(4)
        tableau_df['dropoff_lat_rounded'] = tableau_df['dropoff_latitude'].round(4)
        tableau_df['dropoff_lon_rounded'] = tableau_df['dropoff_longitude'].round(4)
        
        # Save the Tableau-optimized dataset
        tableau_df.to_csv('uber_tableau_ready.csv', index=False)
        
        print(f"✅ Tableau-optimized dataset created:")
        print(f"   • File: uber_tableau_ready.csv")
        print(f"   • Shape: {tableau_df.shape}")
        print(f"   • Size: {tableau_df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        
        return tableau_df
    
    def create_interactive_dashboard(self):
        """Create interactive Plotly dashboard as reference for Tableau"""
        print("\n" + "=" * 60)
        print("2. CREATING INTERACTIVE DASHBOARD")
        print("=" * 60)
        
        # Create a comprehensive interactive dashboard
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=('Fare Distribution', 'Hourly Ride Patterns',
                          'Geographic Distribution', 'Temporal Heatmap',
                          'Distance vs Fare', 'Borough Analysis'),
            specs=[[{"type": "histogram"}, {"type": "scatter"}],
                   [{"type": "scattermapbox"}, {"type": "heatmap"}],
                   [{"type": "scatter"}, {"type": "bar"}]]
        )
        
        # 1. Fare Distribution
        fig.add_trace(
            go.Histogram(x=self.df['fare_amount'], nbinsx=50, name='Fare Distribution',
                        marker_color='skyblue', opacity=0.7),
            row=1, col=1
        )
        
        # 2. Hourly Ride Patterns
        hourly_data = self.df.groupby('pickup_hour').agg({
            'fare_amount': ['count', 'mean']
        }).reset_index()
        hourly_data.columns = ['hour', 'ride_count', 'avg_fare']
        
        fig.add_trace(
            go.Scatter(x=hourly_data['hour'], y=hourly_data['ride_count'],
                      mode='lines+markers', name='Rides per Hour',
                      line=dict(color='red', width=3)),
            row=1, col=2
        )
        
        # 3. Geographic Distribution (sample for performance)
        sample_df = self.df.sample(n=min(1000, len(self.df)), random_state=42)
        
        fig.add_trace(
            go.Scattermapbox(
                lat=sample_df['pickup_latitude'],
                lon=sample_df['pickup_longitude'],
                mode='markers',
                marker=dict(size=5, color=sample_df['fare_amount'], 
                          colorscale='Viridis', showscale=True),
                text=sample_df['fare_amount'],
                name='Pickup Locations'
            ),
            row=2, col=1
        )
        
        # 4. Temporal Heatmap
        pivot_data = self.df.groupby(['pickup_hour', 'pickup_weekday'])['fare_amount'].mean().unstack()
        
        fig.add_trace(
            go.Heatmap(z=pivot_data.values, x=list(range(7)), y=list(range(24)),
                      colorscale='YlOrRd', name='Fare Heatmap'),
            row=2, col=2
        )
        
        # 5. Distance vs Fare
        sample_df2 = self.df.sample(n=min(2000, len(self.df)), random_state=42)
        
        fig.add_trace(
            go.Scatter(x=sample_df2['trip_distance_km'], y=sample_df2['fare_amount'],
                      mode='markers', name='Distance vs Fare',
                      marker=dict(color='green', opacity=0.6)),
            row=3, col=1
        )
        
        # 6. Borough Analysis
        borough_stats = self.df.groupby('pickup_borough')['fare_amount'].agg(['mean', 'count']).reset_index()
        borough_stats = borough_stats[borough_stats['count'] > 100]  # Filter for significant data
        
        fig.add_trace(
            go.Bar(x=borough_stats['pickup_borough'], y=borough_stats['mean'],
                  name='Avg Fare by Borough', marker_color='orange'),
            row=3, col=2
        )
        
        # Update layout
        fig.update_layout(
            height=1200,
            title_text="Uber Fares Interactive Dashboard",
            title_x=0.5,
            showlegend=False
        )
        
        # Update mapbox
        fig.update_layout(
            mapbox=dict(
                style="open-street-map",
                center=dict(lat=40.7589, lon=-73.9851),
                zoom=10
            )
        )
        
        # Save interactive dashboard
        pyo.plot(fig, filename='uber_interactive_dashboard.html', auto_open=False)
        
        print(f"✅ Interactive dashboard created:")
        print(f"   • File: uber_interactive_dashboard.html")
        print(f"   • Open this file in a web browser to view the interactive dashboard")
    
    def create_summary_statistics(self):
        """Create summary statistics for Tableau dashboard"""
        print("\n" + "=" * 60)
        print("3. CREATING SUMMARY STATISTICS")
        print("=" * 60)
        
        # Key Performance Indicators
        total_rides = len(self.df)
        total_revenue = self.df['fare_amount'].sum()
        avg_fare = self.df['fare_amount'].mean()
        avg_distance = self.df['trip_distance_km'].mean()
        avg_duration = self.df['trip_distance_km'].mean() / 25 * 60  # Assuming 25 km/h average speed
        
        # Temporal insights
        busiest_hour = self.df.groupby('pickup_hour').size().idxmax()
        busiest_day = self.df.groupby('day_of_week').size().idxmax()
        peak_month = self.df.groupby('pickup_month').size().idxmax()
        
        # Geographic insights
        top_borough = self.df['pickup_borough'].value_counts().index[0]
        inter_borough_pct = (self.df['is_inter_borough'].sum() / len(self.df)) * 100
        
        # Create KPI summary
        kpi_summary = {
            'Metric': [
                'Total Rides', 'Total Revenue', 'Average Fare', 'Average Distance',
                'Average Duration (min)', 'Busiest Hour', 'Busiest Day', 'Peak Month',
                'Top Borough', 'Inter-Borough Trips (%)'
            ],
            'Value': [
                f"{total_rides:,}",
                f"${total_revenue:,.2f}",
                f"${avg_fare:.2f}",
                f"{avg_distance:.2f} km",
                f"{avg_duration:.1f}",
                f"{busiest_hour}:00",
                busiest_day,
                f"Month {peak_month}",
                top_borough,
                f"{inter_borough_pct:.1f}%"
            ]
        }
        
        kpi_df = pd.DataFrame(kpi_summary)
        kpi_df.to_csv('uber_kpi_summary.csv', index=False)
        
        print(f"✅ KPI Summary created:")
        print(f"   • File: uber_kpi_summary.csv")
        
        # Print KPIs
        print(f"\n📊 Key Performance Indicators:")
        for metric, value in zip(kpi_summary['Metric'], kpi_summary['Value']):
            print(f"   • {metric}: {value}")
        
        # Create aggregated data for Tableau
        # Hourly aggregation
        hourly_agg = self.df.groupby('pickup_hour').agg({
            'fare_amount': ['count', 'mean', 'sum'],
            'trip_distance_km': 'mean',
            'passenger_count': 'mean'
        }).round(2)
        hourly_agg.columns = ['rides_count', 'avg_fare', 'total_revenue', 'avg_distance', 'avg_passengers']
        hourly_agg.reset_index().to_csv('uber_hourly_aggregation.csv', index=False)
        
        # Daily aggregation
        daily_agg = self.df.groupby('day_of_week').agg({
            'fare_amount': ['count', 'mean', 'sum'],
            'trip_distance_km': 'mean',
            'passenger_count': 'mean'
        }).round(2)
        daily_agg.columns = ['rides_count', 'avg_fare', 'total_revenue', 'avg_distance', 'avg_passengers']
        daily_agg.reset_index().to_csv('uber_daily_aggregation.csv', index=False)
        
        # Borough aggregation
        borough_agg = self.df.groupby('pickup_borough').agg({
            'fare_amount': ['count', 'mean', 'sum'],
            'trip_distance_km': 'mean',
            'passenger_count': 'mean'
        }).round(2)
        borough_agg.columns = ['rides_count', 'avg_fare', 'total_revenue', 'avg_distance', 'avg_passengers']
        borough_agg.reset_index().to_csv('uber_borough_aggregation.csv', index=False)
        
        print(f"\n✅ Aggregated datasets created for Tableau:")
        print(f"   • uber_hourly_aggregation.csv")
        print(f"   • uber_daily_aggregation.csv")
        print(f"   • uber_borough_aggregation.csv")
    
    def generate_tableau_instructions(self):
        """Generate instructions for creating Tableau dashboard"""
        print("\n" + "=" * 60)
        print("4. TABLEAU DASHBOARD INSTRUCTIONS")
        print("=" * 60)
        
        instructions = """
TABLEAU PUBLIC DASHBOARD CREATION GUIDE
======================================

1. DATA CONNECTION:
   • Open Tableau Public
   • Connect to Text file: uber_tableau_ready.csv
   • Also connect to the aggregated files for summary views

2. RECOMMENDED DASHBOARD STRUCTURE:

   A. OVERVIEW PAGE:
      • KPI Cards: Total Rides, Revenue, Avg Fare, Avg Distance
      • Fare Distribution Histogram
      • Rides by Hour Line Chart
      • Geographic Map with Pickup Locations

   B. TEMPORAL ANALYSIS PAGE:
      • Hourly Pattern Line Chart
      • Daily Pattern Bar Chart
      • Monthly Trends (if multiple months)
      • Peak vs Off-Peak Comparison

   C. GEOGRAPHIC ANALYSIS PAGE:
      • NYC Map with Pickup/Dropoff Density
      • Borough Comparison Charts
      • Inter-Borough vs Intra-Borough Analysis
      • Distance from Center Analysis

   D. BUSINESS INSIGHTS PAGE:
      • Fare Prediction Factors
      • Revenue Optimization Opportunities
      • Passenger Behavior Analysis
      • Seasonal Patterns

3. KEY VISUALIZATIONS TO CREATE:

   • Map: Use pickup_lat_rounded, pickup_lon_rounded for performance
   • Time Series: Use pickup_datetime for temporal analysis
   • Heatmap: Hour vs Day of Week for fare patterns
   • Scatter Plot: Distance vs Fare relationship
   • Bar Charts: Borough, Time Period, Passenger Category comparisons

4. FILTERS TO ADD:
   • Date Range Filter
   • Borough Filter
   • Time Period Filter
   • Distance Category Filter
   • Passenger Count Filter

5. CALCULATED FIELDS TO CREATE:
   • Revenue per Hour = SUM([fare_amount]) / COUNT([pickup_hour])
   • Efficiency Ratio = [trip_distance_km] / [fare_amount]
   • Peak Hour Indicator = IF [pickup_hour] >= 7 AND [pickup_hour] <= 9 
                          OR [pickup_hour] >= 17 AND [pickup_hour] <= 19 
                          THEN "Peak" ELSE "Off-Peak" END

6. DASHBOARD DESIGN TIPS:
   • Use consistent color scheme
   • Add interactive filters
   • Include tooltips with relevant information
   • Create drill-down capabilities
   • Add trend lines where appropriate
   • Use dashboard actions for interactivity

7. PERFORMANCE OPTIMIZATION:
   • Use data extracts instead of live connections
   • Limit map visualizations to reasonable sample sizes
   • Use aggregated data for summary views
   • Consider using context filters for large datasets
        """
        
        # Save instructions to file
        with open('tableau_dashboard_instructions.txt', 'w') as f:
            f.write(instructions)
        
        print(f"✅ Tableau instructions created:")
        print(f"   • File: tableau_dashboard_instructions.txt")
        print(f"\n📋 Key files for Tableau:")
        print(f"   • uber_tableau_ready.csv (Main dataset)")
        print(f"   • uber_kpi_summary.csv (KPI metrics)")
        print(f"   • uber_hourly_aggregation.csv (Hourly data)")
        print(f"   • uber_daily_aggregation.csv (Daily data)")
        print(f"   • uber_borough_aggregation.csv (Borough data)")

def main():
    """Main function to run Tableau preparation"""
    prep = TableauDataPrep('uber_enhanced.csv')
    prep.load_and_prepare_data()
    tableau_df = prep.create_tableau_optimized_dataset()
    prep.create_interactive_dashboard()
    prep.create_summary_statistics()
    prep.generate_tableau_instructions()
    
    print(f"\n🎯 Tableau preparation completed successfully!")
    print(f"📊 Ready for Tableau Public dashboard creation!")

if __name__ == "__main__":
    main()

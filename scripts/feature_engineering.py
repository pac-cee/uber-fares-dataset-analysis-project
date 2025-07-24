#!/usr/bin/env python3
"""
Feature Engineering for Uber Fares Dataset
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class UberFeatureEngineer:
    """
    Comprehensive feature engineering class for Uber Fares dataset
    """
    
    def __init__(self, data_path='uber_cleaned.csv'):
        """Initialize the feature engineer"""
        self.data_path = data_path
        self.df = None
        self.df_enhanced = None
        
    def load_cleaned_data(self):
        """Load the cleaned dataset"""
        print("=" * 80)
        print("UBER FARES DATASET - FEATURE ENGINEERING")
        print("=" * 80)
        
        self.df = pd.read_csv(self.data_path)
        # Convert pickup_datetime back to datetime if it's not already
        if self.df['pickup_datetime'].dtype == 'object':
            self.df['pickup_datetime'] = pd.to_datetime(self.df['pickup_datetime'])
        
        self.df_enhanced = self.df.copy()
        
        print(f"\n📊 Cleaned dataset loaded:")
        print(f"   • Shape: {self.df.shape}")
        print(f"   • Columns: {list(self.df.columns)}")
        print(f"   • Date range: {self.df['pickup_datetime'].min()} to {self.df['pickup_datetime'].max()}")
        
        return True
    
    def extract_temporal_features(self):
        """Extract comprehensive temporal features"""
        print("\n" + "=" * 60)
        print("1. EXTRACTING TEMPORAL FEATURES")
        print("=" * 60)
        
        # Extract basic time components
        self.df_enhanced['pickup_year'] = self.df_enhanced['pickup_datetime'].dt.year
        self.df_enhanced['pickup_month'] = self.df_enhanced['pickup_datetime'].dt.month
        self.df_enhanced['pickup_day'] = self.df_enhanced['pickup_datetime'].dt.day
        self.df_enhanced['pickup_hour'] = self.df_enhanced['pickup_datetime'].dt.hour
        self.df_enhanced['pickup_minute'] = self.df_enhanced['pickup_datetime'].dt.minute
        self.df_enhanced['pickup_weekday'] = self.df_enhanced['pickup_datetime'].dt.dayofweek
        self.df_enhanced['pickup_week'] = self.df_enhanced['pickup_datetime'].dt.isocalendar().week
        
        # Create categorical time features
        self.df_enhanced['day_of_week'] = self.df_enhanced['pickup_datetime'].dt.day_name()
        self.df_enhanced['month_name'] = self.df_enhanced['pickup_datetime'].dt.month_name()
        
        # Create time periods
        def get_time_period(hour):
            if 5 <= hour < 12:
                return 'Morning'
            elif 12 <= hour < 17:
                return 'Afternoon'
            elif 17 <= hour < 21:
                return 'Evening'
            else:
                return 'Night'
        
        self.df_enhanced['time_period'] = self.df_enhanced['pickup_hour'].apply(get_time_period)
        
        # Create weekend indicator
        self.df_enhanced['is_weekend'] = (self.df_enhanced['pickup_weekday'] >= 5).astype(int)
        
        # Create peak hours indicator (rush hours)
        def is_peak_hour(hour, weekday):
            # Weekday rush hours: 7-9 AM and 5-7 PM
            # Weekend peak: 11 AM - 2 PM and 6-8 PM
            if weekday < 5:  # Weekday
                return 1 if (7 <= hour <= 9) or (17 <= hour <= 19) else 0
            else:  # Weekend
                return 1 if (11 <= hour <= 14) or (18 <= hour <= 20) else 0
        
        self.df_enhanced['is_peak_hour'] = self.df_enhanced.apply(
            lambda row: is_peak_hour(row['pickup_hour'], row['pickup_weekday']), axis=1
        )
        
        print(f"\n✅ Extracted temporal features:")
        temporal_features = ['pickup_year', 'pickup_month', 'pickup_day', 'pickup_hour', 
                           'pickup_weekday', 'day_of_week', 'month_name', 'time_period', 
                           'is_weekend', 'is_peak_hour']
        for feature in temporal_features:
            print(f"   • {feature}")
        
        # Show some statistics
        print(f"\n📊 Temporal feature distributions:")
        print(f"   • Years: {sorted(self.df_enhanced['pickup_year'].unique())}")
        print(f"   • Time periods: {self.df_enhanced['time_period'].value_counts().to_dict()}")
        print(f"   • Weekend vs Weekday: {self.df_enhanced['is_weekend'].value_counts().to_dict()}")
        print(f"   • Peak vs Off-peak: {self.df_enhanced['is_peak_hour'].value_counts().to_dict()}")
    
    def calculate_distance_features(self):
        """Calculate distance and geographical features"""
        print("\n" + "=" * 60)
        print("2. CALCULATING DISTANCE FEATURES")
        print("=" * 60)
        
        def haversine_distance(lat1, lon1, lat2, lon2):
            """Calculate the great circle distance between two points on earth"""
            # Convert decimal degrees to radians
            lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
            
            # Haversine formula
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
            c = 2 * np.arcsin(np.sqrt(a))
            
            # Radius of earth in kilometers
            r = 6371
            return c * r
        
        # Calculate trip distance
        self.df_enhanced['trip_distance_km'] = haversine_distance(
            self.df_enhanced['pickup_latitude'],
            self.df_enhanced['pickup_longitude'],
            self.df_enhanced['dropoff_latitude'],
            self.df_enhanced['dropoff_longitude']
        )
        
        # Calculate Manhattan distance (approximation)
        self.df_enhanced['manhattan_distance_km'] = (
            abs(self.df_enhanced['pickup_latitude'] - self.df_enhanced['dropoff_latitude']) * 111 +
            abs(self.df_enhanced['pickup_longitude'] - self.df_enhanced['dropoff_longitude']) * 85
        )
        
        # Calculate fare per kilometer
        self.df_enhanced['fare_per_km'] = self.df_enhanced['fare_amount'] / (self.df_enhanced['trip_distance_km'] + 0.001)  # Add small value to avoid division by zero
        
        # Create distance categories
        def categorize_distance(distance):
            if distance < 1:
                return 'Very Short'
            elif distance < 3:
                return 'Short'
            elif distance < 7:
                return 'Medium'
            elif distance < 15:
                return 'Long'
            else:
                return 'Very Long'
        
        self.df_enhanced['distance_category'] = self.df_enhanced['trip_distance_km'].apply(categorize_distance)
        
        print(f"\n✅ Calculated distance features:")
        print(f"   • trip_distance_km")
        print(f"   • manhattan_distance_km")
        print(f"   • fare_per_km")
        print(f"   • distance_category")
        
        print(f"\n📊 Distance statistics:")
        print(f"   • Average trip distance: {self.df_enhanced['trip_distance_km'].mean():.2f} km")
        print(f"   • Median trip distance: {self.df_enhanced['trip_distance_km'].median():.2f} km")
        print(f"   • Average fare per km: ${self.df_enhanced['fare_per_km'].mean():.2f}")
        print(f"   • Distance categories: {self.df_enhanced['distance_category'].value_counts().to_dict()}")
    
    def create_location_features(self):
        """Create location-based features"""
        print("\n" + "=" * 60)
        print("3. CREATING LOCATION FEATURES")
        print("=" * 60)
        
        # NYC borough boundaries (approximate)
        def get_borough(lat, lon):
            """Approximate borough classification based on coordinates"""
            # Manhattan
            if -74.02 <= lon <= -73.93 and 40.70 <= lat <= 40.88:
                return 'Manhattan'
            # Brooklyn
            elif -74.05 <= lon <= -73.83 and 40.57 <= lat <= 40.74:
                return 'Brooklyn'
            # Queens
            elif -73.96 <= lon <= -73.70 and 40.54 <= lat <= 40.80:
                return 'Queens'
            # Bronx
            elif -73.93 <= lon <= -73.77 and 40.79 <= lat <= 40.92:
                return 'Bronx'
            # Staten Island
            elif -74.26 <= lon <= -74.05 and 40.48 <= lat <= 40.65:
                return 'Staten Island'
            else:
                return 'Other'
        
        # Get pickup and dropoff boroughs
        self.df_enhanced['pickup_borough'] = self.df_enhanced.apply(
            lambda row: get_borough(row['pickup_latitude'], row['pickup_longitude']), axis=1
        )
        self.df_enhanced['dropoff_borough'] = self.df_enhanced.apply(
            lambda row: get_borough(row['dropoff_latitude'], row['dropoff_longitude']), axis=1
        )
        
        # Create inter-borough trip indicator
        self.df_enhanced['is_inter_borough'] = (
            self.df_enhanced['pickup_borough'] != self.df_enhanced['dropoff_borough']
        ).astype(int)
        
        # Distance from city center (Times Square: 40.7580, -73.9855)
        times_square_lat, times_square_lon = 40.7580, -73.9855
        
        def distance_from_center(lat, lon):
            return np.sqrt((lat - times_square_lat)**2 + (lon - times_square_lon)**2) * 111  # Approximate km
        
        self.df_enhanced['pickup_distance_from_center'] = self.df_enhanced.apply(
            lambda row: distance_from_center(row['pickup_latitude'], row['pickup_longitude']), axis=1
        )
        self.df_enhanced['dropoff_distance_from_center'] = self.df_enhanced.apply(
            lambda row: distance_from_center(row['dropoff_latitude'], row['dropoff_longitude']), axis=1
        )
        
        print(f"\n✅ Created location features:")
        print(f"   • pickup_borough")
        print(f"   • dropoff_borough")
        print(f"   • is_inter_borough")
        print(f"   • pickup_distance_from_center")
        print(f"   • dropoff_distance_from_center")
        
        print(f"\n📊 Location statistics:")
        print(f"   • Pickup boroughs: {self.df_enhanced['pickup_borough'].value_counts().to_dict()}")
        print(f"   • Inter-borough trips: {self.df_enhanced['is_inter_borough'].value_counts().to_dict()}")
    
    def create_passenger_features(self):
        """Create passenger-related features"""
        print("\n" + "=" * 60)
        print("4. CREATING PASSENGER FEATURES")
        print("=" * 60)
        
        # Fare per passenger
        self.df_enhanced['fare_per_passenger'] = self.df_enhanced['fare_amount'] / self.df_enhanced['passenger_count']
        
        # Passenger category
        def categorize_passengers(count):
            if count == 1:
                return 'Solo'
            elif count == 2:
                return 'Couple'
            elif count <= 4:
                return 'Small Group'
            else:
                return 'Large Group'
        
        self.df_enhanced['passenger_category'] = self.df_enhanced['passenger_count'].apply(categorize_passengers)
        
        print(f"\n✅ Created passenger features:")
        print(f"   • fare_per_passenger")
        print(f"   • passenger_category")
        
        print(f"\n📊 Passenger statistics:")
        print(f"   • Average fare per passenger: ${self.df_enhanced['fare_per_passenger'].mean():.2f}")
        print(f"   • Passenger categories: {self.df_enhanced['passenger_category'].value_counts().to_dict()}")
    
    def generate_feature_summary(self):
        """Generate a comprehensive feature summary"""
        print("\n" + "=" * 80)
        print("FEATURE ENGINEERING SUMMARY")
        print("=" * 80)
        
        original_features = len(self.df.columns)
        new_features = len(self.df_enhanced.columns)
        added_features = new_features - original_features
        
        print(f"\n📊 Feature Statistics:")
        print(f"   • Original features: {original_features}")
        print(f"   • Enhanced features: {new_features}")
        print(f"   • New features added: {added_features}")
        
        print(f"\n📋 All Features:")
        for i, col in enumerate(self.df_enhanced.columns, 1):
            feature_type = "Original" if col in self.df.columns else "New"
            print(f"   {i:2d}. {col:30s} ({feature_type})")
        
        print(f"\n📊 Dataset Info:")
        print(f"   • Shape: {self.df_enhanced.shape}")
        print(f"   • Memory usage: {self.df_enhanced.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    
    def save_enhanced_data(self, output_path='uber_enhanced.csv'):
        """Save the enhanced dataset"""
        self.df_enhanced.to_csv(output_path, index=False)
        print(f"\n💾 Enhanced dataset saved to: {output_path}")
        return output_path
    
    def run_feature_engineering(self):
        """Run the complete feature engineering pipeline"""
        self.load_cleaned_data()
        self.extract_temporal_features()
        self.calculate_distance_features()
        self.create_location_features()
        self.create_passenger_features()
        self.generate_feature_summary()
        
        return self.df_enhanced

def main():
    """Main function to run feature engineering"""
    engineer = UberFeatureEngineer('uber_cleaned.csv')
    enhanced_df = engineer.run_feature_engineering()
    output_file = engineer.save_enhanced_data()
    
    print(f"\n🎯 Feature engineering completed successfully!")
    print(f"📁 Enhanced data saved to: {output_file}")
    
    return enhanced_df

if __name__ == "__main__":
    main()

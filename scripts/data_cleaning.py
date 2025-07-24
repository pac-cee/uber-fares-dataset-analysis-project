#!/usr/bin/env python3
"""
Comprehensive Data Cleaning and Preprocessing for Uber Fares Dataset
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class UberDataCleaner:
    """
    Comprehensive data cleaning class for Uber Fares dataset
    """
    
    def __init__(self, data_path='uber.csv'):
        """Initialize the data cleaner"""
        self.data_path = data_path
        self.df_original = None
        self.df_cleaned = None
        self.cleaning_report = {}
        
    def load_data(self):
        """Load the original dataset"""
        print("=" * 80)
        print("UBER FARES DATASET - DATA CLEANING & PREPROCESSING")
        print("=" * 80)
        
        self.df_original = pd.read_csv(self.data_path)
        self.df_cleaned = self.df_original.copy()
        
        print(f"\n📊 Original dataset loaded:")
        print(f"   • Shape: {self.df_original.shape}")
        print(f"   • Memory usage: {self.df_original.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        
        return True
    
    def handle_missing_values(self):
        """Handle missing values in the dataset"""
        print("\n" + "=" * 60)
        print("1. HANDLING MISSING VALUES")
        print("=" * 60)
        
        # Check missing values
        missing_before = self.df_cleaned.isnull().sum()
        print(f"\n📊 Missing values before cleaning:")
        for col, count in missing_before.items():
            if count > 0:
                print(f"   • {col}: {count} ({count/len(self.df_cleaned)*100:.4f}%)")
        
        # Remove rows with missing coordinates (very few)
        initial_rows = len(self.df_cleaned)
        self.df_cleaned = self.df_cleaned.dropna(subset=['dropoff_longitude', 'dropoff_latitude'])
        rows_removed = initial_rows - len(self.df_cleaned)
        
        print(f"\n✅ Removed {rows_removed} rows with missing coordinates")
        
        # Update cleaning report
        self.cleaning_report['missing_values_removed'] = rows_removed
        
    def clean_fare_amounts(self):
        """Clean fare amount data"""
        print("\n" + "=" * 60)
        print("2. CLEANING FARE AMOUNTS")
        print("=" * 60)
        
        # Analyze fare amounts
        print(f"\n📊 Fare amount statistics before cleaning:")
        print(f"   • Min: ${self.df_cleaned['fare_amount'].min():.2f}")
        print(f"   • Max: ${self.df_cleaned['fare_amount'].max():.2f}")
        print(f"   • Mean: ${self.df_cleaned['fare_amount'].mean():.2f}")
        print(f"   • Median: ${self.df_cleaned['fare_amount'].median():.2f}")
        
        # Remove negative and zero fares
        initial_rows = len(self.df_cleaned)
        self.df_cleaned = self.df_cleaned[self.df_cleaned['fare_amount'] > 0]
        negative_removed = initial_rows - len(self.df_cleaned)
        
        # Remove extremely high fares (outliers) - using IQR method
        Q1 = self.df_cleaned['fare_amount'].quantile(0.25)
        Q3 = self.df_cleaned['fare_amount'].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        # For fare amounts, we'll use a more reasonable upper bound
        # Most NYC taxi fares should be under $100
        reasonable_upper_bound = min(upper_bound, 100)
        
        initial_rows = len(self.df_cleaned)
        self.df_cleaned = self.df_cleaned[
            (self.df_cleaned['fare_amount'] >= lower_bound) & 
            (self.df_cleaned['fare_amount'] <= reasonable_upper_bound)
        ]
        outliers_removed = initial_rows - len(self.df_cleaned)
        
        print(f"\n✅ Removed {negative_removed} rows with negative/zero fares")
        print(f"✅ Removed {outliers_removed} rows with extreme fare amounts (>${reasonable_upper_bound:.2f})")
        
        print(f"\n📊 Fare amount statistics after cleaning:")
        print(f"   • Min: ${self.df_cleaned['fare_amount'].min():.2f}")
        print(f"   • Max: ${self.df_cleaned['fare_amount'].max():.2f}")
        print(f"   • Mean: ${self.df_cleaned['fare_amount'].mean():.2f}")
        print(f"   • Median: ${self.df_cleaned['fare_amount'].median():.2f}")
        
        # Update cleaning report
        self.cleaning_report['negative_fares_removed'] = negative_removed
        self.cleaning_report['fare_outliers_removed'] = outliers_removed
    
    def clean_coordinates(self):
        """Clean pickup and dropoff coordinates"""
        print("\n" + "=" * 60)
        print("3. CLEANING COORDINATES")
        print("=" * 60)
        
        # NYC approximate boundaries
        # Longitude: -74.3 to -73.7 (West to East)
        # Latitude: 40.4 to 41.0 (South to North)
        nyc_bounds = {
            'min_longitude': -74.3,
            'max_longitude': -73.7,
            'min_latitude': 40.4,
            'max_latitude': 41.0
        }
        
        print(f"\n📊 Coordinate ranges before cleaning:")
        print(f"   • Pickup Longitude: {self.df_cleaned['pickup_longitude'].min():.6f} to {self.df_cleaned['pickup_longitude'].max():.6f}")
        print(f"   • Pickup Latitude: {self.df_cleaned['pickup_latitude'].min():.6f} to {self.df_cleaned['pickup_latitude'].max():.6f}")
        print(f"   • Dropoff Longitude: {self.df_cleaned['dropoff_longitude'].min():.6f} to {self.df_cleaned['dropoff_longitude'].max():.6f}")
        print(f"   • Dropoff Latitude: {self.df_cleaned['dropoff_latitude'].min():.6f} to {self.df_cleaned['dropoff_latitude'].max():.6f}")
        
        # Filter coordinates within NYC bounds
        initial_rows = len(self.df_cleaned)
        
        self.df_cleaned = self.df_cleaned[
            (self.df_cleaned['pickup_longitude'] >= nyc_bounds['min_longitude']) &
            (self.df_cleaned['pickup_longitude'] <= nyc_bounds['max_longitude']) &
            (self.df_cleaned['pickup_latitude'] >= nyc_bounds['min_latitude']) &
            (self.df_cleaned['pickup_latitude'] <= nyc_bounds['max_latitude']) &
            (self.df_cleaned['dropoff_longitude'] >= nyc_bounds['min_longitude']) &
            (self.df_cleaned['dropoff_longitude'] <= nyc_bounds['max_longitude']) &
            (self.df_cleaned['dropoff_latitude'] >= nyc_bounds['min_latitude']) &
            (self.df_cleaned['dropoff_latitude'] <= nyc_bounds['max_latitude'])
        ]
        
        coordinate_outliers_removed = initial_rows - len(self.df_cleaned)
        
        print(f"\n✅ Removed {coordinate_outliers_removed} rows with coordinates outside NYC bounds")
        
        print(f"\n📊 Coordinate ranges after cleaning:")
        print(f"   • Pickup Longitude: {self.df_cleaned['pickup_longitude'].min():.6f} to {self.df_cleaned['pickup_longitude'].max():.6f}")
        print(f"   • Pickup Latitude: {self.df_cleaned['pickup_latitude'].min():.6f} to {self.df_cleaned['pickup_latitude'].max():.6f}")
        print(f"   • Dropoff Longitude: {self.df_cleaned['dropoff_longitude'].min():.6f} to {self.df_cleaned['dropoff_longitude'].max():.6f}")
        print(f"   • Dropoff Latitude: {self.df_cleaned['dropoff_latitude'].min():.6f} to {self.df_cleaned['dropoff_latitude'].max():.6f}")
        
        # Update cleaning report
        self.cleaning_report['coordinate_outliers_removed'] = coordinate_outliers_removed
    
    def clean_passenger_count(self):
        """Clean passenger count data"""
        print("\n" + "=" * 60)
        print("4. CLEANING PASSENGER COUNT")
        print("=" * 60)
        
        print(f"\n📊 Passenger count distribution before cleaning:")
        print(self.df_cleaned['passenger_count'].value_counts().sort_index())
        
        # Remove unrealistic passenger counts (0 or > 6)
        initial_rows = len(self.df_cleaned)
        self.df_cleaned = self.df_cleaned[
            (self.df_cleaned['passenger_count'] >= 1) & 
            (self.df_cleaned['passenger_count'] <= 6)
        ]
        passenger_outliers_removed = initial_rows - len(self.df_cleaned)
        
        print(f"\n✅ Removed {passenger_outliers_removed} rows with unrealistic passenger counts")
        
        print(f"\n📊 Passenger count distribution after cleaning:")
        print(self.df_cleaned['passenger_count'].value_counts().sort_index())
        
        # Update cleaning report
        self.cleaning_report['passenger_outliers_removed'] = passenger_outliers_removed
    
    def convert_datetime(self):
        """Convert pickup_datetime to proper datetime format"""
        print("\n" + "=" * 60)
        print("5. CONVERTING DATETIME")
        print("=" * 60)
        
        print(f"\n📊 Sample datetime values before conversion:")
        print(self.df_cleaned['pickup_datetime'].head())
        
        # Convert to datetime
        self.df_cleaned['pickup_datetime'] = pd.to_datetime(self.df_cleaned['pickup_datetime'])
        
        print(f"\n✅ Converted pickup_datetime to datetime format")
        print(f"\n📊 Datetime range:")
        print(f"   • Earliest: {self.df_cleaned['pickup_datetime'].min()}")
        print(f"   • Latest: {self.df_cleaned['pickup_datetime'].max()}")
        print(f"   • Date range: {(self.df_cleaned['pickup_datetime'].max() - self.df_cleaned['pickup_datetime'].min()).days} days")
    
    def remove_unnecessary_columns(self):
        """Remove unnecessary columns"""
        print("\n" + "=" * 60)
        print("6. REMOVING UNNECESSARY COLUMNS")
        print("=" * 60)
        
        # Remove the unnamed index column and key column
        columns_to_remove = ['Unnamed: 0', 'key']
        existing_columns = [col for col in columns_to_remove if col in self.df_cleaned.columns]
        
        if existing_columns:
            self.df_cleaned = self.df_cleaned.drop(columns=existing_columns)
            print(f"\n✅ Removed columns: {existing_columns}")
        
        print(f"\n📊 Final columns: {list(self.df_cleaned.columns)}")
    
    def generate_cleaning_summary(self):
        """Generate a comprehensive cleaning summary"""
        print("\n" + "=" * 80)
        print("DATA CLEANING SUMMARY")
        print("=" * 80)
        
        original_rows = len(self.df_original)
        final_rows = len(self.df_cleaned)
        total_removed = original_rows - final_rows
        
        print(f"\n📊 Overall Statistics:")
        print(f"   • Original rows: {original_rows:,}")
        print(f"   • Final rows: {final_rows:,}")
        print(f"   • Total rows removed: {total_removed:,} ({total_removed/original_rows*100:.2f}%)")
        print(f"   • Data retention rate: {final_rows/original_rows*100:.2f}%")
        
        print(f"\n📋 Detailed Cleaning Report:")
        for key, value in self.cleaning_report.items():
            print(f"   • {key.replace('_', ' ').title()}: {value:,}")
        
        print(f"\n📊 Final Dataset Info:")
        print(f"   • Shape: {self.df_cleaned.shape}")
        print(f"   • Memory usage: {self.df_cleaned.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        print(f"   • Data types: {dict(self.df_cleaned.dtypes.value_counts())}")
    
    def save_cleaned_data(self, output_path='uber_cleaned.csv'):
        """Save the cleaned dataset"""
        self.df_cleaned.to_csv(output_path, index=False)
        print(f"\n💾 Cleaned dataset saved to: {output_path}")
        return output_path
    
    def run_full_cleaning(self):
        """Run the complete data cleaning pipeline"""
        self.load_data()
        self.handle_missing_values()
        self.clean_fare_amounts()
        self.clean_coordinates()
        self.clean_passenger_count()
        self.convert_datetime()
        self.remove_unnecessary_columns()
        self.generate_cleaning_summary()
        
        return self.df_cleaned

def main():
    """Main function to run data cleaning"""
    cleaner = UberDataCleaner('uber.csv')
    cleaned_df = cleaner.run_full_cleaning()
    output_file = cleaner.save_cleaned_data()
    
    print(f"\n🎯 Data cleaning completed successfully!")
    print(f"📁 Cleaned data saved to: {output_file}")
    
    return cleaned_df

if __name__ == "__main__":
    main()

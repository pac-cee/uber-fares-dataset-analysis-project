#!/usr/bin/env python3
"""
Quick Data Exploration for Uber Fares Dataset
"""

import pandas as pd
import numpy as np

# Load the dataset
print("Loading Uber dataset...")
df = pd.read_csv('uber.csv')

print("=" * 60)
print("UBER FARES DATASET - QUICK EXPLORATION")
print("=" * 60)

print(f"\n1. Dataset Shape: {df.shape}")
print(f"   Rows: {df.shape[0]:,}")
print(f"   Columns: {df.shape[1]}")

print(f"\n2. Column Names:")
for i, col in enumerate(df.columns, 1):
    print(f"   {i}. {col}")

print(f"\n3. Data Types:")
print(df.dtypes)

print(f"\n4. First 5 rows:")
print(df.head())

print(f"\n5. Basic Info:")
print(df.info())

print(f"\n6. Missing Values:")
missing = df.isnull().sum()
print(missing[missing > 0])

print(f"\n7. Numerical Columns Summary:")
numerical_cols = df.select_dtypes(include=[np.number]).columns
print(df[numerical_cols].describe())

print(f"\n8. Unique Values per Column:")
for col in df.columns:
    print(f"   {col}: {df[col].nunique():,} unique values")

print(f"\n9. Sample of pickup_datetime values:")
print(df['pickup_datetime'].head(10))

print(f"\n10. Passenger count distribution:")
print(df['passenger_count'].value_counts().sort_index())

print(f"\n11. Fare amount statistics:")
print(f"    Min: ${df['fare_amount'].min():.2f}")
print(f"    Max: ${df['fare_amount'].max():.2f}")
print(f"    Mean: ${df['fare_amount'].mean():.2f}")
print(f"    Median: ${df['fare_amount'].median():.2f}")

print("\n" + "=" * 60)
print("EXPLORATION COMPLETED!")
print("=" * 60)

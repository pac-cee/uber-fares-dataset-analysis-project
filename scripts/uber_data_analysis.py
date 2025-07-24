#!/usr/bin/env python3
"""
Uber Fares Dataset Analysis
===========================

This script performs comprehensive analysis of the Uber Fares dataset including:
1. Data Understanding and Initial EDA
2. Data Cleaning and Preprocessing  
3. Feature Engineering
4. Advanced Data Analysis
5. Visualization and Insights

Author: Data Analysis Team
Date: July 2025
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
from datetime import datetime
import os

# Configure display options
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)
warnings.filterwarnings('ignore')

# Set style for matplotlib
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class UberDataAnalyzer:
    """
    A comprehensive class for analyzing Uber Fares dataset
    """
    
    def __init__(self, data_path='uber.csv'):
        """
        Initialize the analyzer with the dataset
        
        Args:
            data_path (str): Path to the Uber dataset CSV file
        """
        self.data_path = data_path
        self.df = None
        self.df_cleaned = None
        self.df_enhanced = None
        
    def load_data(self):
        """
        Load the Uber dataset and perform initial inspection
        """
        print("=" * 80)
        print("UBER FARES DATASET ANALYSIS")
        print("=" * 80)
        print(f"\n📊 Loading dataset from: {self.data_path}")
        
        try:
            self.df = pd.read_csv(self.data_path)
            print(f"✅ Dataset loaded successfully!")
            print(f"📈 Dataset shape: {self.df.shape}")
            return True
        except FileNotFoundError:
            print(f"❌ Error: File {self.data_path} not found!")
            return False
        except Exception as e:
            print(f"❌ Error loading dataset: {str(e)}")
            return False
    
    def data_overview(self):
        """
        Provide comprehensive overview of the dataset
        """
        print("\n" + "=" * 60)
        print("1. DATASET STRUCTURE AND OVERVIEW")
        print("=" * 60)
        
        print(f"\n📊 Dataset Dimensions:")
        print(f"   • Rows: {self.df.shape[0]:,}")
        print(f"   • Columns: {self.df.shape[1]}")
        
        print(f"\n📋 Column Information:")
        print(self.df.info())
        
        print(f"\n🔍 First 5 rows:")
        print(self.df.head())
        
        print(f"\n🔍 Last 5 rows:")
        print(self.df.tail())
        
        print(f"\n📊 Column Names:")
        for i, col in enumerate(self.df.columns, 1):
            print(f"   {i:2d}. {col}")
    
    def data_types_analysis(self):
        """
        Analyze data types and identify potential issues
        """
        print("\n" + "=" * 60)
        print("2. DATA TYPES ANALYSIS")
        print("=" * 60)
        
        print(f"\n📊 Data Types Summary:")
        dtype_counts = self.df.dtypes.value_counts()
        for dtype, count in dtype_counts.items():
            print(f"   • {dtype}: {count} columns")
        
        print(f"\n📋 Detailed Data Types:")
        for col in self.df.columns:
            dtype = self.df[col].dtype
            unique_count = self.df[col].nunique()
            print(f"   • {col:20s} | {str(dtype):10s} | {unique_count:,} unique values")
    
    def missing_values_analysis(self):
        """
        Comprehensive analysis of missing values
        """
        print("\n" + "=" * 60)
        print("3. MISSING VALUES ANALYSIS")
        print("=" * 60)
        
        missing_data = self.df.isnull().sum()
        missing_percent = (missing_data / len(self.df)) * 100
        
        missing_df = pd.DataFrame({
            'Column': missing_data.index,
            'Missing_Count': missing_data.values,
            'Missing_Percentage': missing_percent.values
        }).sort_values('Missing_Count', ascending=False)
        
        print(f"\n📊 Missing Values Summary:")
        if missing_df['Missing_Count'].sum() == 0:
            print("   ✅ No missing values found in the dataset!")
        else:
            print(missing_df[missing_df['Missing_Count'] > 0])
            
            # Visualize missing values
            plt.figure(figsize=(12, 6))
            missing_cols = missing_df[missing_df['Missing_Count'] > 0]
            if not missing_cols.empty:
                plt.subplot(1, 2, 1)
                plt.bar(missing_cols['Column'], missing_cols['Missing_Count'])
                plt.title('Missing Values Count by Column')
                plt.xticks(rotation=45)
                plt.ylabel('Count')
                
                plt.subplot(1, 2, 2)
                plt.bar(missing_cols['Column'], missing_cols['Missing_Percentage'])
                plt.title('Missing Values Percentage by Column')
                plt.xticks(rotation=45)
                plt.ylabel('Percentage (%)')
                
                plt.tight_layout()
                plt.savefig('missing_values_analysis.png', dpi=300, bbox_inches='tight')
                plt.show()
    
    def descriptive_statistics(self):
        """
        Generate comprehensive descriptive statistics
        """
        print("\n" + "=" * 60)
        print("4. DESCRIPTIVE STATISTICS")
        print("=" * 60)
        
        # Numerical columns
        numerical_cols = self.df.select_dtypes(include=[np.number]).columns
        if len(numerical_cols) > 0:
            print(f"\n📊 Numerical Columns Statistics:")
            desc_stats = self.df[numerical_cols].describe()
            print(desc_stats)
            
            # Additional statistics
            print(f"\n📈 Additional Statistics for Numerical Columns:")
            for col in numerical_cols:
                print(f"\n   {col}:")
                print(f"      • Skewness: {self.df[col].skew():.4f}")
                print(f"      • Kurtosis: {self.df[col].kurtosis():.4f}")
                print(f"      • Variance: {self.df[col].var():.4f}")
        
        # Categorical columns
        categorical_cols = self.df.select_dtypes(include=['object']).columns
        if len(categorical_cols) > 0:
            print(f"\n📊 Categorical Columns Summary:")
            for col in categorical_cols:
                unique_count = self.df[col].nunique()
                most_frequent = self.df[col].mode().iloc[0] if len(self.df[col].mode()) > 0 else 'N/A'
                print(f"   • {col}: {unique_count} unique values, Most frequent: '{most_frequent}'")
    
    def detect_outliers(self):
        """
        Detect outliers using IQR method
        """
        print("\n" + "=" * 60)
        print("5. OUTLIER DETECTION")
        print("=" * 60)
        
        numerical_cols = self.df.select_dtypes(include=[np.number]).columns
        outlier_summary = {}
        
        for col in numerical_cols:
            Q1 = self.df[col].quantile(0.25)
            Q3 = self.df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = self.df[(self.df[col] < lower_bound) | (self.df[col] > upper_bound)]
            outlier_count = len(outliers)
            outlier_percentage = (outlier_count / len(self.df)) * 100
            
            outlier_summary[col] = {
                'count': outlier_count,
                'percentage': outlier_percentage,
                'lower_bound': lower_bound,
                'upper_bound': upper_bound
            }
            
            print(f"\n   📊 {col}:")
            print(f"      • Outliers: {outlier_count:,} ({outlier_percentage:.2f}%)")
            print(f"      • Valid range: [{lower_bound:.2f}, {upper_bound:.2f}]")
        
        return outlier_summary

def main():
    """
    Main function to run the analysis
    """
    # Initialize analyzer
    analyzer = UberDataAnalyzer('uber.csv')
    
    # Load data
    if not analyzer.load_data():
        return
    
    # Perform comprehensive analysis
    analyzer.data_overview()
    analyzer.data_types_analysis()
    analyzer.missing_values_analysis()
    analyzer.descriptive_statistics()
    outlier_info = analyzer.detect_outliers()
    
    print("\n" + "=" * 80)
    print("✅ INITIAL DATA ANALYSIS COMPLETED!")
    print("=" * 80)
    print("\n📋 Summary:")
    print(f"   • Dataset loaded with {analyzer.df.shape[0]:,} rows and {analyzer.df.shape[1]} columns")
    print(f"   • Missing values analysis completed")
    print(f"   • Descriptive statistics generated")
    print(f"   • Outlier detection performed")
    print("\n🎯 Ready for data cleaning and feature engineering!")

if __name__ == "__main__":
    main()

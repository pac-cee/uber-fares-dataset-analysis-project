#!/usr/bin/env python3
"""
Advanced Data Analysis for Uber Fares Dataset
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import warnings
warnings.filterwarnings('ignore')

# Set style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class UberAdvancedAnalysis:
    """
    Advanced analysis class for Uber Fares dataset
    """
    
    def __init__(self, data_path='uber_enhanced.csv'):
        """Initialize the advanced analyzer"""
        self.data_path = data_path
        self.df = None
        
    def load_data(self):
        """Load the enhanced dataset"""
        print("=" * 80)
        print("UBER FARES DATASET - ADVANCED DATA ANALYSIS")
        print("=" * 80)
        
        self.df = pd.read_csv(self.data_path)
        # Convert pickup_datetime back to datetime if needed
        if self.df['pickup_datetime'].dtype == 'object':
            self.df['pickup_datetime'] = pd.to_datetime(self.df['pickup_datetime'])
        
        print(f"\n📊 Enhanced dataset loaded:")
        print(f"   • Shape: {self.df.shape}")
        print(f"   • Features: {len(self.df.columns)}")
        
        return True
    
    def correlation_analysis(self):
        """Perform comprehensive correlation analysis"""
        print("\n" + "=" * 60)
        print("1. CORRELATION ANALYSIS")
        print("=" * 60)
        
        # Select numerical columns for correlation
        numerical_cols = self.df.select_dtypes(include=[np.number]).columns
        correlation_matrix = self.df[numerical_cols].corr()
        
        # Create correlation heatmap
        plt.figure(figsize=(16, 12))
        mask = np.triu(np.ones_like(correlation_matrix, dtype=bool))
        sns.heatmap(correlation_matrix, mask=mask, annot=True, cmap='coolwarm', center=0,
                   square=True, linewidths=0.5, cbar_kws={"shrink": .8}, fmt='.2f')
        plt.title('Correlation Matrix of Numerical Features', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig('correlation_matrix.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # Find strongest correlations with fare_amount
        fare_correlations = correlation_matrix['fare_amount'].abs().sort_values(ascending=False)
        
        print(f"\n📊 Strongest correlations with fare_amount:")
        for feature, corr in fare_correlations.head(10).items():
            if feature != 'fare_amount':
                direction = "positive" if correlation_matrix.loc['fare_amount', feature] > 0 else "negative"
                print(f"   • {feature}: {corr:.3f} ({direction})")
        
        # Statistical significance tests
        print(f"\n📈 Statistical Significance Tests:")
        significant_correlations = []
        for col in numerical_cols:
            if col != 'fare_amount':
                corr_coef, p_value = stats.pearsonr(self.df['fare_amount'], self.df[col])
                if p_value < 0.05:  # Significant at 95% confidence level
                    significant_correlations.append((col, corr_coef, p_value))
        
        significant_correlations.sort(key=lambda x: abs(x[1]), reverse=True)
        for feature, corr, p_val in significant_correlations[:5]:
            print(f"   • {feature}: r={corr:.3f}, p-value={p_val:.2e}")
    
    def fare_prediction_factors(self):
        """Analyze factors that predict fare amounts"""
        print("\n" + "=" * 60)
        print("2. FARE PREDICTION FACTORS")
        print("=" * 60)
        
        # Create comprehensive fare factor analysis
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('Factors Affecting Fare Amounts', fontsize=16, fontweight='bold')
        
        # 1. Fare vs Distance
        axes[0, 0].scatter(self.df['trip_distance_km'], self.df['fare_amount'], alpha=0.5, s=1)
        axes[0, 0].set_xlabel('Trip Distance (km)')
        axes[0, 0].set_ylabel('Fare Amount ($)')
        axes[0, 0].set_title('Fare vs Trip Distance')
        
        # Add trend line
        z = np.polyfit(self.df['trip_distance_km'], self.df['fare_amount'], 1)
        p = np.poly1d(z)
        axes[0, 0].plot(self.df['trip_distance_km'], p(self.df['trip_distance_km']), "r--", alpha=0.8)
        
        # 2. Fare by hour (with confidence intervals)
        hourly_stats = self.df.groupby('pickup_hour')['fare_amount'].agg(['mean', 'std', 'count'])
        hourly_stats['se'] = hourly_stats['std'] / np.sqrt(hourly_stats['count'])
        hourly_stats['ci'] = 1.96 * hourly_stats['se']
        
        axes[0, 1].errorbar(hourly_stats.index, hourly_stats['mean'], 
                           yerr=hourly_stats['ci'], capsize=3, capthick=1)
        axes[0, 1].set_xlabel('Hour of Day')
        axes[0, 1].set_ylabel('Average Fare ($)')
        axes[0, 1].set_title('Hourly Fare Patterns (with 95% CI)')
        axes[0, 1].grid(True, alpha=0.3)
        
        # 3. Fare distribution by passenger category
        passenger_categories = ['Solo', 'Couple', 'Small Group', 'Large Group']
        fare_by_passenger = [self.df[self.df['passenger_category'] == cat]['fare_amount'].values 
                           for cat in passenger_categories]
        
        axes[0, 2].boxplot(fare_by_passenger, labels=passenger_categories)
        axes[0, 2].set_xlabel('Passenger Category')
        axes[0, 2].set_ylabel('Fare Amount ($)')
        axes[0, 2].set_title('Fare Distribution by Passenger Category')
        axes[0, 2].tick_params(axis='x', rotation=45)
        
        # 4. Fare vs Distance from center
        axes[1, 0].scatter(self.df['pickup_distance_from_center'], self.df['fare_amount'], alpha=0.5, s=1)
        axes[1, 0].set_xlabel('Distance from City Center (km)')
        axes[1, 0].set_ylabel('Fare Amount ($)')
        axes[1, 0].set_title('Fare vs Distance from Center')
        
        # 5. Weekend vs Weekday fare comparison
        weekend_fares = self.df[self.df['is_weekend'] == 1]['fare_amount']
        weekday_fares = self.df[self.df['is_weekend'] == 0]['fare_amount']
        
        axes[1, 1].hist([weekday_fares, weekend_fares], bins=30, alpha=0.7, 
                       label=['Weekday', 'Weekend'], color=['skyblue', 'lightcoral'])
        axes[1, 1].set_xlabel('Fare Amount ($)')
        axes[1, 1].set_ylabel('Frequency')
        axes[1, 1].set_title('Weekday vs Weekend Fare Distribution')
        axes[1, 1].legend()
        
        # 6. Borough comparison
        borough_order = ['Manhattan', 'Brooklyn', 'Queens', 'Bronx', 'Staten Island']
        borough_data = []
        borough_labels = []
        
        for borough in borough_order:
            if borough in self.df['pickup_borough'].values:
                borough_fares = self.df[self.df['pickup_borough'] == borough]['fare_amount']
                if len(borough_fares) > 100:  # Only include boroughs with sufficient data
                    borough_data.append(borough_fares.values)
                    borough_labels.append(borough)
        
        axes[1, 2].boxplot(borough_data, labels=borough_labels)
        axes[1, 2].set_xlabel('Pickup Borough')
        axes[1, 2].set_ylabel('Fare Amount ($)')
        axes[1, 2].set_title('Fare Distribution by Borough')
        axes[1, 2].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig('fare_prediction_factors.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # Statistical tests
        print(f"\n📊 Statistical Tests:")
        
        # T-test for weekend vs weekday
        t_stat, p_value = stats.ttest_ind(weekend_fares, weekday_fares)
        print(f"   • Weekend vs Weekday t-test: t={t_stat:.3f}, p-value={p_value:.2e}")
        
        # ANOVA for time periods
        time_periods = ['Morning', 'Afternoon', 'Evening', 'Night']
        period_fares = [self.df[self.df['time_period'] == period]['fare_amount'].values 
                       for period in time_periods]
        f_stat, p_value = stats.f_oneway(*period_fares)
        print(f"   • Time period ANOVA: F={f_stat:.3f}, p-value={p_value:.2e}")
        
        # Correlation with distance
        distance_corr, p_value = stats.pearsonr(self.df['trip_distance_km'], self.df['fare_amount'])
        print(f"   • Distance correlation: r={distance_corr:.3f}, p-value={p_value:.2e}")
    
    def seasonal_analysis(self):
        """Analyze seasonal patterns and trends"""
        print("\n" + "=" * 60)
        print("3. SEASONAL ANALYSIS")
        print("=" * 60)
        
        # Create seasonal analysis plots
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Seasonal Patterns and Trends', fontsize=16, fontweight='bold')
        
        # 1. Monthly trends
        monthly_stats = self.df.groupby('pickup_month').agg({
            'fare_amount': ['mean', 'count'],
            'trip_distance_km': 'mean'
        }).round(2)
        
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        axes[0, 0].plot(monthly_stats.index, monthly_stats[('fare_amount', 'mean')], 
                       marker='o', linewidth=2, markersize=8, color='red')
        axes[0, 0].set_xlabel('Month')
        axes[0, 0].set_ylabel('Average Fare ($)', color='red')
        axes[0, 0].set_title('Monthly Fare Trends')
        axes[0, 0].set_xticks(range(1, 13))
        axes[0, 0].set_xticklabels(months)
        axes[0, 0].grid(True, alpha=0.3)
        
        ax2 = axes[0, 0].twinx()
        ax2.bar(monthly_stats.index, monthly_stats[('fare_amount', 'count')], 
               alpha=0.3, color='blue')
        ax2.set_ylabel('Number of Rides', color='blue')
        
        # 2. Yearly trends (if multiple years available)
        yearly_stats = self.df.groupby('pickup_year').agg({
            'fare_amount': 'mean',
            'trip_distance_km': 'mean'
        })
        
        if len(yearly_stats) > 1:
            axes[0, 1].plot(yearly_stats.index, yearly_stats['fare_amount'], 
                           marker='o', linewidth=2, markersize=8)
            axes[0, 1].set_xlabel('Year')
            axes[0, 1].set_ylabel('Average Fare ($)')
            axes[0, 1].set_title('Yearly Fare Trends')
            axes[0, 1].grid(True, alpha=0.3)
        else:
            axes[0, 1].text(0.5, 0.5, 'Insufficient data\nfor yearly trends', 
                           ha='center', va='center', transform=axes[0, 1].transAxes,
                           fontsize=12)
            axes[0, 1].set_title('Yearly Trends (Insufficient Data)')
        
        # 3. Day of week patterns
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        daily_stats = self.df.groupby('day_of_week').agg({
            'fare_amount': 'mean',
            'trip_distance_km': 'mean'
        }).reindex(day_order)
        
        axes[1, 0].bar(daily_stats.index, daily_stats['fare_amount'], color='lightgreen')
        axes[1, 0].set_xlabel('Day of Week')
        axes[1, 0].set_ylabel('Average Fare ($)')
        axes[1, 0].set_title('Daily Fare Patterns')
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        # 4. Heatmap of hour vs day patterns
        pivot_data = self.df.groupby(['pickup_hour', 'pickup_weekday'])['fare_amount'].mean().unstack()
        day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        pivot_data.columns = day_names
        
        im = axes[1, 1].imshow(pivot_data.T, cmap='YlOrRd', aspect='auto')
        axes[1, 1].set_xlabel('Hour of Day')
        axes[1, 1].set_ylabel('Day of Week')
        axes[1, 1].set_title('Average Fare Heatmap (Hour vs Day)')
        axes[1, 1].set_xticks(range(0, 24, 4))
        axes[1, 1].set_xticklabels(range(0, 24, 4))
        axes[1, 1].set_yticks(range(7))
        axes[1, 1].set_yticklabels(day_names)
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=axes[1, 1])
        cbar.set_label('Average Fare ($)')
        
        plt.tight_layout()
        plt.savefig('seasonal_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # Print seasonal insights
        print(f"\n📊 Seasonal Insights:")
        highest_month = monthly_stats[('fare_amount', 'mean')].idxmax()
        lowest_month = monthly_stats[('fare_amount', 'mean')].idxmin()
        print(f"   • Highest fare month: {months[highest_month-1]} (${monthly_stats.loc[highest_month, ('fare_amount', 'mean')]:.2f})")
        print(f"   • Lowest fare month: {months[lowest_month-1]} (${monthly_stats.loc[lowest_month, ('fare_amount', 'mean')]:.2f})")
        
        highest_day = daily_stats['fare_amount'].idxmax()
        lowest_day = daily_stats['fare_amount'].idxmin()
        print(f"   • Highest fare day: {highest_day} (${daily_stats.loc[highest_day, 'fare_amount']:.2f})")
        print(f"   • Lowest fare day: {lowest_day} (${daily_stats.loc[lowest_day, 'fare_amount']:.2f})")

def main():
    """Main function to run advanced analysis"""
    analyzer = UberAdvancedAnalysis('uber_enhanced.csv')
    analyzer.load_data()
    analyzer.correlation_analysis()
    analyzer.fare_prediction_factors()
    analyzer.seasonal_analysis()
    
    print(f"\n🎯 Advanced analysis completed successfully!")
    print(f"📊 Generated visualizations:")
    print(f"   • correlation_matrix.png")
    print(f"   • fare_prediction_factors.png")
    print(f"   • seasonal_analysis.png")

if __name__ == "__main__":
    main()

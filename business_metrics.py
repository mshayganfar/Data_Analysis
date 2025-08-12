"""
Business Metrics Calculation Module for E-commerce Analysis

This module contains functions for calculating key business metrics and KPIs.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns

class EcommerceMetrics:
    """
    A class to calculate various e-commerce business metrics and generate visualizations.
    """
    
    def __init__(self, color_scheme: str = 'viridis'):
        """
        Initialize the metrics calculator.
        
        Args:
            color_scheme (str): Color scheme for visualizations
        """
        self.color_scheme = color_scheme
        
    def calculate_revenue_metrics(self, sales_data: pd.DataFrame, 
                                 comparison_data: Optional[pd.DataFrame] = None) -> Dict:
        """
        Calculate revenue-related metrics.
        
        Args:
            sales_data (pd.DataFrame): Current period sales data
            comparison_data (pd.DataFrame, optional): Previous period for comparison
            
        Returns:
            Dict: Revenue metrics including total revenue, growth rate, etc.
        """
        total_revenue = sales_data['price'].sum()
        total_orders = sales_data['order_id'].nunique()
        avg_order_value = sales_data.groupby('order_id')['price'].sum().mean()
        
        metrics = {
            'total_revenue': total_revenue,
            'total_orders': total_orders,
            'avg_order_value': avg_order_value,
            'total_items_sold': len(sales_data)
        }
        
        if comparison_data is not None:
            prev_revenue = comparison_data['price'].sum()
            prev_orders = comparison_data['order_id'].nunique()
            prev_aov = comparison_data.groupby('order_id')['price'].sum().mean()
            
            metrics.update({
                'revenue_growth_rate': ((total_revenue - prev_revenue) / prev_revenue) * 100,
                'order_growth_rate': ((total_orders - prev_orders) / prev_orders) * 100,
                'aov_growth_rate': ((avg_order_value - prev_aov) / prev_aov) * 100,
                'previous_revenue': prev_revenue,
                'previous_orders': prev_orders,
                'previous_aov': prev_aov
            })
            
        return metrics
    
    def calculate_monthly_trends(self, sales_data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate month-over-month growth trends.
        
        Args:
            sales_data (pd.DataFrame): Sales data with month column
            
        Returns:
            pd.DataFrame: Monthly trends with growth rates
        """
        monthly_revenue = sales_data.groupby('month')['price'].sum()
        monthly_orders = sales_data.groupby('month')['order_id'].nunique()
        monthly_aov = sales_data.groupby(['month', 'order_id'])['price'].sum().groupby('month').mean()
        
        trends = pd.DataFrame({
            'month': monthly_revenue.index,
            'revenue': monthly_revenue.values,
            'orders': monthly_orders.values,
            'avg_order_value': monthly_aov.values
        })
        
        trends['revenue_growth'] = trends['revenue'].pct_change() * 100
        trends['order_growth'] = trends['orders'].pct_change() * 100
        trends['aov_growth'] = trends['avg_order_value'].pct_change() * 100
        
        return trends
    
    def analyze_product_performance(self, product_sales_data: pd.DataFrame) -> Dict:
        """
        Analyze product category performance.
        
        Args:
            product_sales_data (pd.DataFrame): Sales data with product categories
            
        Returns:
            Dict: Product performance metrics
        """
        category_revenue = product_sales_data.groupby('product_category_name')['price'].sum().sort_values(ascending=False)
        category_orders = product_sales_data.groupby('product_category_name')['price'].count().sort_values(ascending=False)
        category_aov = product_sales_data.groupby('product_category_name')['price'].mean().sort_values(ascending=False)
        
        return {
            'top_categories_by_revenue': category_revenue.head(10).to_dict(),
            'top_categories_by_orders': category_orders.head(10).to_dict(),
            'top_categories_by_aov': category_aov.head(10).to_dict(),
            'category_performance': pd.DataFrame({
                'revenue': category_revenue,
                'orders': category_orders,
                'avg_order_value': category_aov
            })
        }
    
    def analyze_geographic_performance(self, geographic_data: pd.DataFrame) -> Dict:
        """
        Analyze sales performance by geographic location.
        
        Args:
            geographic_data (pd.DataFrame): Sales data with geographic information
            
        Returns:
            Dict: Geographic performance metrics
        """
        state_revenue = geographic_data.groupby('customer_state')['price'].sum().sort_values(ascending=False)
        state_orders = geographic_data.groupby('customer_state')['customer_id'].nunique().sort_values(ascending=False)
        state_aov = geographic_data.groupby('customer_state')['price'].mean().sort_values(ascending=False)
        
        return {
            'top_states_by_revenue': state_revenue.head(10).to_dict(),
            'top_states_by_customers': state_orders.head(10).to_dict(),
            'top_states_by_aov': state_aov.head(10).to_dict(),
            'geographic_summary': pd.DataFrame({
                'revenue': state_revenue,
                'customers': state_orders,
                'avg_order_value': state_aov
            })
        }
    
    def analyze_customer_experience(self, review_data: pd.DataFrame) -> Dict:
        """
        Analyze customer experience metrics including delivery and satisfaction.
        
        Args:
            review_data (pd.DataFrame): Sales data with review scores and delivery info
            
        Returns:
            Dict: Customer experience metrics
        """
        # Overall satisfaction metrics
        avg_rating = review_data['review_score'].mean()
        rating_distribution = review_data['review_score'].value_counts(normalize=True).sort_index()
        
        # Delivery performance
        avg_delivery_days = review_data['delivery_days'].mean()
        delivery_by_rating = review_data.groupby('review_score')['delivery_days'].mean()
        
        # Categorize delivery speed and analyze satisfaction
        review_data_copy = review_data.copy()
        review_data_copy['delivery_category'] = review_data_copy['delivery_days'].apply(
            lambda x: '1-3 days' if x <= 3 else '4-7 days' if x <= 7 else '8+ days'
        )
        satisfaction_by_delivery = review_data_copy.groupby('delivery_category')['review_score'].mean()
        
        return {
            'avg_rating': avg_rating,
            'rating_distribution': rating_distribution.to_dict(),
            'avg_delivery_days': avg_delivery_days,
            'delivery_by_rating': delivery_by_rating.to_dict(),
            'satisfaction_by_delivery_speed': satisfaction_by_delivery.to_dict(),
            'delivery_speed_distribution': review_data_copy['delivery_category'].value_counts(normalize=True).to_dict()
        }
    
    def calculate_order_fulfillment_metrics(self, orders_data: pd.DataFrame) -> Dict:
        """
        Calculate order fulfillment and operational metrics.
        
        Args:
            orders_data (pd.DataFrame): Orders data with status information
            
        Returns:
            Dict: Fulfillment metrics
        """
        status_distribution = orders_data['order_status'].value_counts(normalize=True)
        
        return {
            'fulfillment_rate': status_distribution.get('delivered', 0),
            'cancellation_rate': status_distribution.get('canceled', 0),
            'return_rate': status_distribution.get('returned', 0),
            'pending_rate': status_distribution.get('pending', 0) + status_distribution.get('processing', 0),
            'status_distribution': status_distribution.to_dict()
        }
    
    def create_revenue_trend_chart(self, trends_data: pd.DataFrame, 
                                  title_suffix: str = "") -> plt.Figure:
        """
        Create a revenue trend visualization.
        
        Args:
            trends_data (pd.DataFrame): Monthly trends data
            title_suffix (str): Additional text for chart title
            
        Returns:
            plt.Figure: Revenue trend chart
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Create the plot
        ax.plot(trends_data['month'], trends_data['revenue'], 
               marker='o', linewidth=2, markersize=8, color='#1f77b4')
        
        # Customize the chart
        ax.set_title(f'Monthly Revenue Trend {title_suffix}', fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Month', fontsize=12)
        ax.set_ylabel('Revenue ($)', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        # Format y-axis to show currency
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        # Add value labels on points
        for i, v in enumerate(trends_data['revenue']):
            ax.annotate(f'${v:,.0f}', (trends_data['month'].iloc[i], v), 
                       textcoords="offset points", xytext=(0,10), ha='center')
        
        plt.tight_layout()
        return fig
    
    def create_category_performance_chart(self, category_data: Dict, 
                                        title_suffix: str = "") -> plt.Figure:
        """
        Create a product category performance chart.
        
        Args:
            category_data (Dict): Category performance data
            title_suffix (str): Additional text for chart title
            
        Returns:
            plt.Figure: Category performance chart
        """
        fig, ax = plt.subplots(figsize=(12, 8))
        
        categories = list(category_data['top_categories_by_revenue'].keys())[:10]
        revenues = list(category_data['top_categories_by_revenue'].values())[:10]
        
        # Create horizontal bar chart
        bars = ax.barh(range(len(categories)), revenues, color='#ff7f0e')
        
        # Customize the chart
        ax.set_title(f'Top Product Categories by Revenue {title_suffix}', 
                    fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Revenue ($)', fontsize=12)
        ax.set_ylabel('Product Category', fontsize=12)
        ax.set_yticks(range(len(categories)))
        ax.set_yticklabels([cat.replace('_', ' ').title() for cat in categories])
        
        # Format x-axis
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        # Add value labels on bars
        for i, v in enumerate(revenues):
            ax.text(v + max(revenues)*0.01, i, f'${v:,.0f}', 
                   va='center', fontsize=10)
        
        plt.tight_layout()
        return fig
    
    def create_geographic_heatmap(self, geographic_summary: pd.DataFrame, 
                                title_suffix: str = "") -> Any:
        """
        Create a geographic sales heatmap.
        
        Args:
            geographic_summary (pd.DataFrame): Geographic data with state revenue
            title_suffix (str): Additional text for chart title
            
        Returns:
            px.Figure: Geographic heatmap
        """
        # Reset index to get state as column
        geo_data = geographic_summary.reset_index()
        
        # Create choropleth map
        fig = px.choropleth(
            geo_data,
            locations='customer_state',
            color='revenue',
            locationmode='USA-states',
            scope='usa',
            title=f'Revenue by State {title_suffix}',
            color_continuous_scale='Reds',
            labels={'revenue': 'Revenue ($)', 'customer_state': 'State'}
        )
        
        fig.update_layout(
            title_font_size=16,
            geo=dict(showframe=False, showcoastlines=True)
        )
        
        return fig
    
    def create_customer_satisfaction_chart(self, experience_metrics: Dict, 
                                         title_suffix: str = "") -> plt.Figure:
        """
        Create customer satisfaction visualization.
        
        Args:
            experience_metrics (Dict): Customer experience metrics
            title_suffix (str): Additional text for chart title
            
        Returns:
            plt.Figure: Customer satisfaction chart
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Rating distribution
        ratings = list(experience_metrics['rating_distribution'].keys())
        proportions = list(experience_metrics['rating_distribution'].values())
        
        ax1.barh(ratings, proportions, color='#2ca02c')
        ax1.set_title('Review Score Distribution', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Proportion of Reviews', fontsize=12)
        ax1.set_ylabel('Review Score', fontsize=12)
        
        # Satisfaction by delivery speed
        delivery_speeds = list(experience_metrics['satisfaction_by_delivery_speed'].keys())
        satisfaction_scores = list(experience_metrics['satisfaction_by_delivery_speed'].values())
        
        ax2.bar(delivery_speeds, satisfaction_scores, color='#d62728')
        ax2.set_title('Average Rating by Delivery Speed', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Delivery Speed', fontsize=12)
        ax2.set_ylabel('Average Review Score', fontsize=12)
        ax2.set_ylim(0, 5)
        
        # Add value labels
        for i, v in enumerate(satisfaction_scores):
            ax2.text(i, v + 0.05, f'{v:.2f}', ha='center', va='bottom')
        
        plt.suptitle(f'Customer Experience Analysis {title_suffix}', 
                    fontsize=16, fontweight='bold')
        plt.tight_layout()
        return fig
    
    def create_fulfillment_metrics_chart(self, fulfillment_metrics: Dict, 
                                       title_suffix: str = "") -> plt.Figure:
        """
        Create order fulfillment metrics visualization.
        
        Args:
            fulfillment_metrics (Dict): Fulfillment metrics data
            title_suffix (str): Additional text for chart title
            
        Returns:
            plt.Figure: Fulfillment metrics chart
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Create pie chart of order status distribution
        labels = []
        sizes = []
        colors = ['#2ca02c', '#ff7f0e', '#d62728', '#1f77b4', '#9467bd', '#8c564b']
        
        for status, proportion in fulfillment_metrics['status_distribution'].items():
            if proportion > 0.01:  # Only show statuses with >1% share
                labels.append(status.replace('_', ' ').title())
                sizes.append(proportion * 100)
        
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', 
                                         colors=colors[:len(labels)], startangle=90)
        
        ax.set_title(f'Order Status Distribution {title_suffix}', 
                    fontsize=16, fontweight='bold', pad=20)
        
        return fig
    
    def generate_business_summary(self, revenue_metrics: Dict, 
                                product_metrics: Dict, 
                                geo_metrics: Dict, 
                                experience_metrics: Dict,
                                fulfillment_metrics: Dict) -> Dict:
        """
        Generate a comprehensive business summary report.
        
        Args:
            revenue_metrics (Dict): Revenue analysis results
            product_metrics (Dict): Product performance results  
            geo_metrics (Dict): Geographic analysis results
            experience_metrics (Dict): Customer experience results
            fulfillment_metrics (Dict): Order fulfillment results
            
        Returns:
            Dict: Comprehensive business summary
        """
        summary = {
            'executive_summary': {
                'total_revenue': revenue_metrics.get('total_revenue', 0),
                'total_orders': revenue_metrics.get('total_orders', 0),
                'avg_order_value': revenue_metrics.get('avg_order_value', 0),
                'avg_customer_rating': experience_metrics.get('avg_rating', 0),
                'fulfillment_rate': fulfillment_metrics.get('fulfillment_rate', 0),
                'avg_delivery_days': experience_metrics.get('avg_delivery_days', 0)
            },
            'growth_metrics': {
                'revenue_growth': revenue_metrics.get('revenue_growth_rate', None),
                'order_growth': revenue_metrics.get('order_growth_rate', None), 
                'aov_growth': revenue_metrics.get('aov_growth_rate', None)
            },
            'top_performers': {
                'top_product_category': list(product_metrics['top_categories_by_revenue'].keys())[0] if product_metrics['top_categories_by_revenue'] else None,
                'top_state': list(geo_metrics['top_states_by_revenue'].keys())[0] if geo_metrics['top_states_by_revenue'] else None
            },
            'operational_metrics': {
                'fulfillment_rate': fulfillment_metrics.get('fulfillment_rate', 0),
                'cancellation_rate': fulfillment_metrics.get('cancellation_rate', 0),
                'return_rate': fulfillment_metrics.get('return_rate', 0),
                'fast_delivery_rate': experience_metrics.get('delivery_speed_distribution', {}).get('1-3 days', 0)
            }
        }
        
        return summary
    
    def print_business_insights(self, summary: Dict, time_period: str = ""):
        """
        Print formatted business insights and recommendations.
        
        Args:
            summary (Dict): Business summary data
            time_period (str): Description of the analysis period
        """
        print(f"\n{'='*60}")
        print(f"BUSINESS PERFORMANCE SUMMARY {time_period}")
        print(f"{'='*60}")
        
        exec_summary = summary['executive_summary']
        print(f"\nKEY PERFORMANCE INDICATORS:")
        print(f"  • Total Revenue: ${exec_summary['total_revenue']:,.2f}")
        print(f"  • Total Orders: {exec_summary['total_orders']:,}")
        print(f"  • Average Order Value: ${exec_summary['avg_order_value']:,.2f}")
        print(f"  • Customer Satisfaction: {exec_summary['avg_customer_rating']:.2f}/5.0")
        print(f"  • Order Fulfillment Rate: {exec_summary['fulfillment_rate']*100:.1f}%")
        print(f"  • Average Delivery Time: {exec_summary['avg_delivery_days']:.1f} days")
        
        growth_metrics = summary['growth_metrics']
        if any(v is not None for v in growth_metrics.values()):
            print(f"\nGROWTH METRICS:")
            if growth_metrics['revenue_growth'] is not None:
                print(f"  • Revenue Growth: {growth_metrics['revenue_growth']:.1f}%")
            if growth_metrics['order_growth'] is not None:
                print(f"  • Order Growth: {growth_metrics['order_growth']:.1f}%")
            if growth_metrics['aov_growth'] is not None:
                print(f"  • AOV Growth: {growth_metrics['aov_growth']:.1f}%")
        
        top_performers = summary['top_performers']
        print(f"\nTOP PERFORMERS:")
        if top_performers['top_product_category']:
            print(f"  • Leading Product Category: {top_performers['top_product_category'].replace('_', ' ').title()}")
        if top_performers['top_state']:
            print(f"  • Top Revenue State: {top_performers['top_state']}")
        
        operational = summary['operational_metrics']
        print(f"\nOPERATIONAL EFFICIENCY:")
        print(f"  • Order Fulfillment: {operational['fulfillment_rate']*100:.1f}%")
        print(f"  • Cancellation Rate: {operational['cancellation_rate']*100:.1f}%")
        print(f"  • Return Rate: {operational['return_rate']*100:.1f}%")
        print(f"  • Fast Delivery (1-3 days): {operational['fast_delivery_rate']*100:.1f}%")
        
        print(f"\n{'='*60}\n")
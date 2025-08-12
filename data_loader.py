"""
E-commerce Data Loader Module

This module provides the EcommerceDataLoader class for loading, processing, and cleaning
e-commerce datasets. It handles data loading from CSV files, applies necessary transformations,
and provides filtered datasets based on configurable time periods.
"""

import pandas as pd
import os
from typing import Optional, Dict, Any
import warnings
warnings.filterwarnings('ignore')

class EcommerceDataLoader:
    """
    A class to handle loading and preprocessing of e-commerce datasets.
    
    This class loads multiple CSV files containing orders, order items, products,
    customers, and reviews data. It provides methods to merge datasets, filter
    by date ranges, and prepare analysis-ready datasets.
    """
    
    def __init__(self, data_path: str = "ecommerce_data/"):
        """
        Initialize the data loader.
        
        Args:
            data_path (str): Path to the directory containing CSV files
        """
        self.data_path = data_path
        self.orders = None
        self.order_items = None
        self.products = None
        self.customers = None
        self.reviews = None
        self._validate_data_path()
    
    def _validate_data_path(self):
        """Validate that the data path exists and contains required files."""
        required_files = [
            'orders_dataset.csv',
            'order_items_dataset.csv', 
            'products_dataset.csv',
            'customers_dataset.csv',
            'order_reviews_dataset.csv'
        ]
        
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"Data path {self.data_path} does not exist")
        
        missing_files = []
        for file in required_files:
            if not os.path.exists(os.path.join(self.data_path, file)):
                missing_files.append(file)
        
        if missing_files:
            raise FileNotFoundError(f"Missing required files: {missing_files}")
        
    def load_all_datasets(self) -> Dict[str, pd.DataFrame]:
        """
        Load all CSV datasets into memory.
        
        Returns:
            dict: Dictionary containing all loaded datasets
        """
        print("Loading all datasets...")
        
        # Load orders dataset
        self.orders = pd.read_csv(os.path.join(self.data_path, 'orders_dataset.csv'))
        self._process_orders_data()
        
        # Load order items dataset
        self.order_items = pd.read_csv(os.path.join(self.data_path, 'order_items_dataset.csv'))
        
        # Load products dataset  
        self.products = pd.read_csv(os.path.join(self.data_path, 'products_dataset.csv'))
        
        # Load customers dataset
        self.customers = pd.read_csv(os.path.join(self.data_path, 'customers_dataset.csv'))
        
        # Load reviews dataset
        self.reviews = pd.read_csv(os.path.join(self.data_path, 'order_reviews_dataset.csv'))
        self._process_reviews_data()
        
        print("All datasets loaded successfully!")
        return {
            'orders': self.orders,
            'order_items': self.order_items,
            'products': self.products,
            'customers': self.customers,
            'reviews': self.reviews
        }
    
    def _process_orders_data(self):
        """Process and clean orders data."""
        # Convert timestamps to datetime
        date_columns = [
            'order_purchase_timestamp',
            'order_approved_at', 
            'order_delivered_carrier_date',
            'order_delivered_customer_date',
            'order_estimated_delivery_date'
        ]
        
        for col in date_columns:
            if col in self.orders.columns:
                self.orders[col] = pd.to_datetime(self.orders[col], errors='coerce')
        
        # Extract year and month from purchase timestamp
        self.orders['year'] = self.orders['order_purchase_timestamp'].dt.year
        self.orders['month'] = self.orders['order_purchase_timestamp'].dt.month
    
    def _process_reviews_data(self):
        """Process and clean reviews data."""
        # Convert review timestamps to datetime
        self.reviews['review_creation_date'] = pd.to_datetime(
            self.reviews['review_creation_date'], errors='coerce'
        )
        if 'review_answer_timestamp' in self.reviews.columns:
            self.reviews['review_answer_timestamp'] = pd.to_datetime(
                self.reviews['review_answer_timestamp'], errors='coerce'
            )
        
    def prepare_sales_data(self, 
                          year: Optional[int] = None, 
                          month: Optional[int] = None,
                          status: str = 'delivered') -> pd.DataFrame:
        """
        Prepare sales data by merging order items and orders, with optional filtering.
        
        Args:
            year (int, optional): Filter by specific year
            month (int, optional): Filter by specific month  
            status (str): Order status to filter by (default: 'delivered')
            
        Returns:
            pd.DataFrame: Merged and filtered sales data
        """
        if self.orders is None or self.order_items is None:
            raise ValueError("Datasets must be loaded first. Call load_all_datasets()")
        
        # Merge order items with orders
        sales_data = pd.merge(
            left=self.order_items[['order_id', 'order_item_id', 'product_id', 'price', 'freight_value']],
            right=self.orders[[
                'order_id', 'order_status', 'order_purchase_timestamp', 
                'order_delivered_customer_date', 'year', 'month', 'customer_id'
            ]],
            on='order_id',
            how='inner'
        )
        
        # Filter by order status
        if status:
            sales_data = sales_data[sales_data['order_status'] == status].copy()
        
        # Filter by year if specified
        if year is not None:
            sales_data = sales_data[sales_data['year'] == year].copy()
        
        # Filter by month if specified  
        if month is not None:
            sales_data = sales_data[sales_data['month'] == month].copy()
        
        # Calculate delivery speed for delivered orders
        if status == 'delivered':
            sales_data['delivery_days'] = (
                sales_data['order_delivered_customer_date'] - 
                sales_data['order_purchase_timestamp']
            ).dt.days
        
        return sales_data
    
    def get_product_category_data(self, sales_data: pd.DataFrame) -> pd.DataFrame:
        """
        Merge sales data with product categories.
        
        Args:
            sales_data (pd.DataFrame): Processed sales data
            
        Returns:
            pd.DataFrame: Sales data with product categories
        """
        if self.products is None:
            raise ValueError("Products dataset not loaded.")
            
        return pd.merge(
            left=self.products[['product_id', 'product_category_name']],
            right=sales_data[['product_id', 'price']],
            on='product_id'
        )
    
    def get_geographic_data(self, sales_data: pd.DataFrame) -> pd.DataFrame:
        """
        Merge sales data with customer geographic information.
        
        Args:
            sales_data (pd.DataFrame): Processed sales data
            
        Returns:
            pd.DataFrame: Sales data with customer state information
        """
        if self.customers is None:
            raise ValueError("Customers dataset not loaded.")
            
        # Merge with customer data to get geographic info
        sales_with_customers = pd.merge(
            left=sales_data[['order_id', 'customer_id', 'price']],
            right=self.customers[['customer_id', 'customer_state', 'customer_city']],
            on='customer_id'
        )
        
        return sales_with_customers
    
    def get_review_data(self, sales_data: pd.DataFrame) -> pd.DataFrame:
        """
        Merge sales data with review scores.
        
        Args:
            sales_data (pd.DataFrame): Processed sales data
            
        Returns:
            pd.DataFrame: Sales data with review scores
        """
        if self.reviews is None:
            raise ValueError("Reviews dataset not loaded.")
            
        return pd.merge(
            left=sales_data,
            right=self.reviews[['order_id', 'review_score']],
            on='order_id',
            how='left'
        )
    
    def categorize_delivery_speed(self, days: int) -> str:
        """
        Categorize delivery speed into bins.
        
        Args:
            days (int): Number of delivery days
            
        Returns:
            str: Delivery speed category
        """
        if days <= 3:
            return '1-3 days'
        elif days <= 7:
            return '4-7 days'
        else:
            return '8+ days'
    
    def get_sales_with_products(self, 
                               year: Optional[int] = None, 
                               month: Optional[int] = None) -> pd.DataFrame:
        """
        Get sales data merged with product information.
        
        Args:
            year (int, optional): Filter by specific year
            month (int, optional): Filter by specific month
            
        Returns:
            pd.DataFrame: Sales data with product categories
        """
        sales_data = self.prepare_sales_data(year=year, month=month)
        
        # Merge with products to get category information
        sales_with_products = pd.merge(
            left=sales_data,
            right=self.products[['product_id', 'product_category_name']],
            on='product_id',
            how='left'
        )
        
        return sales_with_products
    
    def get_sales_with_customers(self, 
                                year: Optional[int] = None, 
                                month: Optional[int] = None) -> pd.DataFrame:
        """
        Get sales data merged with customer geographic information.
        
        Args:
            year (int, optional): Filter by specific year  
            month (int, optional): Filter by specific month
            
        Returns:
            pd.DataFrame: Sales data with customer location
        """
        sales_data = self.prepare_sales_data(year=year, month=month)
        
        # Merge with customers to get location data
        sales_with_customers = pd.merge(
            left=sales_data,
            right=self.customers[['customer_id', 'customer_state', 'customer_city']],
            on='customer_id',
            how='left'
        )
        
        return sales_with_customers
    
    def get_sales_with_reviews(self, 
                              year: Optional[int] = None, 
                              month: Optional[int] = None) -> pd.DataFrame:
        """
        Get sales data merged with review information.
        
        Args:
            year (int, optional): Filter by specific year
            month (int, optional): Filter by specific month
            
        Returns:
            pd.DataFrame: Sales data with review scores
        """
        sales_data = self.prepare_sales_data(year=year, month=month)
        
        # Merge with reviews
        sales_with_reviews = pd.merge(
            left=sales_data,
            right=self.reviews[['order_id', 'review_score', 'review_creation_date']],
            on='order_id',
            how='left'
        )
        
        return sales_with_reviews
    
    def get_dataset_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics of all loaded datasets.
        
        Returns:
            dict: Summary information for each dataset
        """
        if self.orders is None:
            raise ValueError("Datasets must be loaded first. Call load_all_datasets()")
        
        summary = {
            'orders': {
                'total_records': len(self.orders),
                'date_range': (
                    self.orders['order_purchase_timestamp'].min(),
                    self.orders['order_purchase_timestamp'].max()
                ),
                'unique_customers': self.orders['customer_id'].nunique(),
                'order_statuses': self.orders['order_status'].value_counts().to_dict()
            },
            'order_items': {
                'total_records': len(self.order_items),
                'unique_products': self.order_items['product_id'].nunique(),
                'price_range': (
                    self.order_items['price'].min(),
                    self.order_items['price'].max()
                )
            },
            'products': {
                'total_records': len(self.products),
                'unique_categories': self.products['product_category_name'].nunique(),
                'categories': self.products['product_category_name'].unique().tolist()
            },
            'customers': {
                'total_records': len(self.customers),
                'unique_states': self.customers['customer_state'].nunique(),
                'unique_cities': self.customers['customer_city'].nunique()
            },
            'reviews': {
                'total_records': len(self.reviews),
                'score_distribution': self.reviews['review_score'].value_counts().sort_index().to_dict(),
                'average_score': self.reviews['review_score'].mean()
            }
        }
        
        return summary
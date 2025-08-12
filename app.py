import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
import numpy as np
from data_loader import EcommerceDataLoader
from business_metrics import EcommerceMetrics

st.set_page_config(page_title="E-commerce Dashboard", layout="wide", initial_sidebar_state="collapsed")

@st.cache_data
def load_data():
    data_loader = EcommerceDataLoader("ecommerce_data/")
    datasets = data_loader.load_all_datasets()
    return data_loader, datasets

@st.cache_data
def get_date_range_data(_data_loader):
    orders = _data_loader.orders
    min_date = orders['order_purchase_timestamp'].min()
    max_date = orders['order_purchase_timestamp'].max()
    return min_date, max_date

@st.cache_data
def filter_data_by_date(_data_loader, start_date, end_date):
    orders = _data_loader.orders
    filtered_orders = orders[
        (orders['order_purchase_timestamp'] >= start_date) & 
        (orders['order_purchase_timestamp'] <= end_date)
    ]
    
    # Get delivered orders with all required date fields
    delivered_orders = filtered_orders[
        (filtered_orders['order_status'] == 'delivered') &
        (filtered_orders['order_delivered_customer_date'].notna())
    ].copy()
    
    # Calculate delivery days
    delivered_orders['delivery_days'] = (
        delivered_orders['order_delivered_customer_date'] - 
        delivered_orders['order_purchase_timestamp']
    ).dt.days
    
    sales_data = _data_loader.order_items.merge(
        delivered_orders[['order_id', 'customer_id', 'order_status', 'order_purchase_timestamp', 'delivery_days']],
        on='order_id'
    ).merge(_data_loader.products, on='product_id', how='left')
    
    sales_data = sales_data.merge(_data_loader.customers, on='customer_id', how='left')
    sales_data = sales_data.merge(_data_loader.reviews, on='order_id', how='left')
    
    return sales_data, filtered_orders

def calculate_kpis(current_data, previous_data):
    current_revenue = current_data['price'].sum()
    previous_revenue = previous_data['price'].sum() if len(previous_data) > 0 else 0
    
    current_orders = current_data['order_id'].nunique()
    previous_orders = previous_data['order_id'].nunique() if len(previous_data) > 0 else 0
    
    current_aov = current_revenue / current_orders if current_orders > 0 else 0
    previous_aov = previous_revenue / previous_orders if previous_orders > 0 else 0
    
    revenue_growth = ((current_revenue - previous_revenue) / previous_revenue * 100) if previous_revenue > 0 else 0
    aov_growth = ((current_aov - previous_aov) / previous_aov * 100) if previous_aov > 0 else 0
    orders_growth = ((current_orders - previous_orders) / previous_orders * 100) if previous_orders > 0 else 0
    
    current_data['year_month'] = current_data['order_purchase_timestamp'].dt.to_period('M')
    previous_data['year_month'] = previous_data['order_purchase_timestamp'].dt.to_period('M') if len(previous_data) > 0 else pd.Series([], dtype='period[M]')
    
    current_monthly = current_data.groupby('year_month')['price'].sum()
    previous_monthly = previous_data.groupby('year_month')['price'].sum() if len(previous_data) > 0 else pd.Series([])
    
    if len(current_monthly) >= 2:
        latest_month = current_monthly.iloc[-1]
        prev_month = current_monthly.iloc[-2]
        monthly_growth = ((latest_month - prev_month) / prev_month * 100) if prev_month > 0 else 0
    else:
        monthly_growth = 0
    
    return {
        'total_revenue': current_revenue,
        'revenue_growth': revenue_growth,
        'monthly_growth': monthly_growth,
        'avg_order_value': current_aov,
        'aov_growth': aov_growth,
        'total_orders': current_orders,
        'orders_growth': orders_growth
    }

def format_currency(value):
    if value >= 1_000_000:
        return f"${value/1_000_000:.1f}M"
    elif value >= 1_000:
        return f"${value/1_000:.0f}K"
    else:
        return f"${value:.0f}"

def format_number(value):
    if value >= 1_000_000:
        return f"{value/1_000_000:.1f}M"
    elif value >= 1_000:
        return f"{value/1_000:.0f}K"
    else:
        return f"{value:.0f}"

def create_kpi_card(title, value, growth, is_currency=True):
    if is_currency:
        formatted_value = format_currency(value)
    else:
        formatted_value = format_number(value)
    
    growth_color = "green" if growth >= 0 else "red"
    arrow = "↗" if growth >= 0 else "↘"
    
    card_html = f"""
    <div style="
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
        height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    ">
        <h4 style="margin: 0; color: #666; font-size: 14px;">{title}</h4>
        <h2 style="margin: 10px 0; color: #333; font-size: 24px;">{formatted_value}</h2>
        <div style="color: {growth_color}; font-size: 14px;">
            {arrow} {growth:.2f}%
        </div>
    </div>
    """
    return card_html

def create_revenue_trend_chart(current_data, previous_data):
    current_data['year_month'] = current_data['order_purchase_timestamp'].dt.to_period('M')
    current_monthly = current_data.groupby('year_month')['price'].sum().reset_index()
    current_monthly['date'] = current_monthly['year_month'].dt.to_timestamp()
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=current_monthly['date'],
        y=current_monthly['price'],
        mode='lines',
        name='Current Period',
        line=dict(color='#1f77b4', width=2)
    ))
    
    if len(previous_data) > 0:
        previous_data['year_month'] = previous_data['order_purchase_timestamp'].dt.to_period('M')
        previous_monthly = previous_data.groupby('year_month')['price'].sum().reset_index()
        previous_monthly['date'] = previous_monthly['year_month'].dt.to_timestamp()
        
        if len(previous_monthly) > 0:
            previous_monthly['date'] = previous_monthly['date'] + pd.DateOffset(years=1)
            
            fig.add_trace(go.Scatter(
                x=previous_monthly['date'],
                y=previous_monthly['price'],
                mode='lines',
                name='Previous Period',
                line=dict(color='#ff7f0e', width=2, dash='dash')
            ))
    
    fig.update_layout(
        title="Revenue Trend",
        xaxis_title="Month",
        yaxis_title="Revenue",
        showlegend=True,
        height=400,
        xaxis=dict(showgrid=True, gridcolor='lightgray'),
        yaxis=dict(
            showgrid=True,
            gridcolor='lightgray',
            tickformat='.0s'
        )
    )
    
    return fig

def create_category_chart(data):
    category_revenue = data.groupby('product_category_name')['price'].sum().sort_values(ascending=False).head(10)
    
    colors = px.colors.sequential.Blues_r[:len(category_revenue)]
    
    fig = go.Figure(data=[
        go.Bar(
            y=[cat.replace('_', ' ').title() for cat in category_revenue.index],
            x=category_revenue.values,
            orientation='h',
            marker_color=colors,
            text=[format_currency(val) for val in category_revenue.values],
            textposition='outside'
        )
    ])
    
    fig.update_layout(
        title="Top 10 Categories",
        xaxis_title="Revenue",
        yaxis_title="Category",
        height=400,
        xaxis=dict(tickformat='.0s')
    )
    
    return fig

def create_state_map(data):
    state_revenue = data.groupby('customer_state')['price'].sum().reset_index()
    state_revenue['hover_text'] = state_revenue.apply(
        lambda row: f"{row['customer_state']}<br>Revenue: {format_currency(row['price'])}", axis=1
    )
    
    fig = go.Figure(data=go.Choropleth(
        locations=state_revenue['customer_state'],
        z=state_revenue['price'],
        locationmode='USA-states',
        colorscale='Blues',
        text=state_revenue['hover_text'],
        hovertemplate='%{text}<extra></extra>',
        colorbar_title="Revenue"
    ))
    
    fig.update_layout(
        title="Revenue by State",
        geo_scope='usa',
        height=400
    )
    
    return fig

def create_satisfaction_delivery_chart(data):
    # Check if we have the required columns
    if 'review_score' not in data.columns or 'delivery_days' not in data.columns:
        # Create empty chart with message
        fig = go.Figure()
        fig.add_annotation(
            text="No delivery or review data available for selected period",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False, font=dict(size=16)
        )
        fig.update_layout(
            title="Satisfaction vs Delivery Time",
            xaxis_title="Delivery Time",
            yaxis_title="Average Review Score",
            height=400,
            showlegend=False
        )
        return fig
    
    data_with_reviews = data.dropna(subset=['review_score', 'delivery_days'])
    
    if len(data_with_reviews) == 0:
        # Create empty chart with message
        fig = go.Figure()
        fig.add_annotation(
            text="No data available with both delivery and review information",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False, font=dict(size=16)
        )
        fig.update_layout(
            title="Satisfaction vs Delivery Time",
            xaxis_title="Delivery Time",
            yaxis_title="Average Review Score",
            height=400,
            showlegend=False
        )
        return fig
    
    data_with_reviews['delivery_bucket'] = pd.cut(
        data_with_reviews['delivery_days'],
        bins=[0, 3, 7, 14, float('inf')],
        labels=['1-3 days', '4-7 days', '8-14 days', '15+ days']
    )
    
    satisfaction_by_delivery = data_with_reviews.groupby('delivery_bucket')['review_score'].mean().reset_index()
    
    fig = go.Figure(data=[
        go.Bar(
            x=satisfaction_by_delivery['delivery_bucket'],
            y=satisfaction_by_delivery['review_score'],
            marker_color='#1f77b4',
            text=[f"{score:.2f}" for score in satisfaction_by_delivery['review_score']],
            textposition='outside'
        )
    ])
    
    fig.update_layout(
        title="Satisfaction vs Delivery Time",
        xaxis_title="Delivery Time",
        yaxis_title="Average Review Score",
        height=400,
        yaxis=dict(range=[0, 5])
    )
    
    return fig

def create_bottom_cards(data):
    # Check if we have delivery and review data
    has_delivery = 'delivery_days' in data.columns and data['delivery_days'].notna().any()
    has_reviews = 'review_score' in data.columns and data['review_score'].notna().any()
    
    # Handle delivery card
    if has_delivery:
        data_with_delivery = data.dropna(subset=['delivery_days'])
        avg_delivery = data_with_delivery['delivery_days'].mean()
        
        if 'order_purchase_timestamp' in data_with_delivery.columns:
            current_month_data = data_with_delivery[
                data_with_delivery['order_purchase_timestamp'].dt.to_period('M') == 
                data_with_delivery['order_purchase_timestamp'].dt.to_period('M').max()
            ]
            
            prev_month_data = data_with_delivery[
                data_with_delivery['order_purchase_timestamp'].dt.to_period('M') == 
                (data_with_delivery['order_purchase_timestamp'].dt.to_period('M').max() - 1)
            ]
            
            current_delivery = current_month_data['delivery_days'].mean() if len(current_month_data) > 0 else avg_delivery
            prev_delivery = prev_month_data['delivery_days'].mean() if len(prev_month_data) > 0 else avg_delivery
            
            delivery_trend = ((prev_delivery - current_delivery) / prev_delivery * 100) if prev_delivery > 0 else 0
        else:
            delivery_trend = 0
        
        delivery_card = f"""
        <div style="
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
            height: 120px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        ">
            <h4 style="margin: 0; color: #666; font-size: 14px;">Average Delivery Time</h4>
            <h2 style="margin: 10px 0; color: #333; font-size: 24px;">{avg_delivery:.1f} days</h2>
            <div style="color: {'green' if delivery_trend >= 0 else 'red'}; font-size: 14px;">
                {'↗' if delivery_trend >= 0 else '↘'} {abs(delivery_trend):.2f}%
            </div>
        </div>
        """
    else:
        delivery_card = f"""
        <div style="
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
            height: 120px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        ">
            <h4 style="margin: 0; color: #666; font-size: 14px;">Average Delivery Time</h4>
            <h2 style="margin: 10px 0; color: #333; font-size: 24px;">N/A</h2>
            <div style="color: #999; font-size: 14px;">No delivery data</div>
        </div>
        """
    
    # Handle review card
    if has_reviews:
        data_with_reviews = data.dropna(subset=['review_score'])
        avg_review = data_with_reviews['review_score'].mean()
        stars = "★" * int(round(avg_review)) + "☆" * (5 - int(round(avg_review)))
        
        review_card = f"""
        <div style="
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
            height: 120px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        ">
            <h4 style="margin: 0; color: #666; font-size: 14px;">Average Review Score</h4>
            <h2 style="margin: 10px 0; color: #333; font-size: 24px;">{avg_review:.2f}</h2>
            <div style="color: #ffd700; font-size: 18px;">{stars}</div>
        </div>
        """
    else:
        review_card = f"""
        <div style="
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
            height: 120px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        ">
            <h4 style="margin: 0; color: #666; font-size: 14px;">Average Review Score</h4>
            <h2 style="margin: 10px 0; color: #333; font-size: 24px;">N/A</h2>
            <div style="color: #999; font-size: 14px;">No review data</div>
        </div>
        """
    
    return delivery_card, review_card

def main():
    st.markdown("""
    <style>
    .main > div {
        padding-top: 2rem;
    }
    .stSelectbox > div > div {
        background-color: white;
    }
    </style>
    """, unsafe_allow_html=True)
    
    data_loader, datasets = load_data()
    min_date, max_date = get_date_range_data(data_loader)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.title("E-commerce Business Dashboard")
    
    with col2:
        st.subheader("Date Range Filter")
        
        default_start = max_date - pd.DateOffset(years=1)
        default_end = max_date
        
        start_date = st.date_input(
            "Start Date",
            value=default_start.date(),
            min_value=min_date.date(),
            max_value=max_date.date()
        )
        
        end_date = st.date_input(
            "End Date",
            value=default_end.date(),
            min_value=min_date.date(),
            max_value=max_date.date()
        )
    
    if start_date >= end_date:
        st.error("Start date must be before end date")
        return
    
    current_data, current_orders = filter_data_by_date(data_loader, pd.Timestamp(start_date), pd.Timestamp(end_date))
    
    period_length = (pd.Timestamp(end_date) - pd.Timestamp(start_date)).days
    previous_start = pd.Timestamp(start_date) - pd.DateOffset(days=period_length)
    previous_end = pd.Timestamp(start_date) - pd.DateOffset(days=1)
    
    previous_data, previous_orders = filter_data_by_date(data_loader, previous_start, previous_end)
    
    kpis = calculate_kpis(current_data, previous_data)
    
    st.markdown("### Key Performance Indicators")
    
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    
    with kpi_col1:
        st.markdown(create_kpi_card("Total Revenue", kpis['total_revenue'], kpis['revenue_growth']), unsafe_allow_html=True)
    
    with kpi_col2:
        st.markdown(create_kpi_card("Monthly Growth", kpis['monthly_growth'], kpis['monthly_growth']), unsafe_allow_html=True)
    
    with kpi_col3:
        st.markdown(create_kpi_card("Average Order Value", kpis['avg_order_value'], kpis['aov_growth']), unsafe_allow_html=True)
    
    with kpi_col4:
        st.markdown(create_kpi_card("Total Orders", kpis['total_orders'], kpis['orders_growth'], is_currency=False), unsafe_allow_html=True)
    
    st.markdown("### Performance Analytics")
    
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        revenue_chart = create_revenue_trend_chart(current_data, previous_data)
        st.plotly_chart(revenue_chart, use_container_width=True)
    
    with chart_col2:
        category_chart = create_category_chart(current_data)
        st.plotly_chart(category_chart, use_container_width=True)
    
    chart_col3, chart_col4 = st.columns(2)
    
    with chart_col3:
        state_map = create_state_map(current_data)
        st.plotly_chart(state_map, use_container_width=True)
    
    with chart_col4:
        satisfaction_chart = create_satisfaction_delivery_chart(current_data)
        st.plotly_chart(satisfaction_chart, use_container_width=True)
    
    st.markdown("### Customer Experience")
    
    bottom_col1, bottom_col2 = st.columns(2)
    
    delivery_card, review_card = create_bottom_cards(current_data)
    
    with bottom_col1:
        st.markdown(delivery_card, unsafe_allow_html=True)
    
    with bottom_col2:
        st.markdown(review_card, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
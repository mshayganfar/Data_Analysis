# E-commerce Business Dashboard

A professional Streamlit dashboard for analyzing e-commerce business performance with interactive visualizations and KPIs.

## Features

### Dashboard Layout
- **Header**: Business title with global date range filter
- **KPI Row**: 4 key performance indicators with trend indicators
  - Total Revenue (with growth trend)
  - Monthly Growth Rate
  - Average Order Value (with trend)
  - Total Orders (with growth trend)
- **Charts Grid**: 2x2 layout with interactive visualizations
  - Revenue trend line chart (current vs previous period)
  - Top 10 product categories bar chart
  - Revenue by state choropleth map
  - Customer satisfaction vs delivery time analysis
- **Bottom Cards**: Customer experience metrics
  - Average delivery time with trend
  - Review score with star rating

### Key Features
- **Interactive Date Filtering**: Select any date range for analysis
- **Automatic Period Comparison**: Compare current period with equivalent previous period
- **Professional Styling**: Clean design with consistent card heights and formatting
- **Responsive Charts**: All visualizations built with Plotly for interactivity
- **Trend Indicators**: Color-coded arrows showing performance direction
- **Smart Formatting**: Currency values formatted as $300K, $2M for readability

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure your data modules are available:
   - `data_loader.py` - Contains EcommerceDataLoader class
   - `business_metrics.py` - Contains EcommerceMetrics class
   - `ecommerce_data/` - Directory with your e-commerce data files

## Usage

### Running the Dashboard
```bash
streamlit run app.py
```

The dashboard will open in your default web browser at `http://localhost:8501`

### Dashboard Navigation
1. **Date Range Selection**: Use the date picker in the top-right to filter data
2. **KPI Monitoring**: View key metrics with trend indicators (green ↗ for growth, red ↘ for decline)
3. **Chart Analysis**: Explore the 2x2 grid of interactive charts
4. **Customer Experience**: Review delivery and satisfaction metrics at the bottom

### Chart Details

#### Revenue Trend Chart
- Solid line: Current period performance
- Dashed line: Previous period comparison
- Grid lines for easier reading
- Y-axis formatted as $300K instead of $300,000

#### Top 10 Categories Chart
- Horizontal bar chart sorted by revenue (descending)
- Blue gradient coloring (lighter for lower values)
- Values formatted as $300K, $2M

#### Revenue by State Map
- US choropleth map with blue gradient
- Color intensity represents revenue amount
- Hover for detailed state information

#### Satisfaction vs Delivery Time
- Bar chart showing review scores by delivery speed buckets
- X-axis: Delivery time ranges (1-3 days, 4-7 days, 8-14 days, 15+ days)
- Y-axis: Average review score (1-5 scale)

## Data Requirements

The dashboard expects the following data structure through the EcommerceDataLoader:

- **Orders**: Order-level information with timestamps and status
- **Order Items**: Product-level details with pricing
- **Products**: Product catalog with categories
- **Customers**: Customer information including location
- **Reviews**: Customer feedback and ratings

## Customization

### Modifying KPIs
Edit the `calculate_kpis()` function to add or modify key performance indicators.

### Adding Charts
Create new chart functions following the pattern of existing chart functions (e.g., `create_category_chart()`).

### Styling Changes
Modify the CSS in the `main()` function or update the card HTML templates in `create_kpi_card()`.

### Date Range Logic
Adjust the default date range or comparison period logic in the `main()` function.

## Technical Details

### Performance Optimization
- `@st.cache_data` decorators for expensive data operations
- Efficient data filtering and aggregation
- Minimal data reprocessing on filter changes

### Dependencies
- **Streamlit**: Web dashboard framework
- **Plotly**: Interactive visualization library
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computing support

## Troubleshooting

### Common Issues

1. **Module Import Errors**
   - Ensure `data_loader.py` and `business_metrics.py` are in the same directory
   - Check that all required data files exist in `ecommerce_data/`

2. **Date Range Issues**
   - Verify your data contains the selected date range
   - Check date format in your source data

3. **Chart Rendering Problems**
   - Update Plotly to the latest version
   - Check browser compatibility for Plotly visualizations

4. **Performance Issues**
   - Consider reducing date range for large datasets
   - Monitor memory usage with extensive data filtering

### Data Validation
The dashboard includes basic data validation:
- Date range validation (start < end)
- Empty dataset handling
- Missing data graceful handling

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify all dependencies are correctly installed
3. Ensure data modules and files are properly configured
4. Review Streamlit and Plotly documentation for advanced customization

## License

This dashboard is built for e-commerce business intelligence and analytics purposes.
The @EDA.ipynb contains exploratory data analysis on e-commerce data in @ecommerce_data, focusing on sales metrics for 2023. Keep the same analysis and graphs, and improve the structure and documentation of the notebook.

Review the existing notebook and identify:
- What business metrics are currently calculated
- What visualizations are created
- What data transformations are performed
- Any code quality issues or inefficiencies
  
**Refactoring Requirements**

1. Notebook Structure & Documentation
    - Add proper documentation and markdown cells with clear header and a brief explanation for the section
    - Organize into logical sections:
        - Introduction & Business Objectives
        - Data Loading & Configuration
        - Data Preparation & Transformation
        - Business Metrics Calculation (revenue, product, geographic, customer experience analysis)
        - Summary of observations
    - Add table of contents at the beginning
    - Include data dictionary explaining key columns and business terms
   
2. Code Quality Improvements
   - Create reusable functions with docstrings
   - Implement consistent naming and formatting
   - Create separate Python files:
 	- business_metrics.py containing business metric calculations only
	- data_loader.py loading, processing and cleaning the data  
        
3. Enhanced Visualizations
    - Improve all plots with:
        - Clear and descriptive titles 
        - Proper axis labels with units
        - Legends where needed
        - Appropriate chart types for the data
        - Include date range in plot titles or captions
        - use consistent color business-oriented color schemes
          
4. Configurable Analysis Framework
The notebook shows the computation of metrics for a specific date range (entire year of 2023 compared to 2022). Refactor the code so that the data is first filtered according to configurable month and year & implement general-purpose metric calculations. 
       

**Deliverables Expected**
- Refactored Jupyter notebook (EDA_Refactored.ipynb) with all improvements
- Business metrics module (business_metrics.py) with documented functions
- Requirements file (requirements.txt) listing all dependencies
- README section explaining how to use the refactored analysis

**Success Criteria**
- Easy-to read code & notebook (do not use icons in the printing statements or markdown cells)
- Configurable analysis that works for any date range
- Reusable code that can be applied to future datasets
- Maintainable structure that other analysts can easily understand and extend
- Maintain all existing analyses while improving the quality, structure, and usability of the notebook.
- Do not assume any business thresholds.

---

## How to Use the Refactored E-commerce Analysis

### Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Analysis Parameters**
   Open `EDA_Refactored.ipynb` and modify the configuration section:
   ```python
   ANALYSIS_YEAR = 2023        # Year to analyze
   COMPARISON_YEAR = 2022      # Year for comparison
   ANALYSIS_MONTH = None       # Specific month (1-12) or None for full year
   DATA_PATH = "ecommerce_data/"
   ```

3. **Run the Analysis**
   Execute all cells in the notebook to generate the complete business intelligence report.

### Project Structure

```
├── EDA_Refactored.ipynb     # Main analysis notebook
├── data_loader.py           # Data loading and processing functions
├── business_metrics.py      # Business metrics calculations
├── requirements.txt         # Python dependencies
└── ecommerce_data/         # Data directory
    ├── orders_dataset.csv
    ├── order_items_dataset.csv
    ├── products_dataset.csv
    ├── customers_dataset.csv
    └── order_reviews_dataset.csv
```

### Key Features

**Configurable Time Periods**
- Analyze any year or specific month
- Automatic comparison with previous periods
- Flexible date range filtering

**Modular Architecture**
- `EcommerceDataLoader`: Handles all data loading and preprocessing
- `EcommerceMetrics`: Contains business metric calculations and visualizations
- Clean separation of concerns for maintainability

**Comprehensive Analysis**
- Revenue performance and growth trends
- Product category analysis
- Geographic sales distribution
- Customer experience and satisfaction metrics
- Order fulfillment performance

**Enhanced Visualizations**
- Professional charts with proper labels and formatting
- Interactive geographic heatmaps
- Business-oriented color schemes
- Clear titles with date ranges

### Usage Examples

**Analyze Full Year Performance**
```python
ANALYSIS_YEAR = 2023
COMPARISON_YEAR = 2022
ANALYSIS_MONTH = None
```

**Analyze Specific Month**
```python
ANALYSIS_YEAR = 2023
COMPARISON_YEAR = 2022
ANALYSIS_MONTH = 6  # June analysis
```

**Custom Analysis Using Modules**
```python
from data_loader import EcommerceDataLoader
from business_metrics import EcommerceMetrics

# Initialize tools
loader = EcommerceDataLoader("ecommerce_data/")
metrics = EcommerceMetrics()

# Load and process data
loader.load_all_datasets()
sales_data = loader.prepare_sales_data(year=2023)

# Calculate metrics
revenue_metrics = metrics.calculate_revenue_metrics(sales_data)
```

### Business Metrics Included

- **Revenue Metrics**: Total revenue, growth rates, average order value
- **Product Performance**: Category-wise revenue, order counts, profitability
- **Geographic Analysis**: State-wise performance, customer distribution
- **Customer Experience**: Satisfaction scores, delivery performance, fulfillment rates
- **Operational Metrics**: Order status distribution, delivery speed analysis

### Extending the Analysis

The modular design allows easy extension:

1. **Add New Metrics**: Extend the `EcommerceMetrics` class
2. **New Data Sources**: Modify the `EcommerceDataLoader` class
3. **Custom Visualizations**: Add new chart methods to the metrics class
4. **Different Time Granularity**: Extend filtering capabilities in the data loader

### Support

For issues or enhancements, ensure your data follows the expected schema and all dependencies are properly installed.

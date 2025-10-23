# Clinical Trials Analytics Project

A comprehensive analytics solution for clinical trial data analysis, featuring both a REST API and interactive dashboard for data visualization and insights.

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Architecture & Design Decisions](#architecture--design-decisions)
- [Installation & Setup](#installation--setup)
- [Usage Guide](#usage-guide)
- [API Documentation](#api-documentation)
- [Data Format Requirements](#data-format-requirements)
- [Error Handling & Assumptions](#error-handling--assumptions)
- [Project Structure](#project-structure)
- [Development Decisions](#development-decisions)

## 🎯 Project Overview

This project provides a complete analytics solution for clinical trial data, offering:

- **REST API** for programmatic access to analytics
- **Interactive Dashboard** for visual data exploration
- **Data Generation** tools for testing and development
- **Robust Error Handling** for production reliability

### Key Features

- **Summary Statistics**: Patient counts, completion rates, adverse event analysis
- **Site Performance Analysis**: Compare trial sites across multiple metrics
- **Age Group Analysis**: Performance breakdown by patient age brackets
- **Temporal Trends**: Monthly enrollment and outcome patterns
- **Correlation Analysis**: Variable relationship identification
- **Automated Insights**: AI-generated recommendations

## 🎯 Approach & Design Decisions

### Development Approach

This project was developed with a **modular, production-ready architecture** focusing on separation of concerns and maintainability. The solution prioritizes:

- **Modularity**: Separated analytics logic (`analytics.py`) from presentation layers (API and dashboard)
- **Error Resilience**: Graceful handling of malformed data with informative logging
- **User Experience**: Both programmatic (API) and interactive (dashboard) interfaces
- **Documentation**: Comprehensive inline comments and usage documentation

### Key Design Decisions

1. **Modular Architecture**: 
   - `analytics.py` contains all data processing logic
   - `api.py` handles REST endpoints and file uploads
   - `st_dashboard.py` provides interactive visualization
   - This separation allows for easy testing and maintenance

2. **Error Handling Strategy**:
   - Graceful degradation: drop invalid rows/columns rather than failing
   - Comprehensive logging for debugging and monitoring
   - User-friendly error messages in API responses

3. **Data Processing Pipeline**:
   - Robust CSV parsing with multiple null value representations
   - Type conversion with error handling (dates, booleans, numerics)
   - Automatic data cleaning and validation

4. **API Design**:
   - Simple, focused endpoints (upload + summary)
   - File upload with temporary storage and cleanup
   - JSON responses with consistent error handling

### Bonus Tasks Completed

**All bonus tasks (A-D) were implemented:**

- **A. Advanced Analytics**: Site performance, age group analysis, temporal trends, correlations
- **B. Interactive Dashboard**: Streamlit-based visualization with charts and insights
- **C. REST API**: Flask-based API with file upload and summary statistics
- **D. Data Generation**: Synthetic data generation with Faker for testing

### Time Investment

**Estimated Development Time: 5 hours**

This includes:
- Initial setup and data generation (30 minutes)
- Core analytics implementation (1.5 hours)
- API development and testing (1.5 hours)
- Dashboard creation and integration (1 hour)
- Documentation and error handling (1 hour)

## 🏗️ Architecture & Design Decisions

### Modular Architecture

The project follows a **separation of concerns** principle with three main components:

```
analytics.py     → Core business logic & data processing
api.py          → REST API endpoints & HTTP handling  
st_dashboard.py → Interactive web dashboard
```

**Decision Rationale**: This modular approach enables:
- **Reusability**: Same analytics functions serve both API and dashboard
- **Maintainability**: Changes to analytics logic only need to be made once
- **Scalability**: Easy to add new interfaces (mobile app, CLI, etc.)
- **Testing**: Each component can be tested independently

### Data Processing Pipeline

```
CSV Data → Validation → Cleaning → Analysis → JSON/Visualization
```

**Key Design Decisions**:

1. **Dictionary-based Returns**: Analytics functions return structured dictionaries instead of DataFrames
   - **Rationale**: Better JSON serialization for API responses
   - **Trade-off**: Dashboard needs to convert back to DataFrames for visualization

2. **Simple Error Handling**: Basic missing data cleanup without complex validation
   - **Rationale**: Keeps the system simple and maintainable
   - **Assumption**: Data quality issues are handled at the source

3. **Age Group Categorization**: Fixed age brackets (18-30, 31-50, 51-70, 71-80)
   - **Rationale**: Standard clinical trial age groupings
   - **Assumption**: These brackets are appropriate for most trial analyses

## 🚀 Installation & Setup

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation Steps

1. **Clone or download the project**
   ```bash
   cd /path/to/Takehome_Project
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Generate sample data** (optional)
   ```bash
   python generate_data.py
   ```

4. **Verify installation**
   ```bash
   python -c "from analytics import load_data; print('Installation successful!')"
   ```

## 📖 Usage Guide

### Option 1: REST API

**Start the API server:**
```bash
flask run --host=0.0.0.0 --port=8000
```

The API will be available at `http://localhost:8000`

**Basic Usage:**

**Using cURL:**
```bash
# Get summary statistics from default data
curl http://localhost:8000/api/summary

# Upload and analyze a CSV file
curl -X POST -F "file=@your_data.csv" http://localhost:8000/api/upload
```

**Using Postman:**
1. **Create a new request**
2. **Set method to `POST`**
3. **Set URL to:** `http://localhost:8000/api/upload`
4. **Go to Body tab → Select "form-data"**
5. **Add key:** `file` (set type to "File")
6. **Select your CSV file**
7. **Click Send**

**For GET requests (like `/api/summary`):**
1. **Set method to `GET`**
2. **Set URL to:** `http://localhost:8000/api/summary`
3. **Click Send**

### Option 2: Interactive Dashboard

**Start the dashboard:**
```bash
streamlit run st_dashboard.py
```

The dashboard will be available at `http://localhost:8501`

**Features:**
- Interactive charts and visualizations
- Real-time data analysis
- Export capabilities
- Responsive design

### Option 3: Programmatic Usage

```python
from analytics import load_data, calculate_summary_statistics

# Load and analyze data
df = load_data()
stats = calculate_summary_statistics(df)
print(f"Total patients: {stats['total_patients']}")
print(f"Completion rate: {stats['completion_rate']}%")
```

## 🔌 API Documentation

### Endpoints

| Endpoint | Method | Description | Parameters |
|----------|--------|-------------|------------|
| `/api/summary` | GET | Get summary statistics from default data | None |
| `/api/upload` | POST | Upload CSV file and get analysis | `file` (multipart/form-data) |
| `/api/docs` | GET | Get API documentation | None |

### Response Format

**Success Response:**
```json
{
  "total_patients": 40,
  "patients_per_site": [
    {"trial_site": "Boston", "patient_count": 8},
    {"trial_site": "Chicago", "patient_count": 8}
  ],
  "average_age": 52.3,
  "completion_rate": 87.5,
  "adverse_event_rate": 30.0,
  "completion_rate_with_ae": 70.0,
  "completion_rate_without_ae": 90.0
}
```

**Error Response:**
```json
{
  "error": "CSV file not found: data/clinical_trials.csv"
}
```

### Example Usage

**Python:**
```python
import requests

# Get summary statistics
response = requests.get('http://localhost:8000/api/summary')
data = response.json()
print(f"Completion rate: {data['completion_rate']}%")

# Upload file
with open('data.csv', 'rb') as f:
    response = requests.post('http://localhost:8000/api/upload', files={'file': f})
    result = response.json()
```

**cURL:**
```bash
# Get summary
curl http://localhost:8000/api/summary

# Upload file
curl -X POST -F "file=@data.csv" http://localhost:8000/api/upload
```

## 📊 Data Format Requirements

### CSV File Structure

Your CSV file must contain the following columns:

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `patient_id` | String | Unique patient identifier | "P001" |
| `trial_site` | String | Location where trial was conducted | "Boston" |
| `enrollment_date` | Date | Date patient enrolled (YYYY-MM-DD) | "2024-01-15" |
| `age` | Integer | Patient age (18-100) | 45 |
| `adverse_event` | Boolean | Whether patient had adverse event | true/false |
| `completed_trial` | Boolean | Whether patient completed trial | true/false |

### Sample CSV Format

```csv
patient_id,trial_site,enrollment_date,age,adverse_event,completed_trial
P001,Boston,2024-01-15,45,false,true
P002,Chicago,2024-01-20,32,true,true
P003,New York,2024-02-01,67,false,false
```

### Data Quality Assumptions

1. **Date Format**: Assumes ISO date format (YYYY-MM-DD)
2. **Boolean Values**: Accepts true/false, 1/0, yes/no
3. **Age Range**: Assumes ages between 18-100 are valid
4. **Missing Data**: Rows/columns with missing data are automatically dropped
5. **Encoding**: Assumes UTF-8 encoding for CSV files

## ⚠️ Error Handling & Assumptions

### Error Handling Strategy

The project implements a **graceful degradation** approach:

1. **Data Loading**: Missing data is automatically cleaned (rows/columns dropped)
2. **API Errors**: Returns structured error responses with HTTP status codes
3. **File Upload**: Validates file type and size before processing
4. **Logging**: Important events are logged for debugging

### Key Assumptions Made

1. **Data Quality**: 
   - **Assumption**: Source data is generally clean with occasional missing values
   - **Decision**: Simple dropna() approach rather than complex imputation
   - **Rationale**: Maintains data integrity while keeping system simple

2. **Age Grouping**:
   - **Assumption**: Standard clinical trial age brackets are appropriate
   - **Decision**: Fixed age groups (18-30, 31-50, 51-70, 71-80)
   - **Rationale**: Aligns with industry standards

3. **Temporal Analysis**:
   - **Assumption**: Monthly granularity is sufficient for trend analysis
   - **Decision**: Extract enrollment month for temporal patterns
   - **Rationale**: Balances detail with analysis complexity

4. **Site Performance**:
   - **Assumption**: All sites should be compared on same metrics
   - **Decision**: Standardized performance metrics across sites
   - **Rationale**: Enables fair comparison and benchmarking

5. **API Design**:
   - **Assumption**: Simple REST API is sufficient for most use cases
   - **Decision**: Focus on basic upload and summary endpoints
   - **Rationale**: Keeps API simple and maintainable

### Error Scenarios Handled

- **Missing CSV file**: Clear error message with file path
- **Empty CSV file**: Graceful handling with informative message
- **Malformed CSV**: Pandas parsing errors caught and reported
- **Missing columns**: System continues with available data
- **Invalid data types**: Automatic conversion where possible
- **File upload errors**: Size limits and type validation

## 📁 Project Structure

```
Takehome_Project/
├── analytics.py              # Core analytics functions
├── api.py                   # REST API server
├── st_dashboard.py          # Streamlit dashboard
├── generate_data.py         # Sample data generator
├── requirements.txt         # Python dependencies
├── README.md               # This documentation
└── data/
    └── clinical_trials.csv  # Sample data file
```

### File Responsibilities

- **`analytics.py`**: data processing and statistical calculations (Project Requirements)
- **`api.py`**: HTTP endpoints, file upload handling, JSON responses (Bonus Question: B)
- **`st_dashboard.py`**: Interactive visualizations, user interface (Bonus Question A, C, D)
- **`generate_data.py`**: Synthetic data generation for testing
- **`requirements.txt`**: library management and version control

## Development Decisions

### Technology Stack Choices

1. **Python + Pandas**: 
   - **Rationale**: Excellent for data analysis and statistical operations
   - **Alternative Considered**: R (chose Python for better API integration)

2. **Flask for API**:
   - **Rationale**: Lightweight, simple, and sufficient for basic REST endpoints
   - **Alternative Considered**: FastAPI (chose Flask for simplicity)

3. **Streamlit for Dashboard**:
   - **Rationale**: Rapid development, built-in visualization support
   - **Alternative Considered**: Dash (chose Streamlit for ease of use)

4. **Plotly for Visualizations**:
   - **Rationale**: Interactive charts, good integration with Streamlit
   - **Alternative Considered**: Matplotlib (chose Plotly for interactivity)

### Design Patterns Used

1. **Separation of Concerns**: Analytics logic separated from presentation
2. **Single Responsibility**: Each function has one clear purpose
3. **Error Handling**: Graceful degradation with informative messages
4. **Modularity**: Components can be used independently

### Performance Considerations

1. **Data Loading**: Single CSV read with in-memory processing
2. **API Responses**: JSON serialization for fast data transfer
3. **Dashboard**: Client-side rendering for interactive charts
4. **Memory Usage**: DataFrames kept in memory for analysis speed

### Security Considerations

1. **File Upload**: File type validation and size limits
2. **Input Sanitization**: Secure filename handling
3. **Error Messages**: No sensitive information in error responses
4. **CORS**: Enabled for cross-origin requests (development only)

## Future Enhancements

### Potential Improvements

1. **Database Integration**: Replace CSV files with proper database
2. **Authentication**: Add user authentication and authorization
3. **Caching**: Implement response caching for better performance
4. **Advanced Analytics**: Add statistical significance testing
5. **Export Features**: PDF reports and data export capabilities
6. **Real-time Updates**: WebSocket support for live data updates

### Scalability Considerations

1. **Horizontal Scaling**: API can be deployed behind load balancer
2. **Data Volume**: Current design handles thousands of records efficiently
3. **Concurrent Users**: Streamlit supports multiple concurrent sessions
4. **Storage**: File-based approach can be replaced with database





# Stock Analysis API

A comprehensive FastAPI backend for stock analysis, predictions, and news aggregation.

## Features

- **Historical Stock Data**: Fetch 30 days of historical stock prices
- **Price Predictions**: Use Prophet ML model to predict next 5 days of stock prices
- **Company News**: Fetch recent news articles about companies using Tavily API
- **Top Gainers**: Get a list of top performing stocks
- **AWS Lambda Ready**: Designed for easy deployment to AWS Lambda

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Keys

Edit `app.py` and replace the Tavily API key:

```python
TAVILY_API_KEY = "your_actual_tavily_api_key_here"
```

Get your Tavily API key from: https://tavily.com/

### 3. Run Locally

```bash
# Option 1: Using uvicorn directly
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# Option 2: Using Python
python app.py
```

The API will be available at: http://localhost:8000

## API Endpoints

### 1. GET /stock?ticker=<symbol>

Fetch the last 30 days of historical stock prices.

**Example:**
```bash
curl "http://localhost:8000/stock?ticker=AAPL"
```

**Response:**
```json
{
  "ticker": "AAPL",
  "company_name": "Apple Inc.",
  "data": [
    {
      "date": "2023-11-01",
      "open": 150.25,
      "high": 152.50,
      "low": 149.80,
      "close": 151.20,
      "volume": 12345678
    }
  ],
  "last_updated": "2023-11-01T10:30:00"
}
```

### 2. GET /predict?ticker=<symbol>

Predict the next 5 days of stock prices using Prophet ML model.

**Example:**
```bash
curl "http://localhost:8000/predict?ticker=GOOGL"
```

**Response:**
```json
{
  "ticker": "GOOGL",
  "company_name": "Alphabet Inc.",
  "predictions": [
    {
      "ds": "2023-11-02",
      "yhat": 145.50,
      "yhat_lower": 143.20,
      "yhat_upper": 147.80
    }
  ],
  "model_info": {
    "training_period": "2023-05-01 to 2023-11-01",
    "prediction_horizon": "5 days"
  },
  "last_updated": "2023-11-01T10:30:00"
}
```

### 3. GET /news?company=<name>

Fetch recent news articles about a company.

**Example:**
```bash
curl "http://localhost:8000/news?company=Apple"
```

**Response:**
```json
{
  "company": "Apple",
  "articles": [
    {
      "title": "Apple Reports Strong Q4 Earnings",
      "summary": "Apple Inc. reported better-than-expected quarterly results...",
      "url": "https://example.com/article1",
      "published_date": "2023-11-01",
      "source": "Reuters"
    }
  ],
  "total_articles": 10,
  "search_query": "Apple stock news",
  "last_updated": "2023-11-01T10:30:00"
}
```

### 4. GET /suggest

Get a list of top gaining stocks.

**Example:**
```bash
curl "http://localhost:8000/suggest"
```

**Response:**
```json
{
  "top_gainers": [
    {
      "ticker": "NVDA",
      "company_name": "NVIDIA Corporation",
      "current_price": 450.25,
      "previous_close": 440.00,
      "change_percent": 2.33,
      "change_amount": 10.25
    }
  ],
  "total_analyzed": 16,
  "last_updated": "2023-11-01T10:30:00"
}
```

### 5. GET /health

Health check endpoint for monitoring.

**Example:**
```bash
curl "http://localhost:8000/health"
```

## AWS Lambda Deployment

### Using Zappa

1. Install Zappa:
```bash
pip install zappa
```

2. Initialize Zappa:
```bash
zappa init
```

3. Deploy:
```bash
zappa deploy
```

### Using AWS SAM

1. Create `template.yaml`:
```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Resources:
  StockAnalysisAPI:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: ./
      Handler: app.handler
      Runtime: python3.9
      Timeout: 30
      Events:
        Api:
          Type: Api
          Properties:
            Path: /{proxy+}
            Method: ANY
```

2. Deploy:
```bash
sam build
sam deploy --guided
```

## Error Handling

The API includes comprehensive error handling:

- **400 Bad Request**: Invalid input parameters
- **404 Not Found**: Stock data not found
- **500 Internal Server Error**: Server-side errors

## Environment Variables

For production deployment, consider using environment variables:

```bash
export TAVILY_API_KEY="your_api_key"
export ENVIRONMENT="production"
```

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

### API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Notes

- The Prophet model uses 6 months of historical data for predictions
- News API requires a valid Tavily API key
- All endpoints return JSON responses
- CORS is enabled for frontend integration
- The API is designed to be stateless for Lambda deployment

## Troubleshooting

1. **Prophet installation issues**: On Windows, you might need to install Microsoft C++ Build Tools
2. **yfinance data issues**: Some stocks might not have complete data
3. **API rate limits**: Consider implementing rate limiting for production use
4. **Memory usage**: Prophet models can be memory-intensive; consider model optimization for Lambda

## License

MIT License 
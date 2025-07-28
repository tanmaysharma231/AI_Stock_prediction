from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict, Any
import yfinance as yf
import pandas as pd
from prophet import Prophet
import requests
import json
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Stock Analysis API",
    description="A comprehensive API for stock analysis, predictions, and news",
    version="1.0.0"
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
TAVILY_API_KEY = "YOUR_TAVILY_API_KEY"  # Replace with your actual API key
TAVILY_BASE_URL = "https://api.tavily.com/search"

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Stock Analysis API",
        "version": "1.0.0",
        "endpoints": {
            "/stock": "Get historical stock data",
            "/predict": "Get stock price predictions",
            "/news": "Get company news",
            "/suggest": "Get top gainers"
        }
    }

@app.get("/stock")
async def get_stock_data(ticker: str = Query(..., description="Stock ticker symbol")):
    """
    Fetch the last 30 days of historical stock prices for the given ticker.
    
    Args:
        ticker (str): Stock ticker symbol (e.g., 'AAPL', 'GOOGL')
    
    Returns:
        dict: Historical stock data with dates and prices
    """
    try:
        # Validate ticker input
        ticker = ticker.upper().strip()
        if not ticker:
            raise HTTPException(status_code=400, detail="Ticker symbol cannot be empty")
        
        # Fetch stock data using yfinance
        stock = yf.Ticker(ticker)
        
        # Get historical data for the last 30 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        hist_data = stock.history(start=start_date, end=end_date)
        
        if hist_data.empty:
            raise HTTPException(status_code=404, detail=f"No data found for ticker {ticker}")
        
        # Convert to JSON-serializable format
        stock_data = []
        for date, row in hist_data.iterrows():
            stock_data.append({
                "date": date.strftime("%Y-%m-%d"),
                "open": float(row['Open']),
                "high": float(row['High']),
                "low": float(row['Low']),
                "close": float(row['Close']),
                "volume": int(row['Volume'])
            })
        
        # Get basic stock info
        info = stock.info
        company_name = info.get('longName', ticker)
        
        return {
            "ticker": ticker,
            "company_name": company_name,
            "data": stock_data,
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching stock data for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching stock data: {str(e)}")

@app.get("/predict")
async def predict_stock_prices(ticker: str = Query(..., description="Stock ticker symbol")):
    """
    Use Prophet to predict the next 5 days of stock prices based on the last 6 months of data.
    
    Args:
        ticker (str): Stock ticker symbol (e.g., 'AAPL', 'GOOGL')
    
    Returns:
        dict: Predictions with date, yhat, yhat_lower, yhat_upper
    """
    try:
        # Validate ticker input
        ticker = ticker.upper().strip()
        if not ticker:
            raise HTTPException(status_code=400, detail="Ticker symbol cannot be empty")
        
        # Fetch stock data using yfinance
        stock = yf.Ticker(ticker)
        
        # Get historical data for the last 6 months
        end_date = datetime.now()
        start_date = end_date - timedelta(days=180)
        
        hist_data = stock.history(start=start_date, end=end_date)
        
        if hist_data.empty:
            raise HTTPException(status_code=404, detail=f"No data found for ticker {ticker}")
        
        # Prepare data for Prophet (requires 'ds' for dates and 'y' for values)
        df = pd.DataFrame({
            'ds': hist_data.index,
            'y': hist_data['Close']
        })
        
        # Initialize and fit Prophet model
        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False,
            seasonality_mode='multiplicative'
        )
        
        # Fit the model
        model.fit(df)
        
        # Create future dataframe for predictions (next 5 days)
        future_dates = model.make_future_dataframe(periods=5)
        forecast = model.predict(future_dates)
        
        # Extract only the future predictions (last 5 rows)
        future_predictions = forecast.tail(5)
        
        # Convert predictions to JSON-serializable format
        predictions = []
        for _, row in future_predictions.iterrows():
            predictions.append({
                "ds": row['ds'].strftime("%Y-%m-%d"),
                "yhat": float(row['yhat']),
                "yhat_lower": float(row['yhat_lower']),
                "yhat_upper": float(row['yhat_upper'])
            })
        
        # Get basic stock info
        info = stock.info
        company_name = info.get('longName', ticker)
        
        return {
            "ticker": ticker,
            "company_name": company_name,
            "predictions": predictions,
            "model_info": {
                "training_period": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
                "prediction_horizon": "5 days"
            },
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error predicting stock prices for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error predicting stock prices: {str(e)}")

@app.get("/news")
async def get_company_news(company: str = Query(..., description="Company name or ticker")):
    """
    Use the Tavily API to fetch recent news articles about the company.
    
    Args:
        company (str): Company name or ticker symbol
    
    Returns:
        dict: News articles with titles, summaries, and URLs
    """
    try:
        # Validate company input
        company = company.strip()
        if not company:
            raise HTTPException(status_code=400, detail="Company name cannot be empty")
        
        # Check if API key is configured
        if TAVILY_API_KEY == "YOUR_TAVILY_API_KEY":
            raise HTTPException(
                status_code=500, 
                detail="Tavily API key not configured. Please set TAVILY_API_KEY in the code."
            )
        
        # Prepare search query
        search_query = f"{company} stock news"
        
        # Make request to Tavily API
        headers = {
            "api-key": TAVILY_API_KEY,
            "content-type": "application/json"
        }
        
        payload = {
            "query": search_query,
            "search_depth": "basic",
            "include_answer": False,
            "include_raw_content": False,
            "max_results": 10
        }
        
        response = requests.post(TAVILY_BASE_URL, headers=headers, json=payload)
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Tavily API error: {response.text}"
            )
        
        data = response.json()
        
        # Extract and format news articles
        articles = []
        if 'results' in data:
            for result in data['results']:
                articles.append({
                    "title": result.get('title', ''),
                    "summary": result.get('content', ''),
                    "url": result.get('url', ''),
                    "published_date": result.get('published_date', ''),
                    "source": result.get('source', '')
                })
        
        return {
            "company": company,
            "articles": articles,
            "total_articles": len(articles),
            "search_query": search_query,
            "last_updated": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching news for {company}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching news: {str(e)}")

@app.get("/suggest")
async def get_top_gainers():
    """
    Return a simple list of top gainers using yfinance.
    
    Returns:
        dict: List of top gaining stocks
    """
    try:
        # List of popular stocks to check
        popular_tickers = [
            'AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX',
            'AMD', 'INTC', 'CRM', 'ORCL', 'ADBE', 'PYPL', 'UBER', 'LYFT'
        ]
        
        gainers = []
        
        for ticker in popular_tickers:
            try:
                stock = yf.Ticker(ticker)
                
                # Get current price and previous close
                current_price = stock.info.get('currentPrice')
                previous_close = stock.info.get('previousClose')
                
                if current_price and previous_close:
                    change_percent = ((current_price - previous_close) / previous_close) * 100
                    
                    gainers.append({
                        "ticker": ticker,
                        "company_name": stock.info.get('longName', ticker),
                        "current_price": current_price,
                        "previous_close": previous_close,
                        "change_percent": round(change_percent, 2),
                        "change_amount": round(current_price - previous_close, 2)
                    })
                    
            except Exception as e:
                logger.warning(f"Error fetching data for {ticker}: {str(e)}")
                continue
        
        # Sort by percentage gain (descending)
        gainers.sort(key=lambda x: x['change_percent'], reverse=True)
        
        # Return top 10 gainers
        top_gainers = gainers[:10]
        
        return {
            "top_gainers": top_gainers,
            "total_analyzed": len(popular_tickers),
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching top gainers: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching top gainers: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Stock Analysis API"
    }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {"error": "Endpoint not found", "detail": str(exc)}

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {"error": "Internal server error", "detail": str(exc)}

if __name__ == "__main__":
    # For local development, run with: uvicorn app:app --reload --host 0.0.0.0 --port 8000
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
#!/usr/bin/env python3
"""
Simple test script for the Stock Analysis API
Run this after starting the server to test all endpoints
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_endpoint(endpoint, params=None):
    """Test an API endpoint and print results"""
    try:
        url = f"{BASE_URL}{endpoint}"
        response = requests.get(url, params=params)
        
        print(f"\n{'='*50}")
        print(f"Testing: {endpoint}")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Success!")
            print(f"Response keys: {list(data.keys())}")
            
            # Print a sample of the data
            if isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, list) and len(value) > 0:
                        print(f"{key}: {len(value)} items")
                        if len(value) > 0:
                            print(f"Sample: {value[0]}")
                    elif isinstance(value, dict):
                        print(f"{key}: {len(value)} keys")
                    else:
                        print(f"{key}: {value}")
        else:
            print("❌ Failed!")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

def main():
    """Run all API tests"""
    print("🧪 Testing Stock Analysis API")
    print(f"Base URL: {BASE_URL}")
    
    # Test root endpoint
    test_endpoint("/")
    
    # Test health endpoint
    test_endpoint("/health")
    
    # Test stock data endpoint
    test_endpoint("/stock", {"ticker": "AAPL"})
    
    # Test prediction endpoint (this might take longer due to ML model)
    print("\n⏳ Testing prediction endpoint (this may take 30-60 seconds)...")
    test_endpoint("/predict", {"ticker": "AAPL"})
    
    # Test suggest endpoint
    test_endpoint("/suggest")
    
    # Test news endpoint (will fail without API key, but that's expected)
    test_endpoint("/news", {"company": "Apple"})
    
    print(f"\n{'='*50}")
    print("🎉 Testing complete!")
    print("\nNote: News endpoint will fail without a valid Tavily API key.")
    print("To fix this, update the TAVILY_API_KEY in app.py")

if __name__ == "__main__":
    main() 
import os
import yfinance as yf
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
from decimal import Decimal
import boto3
import time
import random
from strands import Agent
from strands.models import BedrockModel


def convert_decimal_to_float(obj):
    """Convert Decimal objects to float for JSON serialization"""
    if isinstance(obj, list):
        return [convert_decimal_to_float(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: convert_decimal_to_float(value) for key, value in obj.items()}
    elif isinstance(obj, Decimal):
        return float(obj)
    else:
        return obj


class StrandMarketDataAgent:
    """
    Strands SDK Market Data Agent with intelligent fallback system
    Enhanced for Indian Market
    """
    
    def __init__(self, delay_between_calls=0.3, max_retries=3):
        """Initialize with multiple API configurations"""
        self.dynamodb = boto3.resource("dynamodb", region_name=os.getenv("AWS_REGION", "us-east-1"))
        self.portfolios_table = self.dynamodb.Table('WealthWisePortfolios')
        
        # API Configuration
        self.apis = {
            # US Market APIs
            'alpha_vantage': {
                'key': os.getenv('ALPHA_VANTAGE_API_KEY', 'LO1QXEUYC52A2F4J'),
                'base_url': 'https://www.alphavantage.co/query',
                'rate_limit': 0.5,
                'last_call': 0,
                'enabled': bool(os.getenv('ALPHA_VANTAGE_API_KEY', 'LO1QXEUYC52A2F4J')),
                'market': 'US'
            },
            'finnhub': {
                'key': os.getenv('FINNHUB_API_KEY', ''),
                'base_url': 'https://finnhub.io/api/v1',
                'rate_limit': 1.0,
                'last_call': 0,
                'enabled': bool(os.getenv('FINNHUB_API_KEY', 'd3p2u71r01quo6o6jlngd3p2u71r01quo6o6jlo0')),
                'market': 'US'
            },
            'polygon': {
                'key': os.getenv('POLYGON_API_KEY', ''),
                'base_url': 'https://api.polygon.io',
                'rate_limit': 12.0,
                'last_call': 0,
                'enabled': bool(os.getenv('POLYGON_API_KEY')),
                'market': 'US'
            },
            
            # Universal APIs (US + Indian)
            'yahoo': {
                'enabled': True,
                'rate_limit': 0.5,
                'last_call': 0,
                'market': 'BOTH'
            },
            
            # Indian Market APIs (FREE)
            'nse_india': {
                'enabled': True,
                'base_url': 'https://www.nseindia.com/api',
                'rate_limit': 1.0,
                'last_call': 0,
                'market': 'IN'
            },
            'bse_india': {
                'enabled': True,
                'base_url': 'https://api.bseindia.com/BseIndiaAPI/api',
                'rate_limit': 1.0,
                'last_call': 0,
                'market': 'IN'
            },
            'groww': {
                'enabled': True,
                'base_url': 'https://groww.in/v1/api',
                'rate_limit': 1.0,
                'last_call': 0,
                'market': 'IN'
            }
        }
        
        self.delay_between_calls = delay_between_calls
        self.max_retries = max_retries
        self.cache = {}
        self.cache_ttl = 60
        
        active_apis = [name for name, config in self.apis.items() if config['enabled']]
        print(f"📌 [Strand Market Agent] Active APIs: {', '.join(active_apis)}")
    
    def _is_indian_symbol(self, symbol: str) -> bool:
        """Check if a symbol is likely an Indian stock"""
        indian_stocks = [
            'RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK', 
            'SBIN', 'BHARTIARTL', 'ITC', 'KOTAKBANK', 'LT', 
            'AXISBANK', 'HINDUNILVR', 'BAJFINANCE', 'ASIANPAINT',
            'MARUTI', 'TITAN', 'WIPRO', 'ULTRACEMCO', 'SUNPHARMA',
            'NESTLEIND', 'HCLTECH', 'TECHM', 'TATAMOTORS', 'ADANIPORTS',
            'POWERGRID', 'ONGC', 'NTPC', 'COALINDIA', 'DRREDDY', 'CIPLA'
        ]
        
        # Check if symbol is in known Indian stocks or has Indian exchange suffix
        return (symbol.upper() in indian_stocks or 
                '.NS' in symbol.upper() or 
                '.BO' in symbol.upper())
    
    def _respect_rate_limit(self, api_name: str):
        """Enforce rate limiting for each API"""
        api = self.apis[api_name]
        elapsed = time.time() - api['last_call']
        if elapsed < api['rate_limit']:
            sleep_time = api['rate_limit'] - elapsed
            time.sleep(sleep_time)
        api['last_call'] = time.time()
    
    def _check_cache(self, symbol: str) -> Optional[Dict]:
        """Check if we have cached data for symbol"""
        if symbol in self.cache:
            cached_time, data = self.cache[symbol]
            if time.time() - cached_time < self.cache_ttl:
                print(f"💾 Using cached data for {symbol}")
                return data
        return None
    
    def _update_cache(self, symbol: str, data: Dict):
        """Update cache with new data"""
        self.cache[symbol] = (time.time(), data)
    
    def _get_fallback_data(self, symbol: str) -> Optional[Dict]:
        """
        Comprehensive fallback data for when all APIs fail
        Provides realistic estimates for common ETFs, stocks, and funds
        """
        symbol_upper = symbol.upper()
        
        # ETF Fallback Data - Common US ETFs
        etf_fallbacks = {
            'SPY': {
                'currentPrice': 445.0,
                'sector': 'ETF - Large Cap',
                'industry': 'Index Fund',
                'beta': 1.0,
                'week52High': 470.0,
                'week52Low': 380.0,
                'dayChange': 2.5,
                'dayChangePct': 0.56,
                'dividendYield': 1.3,
                'ytdReturn': 12.5
            },
            'QQQ': {
                'currentPrice': 385.0,
                'sector': 'ETF - Technology',
                'industry': 'Index Fund',
                'beta': 1.15,
                'week52High': 410.0,
                'week52Low': 310.0,
                'dayChange': 3.2,
                'dayChangePct': 0.84,
                'dividendYield': 0.6,
                'ytdReturn': 18.2
            },
            'VTI': {
                'currentPrice': 250.0,
                'sector': 'ETF - Total Market',
                'industry': 'Index Fund',
                'beta': 1.0,
                'week52High': 265.0,
                'week52Low': 210.0,
                'dayChange': 1.8,
                'dayChangePct': 0.72,
                'dividendYield': 1.4,
                'ytdReturn': 11.8
            },
            'BND': {
                'currentPrice': 78.5,
                'sector': 'ETF - Bonds',
                'industry': 'Bond Fund',
                'beta': 0.1,
                'week52High': 82.0,
                'week52Low': 75.0,
                'dayChange': 0.1,
                'dayChangePct': 0.13,
                'dividendYield': 3.8,
                'ytdReturn': 2.1
            },
            'VXUS': {
                'currentPrice': 62.0,
                'sector': 'ETF - International',
                'industry': 'Index Fund',
                'beta': 0.85,
                'week52High': 68.0,
                'week52Low': 55.0,
                'dayChange': 0.8,
                'dayChangePct': 1.31,
                'dividendYield': 2.8,
                'ytdReturn': 8.4
            },
            'VNQ': {
                'currentPrice': 95.0,
                'sector': 'ETF - Real Estate',
                'industry': 'REIT Fund',
                'beta': 1.2,
                'week52High': 105.0,
                'week52Low': 80.0,
                'dayChange': 1.2,
                'dayChangePct': 1.28,
                'dividendYield': 3.5,
                'ytdReturn': 6.8
            },
            'IWM': {
                'currentPrice': 220.0,
                'sector': 'ETF - Small Cap',
                'industry': 'Index Fund',
                'beta': 1.3,
                'week52High': 240.0,
                'week52Low': 180.0,
                'dayChange': 2.8,
                'dayChangePct': 1.29,
                'dividendYield': 1.1,
                'ytdReturn': 9.2
            },
            'EFA': {
                'currentPrice': 75.0,
                'sector': 'ETF - International Developed',
                'industry': 'Index Fund',
                'beta': 0.9,
                'week52High': 82.0,
                'week52Low': 65.0,
                'dayChange': 0.9,
                'dayChangePct': 1.22,
                'dividendYield': 2.9,
                'ytdReturn': 7.8
            },
            'EEM': {
                'currentPrice': 42.0,
                'sector': 'ETF - Emerging Markets',
                'industry': 'Index Fund',
                'beta': 1.1,
                'week52High': 48.0,
                'week52Low': 36.0,
                'dayChange': 0.6,
                'dayChangePct': 1.45,
                'dividendYield': 2.4,
                'ytdReturn': 5.2
            },
            'GLD': {
                'currentPrice': 185.0,
                'sector': 'ETF - Commodities',
                'industry': 'Gold Fund',
                'beta': 0.2,
                'week52High': 210.0,
                'week52Low': 170.0,
                'dayChange': -0.8,
                'dayChangePct': -0.43,
                'dividendYield': 0.0,
                'ytdReturn': -2.1
            },
            'TLT': {
                'currentPrice': 92.0,
                'sector': 'ETF - Long Term Bonds',
                'industry': 'Bond Fund',
                'beta': -0.3,
                'week52High': 105.0,
                'week52Low': 85.0,
                'dayChange': 0.3,
                'dayChangePct': 0.33,
                'dividendYield': 4.2,
                'ytdReturn': -8.5
            },
            'XLF': {
                'currentPrice': 38.0,
                'sector': 'ETF - Financial',
                'industry': 'Sector Fund',
                'beta': 1.2,
                'week52High': 42.0,
                'week52Low': 32.0,
                'dayChange': 0.5,
                'dayChangePct': 1.33,
                'dividendYield': 1.8,
                'ytdReturn': 14.2
            },
            'XLK': {
                'currentPrice': 175.0,
                'sector': 'ETF - Technology',
                'industry': 'Sector Fund',
                'beta': 1.1,
                'week52High': 190.0,
                'week52Low': 140.0,
                'dayChange': 2.1,
                'dayChangePct': 1.22,
                'dividendYield': 0.7,
                'ytdReturn': 22.8
            }
        }
        
        # Indian ETF/Mutual Fund Fallbacks
        indian_fund_fallbacks = {
            'NIFTYBEES': {
                'currentPrice': 250.0,
                'sector': 'ETF - Indian Large Cap',
                'industry': 'Index Fund',
                'beta': 1.0,
                'week52High': 280.0,
                'week52Low': 220.0,
                'dayChange': 3.5,
                'dayChangePct': 1.42,
                'dividendYield': 1.2,
                'ytdReturn': 15.8
            },
            'NIFTYBEES.NS': {
                'currentPrice': 250.0,
                'sector': 'ETF - Indian Large Cap',
                'industry': 'Index Fund',
                'beta': 1.0,
                'week52High': 280.0,
                'week52Low': 220.0,
                'dayChange': 3.5,
                'dayChangePct': 1.42,
                'dividendYield': 1.2,
                'ytdReturn': 15.8
            },
            'JUNIORBEES': {
                'currentPrice': 450.0,
                'sector': 'ETF - Indian Small Cap',
                'industry': 'Index Fund',
                'beta': 1.4,
                'week52High': 520.0,
                'week52Low': 380.0,
                'dayChange': 8.2,
                'dayChangePct': 1.85,
                'dividendYield': 0.8,
                'ytdReturn': 18.5
            },
            'JUNIORBEES.NS': {
                'currentPrice': 450.0,
                'sector': 'ETF - Indian Small Cap',
                'industry': 'Index Fund',
                'beta': 1.4,
                'week52High': 520.0,
                'week52Low': 380.0,
                'dayChange': 8.2,
                'dayChangePct': 1.85,
                'dividendYield': 0.8,
                'ytdReturn': 18.5
            },
            'BANKBEES': {
                'currentPrice': 520.0,
                'sector': 'ETF - Indian Banking',
                'industry': 'Sector Fund',
                'beta': 1.3,
                'week52High': 580.0,
                'week52Low': 450.0,
                'dayChange': 7.8,
                'dayChangePct': 1.52,
                'dividendYield': 1.5,
                'ytdReturn': 12.4
            },
            'BANKBEES.NS': {
                'currentPrice': 520.0,
                'sector': 'ETF - Indian Banking',
                'industry': 'Sector Fund',
                'beta': 1.3,
                'week52High': 580.0,
                'week52Low': 450.0,
                'dayChange': 7.8,
                'dayChangePct': 1.52,
                'dividendYield': 1.5,
                'ytdReturn': 12.4
            },
            'MOSL500.NS': {
                'currentPrice': 45.0,
                'sector': 'ETF - Indian Large Cap',
                'industry': 'Index Fund',
                'beta': 1.0,
                'week52High': 52.0,
                'week52Low': 38.0,
                'dayChange': 0.6,
                'dayChangePct': 1.35,
                'dividendYield': 1.1,
                'ytdReturn': 14.2
            },
            'CPSEETF.NS': {
                'currentPrice': 94.0,
                'sector': 'ETF - Indian Bonds',
                'industry': 'Bond Fund',
                'beta': 0.1,
                'week52High': 98.0,
                'week52Low': 90.0,
                'dayChange': 0.1,
                'dayChangePct': 0.11,
                'dividendYield': 6.8,
                'ytdReturn': 4.2
            },
            'LIQUIDBEES.NS': {
                'currentPrice': 1000.0,
                'sector': 'ETF - Liquid Fund',
                'industry': 'Money Market',
                'beta': 0.01,
                'week52High': 1002.0,
                'week52Low': 998.0,
                'dayChange': 0.2,
                'dayChangePct': 0.02,
                'dividendYield': 6.5,
                'ytdReturn': 6.8
            },
            'GOLDBEES.NS': {
                'currentPrice': 55.0,
                'sector': 'ETF - Gold',
                'industry': 'Commodity Fund',
                'beta': 0.2,
                'week52High': 62.0,
                'week52Low': 48.0,
                'dayChange': -0.3,
                'dayChangePct': -0.54,
                'dividendYield': 0.0,
                'ytdReturn': -1.8
            }
        }
        
        # Stock Fallbacks for common symbols
        stock_fallbacks = {
            'AAPL': {
                'currentPrice': 175.0,
                'sector': 'Technology',
                'industry': 'Consumer Electronics',
                'beta': 1.2,
                'week52High': 195.0,
                'week52Low': 140.0,
                'dayChange': 2.1,
                'dayChangePct': 1.22,
                'dividendYield': 0.5,
                'ytdReturn': 18.5
            },
            'MSFT': {
                'currentPrice': 380.0,
                'sector': 'Technology',
                'industry': 'Software',
                'beta': 0.9,
                'week52High': 420.0,
                'week52Low': 310.0,
                'dayChange': 4.2,
                'dayChangePct': 1.12,
                'dividendYield': 0.7,
                'ytdReturn': 16.8
            },
            'GOOGL': {
                'currentPrice': 140.0,
                'sector': 'Technology',
                'industry': 'Internet Services',
                'beta': 1.1,
                'week52High': 155.0,
                'week52Low': 115.0,
                'dayChange': 1.8,
                'dayChangePct': 1.31,
                'dividendYield': 0.0,
                'ytdReturn': 12.2
            },
            'TSLA': {
                'currentPrice': 220.0,
                'sector': 'Consumer Cyclical',
                'industry': 'Auto Manufacturers',
                'beta': 2.0,
                'week52High': 280.0,
                'week52Low': 140.0,
                'dayChange': 8.5,
                'dayChangePct': 4.01,
                'dividendYield': 0.0,
                'ytdReturn': 28.5
            },
            'NVDA': {
                'currentPrice': 450.0,
                'sector': 'Technology',
                'industry': 'Semiconductors',
                'beta': 1.8,
                'week52High': 500.0,
                'week52Low': 200.0,
                'dayChange': 12.5,
                'dayChangePct': 2.85,
                'dividendYield': 0.1,
                'ytdReturn': 85.2
            },
            'AMZN': {
                'currentPrice': 145.0,
                'sector': 'Consumer Cyclical',
                'industry': 'Internet Retail',
                'beta': 1.3,
                'week52High': 170.0,
                'week52Low': 120.0,
                'dayChange': 2.8,
                'dayChangePct': 1.97,
                'dividendYield': 0.0,
                'ytdReturn': 14.8
            }
        }
        
        # Indian Stock Fallbacks
        indian_stock_fallbacks = {
            'RELIANCE': {
                'currentPrice': 2850.0,
                'sector': 'Energy',
                'industry': 'Oil & Gas Integrated',
                'beta': 0.8,
                'week52High': 3100.0,
                'week52Low': 2400.0,
                'dayChange': 25.5,
                'dayChangePct': 0.90,
                'dividendYield': 0.4,
                'ytdReturn': 8.5
            },
            'TCS': {
                'currentPrice': 3950.0,
                'sector': 'Technology',
                'industry': 'IT Services',
                'beta': 0.7,
                'week52High': 4200.0,
                'week52Low': 3200.0,
                'dayChange': 42.0,
                'dayChangePct': 1.08,
                'dividendYield': 1.2,
                'ytdReturn': 12.8
            },
            'INFY': {
                'currentPrice': 1750.0,
                'sector': 'Technology',
                'industry': 'IT Services',
                'beta': 0.8,
                'week52High': 1900.0,
                'week52Low': 1400.0,
                'dayChange': 18.5,
                'dayChangePct': 1.07,
                'dividendYield': 2.1,
                'ytdReturn': 15.2
            },
            'HDFCBANK': {
                'currentPrice': 1680.0,
                'sector': 'Financial Services',
                'industry': 'Banks',
                'beta': 1.1,
                'week52High': 1800.0,
                'week52Low': 1450.0,
                'dayChange': 22.5,
                'dayChangePct': 1.36,
                'dividendYield': 1.0,
                'ytdReturn': 9.8
            }
        }
        
        # Bond/Treasury Fallbacks
        bond_fallbacks = {
            'US_TREASURY_10Y': {
                'currentPrice': 95.5,
                'sector': 'Government Bonds',
                'industry': 'Treasury Securities',
                'beta': -0.2,
                'week52High': 98.0,
                'week52Low': 92.0,
                'dayChange': 0.1,
                'dayChangePct': 0.10,
                'dividendYield': 4.2,
                'ytdReturn': -2.1
            },
            'US_TREASURY_2Y': {
                'currentPrice': 98.2,
                'sector': 'Government Bonds',
                'industry': 'Treasury Securities',
                'beta': -0.1,
                'week52High': 99.5,
                'week52Low': 96.8,
                'dayChange': 0.05,
                'dayChangePct': 0.05,
                'dividendYield': 4.8,
                'ytdReturn': -0.8
            },
            'US_TREASURY_30Y': {
                'currentPrice': 88.5,
                'sector': 'Government Bonds',
                'industry': 'Treasury Securities',
                'beta': -0.4,
                'week52High': 95.0,
                'week52Low': 82.0,
                'dayChange': 0.2,
                'dayChangePct': 0.23,
                'dividendYield': 4.5,
                'ytdReturn': -8.2
            },
            'CORPORATE_AAA': {
                'currentPrice': 92.0,
                'sector': 'Corporate Bonds',
                'industry': 'Investment Grade',
                'beta': 0.1,
                'week52High': 96.0,
                'week52Low': 88.0,
                'dayChange': 0.15,
                'dayChangePct': 0.16,
                'dividendYield': 5.2,
                'ytdReturn': -1.5
            },
            'CORPORATE_BBB': {
                'currentPrice': 89.5,
                'sector': 'Corporate Bonds',
                'industry': 'Investment Grade',
                'beta': 0.2,
                'week52High': 94.0,
                'week52Low': 85.0,
                'dayChange': 0.2,
                'dayChangePct': 0.22,
                'dividendYield': 6.1,
                'ytdReturn': -2.8
            },
            'HIGH_YIELD_CORP': {
                'currentPrice': 85.0,
                'sector': 'Corporate Bonds',
                'industry': 'High Yield',
                'beta': 0.4,
                'week52High': 92.0,
                'week52Low': 78.0,
                'dayChange': 0.3,
                'dayChangePct': 0.35,
                'dividendYield': 8.5,
                'ytdReturn': -5.2
            }
        }
        
        # Debt Fund Fallbacks
        debt_fund_keywords = [
            'GILT', 'DEBT', 'BOND', 'LIQUID', 
            'IDFC', 'ICICI', 'HDFC', 'SBI', 'AXIS',
            'CORP', 'BANKING', 'PSU', 'SHORT', 'ULTRA',
            'TREASURY', 'AAA', 'BBB', 'YIELD'
        ]
        
        # Check fallback databases in order of preference
        fallback_sources = [
            (etf_fallbacks, "ETF"),
            (bond_fallbacks, "Bond/Treasury"),
            (indian_fund_fallbacks, "Indian Fund"),
            (stock_fallbacks, "US Stock"),
            (indian_stock_fallbacks, "Indian Stock")
        ]
        
        # Try exact symbol match first
        for fallback_db, source_type in fallback_sources:
            if symbol_upper in fallback_db:
                base_data = fallback_db[symbol_upper].copy()
                print(f"💡 Using {source_type} fallback for {symbol}")
                return self._build_fallback_response(base_data)
        
        # Check for debt fund patterns
        is_debt_fund = any(keyword in symbol_upper for keyword in debt_fund_keywords)
        if is_debt_fund:
            print(f"💡 {symbol} appears to be debt fund - using generic debt fallback")
            base_data = {
                'currentPrice': 25.0,
                'sector': 'Debt Fund',
                'industry': 'Mutual Fund',
                'beta': 0.05,
                'week52High': 26.0,
                'week52Low': 24.5,
                'dayChange': 0.02,
                'dayChangePct': 0.08,
                'dividendYield': 6.5,
                'ytdReturn': 5.2
            }
            return self._build_fallback_response(base_data)
        
        # Generic fallback based on symbol characteristics
        if any(etf_keyword in symbol_upper for etf_keyword in ['ETF', 'FUND', 'INDEX', 'SPDR', 'ISHARES', 'VANGUARD']):
            print(f"💡 {symbol} appears to be ETF - using generic ETF fallback")
            base_data = {
                'currentPrice': 100.0,
                'sector': 'ETF - Mixed',
                'industry': 'Index Fund',
                'beta': 1.0,
                'week52High': 115.0,
                'week52Low': 85.0,
                'dayChange': 0.8,
                'dayChangePct': 0.81,
                'dividendYield': 1.5,
                'ytdReturn': 8.5
            }
            return self._build_fallback_response(base_data)
        
        # No specific fallback found
        return None
    
    def _build_fallback_response(self, base_data: Dict) -> Dict:
        """Build standardized fallback response with all required fields"""
        return {
            'currentPrice': base_data['currentPrice'],
            'marketCap': base_data.get('marketCap'),
            'sector': base_data['sector'],
            'industry': base_data['industry'],
            'beta': base_data.get('beta'),
            'week52High': base_data.get('week52High'),
            'week52Low': base_data.get('week52Low'),
            'dayChange': base_data.get('dayChange'),
            'dayChangePct': base_data.get('dayChangePct'),
            'volume': base_data.get('volume'),
            'peRatio': base_data.get('peRatio'),
            'dividendYield': base_data.get('dividendYield'),
            'ytdReturn': base_data.get('ytdReturn'),
            '_fallback': True  # Flag to indicate this is fallback data
        }
    
    def fetch_from_alpha_vantage(self, symbol: str) -> Optional[Dict]:
        """Fetch from Alpha Vantage API"""
        if not self.apis['alpha_vantage']['enabled']:
            return None
        
        try:
            self._respect_rate_limit('alpha_vantage')
            
            api_key = self.apis['alpha_vantage']['key']
            quote_url = f"{self.apis['alpha_vantage']['base_url']}?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}"
            response = requests.get(quote_url, timeout=10)
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            
            if 'Global Quote' not in data or not data['Global Quote']:
                return None
            
            quote = data['Global Quote']
            
            overview_url = f"{self.apis['alpha_vantage']['base_url']}?function=OVERVIEW&symbol={symbol}&apikey={api_key}"
            self._respect_rate_limit('alpha_vantage')
            overview_response = requests.get(overview_url, timeout=10)
            overview = overview_response.json() if overview_response.status_code == 200 else {}
            
            market_data = {
                'currentPrice': float(quote.get('05. price', 0)),
                'marketCap': int(overview.get('MarketCapitalization', 0)) if overview.get('MarketCapitalization') else None,
                'sector': overview.get('Sector', 'N/A'),
                'industry': overview.get('Industry', 'N/A'),
                'beta': float(overview.get('Beta', 0)) if overview.get('Beta') else None,
                'week52High': float(overview.get('52WeekHigh', 0)) if overview.get('52WeekHigh') else None,
                'week52Low': float(overview.get('52WeekLow', 0)) if overview.get('52WeekLow') else None,
                'dayChange': float(quote.get('09. change', 0)),
                'dayChangePct': float(quote.get('10. change percent', '0').replace('%', '')),
                'volume': int(quote.get('06. volume', 0)),
                'peRatio': float(overview.get('PERatio', 0)) if overview.get('PERatio') else None,
                'dividendYield': float(overview.get('DividendYield', 0)) * 100 if overview.get('DividendYield') else None,
                'ytdReturn': None
            }
            
            print(f"✅ Alpha Vantage: {symbol} @ ₹{market_data['currentPrice']:.2f}")
            return market_data
            
        except Exception as e:
            print(f"⚠️  Alpha Vantage failed for {symbol}: {e}")
            return None
    
    def fetch_from_finnhub(self, symbol: str) -> Optional[Dict]:
        """Fetch from Finnhub API"""
        if not self.apis['finnhub']['enabled']:
            return None
        
        try:
            self._respect_rate_limit('finnhub')
            
            api_key = self.apis['finnhub']['key']
            base_url = self.apis['finnhub']['base_url']
            
            quote_url = f"{base_url}/quote?symbol={symbol}&token={api_key}"
            response = requests.get(quote_url, timeout=10)
            
            if response.status_code != 200:
                return None
            
            quote = response.json()
            
            profile_url = f"{base_url}/stock/profile2?symbol={symbol}&token={api_key}"
            self._respect_rate_limit('finnhub')
            profile_response = requests.get(profile_url, timeout=10)
            profile = profile_response.json() if profile_response.status_code == 200 else {}
            
            market_data = {
                'currentPrice': float(quote.get('c', 0)),
                'marketCap': profile.get('marketCapitalization', None),
                'sector': profile.get('finnhubIndustry', 'N/A'),
                'industry': profile.get('finnhubIndustry', 'N/A'),
                'beta': None,
                'week52High': float(quote.get('h', 0)) if quote.get('h') else None,
                'week52Low': float(quote.get('l', 0)) if quote.get('l') else None,
                'dayChange': float(quote.get('d', 0)),
                'dayChangePct': float(quote.get('dp', 0)),
                'volume': None,
                'peRatio': None,
                'dividendYield': None,
                'ytdReturn': None
            }
            
            print(f"✅ Finnhub: {symbol} @ ₹{market_data['currentPrice']:.2f}")
            return market_data
            
        except Exception as e:
            print(f"⚠️  Finnhub failed for {symbol}: {e}")
            return None
    
    def fetch_from_yahoo(self, symbol: str) -> Optional[Dict]:
        """Fetch from Yahoo Finance - Enhanced for Indian market"""
        try:
            self._respect_rate_limit('yahoo')
            
            # Auto-add .NS suffix for Indian stocks if not present
            yahoo_symbol = symbol
            if not ('.' in symbol or '_' in symbol):
                # List of common Indian stocks
                indian_stocks = [
                    'RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK', 
                    'SBIN', 'BHARTIARTL', 'ITC', 'KOTAKBANK', 'LT', 
                    'AXISBANK', 'HINDUNILVR', 'BAJFINANCE', 'ASIANPAINT',
                    'MARUTI', 'TITAN', 'WIPRO', 'ULTRACEMCO', 'SUNPHARMA',
                    'NESTLEIND', 'HCLTECH', 'TECHM', 'TATAMOTORS', 'ADANIPORTS',
                    'POWERGRID', 'ONGC', 'NTPC', 'COALINDIA', 'DRREDDY', 'CIPLA'
                ]
                
                if symbol.upper() in indian_stocks:
                    yahoo_symbol = f"{symbol}.NS"
                    print(f"   🇮🇳 Auto-adding NSE suffix: {symbol} → {yahoo_symbol}")
            
            ticker = yf.Ticker(yahoo_symbol)
            info = ticker.info
            hist = ticker.history(period="ytd")
            
            ytd_return = None
            if not hist.empty and len(hist) > 0:
                first_price = hist['Close'].iloc[0]
                last_price = hist['Close'].iloc[-1]
                ytd_return = ((last_price - first_price) / first_price) * 100
            
            market_data = {
                'currentPrice': info.get('currentPrice') or info.get('regularMarketPrice') or info.get('previousClose'),
                'marketCap': info.get('marketCap'),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'beta': info.get('beta'),
                'week52High': info.get('fiftyTwoWeekHigh'),
                'week52Low': info.get('fiftyTwoWeekLow'),
                'dayChange': info.get('regularMarketChange'),
                'dayChangePct': info.get('regularMarketChangePercent'),
                'volume': info.get('volume'),
                'peRatio': info.get('trailingPE') or info.get('forwardPE'),
                'dividendYield': info.get('dividendYield') * 100 if info.get('dividendYield') else None,
                'ytdReturn': ytd_return
            }
            
            if market_data['currentPrice'] is None:
                return None
            
            print(f"✅ Yahoo Finance: {yahoo_symbol} @ ₹{market_data['currentPrice']:.2f}")
            return market_data
            
        except Exception as e:
            print(f"⚠️  Yahoo Finance failed for {symbol}: {e}")
            return None
    
    def fetch_from_nse_india(self, symbol: str) -> Optional[Dict]:
        """Fetch from NSE India API (Free)"""
        if not self.apis['nse_india']['enabled']:
            return None
        
        try:
            self._respect_rate_limit('nse_india')
            
            # NSE API requires specific headers to avoid blocking
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            # Try NSE quote API
            base_url = self.apis['nse_india']['base_url']
            quote_url = f"{base_url}/quote-equity?symbol={symbol}"
            
            response = requests.get(quote_url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            
            if 'priceInfo' not in data:
                return None
            
            price_info = data['priceInfo']
            info = data.get('info', {})
            
            market_data = {
                'currentPrice': float(price_info.get('lastPrice', 0)),
                'marketCap': None,  # NSE doesn't provide market cap in this API
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'beta': None,
                'week52High': float(price_info.get('weekHighLow', {}).get('max', 0)) if price_info.get('weekHighLow') else None,
                'week52Low': float(price_info.get('weekHighLow', {}).get('min', 0)) if price_info.get('weekHighLow') else None,
                'dayChange': float(price_info.get('change', 0)),
                'dayChangePct': float(price_info.get('pChange', 0)),
                'volume': int(price_info.get('totalTradedVolume', 0)),
                'peRatio': None,
                'dividendYield': None,
                'ytdReturn': None
            }
            
            print(f"✅ NSE India: {symbol} @ ₹{market_data['currentPrice']:.2f}")
            return market_data
            
        except Exception as e:
            print(f"⚠️  NSE India failed for {symbol}: {e}")
            return None
    
    def fetch_from_bse_india(self, symbol: str) -> Optional[Dict]:
        """Fetch from BSE India API (Free)"""
        if not self.apis['bse_india']['enabled']:
            return None
        
        try:
            self._respect_rate_limit('bse_india')
            
            # BSE API requires specific headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://www.bseindia.com/',
                'Connection': 'keep-alive'
            }
            
            # BSE uses scrip codes, try to get quote by symbol first
            base_url = self.apis['bse_india']['base_url']
            
            # Try BSE search API to get scrip code
            search_url = f"{base_url}/Sensex/getSecurityInfo"
            search_params = {
                'SecurityId': symbol,
                'Debtflag': 'N'
            }
            
            response = requests.get(search_url, headers=headers, params=search_params, timeout=10)
            
            if response.status_code != 200:
                return None
            
            search_data = response.json()
            
            if not search_data or 'Table' not in search_data or not search_data['Table']:
                return None
            
            # Get scrip code from search results
            scrip_code = search_data['Table'][0].get('Scrip_cd')
            if not scrip_code:
                return None
            
            # Now get the actual quote using scrip code
            quote_url = f"{base_url}/StockReachGraph/w"
            quote_params = {
                'scripcode': scrip_code,
                'flag': '0'
            }
            
            quote_response = requests.get(quote_url, headers=headers, params=quote_params, timeout=10)
            
            if quote_response.status_code != 200:
                return None
            
            quote_data = quote_response.json()
            
            if not quote_data or 'Data' not in quote_data or not quote_data['Data']:
                return None
            
            # Extract price data
            latest_data = quote_data['Data'][-1] if quote_data['Data'] else {}
            
            current_price = float(latest_data.get('CurrRate', 0))
            prev_close = float(latest_data.get('PrevRate', current_price))
            
            day_change = current_price - prev_close
            day_change_pct = (day_change / prev_close * 100) if prev_close > 0 else 0
            
            market_data = {
                'currentPrice': current_price,
                'marketCap': None,  # BSE API doesn't provide market cap directly
                'sector': search_data['Table'][0].get('Industry', 'N/A'),
                'industry': search_data['Table'][0].get('Industry', 'N/A'),
                'beta': None,
                'week52High': float(search_data['Table'][0].get('High52', 0)) if search_data['Table'][0].get('High52') else None,
                'week52Low': float(search_data['Table'][0].get('Low52', 0)) if search_data['Table'][0].get('Low52') else None,
                'dayChange': day_change,
                'dayChangePct': day_change_pct,
                'volume': int(latest_data.get('Volume', 0)),
                'peRatio': None,
                'dividendYield': None,
                'ytdReturn': None
            }
            
            print(f"✅ BSE India: {symbol} @ ₹{market_data['currentPrice']:.2f}")
            return market_data
            
        except Exception as e:
            print(f"⚠️  BSE India failed for {symbol}: {e}")
            return None
    
    def fetch_from_groww(self, symbol: str) -> Optional[Dict]:
        """Fetch from Groww API (Unofficial but Free)"""
        if not self.apis['groww']['enabled']:
            return None
        
        try:
            self._respect_rate_limit('groww')
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json'
            }
            
            # Groww search API to get stock info
            base_url = self.apis['groww']['base_url']
            search_url = f"{base_url}/stocks_data/v1/accord_points/exchange/NSE/segment/CASH/{symbol}"
            
            response = requests.get(search_url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            
            if not data or 'ltp' not in data:
                return None
            
            market_data = {
                'currentPrice': float(data.get('ltp', 0)),
                'marketCap': None,
                'sector': data.get('sector', 'N/A'),
                'industry': data.get('industry', 'N/A'),
                'beta': None,
                'week52High': float(data.get('high_52w', 0)) if data.get('high_52w') else None,
                'week52Low': float(data.get('low_52w', 0)) if data.get('low_52w') else None,
                'dayChange': float(data.get('day_change', 0)),
                'dayChangePct': float(data.get('day_change_perc', 0)),
                'volume': int(data.get('volume', 0)),
                'peRatio': float(data.get('pe', 0)) if data.get('pe') else None,
                'dividendYield': None,
                'ytdReturn': None
            }
            
            print(f"✅ Groww: {symbol} @ ₹{market_data['currentPrice']:.2f}")
            return market_data
            
        except Exception as e:
            print(f"⚠️  Groww failed for {symbol}: {e}")
            return None
    
    def fetch_market_data(self, symbol: str, retry_count=0) -> Optional[Dict]:
        """
        Hybrid fetch with intelligent fallback
        Enhanced for Indian market with debt fund support
        """
        # Check cache first
        cached_data = self._check_cache(symbol)
        if cached_data:
            return cached_data
        
        # Try APIs in order of preference
        api_methods = []
        
        # Check if this might be an Indian stock
        indian_stocks = [
            'RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK', 
            'SBIN', 'BHARTIARTL', 'ITC', 'KOTAKBANK', 'LT', 
            'AXISBANK', 'HINDUNILVR', 'BAJFINANCE', 'ASIANPAINT',
            'MARUTI', 'TITAN', 'WIPRO', 'ULTRACEMCO', 'SUNPHARMA'
        ]
        
        is_likely_indian = symbol.upper() in indian_stocks or '.NS' in symbol.upper() or '.BO' in symbol.upper()
        
        if is_likely_indian:
            # For Indian stocks, try Indian APIs first
            if self.apis['nse_india']['enabled']:
                api_methods.append(('NSE India', self.fetch_from_nse_india))
            
            if self.apis['bse_india']['enabled']:
                api_methods.append(('BSE India', self.fetch_from_bse_india))
            
            if self.apis['groww']['enabled']:
                api_methods.append(('Groww', self.fetch_from_groww))
        
        # Add US APIs
        if self.apis['alpha_vantage']['enabled']:
            api_methods.append(('Alpha Vantage', self.fetch_from_alpha_vantage))
        
        if self.apis['finnhub']['enabled']:
            api_methods.append(('Finnhub', self.fetch_from_finnhub))
        
        # Yahoo Finance works for both markets
        api_methods.append(('Yahoo Finance', self.fetch_from_yahoo))
        
        # Try each API
        for api_name, fetch_method in api_methods:
            print(f"🔄 Trying {api_name} for {symbol}...")
            data = fetch_method(symbol)
            
            if data and data.get('currentPrice'):
                self._update_cache(symbol, data)
                return data
        
        # ⚠️ All APIs failed - use comprehensive fallback system
        print(f"⚠️  All APIs failed for {symbol} - using fallback data")
        
        fallback_data = self._get_fallback_data(symbol)
        if fallback_data:
            # Cache the fallback data
            self._update_cache(symbol, fallback_data)
            print(f"✅ Using fallback data: {symbol} @ ${fallback_data['currentPrice']:.2f}")
            return fallback_data
        
        # No fallback available
        print(f"❌ Cannot fetch data for {symbol} - no fallback available")
        return None
    
    def get_portfolio(self, user_email: str) -> Optional[Dict]:
        """Fetch user portfolio from DynamoDB"""
        try:
            response = self.portfolios_table.get_item(Key={'userId': user_email})
            if 'Item' in response:
                return response['Item']
            return None
        except Exception as e:
            print(f"❌ Error fetching portfolio: {e}")
            return None
    
    def extract_symbols(self, portfolio: Dict) -> List[Dict[str, Any]]:
        """Extract all stock, ETF, and BOND symbols with their quantities"""
        symbols = []
        
        # Extract BONDS - CRITICAL: This was missing!
        for bond in portfolio.get('bonds', []):
            if isinstance(bond, dict) and bond.get('symbol') and bond.get('quantity'):
                symbols.append({
                    'symbol': bond['symbol'],
                    'quantity': float(bond['quantity']),
                    'type': 'bond',
                    'avgPrice': float(bond.get('avgPrice', 0)),
                })
                print(f"   Added BOND: {bond['symbol']} (qty: {bond['quantity']})")
        
        # Extract STOCKS
        for stock in portfolio.get('stocks', []):
            if isinstance(stock, dict) and stock.get('symbol') and stock.get('quantity'):
                symbols.append({
                    'symbol': stock['symbol'],
                    'quantity': float(stock['quantity']),
                    'avgPrice': float(stock.get('avgPrice', 0)),
                    'type': 'stock'
                })
                print(f"   Added STOCK: {stock['symbol']} (qty: {stock['quantity']})")
        
        # Extract ETFs
        for etf in portfolio.get('etfs', []):
            if isinstance(etf, dict) and etf.get('symbol') and etf.get('quantity'):
                symbols.append({
                    'symbol': etf['symbol'],
                    'quantity': float(etf['quantity']),
                    'avgPrice': float(etf.get('avgPrice', 0)),
                    'type': 'etf'
                })
                print(f"   Added ETF: {etf['symbol']} (qty: {etf['quantity']})")
        
        print(f"📊 Found {len(symbols)} total holdings:")
        print(f"   - Bonds: {len([s for s in symbols if s['type'] == 'bond'])}")
        print(f"   - Stocks: {len([s for s in symbols if s['type'] == 'stock'])}")
        print(f"   - ETFs: {len([s for s in symbols if s['type'] == 'etf'])}")
        
        return symbols
    
    def fetch_batch_market_data(self, symbols: List[Dict[str, Any]]) -> Dict[str, Dict]:
        """Fetch market data for multiple symbols using hybrid approach"""
        print(f"🔄 Fetching market data for {len(symbols)} symbols (Hybrid Mode)")
        print()
        
        market_data_map = {}
        
        for i, holding in enumerate(symbols, 1):
            symbol = holding['symbol']
            print(f"[{i}/{len(symbols)}] Fetching {symbol}...")
            
            market_data = self.fetch_market_data(symbol)
            if market_data:
                market_data_map[symbol] = market_data
            else:
                print(f"⚠️  Skipping {symbol} - could not fetch from any API")
            
            print()
        
        success_rate = len(market_data_map) / len(symbols) * 100 if len(symbols) > 0 else 0
        print(f"📊 Successfully fetched {len(market_data_map)}/{len(symbols)} symbols ({success_rate:.0f}%)")
        print()
        
        return market_data_map
    
    def enrich_holding(self, holding: Dict, market_data: Dict) -> Dict:
        """Enrich a single holding with market data"""
        quantity = holding['quantity']
        current_price = market_data['currentPrice']
        current_value = quantity * current_price
        avg_price = holding.get('avgPrice', current_price)
        
        enriched = {
            'symbol': holding['symbol'],
            'type': holding['type'],
            'quantity': quantity,
            'avgPrice': round(avg_price, 2),
            'currentValue': round(current_value, 2),
            'currentPrice': round(current_price, 2),
            'marketCap': market_data['marketCap'],
            'sector': market_data['sector'],
            'industry': market_data['industry'],
            'beta': round(market_data['beta'], 2) if market_data['beta'] else None,
            'week52High': round(market_data['week52High'], 2) if market_data['week52High'] else None,
            'week52Low': round(market_data['week52Low'], 2) if market_data['week52Low'] else None,
            'dayChange': round(market_data['dayChange'], 2) if market_data['dayChange'] else None,
            'dayChangePct': round(market_data['dayChangePct'], 2) if market_data['dayChangePct'] else None,
            'volume': market_data['volume'],
            'peRatio': round(market_data['peRatio'], 2) if market_data['peRatio'] else None,
            'dividendYield': round(market_data['dividendYield'], 2) if market_data['dividendYield'] else None,
            'ytdReturn': round(market_data['ytdReturn'], 2) if market_data['ytdReturn'] else None,
            'dataSource': 'fallback' if market_data.get('_fallback') else 'live'
        }
        
        # Add warning for fallback data
        if market_data.get('_fallback'):
            enriched['warning'] = 'Using estimated data - live market data unavailable'
        
        return enriched
    
    def calculate_portfolio_metrics(self, enriched_holdings: List[Dict]) -> Dict:
        """Calculate portfolio-level aggregate metrics"""
        total_value = sum(h['currentValue'] for h in enriched_holdings)
        
        for holding in enriched_holdings:
            holding['portfolioWeight'] = round((holding['currentValue'] / total_value) * 100, 2) if total_value > 0 else 0
        
        sector_allocation = {}
        for holding in enriched_holdings:
            sector = holding['sector']
            if sector not in sector_allocation:
                sector_allocation[sector] = 0
            sector_allocation[sector] += holding['currentValue']
        
        sector_breakdown = {
            sector: round((value / total_value) * 100, 2)
            for sector, value in sector_allocation.items()
        } if total_value > 0 else {}
        
        portfolio_beta = 0
        beta_weight_sum = 0
        for holding in enriched_holdings:
            if holding['beta'] is not None:
                weight = holding['currentValue'] / total_value if total_value > 0 else 0
                portfolio_beta += holding['beta'] * weight
                beta_weight_sum += weight
        
        portfolio_beta = round(portfolio_beta, 2) if beta_weight_sum > 0 else None
        
        top_holdings = sorted(enriched_holdings, key=lambda x: x['currentValue'], reverse=True)[:5]
        top_5 = [
            {
                'symbol': h['symbol'],
                'value': h['currentValue'],
                'weight': h['portfolioWeight']
            }
            for h in top_holdings
        ]
        
        day_total_change = sum(
            h['dayChange'] * h['quantity'] 
            for h in enriched_holdings 
            if h['dayChange'] is not None
        )
        day_total_change_pct = (day_total_change / total_value) * 100 if total_value > 0 else 0
        
        return {
            'totalValue': round(total_value, 2),
            'portfolioBeta': portfolio_beta,
            'sectorBreakdown': sector_breakdown,
            'topHoldings': top_5,
            'dayTotalChange': round(day_total_change, 2),
            'dayTotalChangePct': round(day_total_change_pct, 2)
        }
    
    def generate_report(self, user_email: str) -> Dict:
        """Generate complete market report using hybrid API approach"""
        print("=" * 60)
        print(f"📊 [Strand Market Agent] Starting report generation")
        print(f"👤 User: {user_email}")
        print("=" * 60)
        
        try:
            portfolio = self.get_portfolio(user_email)
            if not portfolio:
                return {
                    'success': False,
                    'error': 'Portfolio not found',
                    'userId': user_email
                }
            
            holdings = self.extract_symbols(portfolio)
            if not holdings:
                return {
                    'success': False,
                    'error': 'No holdings found in portfolio',
                    'userId': user_email
                }
            
            market_data_map = self.fetch_batch_market_data(holdings)
            
            if not market_data_map:
                return {
                    'success': False,
                    'error': 'Could not fetch market data from any API',
                    'userId': user_email
                }
            
            enriched_holdings = []
            fallback_count = 0
            live_count = 0
            
            for holding in holdings:
                symbol = holding['symbol']
                if symbol in market_data_map:
                    enriched = self.enrich_holding(holding, market_data_map[symbol])
                    enriched_holdings.append(enriched)
                    
                    # Count data sources
                    if market_data_map[symbol].get('_fallback'):
                        fallback_count += 1
                    else:
                        live_count += 1
            
            if not enriched_holdings:
                return {
                    'success': False,
                    'error': 'Could not enrich any holdings',
                    'userId': user_email
                }
            
            portfolio_metrics = self.calculate_portfolio_metrics(enriched_holdings)
            
            print("=" * 60)
            print(f"✅ [Strand Market Agent] Report Generated Successfully")
            print(f"📈 Total Portfolio Value: ${portfolio_metrics['totalValue']:,.2f}")
            print(f"📊 Holdings Processed: {len(enriched_holdings)}/{len(holdings)}")
            print(f"📡 Live Data: {live_count} | 🔄 Fallback Data: {fallback_count}")
            if fallback_count > 0:
                print(f"⚠️  {fallback_count} holdings using estimated data due to API unavailability")
            print("=" * 60)
            
            return {
                'success': True,
                'timestamp': datetime.utcnow().isoformat(),
                'userId': user_email,
                'holdings': enriched_holdings,
                'portfolioMetrics': portfolio_metrics,
                'cashSavings': float(portfolio.get('cashSavings', 0)),
                'dataQuality': {
                    'totalHoldings': len(enriched_holdings),
                    'liveDataCount': live_count,
                    'fallbackDataCount': fallback_count,
                    'dataReliability': 'high' if fallback_count == 0 else 'medium' if fallback_count < live_count else 'estimated'
                },
                'agent': 'StrandMarketDataAgent',
                'version': '1.0.0-strand'
            }
            
        except Exception as e:
            print(f"❌ [Strand Market Agent] Error generating report: {e}")
            return {
                'success': False,
                'error': str(e),
                'userId': user_email
            }


def create_market_agent():
    print("🏭 [Factory] Creating Strand Market Data Agent...")
    agent = StrandMarketDataAgent(
        delay_between_calls=0.3,
        max_retries=3
    )
    
    print("✅ [Factory] Strand Market Data Agent created successfully")
    return agent


# For backward compatibility and testing
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    print("🧪 Testing Strand Market Data Agent")
    
    agent = create_market_agent()
    
    test_email = "lok@gmail.com"
    report = agent.generate_report(test_email)
    
    if report['success']:
        print("\n🎉 SUCCESS!")
        print(f"\nPortfolio Value: ₹{report['portfolioMetrics']['totalValue']:,.2f}")
        print(f"Agent: {report['agent']} v{report['version']}")
    else:
        print(f"\n❌ ERROR: {report.get('error')}")

import os
import yfinance as yf
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
from decimal import Decimal
import boto3
import time
import random


class HybridMarketDataAgent:
    """
    Multi-API Market Data Agent with intelligent fallback system
    Enhanced for Indian Market
    """
    
    def __init__(self, delay_between_calls=0.3, max_retries=3):
        """Initialize with multiple API configurations"""
        # self.dynamodb = boto3.resource(
        #     'dynamodb',
        #     region_name=os.getenv('AWS_REGION', 'us-east-1'),
        #     aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        #     aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        #     aws_session_token=os.getenv('AWS_SESSION_TOKEN')
        # )

        
        

        self.dynamodb = boto3.resource("dynamodb", region_name=os.getenv("AWS_REGION", "us-east-1"))

        self.portfolios_table = self.dynamodb.Table('WealthWisePortfolios')
        
        # API Configuration
        self.apis = {
            'alpha_vantage': {
                'key': os.getenv('ALPHA_VANTAGE_API_KEY', ''),
                'base_url': 'https://www.alphavantage.co/query',
                'rate_limit': 0.5,
                'last_call': 0,
                'enabled': bool(os.getenv('ALPHA_VANTAGE_API_KEY'))
            },
            'finnhub': {
                'key': os.getenv('FINNHUB_API_KEY', ''),
                'base_url': 'https://finnhub.io/api/v1',
                'rate_limit': 1.0,
                'last_call': 0,
                'enabled': bool(os.getenv('FINNHUB_API_KEY'))
            },
            'polygon': {
                'key': os.getenv('POLYGON_API_KEY', ''),
                'base_url': 'https://api.polygon.io',
                'rate_limit': 12.0,
                'last_call': 0,
                'enabled': bool(os.getenv('POLYGON_API_KEY'))
            },
            'yahoo': {
                'enabled': True,
                'rate_limit': 0.5,
                'last_call': 0
            }
        }
        
        self.delay_between_calls = delay_between_calls
        self.max_retries = max_retries
        self.cache = {}
        self.cache_ttl = 60
        
        active_apis = [name for name, config in self.apis.items() if config['enabled']]
        print(f"📌 Active APIs: {', '.join(active_apis)}")
    
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
        
        if self.apis['alpha_vantage']['enabled']:
            api_methods.append(('Alpha Vantage', self.fetch_from_alpha_vantage))
        
        if self.apis['finnhub']['enabled']:
            api_methods.append(('Finnhub', self.fetch_from_finnhub))
        
        api_methods.append(('Yahoo Finance', self.fetch_from_yahoo))
        
        # Try each API
        for api_name, fetch_method in api_methods:
            print(f"🔄 Trying {api_name} for {symbol}...")
            data = fetch_method(symbol)
            
            if data and data.get('currentPrice'):
                self._update_cache(symbol, data)
                return data
        
        # ⚠️ All APIs failed - try fallback for Indian debt funds
        print(f"⚠️  All APIs failed for {symbol}")
        
        # Check if this is an Indian debt fund (custom identifier)
        indian_debt_keywords = [
            'GILT', 'DEBT', 'BOND', 'LIQUID', 
            'IDFC', 'ICICI', 'HDFC', 'SBI', 'AXIS',
            'CORP', 'BANKING', 'PSU', 'SHORT'
        ]
        
        # Check if symbol contains any debt fund keyword
        is_indian_debt = any(keyword in symbol.upper() for keyword in indian_debt_keywords)
        
        if is_indian_debt:
            print(f"💡 {symbol} appears to be Indian debt fund - using estimated NAV")
            
            # Return estimated NAV for debt fund
            fallback_data = {
                'currentPrice': 25.0,  # Typical debt fund NAV
                'marketCap': None,
                'sector': 'Debt Fund',
                'industry': 'Mutual Fund',
                'beta': 0.05,  # Very low beta for debt
                'week52High': 26.0,
                'week52Low': 24.5,
                'dayChange': 0.02,
                'dayChangePct': 0.08,
                'volume': None,
                'peRatio': None,
                'dividendYield': 6.5,  # Typical debt fund return
                'ytdReturn': 5.2
            }
            
            # Cache the fallback data
            self._update_cache(symbol, fallback_data)
            
            print(f"✅ Using fallback NAV: {symbol} @ ₹{fallback_data['currentPrice']:.2f}")
            return fallback_data
        
        # Not a debt fund and all APIs failed
        print(f"❌ Cannot fetch data for {symbol}")
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
            'ytdReturn': round(market_data['ytdReturn'], 2) if market_data['ytdReturn'] else None
        }
        
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
        print(f"📊 Hybrid Market Report Agent - Starting")
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
            for holding in holdings:
                symbol = holding['symbol']
                if symbol in market_data_map:
                    enriched = self.enrich_holding(holding, market_data_map[symbol])
                    enriched_holdings.append(enriched)
            
            if not enriched_holdings:
                return {
                    'success': False,
                    'error': 'Could not enrich any holdings',
                    'userId': user_email
                }
            
            portfolio_metrics = self.calculate_portfolio_metrics(enriched_holdings)
            
            print("=" * 60)
            print(f"✅ Report Generated Successfully")
            print(f"📈 Total Portfolio Value: ₹{portfolio_metrics['totalValue']:,.2f}")
            print(f"📊 Holdings Processed: {len(enriched_holdings)}/{len(holdings)}")
            print("=" * 60)
            
            return {
                'success': True,
                'timestamp': datetime.utcnow().isoformat(),
                'userId': user_email,
                'holdings': enriched_holdings,
                'portfolioMetrics': portfolio_metrics,
                'cashSavings': float(portfolio.get('cashSavings', 0))
            }
            
        except Exception as e:
            print(f"❌ Error generating report: {e}")
            return {
                'success': False,
                'error': str(e),
                'userId': user_email
            }


# Testing
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    agent = HybridMarketDataAgent(delay_between_calls=0.3, max_retries=3)
    
    test_email = "lok@gmail.com"
    report = agent.generate_report(test_email)
    
    if report['success']:
        print("\n🎉 SUCCESS!")
        print(f"\nPortfolio Value: ₹{report['portfolioMetrics']['totalValue']:,.2f}")
    else:
        print(f"\n❌ ERROR: {report.get('error')}")#!/usr/bin/env python3
"""
Portfolio Analysis System using Strands Multi-Agent Framework
Specialized agents for market data fetching and portfolio analysis
"""

import os
import logging
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
from decimal import Decimal

import boto3
import yfinance as yf
import requests
from strands import Agent, tool
from strands.models import BedrockModel
from strands.multiagent import Swarm
from strands_tools import think

# Configure logging
logging.basicConfig(
    format="%(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
    handlers=[logging.StreamHandler()]
)

# =============================================================================
# GLOBAL DATA STRUCTURES & CONFIG
# =============================================================================

# API Configuration
API_CONFIG = {
    'alpha_vantage': {
        'key': os.getenv('ALPHA_VANTAGE_API_KEY', ''),
        'base_url': 'https://www.alphavantage.co/query',
        'rate_limit': 0.5,
        'last_call': 0,
        'enabled': bool(os.getenv('ALPHA_VANTAGE_API_KEY'))
    },
    'finnhub': {
        'key': os.getenv('FINNHUB_API_KEY', ''),
        'base_url': 'https://finnhub.io/api/v1',
        'rate_limit': 1.0,
        'last_call': 0,
        'enabled': bool(os.getenv('FINNHUB_API_KEY'))
    },
    'polygon': {
        'key': os.getenv('POLYGON_API_KEY', ''),
        'base_url': 'https://api.polygon.io',
        'rate_limit': 12.0,
        'last_call': 0,
        'enabled': bool(os.getenv('POLYGON_API_KEY'))
    },
    'yahoo': {
        'enabled': True,
        'rate_limit': 0.5,
        'last_call': 0
    }
}

# Cache for market data
MARKET_DATA_CACHE = {}
CACHE_TTL = 60

# DynamoDB client
dynamodb = boto3.resource("dynamodb", region_name=os.getenv("AWS_REGION", "us-east-1"))
portfolios_table = dynamodb.Table('WealthWisePortfolios')

# Indian stock symbols
INDIAN_STOCKS = [
    'RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK', 
    'SBIN', 'BHARTIARTL', 'ITC', 'KOTAKBANK', 'LT', 
    'AXISBANK', 'HINDUNILVR', 'BAJFINANCE', 'ASIANPAINT',
    'MARUTI', 'TITAN', 'WIPRO', 'ULTRACEMCO', 'SUNPHARMA',
    'NESTLEIND', 'HCLTECH', 'TECHM', 'TATAMOTORS', 'ADANIPORTS',
    'POWERGRID', 'ONGC', 'NTPC', 'COALINDIA', 'DRREDDY', 'CIPLA'
]

INDIAN_DEBT_KEYWORDS = [
    'GILT', 'DEBT', 'BOND', 'LIQUID', 
    'IDFC', 'ICICI', 'HDFC', 'SBI', 'AXIS',
    'CORP', 'BANKING', 'PSU', 'SHORT'
]

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _respect_rate_limit(api_name: str):
    """Enforce rate limiting for each API"""
    api = API_CONFIG[api_name]
    elapsed = time.time() - api['last_call']
    if elapsed < api['rate_limit']:
        sleep_time = api['rate_limit'] - elapsed
        time.sleep(sleep_time)
    api['last_call'] = time.time()

def _check_cache(symbol: str) -> Optional[Dict]:
    """Check if we have cached data for symbol"""
    if symbol in MARKET_DATA_CACHE:
        cached_time, data = MARKET_DATA_CACHE[symbol]
        if time.time() - cached_time < CACHE_TTL:
            print(f"💾 Using cached data for {symbol}")
            return data
    return None

def _update_cache(symbol: str, data: Dict):
    """Update cache with new data"""
    MARKET_DATA_CACHE[symbol] = (time.time(), data)

# =============================================================================
# TOOLS - Market Data Fetching
# =============================================================================

@tool
def fetch_from_alpha_vantage(symbol: str) -> Dict[str, Any]:
    """
    Fetch market data from Alpha Vantage API.
    
    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'RELIANCE.NS')
    
    Returns:
        Dictionary with market data or error status
    """
    if not API_CONFIG['alpha_vantage']['enabled']:
        return {"status": "error", "message": "Alpha Vantage API not configured"}
    
    try:
        _respect_rate_limit('alpha_vantage')
        
        api_key = API_CONFIG['alpha_vantage']['key']
        quote_url = f"{API_CONFIG['alpha_vantage']['base_url']}?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}"
        response = requests.get(quote_url, timeout=10)
        
        if response.status_code != 200:
            return {"status": "error", "message": f"HTTP {response.status_code}"}
        
        data = response.json()
        
        if 'Global Quote' not in data or not data['Global Quote']:
            return {"status": "error", "message": "No data in response"}
        
        quote = data['Global Quote']
        
        # Get overview
        overview_url = f"{API_CONFIG['alpha_vantage']['base_url']}?function=OVERVIEW&symbol={symbol}&apikey={api_key}"
        _respect_rate_limit('alpha_vantage')
        overview_response = requests.get(overview_url, timeout=10)
        overview = overview_response.json() if overview_response.status_code == 200 else {}
        
        market_data = {
            'status': 'success',
            'source': 'alpha_vantage',
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
        return {"status": "error", "message": f"Alpha Vantage error: {str(e)}"}

@tool
def fetch_from_finnhub(symbol: str) -> Dict[str, Any]:
    """
    Fetch market data from Finnhub API.
    
    Args:
        symbol: Stock ticker symbol
    
    Returns:
        Dictionary with market data or error status
    """
    if not API_CONFIG['finnhub']['enabled']:
        return {"status": "error", "message": "Finnhub API not configured"}
    
    try:
        _respect_rate_limit('finnhub')
        
        api_key = API_CONFIG['finnhub']['key']
        base_url = API_CONFIG['finnhub']['base_url']
        
        quote_url = f"{base_url}/quote?symbol={symbol}&token={api_key}"
        response = requests.get(quote_url, timeout=10)
        
        if response.status_code != 200:
            return {"status": "error", "message": f"HTTP {response.status_code}"}
        
        quote = response.json()
        
        # Get profile
        profile_url = f"{base_url}/stock/profile2?symbol={symbol}&token={api_key}"
        _respect_rate_limit('finnhub')
        profile_response = requests.get(profile_url, timeout=10)
        profile = profile_response.json() if profile_response.status_code == 200 else {}
        
        market_data = {
            'status': 'success',
            'source': 'finnhub',
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
        return {"status": "error", "message": f"Finnhub error: {str(e)}"}

@tool
def fetch_from_yahoo(symbol: str) -> Dict[str, Any]:
    """
    Fetch market data from Yahoo Finance - Enhanced for Indian market.
    
    Args:
        symbol: Stock ticker symbol (auto-adds .NS for Indian stocks)
    
    Returns:
        Dictionary with comprehensive market data or error status
    """
    try:
        _respect_rate_limit('yahoo')
        
        # Auto-add .NS suffix for Indian stocks
        yahoo_symbol = symbol
        if not ('.' in symbol or '_' in symbol):
            if symbol.upper() in INDIAN_STOCKS:
                yahoo_symbol = f"{symbol}.NS"
                print(f"   🇮🇳 Auto-adding NSE suffix: {symbol} → {yahoo_symbol}")
        
        ticker = yf.Ticker(yahoo_symbol)
        info = ticker.info
        hist = ticker.history(period="ytd")
        
        # Calculate YTD return
        ytd_return = None
        if not hist.empty and len(hist) > 0:
            first_price = hist['Close'].iloc[0]
            last_price = hist['Close'].iloc[-1]
            ytd_return = ((last_price - first_price) / first_price) * 100
        
        market_data = {
            'status': 'success',
            'source': 'yahoo',
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
            return {"status": "error", "message": "No price data available"}
        
        print(f"✅ Yahoo Finance: {yahoo_symbol} @ ₹{market_data['currentPrice']:.2f}")
        return market_data
        
    except Exception as e:
        return {"status": "error", "message": f"Yahoo Finance error: {str(e)}"}

@tool
def fetch_market_data_with_fallback(symbol: str) -> Dict[str, Any]:
    """
    Hybrid fetch with intelligent fallback across multiple APIs.
    Includes special handling for Indian debt funds.
    
    Args:
        symbol: Stock/Fund ticker symbol
    
    Returns:
        Dictionary with market data from best available source
    """
    # Check cache first
    cached_data = _check_cache(symbol)
    if cached_data:
        return cached_data
    
    # Try APIs in order of preference
    api_methods = [
        ('Yahoo Finance', fetch_from_yahoo),
        ('Alpha Vantage', fetch_from_alpha_vantage),
        ('Finnhub', fetch_from_finnhub),
    ]
    
    # Try each API
    for api_name, fetch_method in api_methods:
        print(f"🔄 Trying {api_name} for {symbol}...")
        result = fetch_method(symbol)
        
        if result.get('status') == 'success' and result.get('currentPrice'):
            _update_cache(symbol, result)
            return result
    
    # All APIs failed - check for Indian debt fund
    print(f"⚠️  All APIs failed for {symbol}")
    
    is_indian_debt = any(keyword in symbol.upper() for keyword in INDIAN_DEBT_KEYWORDS)
    
    if is_indian_debt:
        print(f"💡 {symbol} appears to be Indian debt fund - using estimated NAV")
        
        fallback_data = {
            'status': 'success',
            'source': 'fallback_estimate',
            'currentPrice': 25.0,
            'marketCap': None,
            'sector': 'Debt Fund',
            'industry': 'Mutual Fund',
            'beta': 0.05,
            'week52High': 26.0,
            'week52Low': 24.5,
            'dayChange': 0.02,
            'dayChangePct': 0.08,
            'volume': None,
            'peRatio': None,
            'dividendYield': 6.5,
            'ytdReturn': 5.2
        }
        
        _update_cache(symbol, fallback_data)
        print(f"✅ Using fallback NAV: {symbol} @ ₹{fallback_data['currentPrice']:.2f}")
        return fallback_data
    
    return {"status": "error", "message": f"Cannot fetch data for {symbol} from any source"}

# =============================================================================
# TOOLS - Portfolio Management
# =============================================================================

@tool
def get_user_portfolio(user_email: str) -> Dict[str, Any]:
    """
    Fetch user portfolio from DynamoDB.
    
    Args:
        user_email: User's email address
    
    Returns:
        Portfolio data including stocks, bonds, ETFs, and cash
    """
    try:
        response = portfolios_table.get_item(Key={'userId': user_email})
        if 'Item' in response:
            portfolio = response['Item']
            
            # Count holdings
            stocks_count = len(portfolio.get('stocks', []))
            bonds_count = len(portfolio.get('bonds', []))
            etfs_count = len(portfolio.get('etfs', []))
            
            print(f"📊 Portfolio loaded: {stocks_count} stocks, {bonds_count} bonds, {etfs_count} ETFs")
            
            return {
                'status': 'success',
                'portfolio': portfolio
            }
        return {
            'status': 'error',
            'message': 'Portfolio not found'
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f"Database error: {str(e)}"
        }

@tool
def extract_portfolio_symbols(portfolio_data: str) -> Dict[str, Any]:
    """
    Extract all symbols from portfolio (stocks, bonds, ETFs).
    
    Args:
        portfolio_data: JSON string of portfolio data
    
    Returns:
        List of holdings with symbol, quantity, type, and average price
    """
    try:
        import json
        portfolio = json.loads(portfolio_data) if isinstance(portfolio_data, str) else portfolio_data
        
        if portfolio.get('status') == 'error':
            return portfolio
        
        if 'portfolio' in portfolio:
            portfolio = portfolio['portfolio']
        
        symbols = []
        
        # Extract BONDS
        for bond in portfolio.get('bonds', []):
            if isinstance(bond, dict) and bond.get('symbol') and bond.get('quantity'):
                symbols.append({
                    'symbol': bond['symbol'],
                    'quantity': float(bond['quantity']),
                    'type': 'bond',
                    'avgPrice': float(bond.get('avgPrice', 0)),
                })
        
        # Extract STOCKS
        for stock in portfolio.get('stocks', []):
            if isinstance(stock, dict) and stock.get('symbol') and stock.get('quantity'):
                symbols.append({
                    'symbol': stock['symbol'],
                    'quantity': float(stock['quantity']),
                    'avgPrice': float(stock.get('avgPrice', 0)),
                    'type': 'stock'
                })
        
        # Extract ETFs
        for etf in portfolio.get('etfs', []):
            if isinstance(etf, dict) and etf.get('symbol') and etf.get('quantity'):
                symbols.append({
                    'symbol': etf['symbol'],
                    'quantity': float(etf['quantity']),
                    'avgPrice': float(etf.get('avgPrice', 0)),
                    'type': 'etf'
                })
        
        print(f"📊 Extracted {len(symbols)} holdings:")
        print(f"   - Bonds: {len([s for s in symbols if s['type'] == 'bond'])}")
        print(f"   - Stocks: {len([s for s in symbols if s['type'] == 'stock'])}")
        print(f"   - ETFs: {len([s for s in symbols if s['type'] == 'etf'])}")
        
        return {
            'status': 'success',
            'holdings': symbols,
            'cashSavings': float(portfolio.get('cashSavings', 0))
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': f"Error extracting symbols: {str(e)}"
        }

@tool
def enrich_holdings_with_market_data(holdings_data: str) -> Dict[str, Any]:
    """
    Enrich portfolio holdings with current market data.
    
    Args:
        holdings_data: JSON string of holdings data
    
    Returns:
        Enriched holdings with current prices and values
    """
    try:
        import json
        holdings_dict = json.loads(holdings_data) if isinstance(holdings_data, str) else holdings_data
        
        if holdings_dict.get('status') == 'error':
            return holdings_dict
        
        holdings = holdings_dict.get('holdings', [])
        enriched_holdings = []
        
        for i, holding in enumerate(holdings, 1):
            symbol = holding['symbol']
            print(f"[{i}/{len(holdings)}] Enriching {symbol}...")
            
            market_data = fetch_market_data_with_fallback(symbol)
            
            if market_data.get('status') == 'success':
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
                    'marketCap': market_data.get('marketCap'),
                    'sector': market_data.get('sector', 'N/A'),
                    'industry': market_data.get('industry', 'N/A'),
                    'beta': round(market_data['beta'], 2) if market_data.get('beta') else None,
                    'week52High': round(market_data['week52High'], 2) if market_data.get('week52High') else None,
                    'week52Low': round(market_data['week52Low'], 2) if market_data.get('week52Low') else None,
                    'dayChange': round(market_data['dayChange'], 2) if market_data.get('dayChange') else None,
                    'dayChangePct': round(market_data['dayChangePct'], 2) if market_data.get('dayChangePct') else None,
                    'volume': market_data.get('volume'),
                    'peRatio': round(market_data['peRatio'], 2) if market_data.get('peRatio') else None,
                    'dividendYield': round(market_data['dividendYield'], 2) if market_data.get('dividendYield') else None,
                    'ytdReturn': round(market_data['ytdReturn'], 2) if market_data.get('ytdReturn') else None,
                    'dataSource': market_data.get('source', 'unknown')
                }
                
                enriched_holdings.append(enriched)
            else:
                print(f"⚠️  Skipping {symbol} - could not fetch market data")
        
        success_rate = len(enriched_holdings) / len(holdings) * 100 if len(holdings) > 0 else 0
        print(f"📊 Successfully enriched {len(enriched_holdings)}/{len(holdings)} holdings ({success_rate:.0f}%)")
        
        return {
            'status': 'success',
            'enrichedHoldings': enriched_holdings,
            'cashSavings': holdings_dict.get('cashSavings', 0)
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': f"Error enriching holdings: {str(e)}"
        }

@tool
def calculate_portfolio_metrics(enriched_data: str) -> Dict[str, Any]:
    """
    Calculate comprehensive portfolio metrics and analytics.
    
    Args:
        enriched_data: JSON string of enriched holdings
    
    Returns:
        Portfolio metrics including total value, sector allocation, top holdings
    """
    try:
        import json
        data = json.loads(enriched_data) if isinstance(enriched_data, str) else enriched_data
        
        if data.get('status') == 'error':
            return data
        
        enriched_holdings = data.get('enrichedHoldings', [])
        
        if not enriched_holdings:
            return {
                'status': 'error',
                'message': 'No enriched holdings to calculate metrics'
            }
        
        # Total portfolio value
        total_value = sum(h['currentValue'] for h in enriched_holdings)
        
        # Calculate portfolio weights
        for holding in enriched_holdings:
            holding['portfolioWeight'] = round((holding['currentValue'] / total_value) * 100, 2) if total_value > 0 else 0
        
        # Sector allocation
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
        
        # Portfolio beta (weighted average)
        portfolio_beta = 0
        beta_weight_sum = 0
        for holding in enriched_holdings:
            if holding['beta'] is not None:
                weight = holding['currentValue'] / total_value if total_value > 0 else 0
                portfolio_beta += holding['beta'] * weight
                beta_weight_sum += weight
        
        portfolio_beta = round(portfolio_beta, 2) if beta_weight_sum > 0 else None
        
        # Top 5 holdings
        top_holdings = sorted(enriched_holdings, key=lambda x: x['currentValue'], reverse=True)[:5]
        top_5 = [
            {
                'symbol': h['symbol'],
                'value': h['currentValue'],
                'weight': h['portfolioWeight']
            }
            for h in top_holdings
        ]
        
        # Daily change
        day_total_change = sum(
            h['dayChange'] * h['quantity'] 
            for h in enriched_holdings 
            if h['dayChange'] is not None
        )
        day_total_change_pct = (day_total_change / total_value) * 100 if total_value > 0 else 0
        
        return {
            'status': 'success',
            'totalValue': round(total_value, 2),
            'portfolioBeta': portfolio_beta,
            'sectorBreakdown': sector_breakdown,
            'topHoldings': top_5,
            'dayTotalChange': round(day_total_change, 2),
            'dayTotalChangePct': round(day_total_change_pct, 2),
            'holdingsCount': len(enriched_holdings),
            'enrichedHoldings': enriched_holdings,
            'cashSavings': data.get('cashSavings', 0)
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': f"Error calculating metrics: {str(e)}"
        }

# =============================================================================
# AGENT CREATION
# =============================================================================

def create_data_fetcher_agent() -> Agent:
    """Agent specialized in fetching market data from multiple sources"""
    return Agent(
        name="data_fetcher",
        system_prompt="""You are a market data specialist agent. Your role is to:
        
1. Fetch real-time market data from multiple APIs (Yahoo, Alpha Vantage, Finnhub)
2. Use fetch_market_data_with_fallback for intelligent multi-API fetching
3. Handle Indian market stocks with automatic .NS suffix addition
4. Provide fallback estimates for debt funds when APIs fail
5. Cache results to optimize performance

WORKFLOW:
- Use fetch_market_data_with_fallback for each symbol
- Report which API source was used
- Handle errors gracefully with fallback mechanisms

Pass data to portfolio_analyst agent for enrichment.""",
        model=BedrockModel(model_id="us.amazon.nova-lite-v1:0", region="us-east-1"),
        tools=[
            fetch_from_yahoo,
            fetch_from_alpha_vantage,
            fetch_from_finnhub,
            fetch_market_data_with_fallback
        ]
    )

def create_portfolio_analyst_agent() -> Agent:
    """Agent specialized in portfolio analysis and enrichment"""
    return Agent(
        name="portfolio_analyst",
        system_prompt="""You are a portfolio analysis specialist. Your role is to:

1. Retrieve user portfolios from database
2. Extract all holdings (stocks, bonds, ETFs)
3. Enrich holdings with market data
4. Calculate portfolio metrics and analytics

WORKFLOW:
1. Use get_user_portfolio to fetch portfolio
2. Use extract_portfolio_symbols to get all holdings
3. Use enrich_holdings_with_market_data to add market prices
4. Use calculate_portfolio_metrics for final analytics

Always pass complete JSON data between tools. Report progress clearly.""",
        model=BedrockModel(model_id="us.amazon.nova-lite-v1:0", region="us-east-1"),
        tools=[
            get_user_portfolio,
            extract_portfolio_symbols,
            enrich_holdings_with_market_data,
            calculate_portfolio_metrics
        ]
    )

def create_report_orchestrator() -> Agent:
    """Main orchestrator agent using Nova Pro for synthesis"""
    return Agent(
        name="report_orchestrator",
        system_prompt="""You are the senior portfolio report orchestrator using Nova Pro.

WORKFLOW:
1. Receive user email
2. Coordinate with portfolio_analyst to get complete portfolio analysis
3. Use think tool for strategic insights
4. Generate comprehensive portfolio report

REPORT STRUCTURE:
1. **Executive Summary**
   - Total portfolio value with cash savings
   - Day change (absolute and percentage)
   - Number of holdings

2. **Holdings Breakdown**
   - All enriched holdings with current prices
   - Portfolio weights
   - Profit/loss for each position

3. **Portfolio Analytics**
   - Sector allocation breakdown
   - Top 5 holdings
   - Portfolio beta (risk metric)

4. **Market Data Sources**
   - Report which APIs were used
   - Highlight any fallback estimates

5. **Strategic Insights** (use think tool)
   - Diversification analysis
   - Risk assessment
   - Rebalancing recommendations

Present data in clear, formatted way with Indian Rupee (₹) currency.""",
        model=BedrockModel(model_id="us.amazon.nova-pro-v1:0", region="us-east-1"),
        tools=[think]
    )

# =============================================================================
# MAIN EXECUTION
# =============================================================================

def generate_portfolio_report(user_email: str) -> Dict[str, Any]:
    """
    Generate complete portfolio report using Strands multi-agent system.
    
    Args:
        user_email: User's email address
    
    Returns:
        Comprehensive portfolio report with all analytics
    """
    print("=" * 60)
    print("📊 Strands Multi-Agent Portfolio Report System")
    print(f"👤 User: {user_email}")
    print("=" * 60)
    
    try:
        # Create specialized agents
        portfolio_analyst = create_portfolio_analyst_agent()
        report_orchestrator = create_report_orchestrator()
        
        # Create swarm for collaborative analysis
        swarm = Swarm(
            [portfolio_analyst, report_orchestrator],
            max_handoffs=3,
            max_iterations=5,
            execution_timeout=180.0,
            node_timeout=45.0
        )
        
        # Execute analysis
        print("\n🔄 Starting multi-agent portfolio analysis...\n")
        
        result = swarm(
            f"Generate a comprehensive portfolio report for user: {user_email}. "
            f"Fetch their portfolio, enrich all holdings with market data, "
            f"calculate metrics, and provide strategic insights."
        )
        
        print("\n" + "=" * 60)
        print("✅ Portfolio Report Generated Successfully")
        print("=" * 60)
        
        return {
            'success': True,
            'timestamp': datetime.utcnow().isoformat(),
            'userId': user_email,
            'report': result.final_response,
            'collaboration_path': [node.node_id for node in result.node_history]
        }
        
    except Exception as e:
        print(f"\n❌ Error generating report: {e}")
        return {
            'success': False,
            'error': str(e),
            'userId': user_email
        }

def main():
    """Main function to run the portfolio analysis system"""
    from dotenv import load_dotenv
    load_dotenv()
    
    print("\n🤖 Strands Multi-Agent Portfolio Analysis System 📊")
    print("Features: Multi-API data fetching + Collaborative agent analysis\n")
    
    # Check active APIs
    active_apis = [name for name, config in API_CONFIG.items() if config['enabled']]
    print(f"📌 Active APIs: {', '.join(active_apis)}\n")
    
    while True:
        user_email = input("\nEnter user email (or 'exit' to quit): ")
        
        if user_email.lower() == 'exit':
            print("\nGoodbye! 👋")
            break
        
        if not user_email or '@' not in user_email:
            print("⚠️  Please enter a valid email address")
            continue
        
        report = generate_portfolio_report(user_email)
        
        if report['success']:
            print("\n" + "=" * 60)
            print("📋 PORTFOLIO REPORT")
            print("=" * 60)
            print(report['report'])
            print("\n" + "=" * 60)
        else:
            print(f"\n❌ Error: {report.get('error')}")

if __name__ == "__main__":
    main()
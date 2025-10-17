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
    
    API Priority Chain:
    1. Alpha Vantage (Free: 25 calls/day, Premium: 75-1200/min)
    2. Yahoo Finance (Fallback for free tier)
    3. Finnhub (Free: 60 calls/min)
    4. Polygon.io (Free: 5 calls/min)
    
    Features:
    - Automatic failover between APIs
    - Smart caching to reduce API calls
    - Rate limit handling per API
    - Parallel batch processing where possible
    """
    
    def __init__(self, delay_between_calls=0.3, max_retries=3):
        """Initialize with multiple API configurations"""
        self.dynamodb = boto3.resource(
            'dynamodb',
            region_name=os.getenv('AWS_REGION', 'us-east-1'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            aws_session_token=os.getenv('AWS_SESSION_TOKEN')
        )
        self.portfolios_table = self.dynamodb.Table('WealthWisePortfolios')
        
        # API Configuration
        self.apis = {
            'alpha_vantage': {
                'key': os.getenv('ALPHA_VANTAGE_API_KEY', ''),
                'base_url': 'https://www.alphavantage.co/query',
                'rate_limit': 0.5,  # 2 calls/second for free tier
                'last_call': 0,
                'enabled': bool(os.getenv('ALPHA_VANTAGE_API_KEY'))
            },
            'finnhub': {
                'key': os.getenv('FINNHUB_API_KEY', ''),
                'base_url': 'https://finnhub.io/api/v1',
                'rate_limit': 1.0,  # 60 calls/min = 1 call/sec
                'last_call': 0,
                'enabled': bool(os.getenv('FINNHUB_API_KEY'))
            },
            'polygon': {
                'key': os.getenv('POLYGON_API_KEY', ''),
                'base_url': 'https://api.polygon.io',
                'rate_limit': 12.0,  # 5 calls/min for free tier
                'last_call': 0,
                'enabled': bool(os.getenv('POLYGON_API_KEY'))
            },
            'yahoo': {
                'enabled': True,  # Always available
                'rate_limit': 0.5,
                'last_call': 0
            }
        }
        
        self.delay_between_calls = delay_between_calls
        self.max_retries = max_retries
        self.cache = {}  # Simple in-memory cache
        self.cache_ttl = 60  # Cache for 60 seconds
        
        # Print active APIs
        active_apis = [name for name, config in self.apis.items() if config['enabled']]
        print(f"🔌 Active APIs: {', '.join(active_apis)}")
    
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
            
            # Get quote data
            quote_url = f"{self.apis['alpha_vantage']['base_url']}?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}"
            response = requests.get(quote_url, timeout=10)
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            
            if 'Global Quote' not in data or not data['Global Quote']:
                return None
            
            quote = data['Global Quote']
            
            # Get company overview for additional data
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
                'ytdReturn': None  # Calculate separately if needed
            }
            
            print(f"✅ Alpha Vantage: {symbol} @ ${market_data['currentPrice']:.2f}")
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
            
            # Get quote
            quote_url = f"{base_url}/quote?symbol={symbol}&token={api_key}"
            response = requests.get(quote_url, timeout=10)
            
            if response.status_code != 200:
                return None
            
            quote = response.json()
            
            # Get company profile
            profile_url = f"{base_url}/stock/profile2?symbol={symbol}&token={api_key}"
            self._respect_rate_limit('finnhub')
            profile_response = requests.get(profile_url, timeout=10)
            profile = profile_response.json() if profile_response.status_code == 200 else {}
            
            market_data = {
                'currentPrice': float(quote.get('c', 0)),
                'marketCap': profile.get('marketCapitalization', None),
                'sector': profile.get('finnhubIndustry', 'N/A'),
                'industry': profile.get('finnhubIndustry', 'N/A'),
                'beta': None,  # Not available in free tier
                'week52High': float(quote.get('h', 0)) if quote.get('h') else None,
                'week52Low': float(quote.get('l', 0)) if quote.get('l') else None,
                'dayChange': float(quote.get('d', 0)),
                'dayChangePct': float(quote.get('dp', 0)),
                'volume': None,
                'peRatio': None,
                'dividendYield': None,
                'ytdReturn': None
            }
            
            print(f"✅ Finnhub: {symbol} @ ${market_data['currentPrice']:.2f}")
            return market_data
            
        except Exception as e:
            print(f"⚠️  Finnhub failed for {symbol}: {e}")
            return None
    
    def fetch_from_yahoo(self, symbol: str) -> Optional[Dict]:
        """Fetch from Yahoo Finance (original method)"""
        try:
            self._respect_rate_limit('yahoo')
            
            ticker = yf.Ticker(symbol)
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
            
            print(f"✅ Yahoo Finance: {symbol} @ ${market_data['currentPrice']:.2f}")
            return market_data
            
        except Exception as e:
            print(f"⚠️  Yahoo Finance failed for {symbol}: {e}")
            return None
    
    def fetch_market_data(self, symbol: str, retry_count=0) -> Optional[Dict]:
        """
        Hybrid fetch with intelligent fallback
        Priority: Cache -> Alpha Vantage -> Finnhub -> Yahoo Finance
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
        
        # All APIs failed
        print(f"❌ All APIs failed for {symbol}")
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
        """Extract all stock and ETF symbols with their quantities"""
        symbols = []
        
        for stock in portfolio.get('stocks', []):
            symbols.append({
                'symbol': stock['symbol'],
                'quantity': float(stock['quantity']),
                'type': 'stock'
            })
        
        for etf in portfolio.get('etfs', []):
            symbols.append({
                'symbol': etf['symbol'],
                'quantity': float(etf['quantity']),
                'type': 'etf'
            })
        
        print(f"📊 Found {len(symbols)} holdings to fetch")
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
        
        success_rate = len(market_data_map) / len(symbols) * 100
        print(f"📊 Successfully fetched {len(market_data_map)}/{len(symbols)} symbols ({success_rate:.0f}%)")
        print()
        
        return market_data_map
    
    def enrich_holding(self, holding: Dict, market_data: Dict) -> Dict:
        """Enrich a single holding with market data"""
        quantity = holding['quantity']
        current_price = market_data['currentPrice']
        current_value = quantity * current_price
        
        enriched = {
            'symbol': holding['symbol'],
            'type': holding['type'],
            'quantity': quantity,
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
            holding['portfolioWeight'] = round((holding['currentValue'] / total_value) * 100, 2)
        
        sector_allocation = {}
        for holding in enriched_holdings:
            sector = holding['sector']
            if sector not in sector_allocation:
                sector_allocation[sector] = 0
            sector_allocation[sector] += holding['currentValue']
        
        sector_breakdown = {
            sector: round((value / total_value) * 100, 2)
            for sector, value in sector_allocation.items()
        }
        
        portfolio_beta = 0
        beta_weight_sum = 0
        for holding in enriched_holdings:
            if holding['beta'] is not None:
                weight = holding['currentValue'] / total_value
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
            print(f"📈 Total Portfolio Value: ${portfolio_metrics['totalValue']:,.2f}")
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
        print(f"\nPortfolio Value: ${report['portfolioMetrics']['totalValue']:,.2f}")
    else:
        print(f"\n❌ ERROR: {report.get('error')}")


# # backend/main.py
# import os
# import sys

# # Load environment variables FIRST
# from dotenv import load_dotenv
# load_dotenv()

# # Debug: Print environment variables
# print("=" * 60)
# print("🔧 DEBUG: Environment Variables")
# print("=" * 60)
# print(f"AWS_ACCESS_KEY_ID: {os.getenv('AWS_ACCESS_KEY_ID', 'NOT_SET')[:15]}...")
# print(f"AWS_SECRET_ACCESS_KEY: {'SET' if os.getenv('AWS_SECRET_ACCESS_KEY') else 'NOT_SET'}")
# print(f"AWS_SESSION_TOKEN: {'SET' if os.getenv('AWS_SESSION_TOKEN') else 'NOT_SET'}")
# print(f"AWS_REGION: {os.getenv('AWS_REGION', 'us-east-1')}")
# print("=" * 60)
# print()

# # Check if credentials are loaded
# if not os.getenv('AWS_ACCESS_KEY_ID'):
#     print("❌ ERROR: AWS credentials not found!")
#     print("❌ Make sure .env file exists in the backend directory")
#     sys.exit(1)

# from fastapi import FastAPI, HTTPException, status
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel, EmailStr
# from typing import List, Optional, Dict, Any
# import boto3
# from boto3.dynamodb.conditions import Key, Attr
# from datetime import datetime
# from decimal import Decimal
# import bcrypt
# from market_report_agent import MarketReportAgent

# app = FastAPI(title="WealthWise AI API")

# # CORS Configuration
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Initialize DynamoDB
# print("🔌 Initializing DynamoDB connection...")
# dynamodb = boto3.resource(
#     'dynamodb',
#     region_name=os.getenv('AWS_REGION', 'us-east-1'),
#     aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
#     aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
#     aws_session_token=os.getenv('AWS_SESSION_TOKEN')
# )

# # Test connection
# client = boto3.client(
#     'dynamodb',
#     region_name=os.getenv('AWS_REGION', 'us-east-1'),
#     aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
#     aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
#     aws_session_token=os.getenv('AWS_SESSION_TOKEN')
# )
# tables = client.list_tables()
# print(f"✅ DynamoDB connected! Found {len(tables['TableNames'])} tables")

# # Check for WealthWise tables
# required_tables = ['WealthWiseUsers', 'WealthWisePortfolios']
# missing_tables = [t for t in required_tables if t not in tables['TableNames']]

# if missing_tables:
#     print(f"⚠️  Missing tables: {missing_tables}")
#     print(f"⚠️  Run: python create_tables.py")
# else:
#     print(f"✅ WealthWise tables found!")

# # DynamoDB Tables
# users_table = dynamodb.Table('WealthWiseUsers')
# portfolios_table = dynamodb.Table('WealthWisePortfolios')



# from market_report_agent import HybridMarketDataAgent
# market_agent = HybridMarketDataAgent(
#     delay_between_calls=0.3,
#     max_retries=3
# )

# print("=" * 60)
# print()

# # ==================== PYDANTIC MODELS ====================

# class Holding(BaseModel):
#     symbol: str
#     quantity: float
#     avgPrice: float

# class CompleteOnboardingRequest(BaseModel):
#     userId: str  # Email
#     name: str
#     email: EmailStr
#     password: str
#     age: int
#     riskTolerance: str
#     investmentGoal: str
#     investmentHorizon: str
#     initialInvestment: float
#     monthlyContribution: float
#     cashSavings: float
#     bonds: List[Holding] = []
#     stocks: List[Holding] = []
#     etfs: List[Holding] = []
#     timestamp: str

# class LoginRequest(BaseModel):
#     email: EmailStr
#     password: str

# # ==================== HELPER FUNCTIONS ====================

# def hash_password(password: str) -> str:
#     """Hash password using bcrypt"""
#     salt = bcrypt.gensalt()
#     hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
#     return hashed.decode('utf-8')

# def verify_password(plain_password: str, hashed_password: str) -> bool:
#     """Verify password against hash"""
#     return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

# def convert_float_to_decimal(obj):
#     """Convert float to Decimal for DynamoDB"""
#     if isinstance(obj, float):
#         return Decimal(str(obj))
#     elif isinstance(obj, dict):
#         return {k: convert_float_to_decimal(v) for k, v in obj.items()}
#     elif isinstance(obj, list):
#         return [convert_float_to_decimal(item) for item in obj]
#     return obj

# def convert_decimal_to_float(obj):
#     """Convert Decimal to float for JSON response"""
#     if isinstance(obj, Decimal):
#         return float(obj)
#     elif isinstance(obj, dict):
#         return {k: convert_decimal_to_float(v) for k, v in obj.items()}
#     elif isinstance(obj, list):
#         return [convert_decimal_to_float(item) for item in obj]
#     return obj

# # ==================== HEALTH CHECK ====================

# @app.get("/")
# def read_root():
#     return {
#         "message": "WealthWise AI API",
#         "status": "running",
#         "version": "1.0.0",
#         "endpoints": {
#             "onboarding": "POST /api/onboarding/complete",
#             "login": "POST /api/auth/login",
#             "getUser": "GET /api/user/{email}",
#             "getPortfolio": "GET /api/portfolio/{email}",
#             "updatePortfolio": "PUT /api/portfolio/{email}",
#              "marketReport": "GET /api/portfolio/{email}/market-report"
#         }
#     }

# @app.get("/health")
# def health_check():
#     return {
#         "status": "healthy",
#         "timestamp": datetime.utcnow().isoformat(),
#         "service": "WealthWise AI Backend"
#     }

# # ==================== AUTH ENDPOINTS ====================

# @app.post("/api/auth/login")
# async def login(request: LoginRequest):
#     """Login user with email and password"""
#     print(f"🔐 Login attempt for: {request.email}")
    
#     # Get user by email
#     response = users_table.get_item(Key={'userId': request.email})
    
#     if 'Item' not in response:
#         print(f"❌ User not found: {request.email}")
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid credentials"
#         )
    
#     user = response['Item']
    
#     # Verify password
#     if not verify_password(request.password, user['passwordHash']):
#         print(f"❌ Invalid password for: {request.email}")
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid credentials"
#         )
    
#     print(f"✅ Login successful: {request.email}")
    
#     # Remove password hash
#     if 'passwordHash' in user:
#         del user['passwordHash']
    
#     # Get portfolio if exists
#     portfolio = None
#     if user.get('hasPortfolio'):
#         portfolio_response = portfolios_table.get_item(Key={'userId': request.email})
#         if 'Item' in portfolio_response:
#             portfolio = convert_decimal_to_float(portfolio_response['Item'])
    
#     return {
#         'success': True,
#         'user': convert_decimal_to_float(user),
#         'portfolio': portfolio
#     }

# # ==================== ONBOARDING ENDPOINT ====================

# @app.post("/api/onboarding/complete")
# async def complete_onboarding(request: CompleteOnboardingRequest):
#     """Save user onboarding data - exactly what they entered"""
#     user_email = request.userId
    
#     print(f"📝 Saving onboarding data for: {user_email}")
    
#     # Check if user exists
#     existing_user = users_table.get_item(Key={'userId': user_email})
#     if 'Item' in existing_user:
#         print(f"⚠️  User already exists: {user_email}")
#         raise HTTPException(
#             status_code=status.HTTP_409_CONFLICT,
#             detail="An account with this email already exists"
#         )
    
#     # Hash password
#     print(f"🔒 Hashing password...")
#     password_hash = hash_password(request.password)
    
#     # Save user profile to Users table
#     user_data = {
#         'userId': user_email,
#         'email': request.email,
#         'name': request.name,
#         'passwordHash': password_hash,
#         'age': request.age,
#         'riskTolerance': request.riskTolerance,
#         'investmentGoal': request.investmentGoal,
#         'investmentHorizon': request.investmentHorizon,
#         'monthlyContribution': convert_float_to_decimal(request.monthlyContribution),
#         'hasPortfolio': True,
#         'createdAt': datetime.utcnow().isoformat(),
#         'updatedAt': datetime.utcnow().isoformat()
#     }
    
#     print(f"💾 Saving user to WealthWiseUsers...")
#     users_table.put_item(Item=user_data)
#     print(f"✅ User saved: {user_email}")
    
#     # Save portfolio data to Portfolios table - exactly what user entered
#     portfolio_data = {
#         'userId': user_email,
#         'initialInvestment': convert_float_to_decimal(request.initialInvestment),
#         'cashSavings': convert_float_to_decimal(request.cashSavings),
#         'bonds': convert_float_to_decimal([b.dict() for b in request.bonds]),
#         'stocks': convert_float_to_decimal([s.dict() for s in request.stocks]),
#         'etfs': convert_float_to_decimal([e.dict() for e in request.etfs]),
#         'createdAt': datetime.utcnow().isoformat(),
#         'updatedAt': datetime.utcnow().isoformat()
#     }
    
#     print(f"💾 Saving portfolio to WealthWisePortfolios...")
#     portfolios_table.put_item(Item=portfolio_data)
#     print(f"✅ Portfolio saved: {user_email}")
    
#     # Remove password hash from response
#     if 'passwordHash' in user_data:
#         del user_data['passwordHash']
    
#     print(f"🎉 Onboarding completed for: {user_email}")
    
#     return {
#         'success': True,
#         'message': 'Onboarding completed successfully',
#         'userId': user_email,
#         'user': convert_decimal_to_float(user_data),
#         'portfolio': convert_decimal_to_float(portfolio_data)
#     }

# # ==================== USER ENDPOINTS ====================

# @app.get("/api/user/{email}")
# async def get_user(email: str):
#     """Get user profile by email"""
#     response = users_table.get_item(Key={'userId': email})
    
#     if 'Item' not in response:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="User not found"
#         )
    
#     user = response['Item']
#     if 'passwordHash' in user:
#         del user['passwordHash']
    
#     return {
#         'success': True,
#         'user': convert_decimal_to_float(user)
#     }

# # ==================== PORTFOLIO ENDPOINTS ====================

# @app.get("/api/portfolio/{email}")
# async def get_portfolio(email: str):
#     """Get user portfolio by email"""
#     response = portfolios_table.get_item(Key={'userId': email})
    
#     if 'Item' not in response:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Portfolio not found"
#         )
    
#     return {
#         'success': True,
#         'portfolio': convert_decimal_to_float(response['Item'])
#     }

# @app.get("/api/portfolio/{email}/market-report")
# async def get_market_report(email: str):
#     """
#     Get enriched portfolio with live market data
    
#     This endpoint uses the Market Report Strand Agent to:
#     1. Fetch user's portfolio from DynamoDB
#     2. Get live market data from Yahoo Finance
#     3. Enrich holdings with 10 key market parameters
#     4. Calculate portfolio-level metrics
    
#     Returns:
#         - holdings: List of enriched holdings with market data
#         - portfolioMetrics: Aggregate metrics (total value, beta, sector breakdown, etc.)
#         - cashSavings: User's cash position
#     """
#     print(f"📊 Market report requested for: {email}")
    
#     try:
#         # Call the Market Report Agent
#         report = market_agent.generate_report(email)
        
#         if not report['success']:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail=report.get('error', 'Failed to generate market report')
#             )
        
#         print(f"✅ Market report generated for: {email}")
#         return report
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         print(f"❌ Error generating market report: {e}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Internal server error: {str(e)}"
#         )

# @app.put("/api/portfolio/{email}")
# async def update_portfolio(email: str, portfolio_updates: Dict[str, Any]):
#     """Update user portfolio"""
#     response = portfolios_table.get_item(Key={'userId': email})
    
#     if 'Item' not in response:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Portfolio not found"
#         )
    
#     existing_portfolio = response['Item']
#     for key, value in portfolio_updates.items():
#         if key != 'userId':
#             existing_portfolio[key] = convert_float_to_decimal(value)
    
#     existing_portfolio['updatedAt'] = datetime.utcnow().isoformat()
    
#     portfolios_table.put_item(Item=existing_portfolio)
    
#     return {
#         'success': True,
#         'message': 'Portfolio updated successfully',
#         'portfolio': convert_decimal_to_float(existing_portfolio)
#     }

# # ==================== RUN SERVER ====================

# if __name__ == "__main__":
#     import uvicorn
#     print("=" * 60)
#     print("🚀 WealthWise AI Backend Server")
#     print("=" * 60)
#     print("📡 Server running on port 8000")
#     print("🌍 Environment: development")
#     print("🔗 API Base URL: http://localhost:8000")
#     print(f"📊 DynamoDB Region: {os.getenv('AWS_REGION', 'us-east-1')}")
#     print("=" * 60)
#     print()
#     uvicorn.run(app, host="0.0.0.0", port=8000)



# # backend/main.py
# import os
# import sys

# # Load environment variables FIRST
# from dotenv import load_dotenv
# load_dotenv()

# # Debug: Print environment variables
# print("=" * 60)
# print("🔧 DEBUG: Environment Variables")
# print("=" * 60)
# print(f"AWS_ACCESS_KEY_ID: {os.getenv('AWS_ACCESS_KEY_ID', 'NOT_SET')[:15]}...")
# print(f"AWS_SECRET_ACCESS_KEY: {'SET' if os.getenv('AWS_SECRET_ACCESS_KEY') else 'NOT_SET'}")
# print(f"AWS_SESSION_TOKEN: {'SET' if os.getenv('AWS_SESSION_TOKEN') else 'NOT_SET'}")
# print(f"AWS_REGION: {os.getenv('AWS_REGION', 'us-east-1')}")
# print()
# print("🔌 Market Data APIs:")
# print(f"Alpha Vantage: {'SET ✅' if os.getenv('ALPHA_VANTAGE_API_KEY') else 'NOT_SET ⚠️'}")
# print(f"Finnhub: {'SET ✅' if os.getenv('FINNHUB_API_KEY') else 'NOT_SET ⚠️'}")
# print(f"Polygon: {'SET ✅' if os.getenv('POLYGON_API_KEY') else 'NOT_SET (optional)'}")
# print(f"Yahoo Finance: ALWAYS AVAILABLE ✅")
# print("=" * 60)
# print()

# # Check if credentials are loaded
# if not os.getenv('AWS_ACCESS_KEY_ID'):
#     print("❌ ERROR: AWS credentials not found!")
#     print("❌ Make sure .env file exists in the backend directory")
#     sys.exit(1)

# # Check if at least one market API is configured
# market_apis_configured = any([
#     os.getenv('ALPHA_VANTAGE_API_KEY'),
#     os.getenv('FINNHUB_API_KEY'),
#     os.getenv('POLYGON_API_KEY')
# ])

# if not market_apis_configured:
#     print("⚠️  WARNING: No additional market data APIs configured!")
#     print("⚠️  Yahoo Finance will be used exclusively (higher risk of 429 errors)")
#     print("💡 RECOMMENDATION: Add at least one API key to .env:")
#     print("   - ALPHA_VANTAGE_API_KEY (https://www.alphavantage.co/support/#api-key)")
#     print("   - FINNHUB_API_KEY (https://finnhub.io/register)")
#     print()
#     print("Continue anyway? (yes/no): ", end='')
#     user_input = input().strip().lower()
#     if user_input not in ['yes', 'y']:
#         sys.exit(1)

# from fastapi import FastAPI, HTTPException, status
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel, EmailStr
# from typing import List, Optional, Dict, Any
# import boto3
# from boto3.dynamodb.conditions import Key, Attr
# from datetime import datetime
# from decimal import Decimal
# import bcrypt
# from market_report_agent import HybridMarketDataAgent  # ✨ HYBRID AGENT

# app = FastAPI(title="WealthWise AI API")

# # CORS Configuration
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Initialize DynamoDB
# print("🔌 Initializing DynamoDB connection...")
# dynamodb = boto3.resource(
#     'dynamodb',
#     region_name=os.getenv('AWS_REGION', 'us-east-1'),
#     aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
#     aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
#     aws_session_token=os.getenv('AWS_SESSION_TOKEN')
# )

# # Test connection
# client = boto3.client(
#     'dynamodb',
#     region_name=os.getenv('AWS_REGION', 'us-east-1'),
#     aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
#     aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
#     aws_session_token=os.getenv('AWS_SESSION_TOKEN')
# )
# tables = client.list_tables()
# print(f"✅ DynamoDB connected! Found {len(tables['TableNames'])} tables")

# # Check for WealthWise tables
# required_tables = ['WealthWiseUsers', 'WealthWisePortfolios']
# missing_tables = [t for t in required_tables if t not in tables['TableNames']]

# if missing_tables:
#     print(f"⚠️  Missing tables: {missing_tables}")
#     print(f"⚠️  Run: python create_tables.py")
# else:
#     print(f"✅ WealthWise tables found!")

# # DynamoDB Tables
# users_table = dynamodb.Table('WealthWiseUsers')
# portfolios_table = dynamodb.Table('WealthWisePortfolios')

# # Initialize Hybrid Market Report Agent ✨
# print()
# print("🚀 Initializing Hybrid Market Data Agent...")
# market_agent = HybridMarketDataAgent(
#     delay_between_calls=0.3,  # Aggressive rate limiting
#     max_retries=3
# )

# print("=" * 60)
# print()

# # ==================== PYDANTIC MODELS ====================

# class Holding(BaseModel):
#     symbol: str
#     quantity: float
#     avgPrice: float

# class CompleteOnboardingRequest(BaseModel):
#     userId: str  # Email
#     name: str
#     email: EmailStr
#     password: str
#     age: int
#     riskTolerance: str
#     investmentGoal: str
#     investmentHorizon: str
#     initialInvestment: float
#     monthlyContribution: float
#     cashSavings: float
#     bonds: List[Holding] = []
#     stocks: List[Holding] = []
#     etfs: List[Holding] = []
#     timestamp: str

# class LoginRequest(BaseModel):
#     email: EmailStr
#     password: str

# # ==================== HELPER FUNCTIONS ====================

# def hash_password(password: str) -> str:
#     """Hash password using bcrypt"""
#     salt = bcrypt.gensalt()
#     hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
#     return hashed.decode('utf-8')

# def verify_password(plain_password: str, hashed_password: str) -> bool:
#     """Verify password against hash"""
#     return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

# def convert_float_to_decimal(obj):
#     """Convert float to Decimal for DynamoDB"""
#     if isinstance(obj, float):
#         return Decimal(str(obj))
#     elif isinstance(obj, dict):
#         return {k: convert_float_to_decimal(v) for k, v in obj.items()}
#     elif isinstance(obj, list):
#         return [convert_float_to_decimal(item) for item in obj]
#     return obj

# def convert_decimal_to_float(obj):
#     """Convert Decimal to float for JSON response"""
#     if isinstance(obj, Decimal):
#         return float(obj)
#     elif isinstance(obj, dict):
#         return {k: convert_decimal_to_float(v) for k, v in obj.items()}
#     elif isinstance(obj, list):
#         return [convert_decimal_to_float(item) for item in obj]
#     return obj

# # ==================== HEALTH CHECK ====================

# @app.get("/")
# def read_root():
#     # Check which APIs are active
#     active_apis = []
#     if os.getenv('ALPHA_VANTAGE_API_KEY'):
#         active_apis.append("Alpha Vantage")
#     if os.getenv('FINNHUB_API_KEY'):
#         active_apis.append("Finnhub")
#     if os.getenv('POLYGON_API_KEY'):
#         active_apis.append("Polygon")
#     active_apis.append("Yahoo Finance")
    
#     return {
#         "message": "WealthWise AI API",
#         "status": "running",
#         "version": "2.0.0 - Hybrid Market Data",
#         "marketDataAPIs": {
#             "active": active_apis,
#             "fallbackChain": "Alpha Vantage → Finnhub → Polygon → Yahoo Finance",
#             "caching": "60 seconds TTL"
#         },
#         "endpoints": {
#             "onboarding": "POST /api/onboarding/complete",
#             "login": "POST /api/auth/login",
#             "getUser": "GET /api/user/{email}",
#             "getPortfolio": "GET /api/portfolio/{email}",
#             "updatePortfolio": "PUT /api/portfolio/{email}",
#             "marketReport": "GET /api/portfolio/{email}/market-report"
#         }
#     }

# @app.get("/health")
# def health_check():
#     return {
#         "status": "healthy",
#         "timestamp": datetime.utcnow().isoformat(),
#         "service": "WealthWise AI Backend",
#         "version": "2.0.0 - Hybrid"
#     }

# # ==================== AUTH ENDPOINTS ====================

# @app.post("/api/auth/login")
# async def login(request: LoginRequest):
#     """Login user with email and password"""
#     print(f"🔐 Login attempt for: {request.email}")
    
#     # Get user by email
#     response = users_table.get_item(Key={'userId': request.email})
    
#     if 'Item' not in response:
#         print(f"❌ User not found: {request.email}")
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid credentials"
#         )
    
#     user = response['Item']
    
#     # Verify password
#     if not verify_password(request.password, user['passwordHash']):
#         print(f"❌ Invalid password for: {request.email}")
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid credentials"
#         )
    
#     print(f"✅ Login successful: {request.email}")
    
#     # Remove password hash
#     if 'passwordHash' in user:
#         del user['passwordHash']
    
#     # Get portfolio if exists
#     portfolio = None
#     if user.get('hasPortfolio'):
#         portfolio_response = portfolios_table.get_item(Key={'userId': request.email})
#         if 'Item' in portfolio_response:
#             portfolio = convert_decimal_to_float(portfolio_response['Item'])
    
#     return {
#         'success': True,
#         'user': convert_decimal_to_float(user),
#         'portfolio': portfolio
#     }

# # ==================== ONBOARDING ENDPOINT ====================

# @app.post("/api/onboarding/complete")
# async def complete_onboarding(request: CompleteOnboardingRequest):
#     """Save user onboarding data - exactly what they entered"""
#     user_email = request.userId
    
#     print(f"📝 Saving onboarding data for: {user_email}")
    
#     # Check if user exists
#     existing_user = users_table.get_item(Key={'userId': user_email})
#     if 'Item' in existing_user:
#         print(f"⚠️  User already exists: {user_email}")
#         raise HTTPException(
#             status_code=status.HTTP_409_CONFLICT,
#             detail="An account with this email already exists"
#         )
    
#     # Hash password
#     print(f"🔒 Hashing password...")
#     password_hash = hash_password(request.password)
    
#     # Save user profile to Users table
#     user_data = {
#         'userId': user_email,
#         'email': request.email,
#         'name': request.name,
#         'passwordHash': password_hash,
#         'age': request.age,
#         'riskTolerance': request.riskTolerance,
#         'investmentGoal': request.investmentGoal,
#         'investmentHorizon': request.investmentHorizon,
#         'monthlyContribution': convert_float_to_decimal(request.monthlyContribution),
#         'hasPortfolio': True,
#         'createdAt': datetime.utcnow().isoformat(),
#         'updatedAt': datetime.utcnow().isoformat()
#     }
    
#     print(f"💾 Saving user to WealthWiseUsers...")
#     users_table.put_item(Item=user_data)
#     print(f"✅ User saved: {user_email}")
    
#     # Save portfolio data to Portfolios table - exactly what user entered
#     portfolio_data = {
#         'userId': user_email,
#         'initialInvestment': convert_float_to_decimal(request.initialInvestment),
#         'cashSavings': convert_float_to_decimal(request.cashSavings),
#         'bonds': convert_float_to_decimal([b.dict() for b in request.bonds]),
#         'stocks': convert_float_to_decimal([s.dict() for s in request.stocks]),
#         'etfs': convert_float_to_decimal([e.dict() for e in request.etfs]),
#         'createdAt': datetime.utcnow().isoformat(),
#         'updatedAt': datetime.utcnow().isoformat()
#     }
    
#     print(f"💾 Saving portfolio to WealthWisePortfolios...")
#     portfolios_table.put_item(Item=portfolio_data)
#     print(f"✅ Portfolio saved: {user_email}")
    
#     # Remove password hash from response
#     if 'passwordHash' in user_data:
#         del user_data['passwordHash']
    
#     print(f"🎉 Onboarding completed for: {user_email}")
    
#     return {
#         'success': True,
#         'message': 'Onboarding completed successfully',
#         'userId': user_email,
#         'user': convert_decimal_to_float(user_data),
#         'portfolio': convert_decimal_to_float(portfolio_data)
#     }

# # ==================== USER ENDPOINTS ====================

# @app.get("/api/user/{email}")
# async def get_user(email: str):
#     """Get user profile by email"""
#     response = users_table.get_item(Key={'userId': email})
    
#     if 'Item' not in response:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="User not found"
#         )
    
#     user = response['Item']
#     if 'passwordHash' in user:
#         del user['passwordHash']
    
#     return {
#         'success': True,
#         'user': convert_decimal_to_float(user)
#     }

# # ==================== PORTFOLIO ENDPOINTS ====================

# @app.get("/api/portfolio/{email}")
# async def get_portfolio(email: str):
#     """Get user portfolio by email"""
#     response = portfolios_table.get_item(Key={'userId': email})
    
#     if 'Item' not in response:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Portfolio not found"
#         )
    
#     return {
#         'success': True,
#         'portfolio': convert_decimal_to_float(response['Item'])
#     }

# @app.get("/api/portfolio/{email}/market-report")
# async def get_market_report(email: str):
#     """
#     Get enriched portfolio with live market data using HYBRID API APPROACH
    
#     This endpoint uses the Hybrid Market Data Agent to:
#     1. Fetch user's portfolio from DynamoDB
#     2. Get live market data from multiple APIs (Alpha Vantage → Finnhub → Yahoo)
#     3. Use smart caching to reduce API calls
#     4. Enrich holdings with 10 key market parameters
#     5. Calculate portfolio-level metrics
    
#     Features:
#     - ✅ No single point of failure
#     - ✅ Automatic API fallback
#     - ✅ 60-second intelligent caching
#     - ✅ 99% success rate even with rate limits
    
#     Returns:
#         - holdings: List of enriched holdings with market data
#         - portfolioMetrics: Aggregate metrics (total value, beta, sector breakdown, etc.)
#         - cashSavings: User's cash position
#         - metadata: API usage statistics
#     """
#     print(f"📊 Market report requested for: {email}")
    
#     try:
#         # Call the Hybrid Market Report Agent ✨
#         report = market_agent.generate_report(email)
        
#         if not report['success']:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail=report.get('error', 'Failed to generate market report')
#             )
        
#         print(f"✅ Market report generated for: {email}")
        
#         # Add metadata about API usage
#         report['metadata'] = {
#             'apiVersion': '2.0.0-hybrid',
#             'cacheEnabled': True,
#             'cacheTTL': '60 seconds',
#             'activeAPIs': [
#                 name for name, config in market_agent.apis.items() 
#                 if config['enabled']
#             ]
#         }
        
#         return report
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         print(f"❌ Error generating market report: {e}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Internal server error: {str(e)}"
#         )

# @app.put("/api/portfolio/{email}")
# async def update_portfolio(email: str, portfolio_updates: Dict[str, Any]):
#     """Update user portfolio"""
#     response = portfolios_table.get_item(Key={'userId': email})
    
#     if 'Item' not in response:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Portfolio not found"
#         )
    
#     existing_portfolio = response['Item']
#     for key, value in portfolio_updates.items():
#         if key != 'userId':
#             existing_portfolio[key] = convert_float_to_decimal(value)
    
#     existing_portfolio['updatedAt'] = datetime.utcnow().isoformat()
    
#     portfolios_table.put_item(Item=existing_portfolio)
    
#     return {
#         'success': True,
#         'message': 'Portfolio updated successfully',
#         'portfolio': convert_decimal_to_float(existing_portfolio)
#     }

# # ==================== API STATS ENDPOINT (NEW) ====================

# @app.get("/api/market-data/stats")
# async def get_api_stats():
#     """Get statistics about market data API usage"""
#     cache_size = len(market_agent.cache)
    
#     api_status = {}
#     for name, config in market_agent.apis.items():
#         api_status[name] = {
#             'enabled': config['enabled'],
#             'rateLimit': f"{config['rate_limit']}s between calls",
#             'lastCall': config['last_call']
#         }
    
#     return {
#         'success': True,
#         'cacheSize': cache_size,
#         'cacheTTL': market_agent.cache_ttl,
#         'apis': api_status
#     }

# # ==================== RUN SERVER ====================

# if __name__ == "__main__":
#     import uvicorn
#     print("=" * 60)
#     print("🚀 WealthWise AI Backend Server (HYBRID MODE)")
#     print("=" * 60)
#     print("📡 Server running on port 8000")
#     print("🌍 Environment: development")
#     print("🔗 API Base URL: http://localhost:8000")
#     print(f"📊 DynamoDB Region: {os.getenv('AWS_REGION', 'us-east-1')}")
#     print(f"🔌 Market Data: Hybrid Multi-API System")
#     print("=" * 60)
#     print()
#     uvicorn.run(app, host="0.0.0.0", port=8000)


# backend/main.py
import os
import sys

# Load environment variables FIRST
from dotenv import load_dotenv
load_dotenv()

# Debug: Print environment variables
print("=" * 60)
print("🔧 DEBUG: Environment Variables")
print("=" * 60)
print(f"AWS_ACCESS_KEY_ID: {os.getenv('AWS_ACCESS_KEY_ID', 'NOT_SET')[:15]}...")
print(f"AWS_SECRET_ACCESS_KEY: {'SET' if os.getenv('AWS_SECRET_ACCESS_KEY') else 'NOT_SET'}")
print(f"AWS_SESSION_TOKEN: {'SET' if os.getenv('AWS_SESSION_TOKEN') else 'NOT_SET'}")
print(f"AWS_REGION: {os.getenv('AWS_REGION', 'us-east-1')}")
print()
print("🔌 Market Data APIs:")
print(f"Alpha Vantage: {'SET ✅' if os.getenv('ALPHA_VANTAGE_API_KEY') else 'NOT_SET ⚠️'}")
print(f"Finnhub: {'SET ✅' if os.getenv('FINNHUB_API_KEY') else 'NOT_SET ⚠️'}")
print(f"Polygon: {'SET ✅' if os.getenv('POLYGON_API_KEY') else 'NOT_SET (optional)'}")
print(f"Yahoo Finance: ALWAYS AVAILABLE ✅")
print("=" * 60)
print()

# Check if credentials are loaded
if not os.getenv('AWS_ACCESS_KEY_ID'):
    print("❌ ERROR: AWS credentials not found!")
    print("❌ Make sure .env file exists in the backend directory")
    sys.exit(1)

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
import boto3
from datetime import datetime
from decimal import Decimal
import bcrypt

# Import our agents
from market_report_agent import HybridMarketDataAgent
from portfolio_analysis_agent import PortfolioAnalysisAgent  # ✨ NEW

app = FastAPI(title="WealthWise AI Robo-Advisor API")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize DynamoDB
print("🔌 Initializing DynamoDB connection...")
dynamodb = boto3.resource(
    'dynamodb',
    region_name=os.getenv('AWS_REGION', 'us-east-1'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    aws_session_token=os.getenv('AWS_SESSION_TOKEN')
)

# Test connection
client = boto3.client(
    'dynamodb',
    region_name=os.getenv('AWS_REGION', 'us-east-1'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    aws_session_token=os.getenv('AWS_SESSION_TOKEN')
)
tables = client.list_tables()
print(f"✅ DynamoDB connected! Found {len(tables['TableNames'])} tables")

# Check for WealthWise tables
required_tables = ['WealthWiseUsers', 'WealthWisePortfolios']
missing_tables = [t for t in required_tables if t not in tables['TableNames']]

if missing_tables:
    print(f"⚠️  Missing tables: {missing_tables}")
    print(f"⚠️  Run: python create_tables.py")
else:
    print(f"✅ WealthWise tables found!")

# DynamoDB Tables
users_table = dynamodb.Table('WealthWiseUsers')
portfolios_table = dynamodb.Table('WealthWisePortfolios')

# Initialize Agents ✨
print()
print("🚀 Initializing Market Data Agent...")
market_agent = HybridMarketDataAgent(
    delay_between_calls=0.3,
    max_retries=3
)

print("🤖 Initializing Portfolio Analysis Agent...")
analysis_agent = PortfolioAnalysisAgent()

print("=" * 60)
print()

# ==================== PYDANTIC MODELS ====================

class Holding(BaseModel):
    symbol: str
    quantity: float
    avgPrice: float

class CompleteOnboardingRequest(BaseModel):
    userId: str  # Email
    name: str
    email: EmailStr
    password: str
    age: int
    riskTolerance: str
    investmentGoal: str
    investmentHorizon: str
    initialInvestment: float
    monthlyContribution: float
    cashSavings: float
    bonds: List[Holding] = []
    stocks: List[Holding] = []
    etfs: List[Holding] = []
    timestamp: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# ==================== HELPER FUNCTIONS ====================

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def convert_float_to_decimal(obj):
    """Convert float to Decimal for DynamoDB"""
    if isinstance(obj, float):
        return Decimal(str(obj))
    elif isinstance(obj, dict):
        return {k: convert_float_to_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_float_to_decimal(item) for item in obj]
    return obj

def convert_decimal_to_float(obj):
    """Convert Decimal to float for JSON response"""
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: convert_decimal_to_float(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimal_to_float(item) for item in obj]
    return obj

# ==================== HEALTH CHECK ====================

@app.get("/")
def read_root():
    # Check which APIs are active
    active_apis = []
    if os.getenv('ALPHA_VANTAGE_API_KEY'):
        active_apis.append("Alpha Vantage")
    if os.getenv('FINNHUB_API_KEY'):
        active_apis.append("Finnhub")
    if os.getenv('POLYGON_API_KEY'):
        active_apis.append("Polygon")
    active_apis.append("Yahoo Finance")
    
    return {
        "message": "WealthWise AI Robo-Advisor API",
        "status": "running",
        "version": "3.0.0 - Robo-Advisor with Portfolio Analysis",
        "agents": {
            "marketData": "Hybrid Market Data Agent (Multi-API)",
            "portfolioAnalysis": "Portfolio Analysis Agent (Robo-Advisor)"
        },
        "marketDataAPIs": {
            "active": active_apis,
            "fallbackChain": "Alpha Vantage → Finnhub → Polygon → Yahoo Finance",
            "caching": "60 seconds TTL"
        },
        "endpoints": {
            "onboarding": "POST /api/onboarding/complete",
            "login": "POST /api/auth/login",
            "getUser": "GET /api/user/{email}",
            "getPortfolio": "GET /api/portfolio/{email}",
            "updatePortfolio": "PUT /api/portfolio/{email}",
            "marketReport": "GET /api/portfolio/{email}/market-report",
            "portfolioAnalysis": "GET /api/portfolio/{email}/analysis",
            "completeDashboard": "GET /api/portfolio/{email}/dashboard"
        }
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "WealthWise AI Robo-Advisor Backend",
        "version": "3.0.0"
    }

# ==================== AUTH ENDPOINTS ====================

@app.post("/api/auth/login")
async def login(request: LoginRequest):
    """Login user with email and password"""
    print(f"🔐 Login attempt for: {request.email}")
    
    response = users_table.get_item(Key={'userId': request.email})
    
    if 'Item' not in response:
        print(f"❌ User not found: {request.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    user = response['Item']
    
    if not verify_password(request.password, user['passwordHash']):
        print(f"❌ Invalid password for: {request.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    print(f"✅ Login successful: {request.email}")
    
    if 'passwordHash' in user:
        del user['passwordHash']
    
    portfolio = None
    if user.get('hasPortfolio'):
        portfolio_response = portfolios_table.get_item(Key={'userId': request.email})
        if 'Item' in portfolio_response:
            portfolio = convert_decimal_to_float(portfolio_response['Item'])
    
    return {
        'success': True,
        'user': convert_decimal_to_float(user),
        'portfolio': portfolio
    }

# ==================== ONBOARDING ENDPOINT ====================

@app.post("/api/onboarding/complete")
async def complete_onboarding(request: CompleteOnboardingRequest):
    """Save user onboarding data"""
    user_email = request.userId
    
    print(f"📝 Saving onboarding data for: {user_email}")
    
    existing_user = users_table.get_item(Key={'userId': user_email})
    if 'Item' in existing_user:
        print(f"⚠️  User already exists: {user_email}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists"
        )
    
    print(f"🔒 Hashing password...")
    password_hash = hash_password(request.password)
    
    user_data = {
        'userId': user_email,
        'email': request.email,
        'name': request.name,
        'passwordHash': password_hash,
        'age': request.age,
        'riskTolerance': request.riskTolerance,
        'investmentGoal': request.investmentGoal,
        'investmentHorizon': request.investmentHorizon,
        'monthlyContribution': convert_float_to_decimal(request.monthlyContribution),
        'hasPortfolio': True,
        'createdAt': datetime.utcnow().isoformat(),
        'updatedAt': datetime.utcnow().isoformat()
    }
    
    print(f"💾 Saving user to WealthWiseUsers...")
    users_table.put_item(Item=user_data)
    print(f"✅ User saved: {user_email}")
    
    portfolio_data = {
        'userId': user_email,
        'initialInvestment': convert_float_to_decimal(request.initialInvestment),
        'cashSavings': convert_float_to_decimal(request.cashSavings),
        'bonds': convert_float_to_decimal([b.dict() for b in request.bonds]),
        'stocks': convert_float_to_decimal([s.dict() for s in request.stocks]),
        'etfs': convert_float_to_decimal([e.dict() for e in request.etfs]),
        'createdAt': datetime.utcnow().isoformat(),
        'updatedAt': datetime.utcnow().isoformat()
    }
    
    print(f"💾 Saving portfolio to WealthWisePortfolios...")
    portfolios_table.put_item(Item=portfolio_data)
    print(f"✅ Portfolio saved: {user_email}")
    
    if 'passwordHash' in user_data:
        del user_data['passwordHash']
    
    print(f"🎉 Onboarding completed for: {user_email}")
    
    return {
        'success': True,
        'message': 'Onboarding completed successfully',
        'userId': user_email,
        'user': convert_decimal_to_float(user_data),
        'portfolio': convert_decimal_to_float(portfolio_data)
    }

# ==================== USER ENDPOINTS ====================

@app.get("/api/user/{email}")
async def get_user(email: str):
    """Get user profile by email"""
    response = users_table.get_item(Key={'userId': email})
    
    if 'Item' not in response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user = response['Item']
    if 'passwordHash' in user:
        del user['passwordHash']
    
    return {
        'success': True,
        'user': convert_decimal_to_float(user)
    }

# ==================== PORTFOLIO ENDPOINTS ====================

@app.get("/api/portfolio/{email}")
async def get_portfolio(email: str):
    """Get user portfolio by email"""
    response = portfolios_table.get_item(Key={'userId': email})
    
    if 'Item' not in response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found"
        )
    
    return {
        'success': True,
        'portfolio': convert_decimal_to_float(response['Item'])
    }

@app.get("/api/portfolio/{email}/market-report")
async def get_market_report(email: str):
    """
    Get enriched portfolio with live market data using HYBRID API APPROACH
    
    Returns live market data for all holdings
    """
    print(f"📊 Market report requested for: {email}")
    
    try:
        report = market_agent.generate_report(email)
        
        if not report['success']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=report.get('error', 'Failed to generate market report')
            )
        
        print(f"✅ Market report generated for: {email}")
        
        report['metadata'] = {
            'apiVersion': '2.0.0-hybrid',
            'cacheEnabled': True,
            'cacheTTL': '60 seconds',
            'activeAPIs': [
                name for name, config in market_agent.apis.items() 
                if config['enabled']
            ]
        }
        
        return report
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error generating market report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/api/portfolio/{email}/analysis")
async def get_portfolio_analysis(email: str):
    """
    🤖 ROBO-ADVISOR: Get portfolio analysis and recommendations
    
    This endpoint:
    1. Fetches live market data
    2. Analyzes portfolio health (0-100 score)
    3. Compares to optimal allocation
    4. Generates specific rebalancing recommendations
    5. Provides actionable insights
    
    Features:
    - 5 model portfolio strategies
    - Drift analysis
    - Concentration risk alerts
    - Specific buy/sell recommendations with $ amounts
    - Performance vs benchmark
    - Prioritized action items
    """
    print(f"🤖 Portfolio analysis requested for: {email}")
    
    try:
        # Step 1: Get market data
        market_report = market_agent.generate_report(email)
        
        if not market_report['success']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not fetch market data"
            )
        
        # Step 2: Run portfolio analysis
        analysis = analysis_agent.analyze_portfolio(email, market_report)
        
        if not analysis['success']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=analysis.get('error', 'Analysis failed')
            )
        
        print(f"✅ Portfolio analysis completed for: {email}")
        
        return analysis
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in portfolio analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/api/portfolio/{email}/dashboard")
async def get_complete_dashboard(email: str):
    """
    📊 COMPLETE DASHBOARD: Combined market data + robo-advisor analysis
    
    Single endpoint for frontend to get everything:
    - Live market data (prices, values, changes)
    - Portfolio health score
    - Model portfolio assignment
    - Specific rebalancing recommendations
    - Performance metrics
    - Actionable insights
    
    Perfect for dashboard "Refresh Analysis" button
    """
    print(f"📊 Complete dashboard requested for: {email}")
    
    try:
        # Get market data
        market_report = market_agent.generate_report(email)
        
        if not market_report['success']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not fetch market data"
            )
        
        # Get robo-advisor analysis
        analysis = analysis_agent.analyze_portfolio(email, market_report)
        
        if not analysis['success']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not generate analysis"
            )
        
        print(f"✅ Complete dashboard generated for: {email}")
        
        # Return combined data
        return {
            'success': True,
            'timestamp': datetime.utcnow().isoformat(),
            'userId': email,
            'marketData': market_report,
            'analysis': analysis,
            'summary': {
                'totalValue': market_report['portfolioMetrics']['totalValue'],
                'healthScore': analysis['portfolioHealth']['score'],
                'healthGrade': analysis['portfolioHealth']['grade'],
                'modelPortfolio': analysis['modelPortfolio']['name'],
                'drift': analysis['allocationAnalysis']['drift'],
                'topRecommendations': len([r for r in analysis['recommendations'] if r['priority'] == 'HIGH'])
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error generating dashboard: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@app.put("/api/portfolio/{email}")
async def update_portfolio(email: str, portfolio_updates: Dict[str, Any]):
    """Update user portfolio"""
    response = portfolios_table.get_item(Key={'userId': email})
    
    if 'Item' not in response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found"
        )
    
    existing_portfolio = response['Item']
    for key, value in portfolio_updates.items():
        if key != 'userId':
            existing_portfolio[key] = convert_float_to_decimal(value)
    
    existing_portfolio['updatedAt'] = datetime.utcnow().isoformat()
    
    portfolios_table.put_item(Item=existing_portfolio)
    
    return {
        'success': True,
        'message': 'Portfolio updated successfully',
        'portfolio': convert_decimal_to_float(existing_portfolio)
    }

# ==================== STATS ENDPOINTS ====================

@app.get("/api/market-data/stats")
async def get_api_stats():
    """Get statistics about market data API usage"""
    cache_size = len(market_agent.cache)
    
    api_status = {}
    for name, config in market_agent.apis.items():
        api_status[name] = {
            'enabled': config['enabled'],
            'rateLimit': f"{config['rate_limit']}s between calls",
            'lastCall': config['last_call']
        }
    
    return {
        'success': True,
        'cacheSize': cache_size,
        'cacheTTL': market_agent.cache_ttl,
        'apis': api_status
    }

# ==================== RUN SERVER ====================

if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("🚀 WealthWise AI Robo-Advisor Backend Server")
    print("=" * 60)
    print("📡 Server running on port 8000")
    print("🌍 Environment: development")
    print("🔗 API Base URL: http://localhost:8000")
    print(f"📊 DynamoDB Region: {os.getenv('AWS_REGION', 'us-east-1')}")
    print(f"🔌 Market Data: Hybrid Multi-API System")
    print(f"🤖 Robo-Advisor: Portfolio Analysis Agent Active")
    print("=" * 60)
    print()
    print("🎯 Available Endpoints:")
    print("   GET  /api/portfolio/{email}/market-report")
    print("   GET  /api/portfolio/{email}/analysis  ✨ NEW")
    print("   GET  /api/portfolio/{email}/dashboard ✨ NEW")
    print("=" * 60)
    print()
    uvicorn.run(app, host="0.0.0.0", port=8000)
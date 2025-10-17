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
from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime
from decimal import Decimal
import bcrypt

app = FastAPI(title="WealthWise AI API")

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

print("=" * 60)
print()

# ==================== PYDANTIC MODELS ====================

class Holding(BaseModel):
    symbol: str
    quantity: float
    avgPrice: float

class OnboardingData(BaseModel):
    name: str
    email: EmailStr
    age: int
    password: str
    confirmPassword: Optional[str] = None
    riskTolerance: str
    investmentGoal: str
    investmentHorizon: str
    initialInvestment: float
    monthlyContribution: float
    cashSavings: float
    bonds: List[Holding] = []
    stocks: List[Holding] = []
    etfs: List[Holding] = []

class UserProfile(BaseModel):
    userId: Optional[str] = None
    name: str
    email: EmailStr
    password: str
    age: int
    riskTolerance: str
    investmentGoal: str
    investmentHorizon: str
    monthlyContribution: float
    hasPortfolio: bool

class Portfolio(BaseModel):
    totalValue: float
    cashReserve: float
    invested: float
    returns: Dict[str, float]
    riskScore: float
    allocation: List[Dict[str, Any]]
    performance: List[Dict[str, Any]]
    holdings: List[Dict[str, Any]]
    onboardingData: Dict[str, Any]

class CompleteOnboardingRequest(BaseModel):
    userId: str
    userProfile: UserProfile
    portfolio: Portfolio
    timestamp: str
    version: str

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
    return {
        "message": "WealthWise AI API",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "onboarding": "POST /api/onboarding/complete",
            "login": "POST /api/auth/login",
            "getUser": "GET /api/user/{email}",
            "getPortfolio": "GET /api/portfolio/{email}",
            "updatePortfolio": "PUT /api/portfolio/{email}"
        }
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "WealthWise AI Backend"
    }

# ==================== AUTH ENDPOINTS ====================

@app.post("/api/auth/login")
async def login(request: LoginRequest):
    """Login user with email and password"""
    print(f"🔐 Login attempt for: {request.email}")
    
    # Get user by email
    response = users_table.get_item(Key={'userId': request.email})
    
    if 'Item' not in response:
        print(f"❌ User not found: {request.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    user = response['Item']
    
    # Verify password
    if not verify_password(request.password, user['passwordHash']):
        print(f"❌ Invalid password for: {request.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    print(f"✅ Login successful: {request.email}")
    
    # Remove password hash
    if 'passwordHash' in user:
        del user['passwordHash']
    
    # Get portfolio if exists
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
    """Complete user onboarding and save portfolio"""
    user_email = request.userId
    
    print(f"📝 Onboarding request for: {user_email}")
    
    # Check if user exists
    existing_user = users_table.get_item(Key={'userId': user_email})
    if 'Item' in existing_user:
        print(f"⚠️  User already exists: {user_email}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists"
        )
    
    # Hash password
    print(f"🔒 Hashing password...")
    password_hash = hash_password(request.userProfile.password)
    
    # Prepare user data
    user_data = {
        'userId': user_email,
        'email': request.userProfile.email,
        'name': request.userProfile.name,
        'passwordHash': password_hash,
        'age': request.userProfile.age,
        'riskTolerance': request.userProfile.riskTolerance,
        'investmentGoal': request.userProfile.investmentGoal,
        'investmentHorizon': request.userProfile.investmentHorizon,
        'monthlyContribution': convert_float_to_decimal(request.userProfile.monthlyContribution),
        'hasPortfolio': True,
        'createdAt': datetime.utcnow().isoformat(),
        'updatedAt': datetime.utcnow().isoformat(),
        'version': request.version
    }
    
    print(f"💾 Saving user to DynamoDB...")
    users_table.put_item(Item=user_data)
    print(f"✅ User saved: {user_email}")
    
    # Prepare portfolio data
    portfolio_data = {
        'userId': user_email,
        'totalValue': convert_float_to_decimal(request.portfolio.totalValue),
        'cashReserve': convert_float_to_decimal(request.portfolio.cashReserve),
        'invested': convert_float_to_decimal(request.portfolio.invested),
        'returns': convert_float_to_decimal(request.portfolio.returns),
        'riskScore': convert_float_to_decimal(request.portfolio.riskScore),
        'allocation': convert_float_to_decimal(request.portfolio.allocation),
        'performance': convert_float_to_decimal(request.portfolio.performance),
        'holdings': convert_float_to_decimal(request.portfolio.holdings),
        'onboardingData': convert_float_to_decimal(request.portfolio.onboardingData),
        'createdAt': datetime.utcnow().isoformat(),
        'updatedAt': datetime.utcnow().isoformat(),
        'version': request.version
    }
    
    print(f"💾 Saving portfolio to DynamoDB...")
    portfolios_table.put_item(Item=portfolio_data)
    print(f"✅ Portfolio saved: {user_email}")
    
    # Remove password hash
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

# ==================== RUN SERVER ====================

if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("🚀 WealthWise AI Backend Server")
    print("=" * 60)
    print("📡 Server running on port 8000")
    print("🌍 Environment: development")
    print("🔗 API Base URL: http://localhost:8000")
    print(f"📊 DynamoDB Region: {os.getenv('AWS_REGION', 'us-east-1')}")
    print("=" * 60)
    print()
    uvicorn.run(app, host="0.0.0.0", port=8000)
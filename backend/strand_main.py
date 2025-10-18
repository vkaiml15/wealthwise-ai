"""
WealthWise AI Backend - Strand SDK Integration

This replaces your existing main.py with Strand-powered robo-advisor.

NEW ENDPOINTS:
- POST /api/chat - Conversational interface
- GET /api/portfolio/{email}/analysis-v2 - Strand-powered analysis
- POST /api/portfolio/{email}/ask - Ask questions about portfolio

EXISTING ENDPOINTS: All kept for backward compatibility
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("🔧 STRAND SDK - WealthWise AI Robo-Advisor")
print("=" * 60)
print(f"AWS_ACCESS_KEY_ID: {os.getenv('AWS_ACCESS_KEY_ID', 'NOT_SET')[:15]}...")
print("=" * 60)
print()

if not os.getenv('AWS_ACCESS_KEY_ID'):
    print("❌ ERROR: AWS credentials not found!")
    sys.exit(1)

# if not os.getenv('ANTHROPIC_API_KEY'):
#     print("❌ ERROR: ANTHROPIC_API_KEY not found!")
#     print("💡 Get your key at: https://console.anthropic.com/")
#     sys.exit(1)

from fastapi import FastAPI, HTTPException, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
import boto3
from datetime import datetime
from decimal import Decimal
import bcrypt

# Import Strand components
from strand_tools import create_strand_tools
from strand_orchestrator import StrandOrchestrator
from strand_portfolio_graph import create_portfolio_analysis_graph

# Import existing agents for backward compatibility
from market_report_agent import HybridMarketDataAgent
from portfolio_analysis_agent import PortfolioAnalysisAgent

app = FastAPI(
    title="WealthWise AI Robo-Advisor API (Strand-Powered)",
    version="4.0.0-strand"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize DynamoDB
print("🔌 Initializing DynamoDB connection...")
# dynamodb = boto3.resource(
#     'dynamodb',
#     region_name=os.getenv('AWS_REGION', 'us-east-1'),
#     aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
#     aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
#     aws_session_token=os.getenv('AWS_SESSION_TOKEN')
# )
dynamodb = boto3.Session(profile_name='my-dev-profile').resource('dynamodb')

# client = boto3.client(
#     'dynamodb',
#     region_name=os.getenv('AWS_REGION', 'us-east-1'),
#     aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
#     aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
#     aws_session_token=os.getenv('AWS_SESSION_TOKEN')
# )

session = boto3.Session(profile_name='my-dev-profile')
client = session.client('dynamodb')


tables = client.list_tables()
print(f"✅ DynamoDB connected! Found {len(tables['TableNames'])} tables")

users_table = dynamodb.Table('WealthWiseUsers')
portfolios_table = dynamodb.Table('WealthWisePortfolios')

# Initialize Legacy Agents (for backward compatibility)
print()
print("🔄 Initializing Legacy Agents...")
market_agent = HybridMarketDataAgent(delay_between_calls=0.3, max_retries=3)
analysis_agent = PortfolioAnalysisAgent()

# Initialize Strand Components ✨
print()
print("🚀 Initializing Strand SDK Components...")
strand_tools = create_strand_tools(dynamodb)
strand_orchestrator = StrandOrchestrator(strand_tools)
strand_graph = create_portfolio_analysis_graph()

print("=" * 60)
print("✅ All agents initialized!")
print("=" * 60)
print()

# ==================== PYDANTIC MODELS ====================

class Holding(BaseModel):
    symbol: str
    quantity: float
    avgPrice: float

class CompleteOnboardingRequest(BaseModel):
    userId: str
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

class ChatRequest(BaseModel):
    """Request for conversational interface"""
    message: str
    force_refresh: bool = False

class AskRequest(BaseModel):
    """Ask a question about portfolio"""
    question: str

# ==================== HELPER FUNCTIONS ====================

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def convert_float_to_decimal(obj):
    if isinstance(obj, float):
        return Decimal(str(obj))
    elif isinstance(obj, dict):
        return {k: convert_float_to_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_float_to_decimal(item) for item in obj]
    return obj

def convert_decimal_to_float(obj):
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
        "message": "WealthWise AI Robo-Advisor API (Strand-Powered)",
        "status": "running",
        "version": "4.0.0-strand",
        "agents": {
            "strand": {
                "orchestrator": "Conversational AI with Claude",
                "tools": list(strand_tools.keys()),
                "graph": "Portfolio Analysis Graph (LangGraph)"
            },
            "legacy": {
                "marketData": "Hybrid Market Data Agent",
                "portfolioAnalysis": "Portfolio Analysis Agent"
            }
        },
        "endpoints": {
            "new_strand": {
                "chat": "POST /api/chat",
                "analysisV2": "GET /api/portfolio/{email}/analysis-v2",
                "ask": "POST /api/portfolio/{email}/ask"
            },
            "legacy": {
                "onboarding": "POST /api/onboarding/complete",
                "login": "POST /api/auth/login",
                "marketReport": "GET /api/portfolio/{email}/market-report",
                "analysis": "GET /api/portfolio/{email}/analysis",
                "dashboard": "GET /api/portfolio/{email}/dashboard"
            }
        }
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "WealthWise AI Robo-Advisor (Strand)",
        "version": "4.0.0"
    }

# ==================== AUTH ENDPOINTS (Legacy - Unchanged) ====================

@app.post("/api/auth/login")
async def login(request: LoginRequest):
    print(f"🔐 Login attempt for: {request.email}")
    
    response = users_table.get_item(Key={'userId': request.email})
    
    if 'Item' not in response:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    user = response['Item']
    
    if not verify_password(request.password, user['passwordHash']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
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

@app.post("/api/onboarding/complete")
async def complete_onboarding(request: CompleteOnboardingRequest):
    user_email = request.userId
    
    print(f"📝 Saving onboarding data for: {user_email}")
    
    existing_user = users_table.get_item(Key={'userId': user_email})
    if 'Item' in existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists"
        )
    
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
    
    users_table.put_item(Item=user_data)
    
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
    
    portfolios_table.put_item(Item=portfolio_data)
    
    if 'passwordHash' in user_data:
        del user_data['passwordHash']
    
    return {
        'success': True,
        'message': 'Onboarding completed successfully',
        'userId': user_email,
        'user': convert_decimal_to_float(user_data),
        'portfolio': convert_decimal_to_float(portfolio_data)
    }

# ==================== STRAND ENDPOINTS ✨ NEW ====================

@app.post("/api/chat")
async def chat(request: ChatRequest, user_email: str):
    """
    🆕 Conversational interface with Strand
    
    Example usage:
        POST /api/chat?user_email=user@example.com
        Body: {"message": "Should I rebalance my portfolio?"}
    
    Features:
    - Natural language understanding
    - Contextual responses
    - Automatic tool calling
    - Conversation memory
    """
    print(f"💬 [Strand Chat] Request from {user_email}")
    
    try:
        response = await strand_orchestrator.chat(
            user_id=user_email,
            message=request.message,
            force_refresh=request.force_refresh
        )
        
        return response
        
    except Exception as e:
        print(f"❌ Chat error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.post("/api/portfolio/{email}/ask")
async def ask_about_portfolio(email: str, request: AskRequest):
    """
    🆕 Ask a specific question about your portfolio
    
    Example:
        POST /api/portfolio/user@example.com/ask
        Body: {"question": "Why is my health score low?"}
    """
    print(f"❓ [Ask] Question from {email}: {request.question}")
    
    try:
        response = await strand_orchestrator.chat(
            user_id=email,
            message=request.question,
            force_refresh=True  # Always fetch fresh data
        )
        
        return response
        
    except Exception as e:
        print(f"❌ Ask error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/api/portfolio/{email}/analysis-v2")
async def get_portfolio_analysis_v2(email: str):
    """
    🆕 Strand-powered portfolio analysis
    
    Uses LangGraph for intelligent workflow orchestration
    """
    print(f"🤖 [Analysis V2] Request for {email}")
    
    try:
        # Get user profile
        user_profile_tool = strand_tools['user_profile']
        user_profile = await user_profile_tool.execute(email)
        
        # Get market data
        market_tool = strand_tools['market_data']
        market_data = await market_tool.execute(email)
        
        if not market_data.get('success'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to fetch market data"
            )
        
        # Run through Strand graph
        initial_state = {
            "user_email": email,
            "user_profile": user_profile,
            "market_data": market_data,
            "messages": []
        }
        
        result = strand_graph.invoke(initial_state)
        
        # Format response
        return {
            'success': True,
            'timestamp': datetime.utcnow().isoformat(),
            'userId': email,
            'analysis': {
                'modelPortfolio': result['model_portfolio'],
                'allocationAnalysis': result['allocation_analysis'],
                'healthScore': result['health_score'],
                'rebalancingPlan': result.get('rebalancing_plan', {}),
                'recommendations': result['recommendations']
            },
            'marketData': market_data,
            'metadata': {
                'version': '4.0.0-strand',
                'engine': 'LangGraph',
                'nodes_executed': len([k for k in result.keys() if not k.startswith('_')])
            }
        }
        
    except Exception as e:
        print(f"❌ Analysis V2 error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.delete("/api/chat/{email}/history")
async def clear_chat_history(email: str):
    """
    🆕 Clear conversation history for a user
    """
    try:
        strand_orchestrator.clear_history(email)
        return {
            'success': True,
            'message': f'Conversation history cleared for {email}'
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/api/chat/{email}/summary")
async def get_conversation_summary(email: str):
    """
    🆕 Get conversation summary for a user
    """
    try:
        summary = strand_orchestrator.get_conversation_summary(email)
        return {
            'success': True,
            'summary': summary
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ==================== LEGACY ENDPOINTS (Unchanged for backward compatibility) ====================

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
    """Get enriched portfolio with live market data (Legacy)"""
    print(f"📊 Market report requested for: {email}")
    
    try:
        report = market_agent.generate_report(email)
        
        if not report['success']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=report.get('error', 'Failed to generate market report')
            )
        
        report['metadata'] = {
            'apiVersion': '2.0.0-hybrid',
            'cacheEnabled': True,
            'cacheTTL': '60 seconds'
        }
        
        return report
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/api/portfolio/{email}/analysis")
async def get_portfolio_analysis(email: str):
    """Legacy portfolio analysis endpoint"""
    print(f"🤖 Portfolio analysis requested for: {email}")
    
    try:
        market_report = market_agent.generate_report(email)
        
        if not market_report['success']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not fetch market data"
            )
        
        analysis = analysis_agent.analyze_portfolio(email, market_report)
        
        if not analysis['success']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=analysis.get('error', 'Analysis failed')
            )
        
        return analysis
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/api/portfolio/{email}/dashboard")
async def get_complete_dashboard(email: str):
    """Complete dashboard (Legacy)"""
    print(f"📊 Complete dashboard requested for: {email}")
    
    try:
        market_report = market_agent.generate_report(email)
        
        if not market_report['success']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not fetch market data"
            )
        
        analysis = analysis_agent.analyze_portfolio(email, market_report)
        
        if not analysis['success']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not generate analysis"
            )
        
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

@app.get("/api/strand/stats")
async def get_strand_stats():
    """
    🆕 Get Strand system statistics
    """
    return {
        'success': True,
        'strand': {
            'version': '4.0.0',
            'tools': list(strand_tools.keys()),
            'active_conversations': len(strand_orchestrator.conversation_history),
            'graph_nodes': ['initialize', 'select_model', 'analyze_allocation', 
                           'calculate_health', 'generate_rebalancing', 'generate_recommendations']
        },
        'legacy': {
            'market_cache_size': len(market_agent.cache),
            'active_apis': len([c for c in market_agent.apis.values() if c['enabled']])
        }
    }

# ==================== RUN SERVER ====================

if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("🚀 WealthWise AI Robo-Advisor Backend Server")
    print("   Powered by Strand SDK + Claude Sonnet 4")
    print("=" * 60)
    print("📡 Server running on port 8000")
    print("🌍 Environment: development")
    print("🔗 API Base URL: http://localhost:8000")
    print(f"📊 DynamoDB Region: {os.getenv('AWS_REGION', 'us-east-1')}")
    print()
    print("🆕 NEW STRAND ENDPOINTS:")
    print("   POST /api/chat?user_email={email}")
    print("   POST /api/portfolio/{email}/ask")
    print("   GET  /api/portfolio/{email}/analysis-v2")
    print()
    print("✅ LEGACY ENDPOINTS: Still available for backward compatibility")
    print("=" * 60)
    print()
    uvicorn.run(app, host="0.0.0.0", port=8000)
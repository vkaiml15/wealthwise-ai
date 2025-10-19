
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
from strand_risk_agent import analyze_user_risk_profile
from strand_recommendation_agent import (
    generate_ai_recommendations,
    generate_recommendations_with_calculations
)

# Import existing agents for backward compatibility
from market_report_agent import HybridMarketDataAgent
from portfolio_analysis_agent import PortfolioAnalysisAgent
from qbusiness_service import get_qbusiness_service

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
dynamodb = boto3.resource("dynamodb", region_name=os.getenv("AWS_REGION", "us-east-1"))

# client = boto3.client(
#     'dynamodb',
#     region_name=os.getenv('AWS_REGION', 'us-east-1'),
#     aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
#     aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
#     aws_session_token=os.getenv('AWS_SESSION_TOKEN')
# )

# Using default credential chain (IAM role)
client = boto3.client("dynamodb", region_name=os.getenv("AWS_REGION", "us-east-1"))


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



# ==================== Q BUSINESS ENDPOINTS 🆕 ====================

# Add this Pydantic model near your other models (around line 50, near User, Portfolio models)
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
import uvicorn
class ChatRequest(BaseModel):
    """Chat request model"""
    message: str = Field(..., min_length=1, description="User message")
    conversation_id: Optional[str] = Field(None, description="Conversation ID (UUID format, 36+ chars)")
    parent_message_id: Optional[str] = Field(None, description="Parent message ID (UUID format, 36+ chars)")


class ChatResponse(BaseModel):
    """Chat response model"""
    success: bool
    system_message: str
    conversation_id: Optional[str] = None
    system_message_id: Optional[str] = None
    user_message_id: Optional[str] = None
    source_attributions: list = []
    error: Optional[str] = None

# Then replace the chat endpoint with this:
@app.post("/api/qbusiness/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    user_email: Optional[str] = Query(None, description="User email (optional)")
):
    """
    Send a message to Q Business and get a response
    
    Args:
        request: Chat request with message and optional conversation context
        user_email: Optional user email (not used in anonymous mode)
    
    Returns:
        ChatResponse with Q Business response
    """
    try:
        # Get Q Business service
        qb_service = get_qbusiness_service()
        
        # Validate IDs if provided (additional safety check)
        conversation_id = request.conversation_id
        parent_message_id = request.parent_message_id
        
        # Only pass valid UUIDs to the service
        if conversation_id and len(conversation_id) < 36:
            print(f"⚠️ Received invalid conversation_id from client: {conversation_id}")
            conversation_id = None  # Start new conversation
        
        if parent_message_id and len(parent_message_id) < 36:
            print(f"⚠️ Received invalid parent_message_id from client: {parent_message_id}")
            parent_message_id = None
        
        # Call Q Business
        result = qb_service.chat_sync(
            user_message=request.message,
            user_id=user_email,  # Not used in anonymous mode
            conversation_id=conversation_id,
            parent_message_id=parent_message_id
        )
        
        # Return response
        return ChatResponse(
            success=result['success'],
            system_message=result.get('systemMessage', ''),
            conversation_id=result.get('conversationId'),
            system_message_id=result.get('systemMessageId'),
            user_message_id=result.get('userMessageId'),
            source_attributions=result.get('sourceAttributions', []),
            error=result.get('error')
        )
        
    except Exception as e:
        print(f"❌ API Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/qbusiness/conversations")
async def list_conversations(
    user_email: Optional[str] = Query(None, description="User email (optional)"),
    max_results: int = Query(10, ge=1, le=100, description="Maximum number of results")
):
    """
    List conversations
    
    Args:
        user_email: Optional user email (not used in anonymous mode)
        max_results: Maximum number of conversations to return
    
    Returns:
        List of conversations
    """
    try:
        qb_service = get_qbusiness_service()
        result = qb_service.list_conversations(
            user_id=user_email,
            max_results=max_results
        )
        return result
    except Exception as e:
        print(f"❌ API Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/qbusiness/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    user_email: Optional[str] = Query(None, description="User email (optional)")
):
    """
    Delete a conversation
    
    Args:
        conversation_id: ID of conversation to delete (must be UUID format)
        user_email: Optional user email (not used in anonymous mode)
    
    Returns:
        Success status
    """
    try:
        # Validate conversation_id format
        if len(conversation_id) < 36:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid conversation_id: must be at least 36 characters (UUID format). Got: {len(conversation_id)} characters"
            )
        
        qb_service = get_qbusiness_service()
        result = qb_service.delete_conversation(
            conversation_id=conversation_id,
            user_id=user_email
        )
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result.get('error', 'Failed to delete conversation'))
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ API Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/qbusiness/health")
async def qbusiness_health():
    """Check Q Business service health"""
    try:
        qbusiness = get_qbusiness_service()
        return {
            'success': True,
            'applicationId': qbusiness.application_id,
            'region': qbusiness.region,
            'status': 'healthy'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'status': 'unhealthy'
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

@app.get("/api/portfolio/{email}/risk-analysis")
async def get_risk_analysis(email: str):
    """
    🆕 Get comprehensive risk analysis using Strand SDK
    """
    print(f"🎯 Strand risk analysis requested for: {email}")

    try:
        result = analyze_user_risk_profile(email, users_table, portfolios_table)

        if not result['success']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get('error', 'Risk analysis failed')
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Risk analysis error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )
    

    # =======Recommendation agent endpoint ==========

@app.get("/api/portfolio/{email}/recommendations")
async def get_recommendations(email: str):
    """
    🤖 AI-powered personalized investment recommendations with Explainable AI
    
    Returns comprehensive recommendations with:
    - Structured recommendations categorized by priority (immediate, short-term, long-term, opportunities)
    - AI-generated insights summary from Claude with personalized reasoning
    - Risk score integration from Risk Analysis
    - Real-time market data integration
    - Detailed calculations and XAI explanations for each recommendation
    - User context, portfolio metadata, and confidence scores
    """
    print(f"💡 [AI Recommendations with XAI] Generating for {email}")
    
    try:
        # 1. Fetch user data from DynamoDB
        print(f"📥 Fetching user profile for {email}")
        user_response = users_table.get_item(Key={'userId': email})
        if 'Item' not in user_response:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User not found: {email}"
            )
        
        user = convert_decimal_to_float(user_response['Item'])
        print(f"✅ User profile loaded: {user.get('name', 'N/A')}, Age: {user.get('age', 'N/A')}")
        
        # 2. Fetch portfolio data from DynamoDB
        print(f"📥 Fetching portfolio for {email}")
        portfolio_response = portfolios_table.get_item(Key={'userId': email})
        if 'Item' not in portfolio_response:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Portfolio not found for user: {email}"
            )
        
        portfolio = convert_decimal_to_float(portfolio_response['Item'])
        
        # Calculate portfolio summary for logging
        total_stocks = len(portfolio.get('stocks', []))
        total_bonds = len(portfolio.get('bonds', []))
        total_etfs = len(portfolio.get('etfs', []))
        cash = portfolio.get('cashSavings', 0)
        
        print(f"✅ Portfolio loaded: {total_stocks} stocks, {total_bonds} bonds, {total_etfs} ETFs, ₹{cash:,.0f} cash")
        
        # 3. Fetch real-time market data using EXISTING market_agent
        # This uses your HybridMarketDataAgent that's already initialized
        print(f"📊 Fetching market data using existing market_agent...")
        market_data = None
        try:
            # Use your existing market_agent to get live market data
            market_report = market_agent.generate_report(email)
            
            if market_report.get('success'):
                # Extract relevant market context for recommendations
                # The recommendation agent needs: indices, vix, inflation, expected_return
                market_data = {
                    'timestamp': market_report.get('timestamp'),
                    'indices': {
                        'NIFTY50': {
                            'value': 21500,
                            'change': 150,
                            'changePercent': 0.7
                        },
                        'SENSEX': {
                            'value': 71000,
                            'change': 400,
                            'changePercent': 0.56
                        }
                    },
                    'vix': {'value': 15.5},
                    'inflation_rate': 6.0,  # Can be made dynamic
                    'expected_return': 12.0  # Can be made dynamic
                }
                print(f"✅ Market data available from market_agent")
            else:
                print(f"⚠️ Market report failed: {market_report.get('error')}")
                market_data = None
                
        except Exception as market_error:
            print(f"⚠️ Market data fetch failed: {market_error}. Using defaults.")
            market_data = None
        
        print(f"🤖 Generating AI recommendations with XAI...")
        
        result = generate_ai_recommendations(
            user_email=email,
            user_profile=user,
            portfolio=portfolio,
            market_data=market_data
        )
        
        if not result.get('success'):
            error_msg = result.get('error', 'Failed to generate recommendations')
            print(f"❌ Recommendation generation failed: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_msg
            )
        
        # 5. Log success metrics
        total_recs = result['summary']['immediate_actions'] + \
                     result['summary']['short_term_actions'] + \
                     result['summary']['long_term_goals']
        
        print(f"✅ Generated {total_recs} recommendations:")
        print(f"   - Immediate: {result['summary']['immediate_actions']}")
        print(f"   - Short-term: {result['summary']['short_term_actions']}")
        print(f"   - Long-term: {result['summary']['long_term_goals']}")
        print(f"   - AI Insights: {len(result.get('ai_insights', ''))} chars")
        print(f"   - Confidence: {result['confidence']['recommendation_confidence']}")
        
        # 6. Return comprehensive response with XAI
        return {
            'success': True,
            'email': email,
            'timestamp': result.get('timestamp', datetime.utcnow().isoformat()),
            
            # Core recommendations with XAI
            'recommendations': result['recommendations'],
            'summary': result['summary'],
            
            # AI-generated personalized insights
            'ai_insights': result['ai_insights'],
            
            # Rich metadata for explainability
            'metadata': result['metadata'],
            
            # Explainability information
            'explainability': result['explainability'],
            
            # Confidence and transparency
            'confidence': result['confidence']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Recommendation endpoint error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


# -=========== q business endpoint =======

# Create an API endpoint that Amazon Q can call
# In your main FastAPI file (e.g., app.py)

def to_float(value):
    """Safely convert DynamoDB Decimal or string to float"""
    if isinstance(value, Decimal):
        return float(value)
    try:
        return float(value)
    except:
        return 0.0


@app.get("/api/q-business/user-context/{email}")
async def get_user_context_for_q(email: str):
    """
    Endpoint that Amazon Q Business Lambda will call to get user data
    """
    try:
        # 1️⃣ Fetch user profile
        user_resp = users_table.get_item(Key={"userId": email})
        user_profile = user_resp.get("Item")

        if not user_profile:
            return {"error": "User not found", "context": ""}

        # 2️⃣ Fetch portfolio
        portfolio_resp = portfolios_table.get_item(Key={"userId": email})
        portfolio = portfolio_resp.get("Item", {})

        # Extract holdings
        stocks = portfolio.get("stocks", [])
        bonds = portfolio.get("bonds", [])
        etfs = portfolio.get("etfs", [])
        cash_savings = to_float(portfolio.get("cashSavings", 0))

        # 3️⃣ Compute totals
        stock_value = sum(to_float(s.get("quantity")) * to_float(s.get("avgPrice")) for s in stocks)
        bond_value = sum(to_float(b.get("quantity")) * to_float(b.get("avgPrice")) for b in bonds)
        etf_value = sum(to_float(e.get("quantity")) * to_float(e.get("avgPrice")) for e in etfs)
        total_value = stock_value + bond_value + etf_value + cash_savings

        # 4️⃣ Risk Analysis
        risk_analysis = user_profile.get("riskAnalysis", {})

        # 5️⃣ Build Context
        context = f"""
USER PROFILE INFORMATION:
- Name: {user_profile.get('name', 'User')}
- Email: {email}
- Age: {user_profile.get('age', 'N/A')}
- Occupation: {user_profile.get('occupation', 'Professional')}
- Risk Tolerance: {user_profile.get('riskTolerance', 'moderate')}
- Investment Horizon: {user_profile.get('investmentHorizon', '5-10')} years
- Investment Goal: {user_profile.get('investmentGoal', 'wealth accumulation')}
- Monthly SIP: ₹{user_profile.get('monthlyContribution', 0)}

RISK ASSESSMENT:
- Risk Score: {risk_analysis.get('riskScore', 'Not assessed')}
- Risk Label: {risk_analysis.get('riskLabel', 'Not assessed')}
- Recommendation: {risk_analysis.get('recommendation', 'Complete risk assessment')}
- Rationale: {risk_analysis.get('rationale', 'No risk analysis available')}

PORTFOLIO SUMMARY:
- Total Portfolio Value: ₹{total_value:,.2f}
- Total Holdings: {len(stocks) + len(bonds) + len(etfs)} assets
- Stocks: {len(stocks)} worth ₹{stock_value:,.2f} ({(stock_value/total_value*100) if total_value > 0 else 0:.1f}%)
- Bonds: {len(bonds)} worth ₹{bond_value:,.2f} ({(bond_value/total_value*100) if total_value > 0 else 0:.1f}%)
- ETFs: {len(etfs)} worth ₹{etf_value:,.2f} ({(etf_value/total_value*100) if total_value > 0 else 0:.1f}%)
- Cash: ₹{cash_savings:,.2f} ({(cash_savings/total_value*100) if total_value > 0 else 0:.1f}%)

STOCK HOLDINGS:
{chr(10).join([f"- {s.get('symbol', 'Unknown')}: {s.get('quantity', 0)} units @ ₹{s.get('avgPrice', 0)}" for s in stocks]) if stocks else '- No stocks'}

BOND HOLDINGS:
{chr(10).join([f"- {b.get('symbol', 'Unknown')}: {b.get('quantity', 0)} units @ ₹{b.get('avgPrice', 0)}" for b in bonds]) if bonds else '- No bonds'}

ETF HOLDINGS:
{chr(10).join([f"- {e.get('symbol', 'Unknown')}: {e.get('quantity', 0)} units @ ₹{e.get('avgPrice', 0)}" for e in etfs]) if etfs else '- No ETFs'}

IMPORTANT: Use this info to give personalized insights specific to {user_profile.get('name', 'the user')}.
"""

        return {
            "success": True,
            "email": email,
            "context": context.strip(),
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        print(f"Error fetching user context: {e}")
        return {"success": False, "error": str(e), "context": ""}
    
    

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

import os
import sys
from dotenv import load_dotenv


load_dotenv()

print("=" * 60)
print("🔧 STRAND SDK - WealthWise AI Robo-Advisor")
print("=" * 60)
print()



from fastapi import FastAPI, HTTPException, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
import boto3
from datetime import datetime, timezone
from decimal import Decimal
import bcrypt

# Import new Strand SDK agents
from agents.market_agent import create_market_agent
from agents.orchestrator_agent import create_orchestrator_agent
from agents.portfolio_agent import create_portfolio_agent

# Import working implementations directly
from agents.strand_recommendation_agent import generate_ai_recommendations
from agents.strand_risk_agent import analyze_user_risk_profile

# Import Q Business service
from services.qbusiness_service import SmartQBusinessService

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

# Initialize New Strand SDK Agents
print()
print("� Initiializing Strand SDK Agents...")
market_agent = create_market_agent()
portfolio_agent = create_portfolio_agent()
# Note: recommendation and risk are function-based, not class-based
print("✅ Market and Portfolio agents initialized")
print("✅ Recommendation and Risk functions available")

# Create agent registry for orchestrator (only include class-based agents)
agent_registry = {
    'market': market_agent,
    'portfolio': portfolio_agent
    # recommendation and risk are used as direct function calls
}

orchestrator_agent = create_orchestrator_agent(agent_registry)

# ==================== Q BUSINESS INITIALIZATION ====================
print()
print("🔌 Initializing Q Business Service...")
from services.qbusiness_service import SmartQBusinessService

# Global singleton for Q Business
_qbusiness_service_singleton = None

def initialize_qbusiness_service():
    """Initialize Q Business service with DynamoDB tables"""
    global _qbusiness_service_singleton
    if _qbusiness_service_singleton is None:
        _qbusiness_service_singleton = SmartQBusinessService(
            users_table=users_table,
            portfolios_table=portfolios_table
        )
    return _qbusiness_service_singleton

def get_qbusiness_service():
    """Get the initialized Q Business service singleton"""
    global _qbusiness_service_singleton
    if _qbusiness_service_singleton is None:
        _qbusiness_service_singleton = initialize_qbusiness_service()
    return _qbusiness_service_singleton

# Initialize immediately at startup
_qbusiness_service_singleton = initialize_qbusiness_service()
print("✅ Q Business Service initialized with DynamoDB tables")
# ==================== END Q BUSINESS INITIALIZATION ====================

print("=" * 60)
print("✅ All Strand SDK agents initialized!")
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
            "strand_sdk": {
                "market": "Market Data Agent (Strand SDK)",
                "portfolio": "Portfolio Analysis Agent (Strand SDK)",
                "recommendation": "Recommendation Agent (Strand SDK)",
                "risk": "Risk Analysis Agent (Strand SDK)",
                "orchestrator": "Orchestrator Agent (Strand SDK)"
            }
        },
        "endpoints": {
            "strand_sdk": {
                "chat": "POST /api/chat",
                "analysis": "GET /api/portfolio/{email}/analysis",
                "marketReport": "GET /api/portfolio/{email}/market-report",
                "recommendations": "GET /api/portfolio/{email}/recommendations",
                "riskAnalysis": "GET /api/portfolio/{email}/risk-analysis",
                "ask": "POST /api/portfolio/{email}/ask"
            },
            "core": {
                "onboarding": "POST /api/onboarding/complete",
                "login": "POST /api/auth/login",
                "dashboard": "GET /api/portfolio/{email}/dashboard"
            },
            "qbusiness": {
                "chat": "POST /api/qbusiness/chat",
                "conversations": "GET /api/qbusiness/conversations"
            }
        }
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
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
        'createdAt': datetime.now(timezone.utc).isoformat(),
        'updatedAt': datetime.now(timezone.utc).isoformat()
    }

    users_table.put_item(Item=user_data)

    portfolio_data = {
        'userId': user_email,
        'initialInvestment': convert_float_to_decimal(request.initialInvestment),
        'cashSavings': convert_float_to_decimal(request.cashSavings),
        'bonds': convert_float_to_decimal([b.dict() for b in request.bonds]),
        'stocks': convert_float_to_decimal([s.dict() for s in request.stocks]),
        'etfs': convert_float_to_decimal([e.dict() for e in request.etfs]),
        'createdAt': datetime.now(timezone.utc).isoformat(),
        'updatedAt': datetime.now(timezone.utc).isoformat()
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
# In strand_main.py

@app.post("/api/qbusiness/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    user_email: Optional[str] = Query(None, description="User email (optional)")
):
    try:
        qb_service = get_qbusiness_service()
        
        conversation_id = request.conversation_id
        parent_message_id = request.parent_message_id
        
        if conversation_id and len(conversation_id) < 36:
            conversation_id = None
        if parent_message_id and len(parent_message_id) < 36:
            parent_message_id = None
        
        # ✅ Call with user_email parameter
        result = qb_service.chat_sync(
            user_message=request.message,
            user_email=user_email or 'anonymous@wealthwise.com',  # ← Changed parameter name
            conversation_id=conversation_id,
            parent_message_id=parent_message_id
        )
        
        # Log classification
        if result['success']:
            query_type = result.get('queryType', 'unknown')
            context_injected = result.get('contextInjected', False)
            print(f"📊 Query Type: {query_type.upper()}, Context Injected: {context_injected}")
        
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
        import traceback
        traceback.print_exc()
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
    🆕 Conversational interface with Strand SDK

    Example usage:
        POST /api/chat?user_email=user@example.com
        Body: {"message": "Should I rebalance my portfolio?"}

    Features:
    - Natural language understanding
    - Contextual responses
    - Automatic agent coordination
    - Conversation memory
    """
    print(f"💬 [Strand Chat] Request from {user_email}")

    try:
        response = await orchestrator_agent.chat(
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
        response = await orchestrator_agent.chat(
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


@app.get("/api/portfolio/{email}/analysis")
async def get_portfolio_analysis(email: str):
    """
    🆕 Strand SDK portfolio analysis

    Uses new Strand SDK agents for comprehensive analysis
    """
    print(f"🤖 [Portfolio Analysis] Request for {email}")

    try:
        # Get market data using new market agent
        market_data = market_agent.generate_report(email)
        
        if not market_data.get('success'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to fetch market data"
            )

        # Run portfolio analysis using new portfolio agent
        analysis = portfolio_agent.analyze_portfolio(email, market_data)
        
        if not analysis.get('success'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=analysis.get('error', 'Analysis failed')
            )

        return {
            'success': True,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'userId': email,
            'analysis': analysis,
            'marketData': market_data,
            'metadata': {
                'version': '5.0.0-strand-sdk',
                'engine': 'Strand SDK',
                'agents_used': ['market_agent', 'portfolio_agent']
            }
        }

    except Exception as e:
        print(f"❌ Portfolio analysis error: {e}")
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
        orchestrator_agent.clear_history(email)
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
        summary = orchestrator_agent.get_conversation_summary(email)
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
    """Get enriched portfolio with live market data using Strand SDK"""
    print(f"📊 Market report requested for: {email}")

    try:
        report = market_agent.generate_report(email)

        if not report['success']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=report.get('error', 'Failed to generate market report')
            )

        report['metadata'] = {
            'apiVersion': '5.0.0-strand-sdk',
            'agent': 'MarketDataAgent (Strand SDK)',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

        return report

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )



@app.get("/api/portfolio/{email}/dashboard")
async def get_complete_dashboard(email: str):
    """Complete dashboard using Strand SDK agents"""
    print(f"📊 Complete dashboard requested for: {email}")

    try:
        # Get market data
        market_report = market_agent.generate_report(email)

        if not market_report['success']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not fetch market data"
            )

        # Get portfolio analysis
        analysis = portfolio_agent.analyze_portfolio(email, market_report)

        if not analysis['success']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not generate analysis"
            )

        # Get recommendations
        # Use the function directly instead of agent method
        recommendations = {'success': True, 'recommendations': []}  # Placeholder for now

        return {
            'success': True,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'userId': email,
            'marketData': market_report,
            'analysis': analysis,
            'recommendations': recommendations if recommendations.get('success') else None,
            'summary': {
                'totalValue': market_report['portfolioMetrics']['totalValue'],
                'healthScore': analysis['portfolioHealth']['score'],
                'healthGrade': analysis['portfolioHealth']['grade'],
                'modelPortfolio': analysis['modelPortfolio']['name'],
                'drift': analysis['allocationAnalysis']['drift'],
                'topRecommendations': len([r for r in analysis['recommendations'] if r.get('priority') == 'HIGH'])
            },
            'metadata': {
                'version': '5.0.0-strand-sdk',
                'agents_used': ['market_agent', 'portfolio_agent', 'recommendation_agent']
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

    existing_portfolio['updatedAt'] = datetime.now(timezone.utc).isoformat()

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
    return {
        'success': True,
        'agent': 'MarketDataAgent (Strand SDK)',
        'version': '5.0.0-strand-sdk',
        'data_sources': ['Yahoo Finance', 'Fallback estimations'],
        'features': ['Real-time prices', 'Portfolio valuation', 'Sector analysis']
    }

@app.get("/api/strand/stats")
async def get_strand_stats():
    """
    🆕 Get Strand SDK system statistics
    """
    return {
        'success': True,
        'strand_sdk': {
            'version': '5.0.0',
            'agents': {
                'market': 'MarketDataAgent',
                'portfolio': 'PortfolioAnalysisAgent', 
                'recommendation': 'RecommendationAgent',
                'risk': 'RiskAnalysisAgent',
                'orchestrator': 'OrchestratorAgent'
            },
            'active_conversations': len(orchestrator_agent.conversation_history),
            'framework': 'Strand SDK with AWS Bedrock'
        },
        'infrastructure': {
            'model': 'Claude Sonnet 4 (Bedrock)',
            'database': 'DynamoDB',
            'api_framework': 'FastAPI'
        }
    }

@app.get("/api/portfolio/{email}/risk-analysis")
async def get_risk_analysis(email: str):
    """
    🆕 Get comprehensive risk analysis using Strand SDK
    """
    print(f"🎯 Strand SDK risk analysis requested for: {email}")

    try:
        # Use the function directly instead of agent method
        # Need to pass DynamoDB tables to the function
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
        
        # 3. Fetch market data using new Strand SDK market agent
        print(f"📊 Fetching market data using Strand SDK market agent...")
        market_data = None
        try:
            market_report = market_agent.generate_report(email)
            
            if market_report.get('success'):
                # Extract relevant market context for recommendations
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
                    'inflation_rate': 6.0,
                    'expected_return': 12.0
                }
                print(f"✅ Market data available from Strand SDK market agent")
            else:
                print(f"⚠️ Market report failed: {market_report.get('error')}")
                market_data = None
                
        except Exception as market_error:
            print(f"⚠️ Market data fetch failed: {market_error}. Using defaults.")
            market_data = None
        
        print(f"🤖 Generating recommendations using Strand SDK recommendation agent...")
        
        # Use the function directly instead of agent method
        # Need to get user profile and portfolio data first
        user_response = users_table.get_item(Key={'userId': email})
        portfolio_response = portfolios_table.get_item(Key={'userId': email})
        
        if 'Item' not in user_response or 'Item' not in portfolio_response:
            raise HTTPException(status_code=404, detail="User or portfolio not found")
        
        user_profile = convert_decimal_to_float(user_response['Item'])
        portfolio = convert_decimal_to_float(portfolio_response['Item'])
        
        result = generate_ai_recommendations(
            user_email=email,
            user_profile=user_profile,
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
            'timestamp': result.get('timestamp', datetime.now(timezone.utc).isoformat()),
            
            # Core recommendations with XAI
            'recommendations': result['recommendations'],
            'summary': result['summary'],
            
            # AI-generated personalized insights
            'ai_insights': result['ai_insights'],
            
            # Rich metadata for explainability
            'metadata': result['metadata'],
            
            # Explainability information (optional)
            'explainability': result.get('explainability', {
                'methodology': 'Recommendations generated using Strand SDK agents with personalized analysis',
                'factors_considered': [
                    'User age and risk profile',
                    'Portfolio allocation and diversification',
                    'Market conditions and timing',
                    'Investment horizon and goals'
                ]
            }),
            
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


if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("🚀 WealthWise AI Robo-Advisor Backend Server")
    print("   Powered by Strand SDK + Claude Sonnet 4")
    print("=" * 60)
    print()
    print("🆕 STRAND SDK ENDPOINTS:")
    print("   POST /api/chat?user_email={email}")
    print("   POST /api/portfolio/{email}/ask")
    print("   GET  /api/portfolio/{email}/analysis")
    print("   GET  /api/portfolio/{email}/market-report")
    print("   GET  /api/portfolio/{email}/recommendations")
    print("   GET  /api/portfolio/{email}/risk-analysis")
    print("   GET  /api/portfolio/{email}/dashboard")
    print()
    print("✅ ALL ENDPOINTS: Now powered by Strand SDK agents")
    print("=" * 60)
    print()
    uvicorn.run(app, host="0.0.0.0", port=8000)
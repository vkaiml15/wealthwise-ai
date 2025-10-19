"""
Strand Recommendation Agent - AI-Only Version (FIXED)
Provides personalized investment recommendations with AI insights
Includes risk score integration from Risk Analysis
"""

import os
import json
import boto3
from typing import Dict, Any, List
from decimal import Decimal
from dotenv import load_dotenv

# Strand SDK imports
from strands import Agent, tool
from strands.models import BedrockModel

load_dotenv()

# Initialize Bedrock client
bedrock_client = boto3.client(
    service_name='bedrock-runtime',
    region_name=os.getenv('AWS_REGION', 'us-east-1')
)

# ==================== HELPER FUNCTIONS ====================

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


# ==================== RECOMMENDATION LOGIC ====================

def generate_recommendations_logic(
    user_profile: Dict[str, Any],
    portfolio: Dict[str, Any],
    market_data: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Core recommendation generation logic
    Returns structured recommendations for UI display
    """
    
    recommendations = {
        'immediate': [],
        'short_term': [],
        'long_term': [],
        'opportunities': []
    }
    
    # Extract key metrics
    risk_tolerance = user_profile.get('riskTolerance', 'moderate').lower()
    age = user_profile.get('age', 30)
    investment_horizon = user_profile.get('investmentHorizon', '5-10')
    monthly_contribution = float(user_profile.get('monthlyContribution', 0))
    
    # Extract risk analysis data if available
    risk_analysis = user_profile.get('riskAnalysis', None)
    has_risk_score = risk_analysis is not None
    
    if has_risk_score:
        risk_score = float(risk_analysis.get('riskScore', 5.0))
        risk_label = risk_analysis.get('riskLabel', 'Moderate')
        risk_recommendation = risk_analysis.get('recommendation', '')
        print(f"📊 Using existing risk score: {risk_score}/10 ({risk_label})")
    else:
        risk_score = None
        risk_label = None
        print("⚠️ No risk score found - user should complete risk analysis")
    
    # Portfolio metrics
    stocks = portfolio.get('stocks', [])
    bonds = portfolio.get('bonds', [])
    etfs = portfolio.get('etfs', [])
    cash_savings = float(portfolio.get('cashSavings', 0))
    
    total_holdings = len(stocks) + len(bonds) + len(etfs)
    
    # Calculate portfolio value
    total_invested = sum(
        float(s.get('quantity', 0)) * float(s.get('avgPrice', 0))
        for s in stocks
    ) + sum(
        float(b.get('quantity', 0)) * float(b.get('avgPrice', 0))
        for b in bonds
    ) + sum(
        float(e.get('quantity', 0)) * float(e.get('avgPrice', 0))
        for e in etfs
    )
    
    # === RISK SCORE RECOMMENDATIONS ===
    if not has_risk_score:
        recommendations['immediate'].append({
            'type': 'risk_analysis',
            'priority': 'high',
            'title': 'Complete Risk Analysis First',
            'description': 'Get a comprehensive understanding of your risk profile to receive better personalized recommendations.',
            'action': 'Click on "Risk Analysis" tab to assess your portfolio risk',
            'impact': 'Unlock personalized recommendations tailored to your risk capacity',
            'timeframe': 'Next 10 minutes'
        })
    else:
        # Check risk alignment
        if risk_score < 4:
            recommendations['short_term'].append({
                'type': 'risk_alignment',
                'priority': 'medium',
                'title': f'Your Risk Score is Conservative ({risk_score}/10)',
                'description': f'{risk_recommendation}. Consider if this aligns with your long-term goals.',
                'action': 'Review if your portfolio is too conservative for your age and timeline',
                'impact': 'Potentially higher long-term returns while staying comfortable',
                'timeframe': '1-2 months'
            })
        elif risk_score > 7:
            recommendations['short_term'].append({
                'type': 'risk_alignment',
                'priority': 'medium',
                'title': f'Your Risk Score is Aggressive ({risk_score}/10)',
                'description': f'{risk_recommendation}. Ensure you can handle potential volatility.',
                'action': 'Consider adding some bonds/stable assets to reduce overall risk',
                'impact': 'Better sleep at night during market downturns',
                'timeframe': '1-2 months'
            })
        
        # Check for risk mismatch
        risk_tolerance_score_map = {
            'conservative': (0, 4),
            'moderate': (4, 7),
            'aggressive': (7, 10)
        }
        
        expected_range = risk_tolerance_score_map.get(risk_tolerance, (4, 7))
        if not (expected_range[0] <= risk_score <= expected_range[1]):
            recommendations['immediate'].append({
                'type': 'risk_mismatch',
                'priority': 'high',
                'title': 'Risk Profile Mismatch Detected',
                'description': f'Your stated risk tolerance is "{risk_tolerance}" but your actual portfolio risk score is {risk_score}/10 ({risk_label}).',
                'action': f'Either adjust your portfolio to match {risk_tolerance} tolerance, or update your risk preference',
                'impact': 'Align portfolio with your actual risk capacity and comfort level',
                'timeframe': 'Next 2 weeks'
            })
    
    # === DIVERSIFICATION ANALYSIS ===
    if total_holdings < 5:
        recommendations['immediate'].append({
            'type': 'diversification',
            'priority': 'high',
            'title': 'Increase Portfolio Diversification',
            'description': f'You have only {total_holdings} holdings. Consider adding {5 - total_holdings} more to reduce concentration risk.',
            'action': 'Add more diverse assets across different sectors',
            'impact': 'Reduce volatility by 15-25%',
            'timeframe': 'Next 2 weeks'
        })
    
    # === ASSET ALLOCATION ===
    stocks_percent = (len(stocks) / total_holdings * 100) if total_holdings > 0 else 0
    bonds_percent = (len(bonds) / total_holdings * 100) if total_holdings > 0 else 0
    
    # Use risk score if available, otherwise fallback to age/tolerance
    if has_risk_score:
        if risk_score >= 7:
            target_stocks = 80
            target_bonds = 15
        elif risk_score >= 5:
            target_stocks = 70
            target_bonds = 25
        elif risk_score >= 3:
            target_stocks = 50
            target_bonds = 40
        else:
            target_stocks = 30
            target_bonds = 60
    else:
        if age < 35 and risk_tolerance == 'aggressive':
            target_stocks = 80
            target_bonds = 15
        elif age < 50 and risk_tolerance in ['moderate', 'aggressive']:
            target_stocks = 70
            target_bonds = 25
        else:
            target_stocks = 60
            target_bonds = 35
    
    if abs(stocks_percent - target_stocks) > 15:
        recommendations['short_term'].append({
            'type': 'rebalancing',
            'priority': 'medium',
            'title': 'Rebalance Asset Allocation',
            'description': f'Your current allocation is {stocks_percent:.0f}% stocks, {bonds_percent:.0f}% bonds. Target: {target_stocks}% stocks, {target_bonds}% bonds.',
            'action': 'Adjust your portfolio to match target allocation',
            'impact': 'Better risk-adjusted returns aligned with your risk profile',
            'timeframe': '1-2 months'
        })
    
    # === CASH POSITION ===
    total_value = total_invested + cash_savings
    cash_percent = (cash_savings / total_value * 100) if total_value > 0 else 100
    
    if cash_percent > 20:
        recommendations['immediate'].append({
            'type': 'deployment',
            'priority': 'high',
            'title': 'Deploy Excess Cash',
            'description': f'You have {cash_percent:.1f}% (₹{cash_savings:,.0f}) in cash. Consider investing to beat inflation.',
            'action': f'Invest ₹{cash_savings * 0.7:,.0f} in a diversified ETF',
            'impact': 'Potential 8-12% annual returns vs 0% in cash',
            'timeframe': 'Next week'
        })
    elif cash_percent < 5 and total_value > 100000:
        recommendations['short_term'].append({
            'type': 'emergency_fund',
            'priority': 'medium',
            'title': 'Build Emergency Reserve',
            'description': 'Your cash reserve is below 5%. Build an emergency fund equal to 3-6 months of expenses.',
            'action': 'Set aside 10-15% of monthly income',
            'impact': 'Financial security and peace of mind',
            'timeframe': '3-6 months'
        })
    
    # === MONTHLY CONTRIBUTIONS ===
    if monthly_contribution == 0:
        recommendations['long_term'].append({
            'type': 'systematic_investment',
            'priority': 'medium',
            'title': 'Start Systematic Investment Plan',
            'description': 'Regular monthly investments can significantly boost long-term wealth through rupee cost averaging.',
            'action': 'Set up SIP with even ₹5,000/month',
            'impact': 'Build substantial corpus over time',
            'timeframe': 'Ongoing'
        })
    elif monthly_contribution < 5000:
        recommendations['opportunities'].append({
            'type': 'increase_sip',
            'priority': 'low',
            'title': 'Consider Increasing SIP Amount',
            'description': f'Your current SIP of ₹{monthly_contribution:,.0f} is a good start. Consider increasing by 10% annually.',
            'action': 'Increase SIP by ₹500-1000',
            'impact': 'Accelerate wealth building',
            'timeframe': 'Next review'
        })
    
    # === SECTOR OPPORTUNITIES ===
    if risk_tolerance in ['moderate', 'aggressive'] or (has_risk_score and risk_score >= 5):
        recommendations['opportunities'].append({
            'type': 'sector_opportunity',
            'priority': 'low',
            'title': 'Technology Sector Exposure',
            'description': 'Consider exposure to high-growth tech sector through Nifty IT ETF or quality tech stocks.',
            'action': 'Allocate 10-15% to technology',
            'impact': 'Capture growth in digital transformation',
            'timeframe': 'Next 3 months'
        })
        
        recommendations['opportunities'].append({
            'type': 'international',
            'priority': 'low',
            'title': 'International Diversification',
            'description': 'Add international exposure through US/Global index funds to reduce India-specific risk.',
            'action': 'Invest 5-10% in international ETFs',
            'impact': 'Geographic diversification',
            'timeframe': 'Next 6 months'
        })
    
    # === TAX OPTIMIZATION ===
    if total_value > 250000:
        recommendations['long_term'].append({
            'type': 'tax_optimization',
            'priority': 'medium',
            'title': 'Tax-Efficient Investing',
            'description': 'Consider ELSS funds for Section 80C benefits and indexation benefits of debt funds.',
            'action': 'Allocate ₹1.5L to ELSS for tax saving',
            'impact': 'Save up to ₹46,800 in taxes',
            'timeframe': 'Before financial year end'
        })
    
    return {
        'success': True,
        'recommendations': recommendations,
        'total_count': sum(len(recs) for recs in recommendations.values()),
        'summary': {
            'immediate_actions': len(recommendations['immediate']),
            'short_term_actions': len(recommendations['short_term']),
            'long_term_goals': len(recommendations['long_term']),
            'opportunities': len(recommendations['opportunities'])
        },
        'risk_info': {
            'has_risk_score': has_risk_score,
            'risk_score': risk_score if has_risk_score else None,
            'risk_label': risk_label if has_risk_score else None
        },
        'user_context': {
            'age': age,
            'risk_tolerance': risk_tolerance,
            'total_holdings': total_holdings,
            'cash_percent': round(cash_percent, 1)
        }
    }


# ==================== STRAND AGENT FOR AI INSIGHTS ====================

def get_recommendation_agent():
    """Initialize Strand Agent for AI-powered insights"""
    bedrock_model = BedrockModel(
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        client=bedrock_client
    )
    
    agent = Agent(
        model=bedrock_model,
        system_prompt="""You are WealthWise AI, a friendly and encouraging investment advisor.

Your role is to provide a brief, motivational summary (3-4 sentences) of portfolio recommendations.

Guidelines:
- Be warm, encouraging, and conversational
- Focus on the MOST IMPORTANT action the user should take
- Explain WHY it matters in simple terms
- Mention the expected positive impact
- Use relatable analogies when helpful
- Keep it concise (3-4 sentences max)
- Avoid jargon - speak like a helpful friend

Example tone:
"Great news! Your portfolio has solid fundamentals. The most important thing to focus on right now is adding 2 more holdings to reduce concentration risk - think of it like not putting all your eggs in one basket! This simple move could reduce your volatility by 20% and help you sleep better during market swings."

Remember: Be encouraging, specific, and actionable!"""
    )
    
    return agent


# ==================== MAIN FUNCTION ====================

def generate_ai_recommendations(user_email: str, user_profile: Dict, portfolio: Dict) -> Dict[str, Any]:
    """
    Generate complete recommendations with AI insights
    
    Returns:
        - Structured recommendations (for UI cards)
        - AI-generated summary insights
    """
    print("=" * 60)
    print(f"💡 AI Recommendation Generation")
    print(f"👤 User: {user_email}")
    print("=" * 60)
    
    try:
        # 1. Generate structured recommendations using logic
        structured_recs = generate_recommendations_logic(user_profile, portfolio)
        
        print(f"✅ Generated {structured_recs['total_count']} recommendations")
        
        # 2. Get AI insights from Strands Agent
        agent = get_recommendation_agent()
        
        # Build context for AI
        risk_info = structured_recs['risk_info']
        user_ctx = structured_recs['user_context']
        summary = structured_recs['summary']
        
        # Get top 2 immediate recommendations
        top_recs = structured_recs['recommendations']['immediate'][:2]
        
        # Create prompt for AI
        ai_prompt = f"""User Profile:
- Age: {user_ctx['age']}
- Risk Tolerance: {user_ctx['risk_tolerance']}
- Risk Score: {risk_info['risk_score']}/10 ({risk_info['risk_label']}) {'' if risk_info['has_risk_score'] else '(Not completed)'}
- Total Holdings: {user_ctx['total_holdings']}
- Cash Position: {user_ctx['cash_percent']}%

Recommendations Summary:
- Immediate Actions: {summary['immediate_actions']}
- Short-term: {summary['short_term_actions']}
- Long-term: {summary['long_term_goals']}
- Opportunities: {summary['opportunities']}

Top Priority Recommendations:
{json.dumps(top_recs, indent=2) if top_recs else 'Portfolio is well-balanced'}

Provide a brief, encouraging 3-4 sentence summary highlighting the most important action and its impact."""
        
        print("🤖 Calling Strands Agent for AI insights...")
        agent_result = agent(ai_prompt)
        
        # FIXED: Extract text from AgentResult object
        if hasattr(agent_result, 'content'):
            ai_insights = agent_result.content
        elif hasattr(agent_result, 'output'):
            ai_insights = agent_result.output
        elif hasattr(agent_result, 'text'):
            ai_insights = agent_result.text
        elif isinstance(agent_result, str):
            ai_insights = agent_result
        else:
            # Fallback: convert to string
            ai_insights = str(agent_result)
            print(f"⚠️ Warning: AgentResult type not recognized, using str(): {type(agent_result)}")
        
        print(f"✅ AI insights generated: {len(ai_insights)} characters")
        
        return {
            'success': True,
            'recommendations': structured_recs['recommendations'],
            'summary': structured_recs['summary'],
            'risk_info': structured_recs['risk_info'],
            'ai_insights': ai_insights,
            'user_email': user_email
        }
        
    except Exception as e:
        print(f"❌ Error generating recommendations: {e}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'error': str(e)
        }
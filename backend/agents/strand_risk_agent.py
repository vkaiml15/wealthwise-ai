import os
import json
import boto3
from typing import Dict, Any
from decimal import Decimal
from dotenv import load_dotenv

# ✅ CORRECT STRAND SDK IMPORTS
from strands import Agent, tool
from strands.models import BedrockModel
from anthropic import Anthropic

load_dotenv()

# Initialize Bedrock Agent Runtime using IAM role
bedrock_agent_runtime = boto3.client(
    service_name='bedrock-agent-runtime',
    region_name=os.getenv('AWS_REGION', 'us-east-1')
)

# ==================== HELPER FUNCTIONS ====================

def convert_floats_to_decimal(obj):
    """
    Recursively convert all float values to Decimal for DynamoDB compatibility
    """
    if isinstance(obj, list):
        return [convert_floats_to_decimal(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: convert_floats_to_decimal(value) for key, value in obj.items()}
    elif isinstance(obj, float):
        return Decimal(str(obj))
    else:
        return obj


# ==================== RISK CALCULATION LOGIC ====================

def compute_risk_score_logic(age: int, horizon: str, tolerance: str,
                             allocation: list = None, monthly_contribution: float = 0) -> dict:
    """
    Core risk score computation logic
    """

    # Age Factor (0-1 scale)
    age_factor = 0.6 if age < 30 else (0.5 if age < 45 else (0.4 if age < 60 else 0.3))

    # Horizon Factor
    horizon_map = {"1-3": (0.3, 2), "3-5": (0.5, 4), "5-10": (0.7, 7.5), "10+": (0.9, 15)}
    horizon_factor, horizon_years = horizon_map.get(horizon, (0.9, 15))

    # Tolerance Factor
    tolerance_map = {"conservative": 0.3, "moderate": 0.6, "aggressive": 0.9}
    tolerance_index = tolerance_map.get(tolerance.lower(), 0.6)

    # Allocation Risk
    allocation_risk = 0.5
    if allocation and len(allocation) > 0:
        risk_weights = {
            "tech": 0.85, "technology": 0.85, "crypto": 1.0,
            "stocks": 0.75, "growth": 0.8, "etf": 0.6, "etfs": 0.6,
            "bonds": 0.2, "cash": 0.1, "healthcare": 0.5,
            "real estate": 0.45, "finance": 0.65, "consumer": 0.6
        }

        total_allocation_risk = 0
        total_percentage = 0

        for asset in allocation:
            name = asset.get("name", "").lower()
            percentage = float(asset.get("percentage", 0))
            asset_risk = 0.5

            for key, val in risk_weights.items():
                if key in name:
                    asset_risk = val
                    break

            total_allocation_risk += asset_risk * percentage
            total_percentage += percentage

        if total_percentage > 0:
            allocation_risk = total_allocation_risk / total_percentage

    # Contribution Factor
    contribution_factor = 0.5
    if monthly_contribution > 0:
        contribution_factor = 0.7 if monthly_contribution >= 1000 else (
            0.6 if monthly_contribution >= 500 else 0.5
        )

    # Weighted Risk Score Calculation
    w_age, w_horizon, w_tol, w_alloc, w_contrib = 0.15, 0.25, 0.35, 0.15, 0.10

    risk_score = (
        (w_age * age_factor) +
        (w_horizon * horizon_factor) +
        (w_tol * tolerance_index) +
        (w_alloc * allocation_risk) +
        (w_contrib * contribution_factor)
    )

    scaled_score = round(risk_score * 10, 1)

    if scaled_score < 4:
        label = "Conservative"
        recommendation = "Focus on capital preservation with bonds and dividend stocks"
    elif scaled_score < 7:
        label = "Moderate"
        recommendation = "Balance growth and stability with diversified portfolio"
    else:
        label = "Aggressive"
        recommendation = "Pursue maximum growth with higher volatility tolerance"

    return {
        "riskScore": scaled_score,
        "riskLabel": label,
        "recommendation": recommendation,
        "factors": {
            "age": age,
            "ageFactor": round(age_factor, 2),
            "horizon": horizon,
            "horizonYears": horizon_years,
            "horizonFactor": round(horizon_factor, 2),
            "tolerance": tolerance,
            "toleranceIndex": round(tolerance_index, 2),
            "allocationRisk": round(allocation_risk, 2),
            "contributionFactor": round(contribution_factor, 2)
        },
        "weights": {
            "age": w_age,
            "horizon": w_horizon,
            "tolerance": w_tol,
            "allocation": w_alloc,
            "contribution": w_contrib
        },
        "breakdown": {
            "ageContribution": round(w_age * age_factor * 10, 2),
            "horizonContribution": round(w_horizon * horizon_factor * 10, 2),
            "toleranceContribution": round(w_tol * tolerance_index * 10, 2),
            "allocationContribution": round(w_alloc * allocation_risk * 10, 2),
            "contributionContribution": round(w_contrib * contribution_factor * 10, 2)
        }
    }


# ==================== STRAND TOOLS ====================

@tool
def get_risk_recommendation(risk_score: float, risk_label: str) -> str:
    """
    Get personalized investment recommendations based on risk score.

    Provides actionable advice on:
    - Appropriate asset allocation
    - Investment strategies
    - Risk management approaches
    """
    recommendations = {
        "Conservative": """For your conservative profile:
- Asset Mix: 70% bonds, 20% dividend stocks, 10% cash
- Focus: Capital preservation and stable income
- Strategy: Invest in high-quality bonds and blue-chip dividend stocks
- Risk Management: Maintain 6-12 months emergency fund""",

        "Moderate": """For your moderate profile:
- Asset Mix: 60% stocks, 30% bonds, 10% cash/alternatives
- Focus: Balanced growth with downside protection
- Strategy: Diversify across sectors and asset classes
- Risk Management: Regular rebalancing and dollar-cost averaging""",

        "Aggressive": """For your aggressive profile:
- Asset Mix: 80% stocks, 15% alternatives, 5% bonds
- Focus: Maximum long-term growth
- Strategy: Growth stocks, emerging markets, sector concentration
- Risk Management: Long-term hold strategy, avoid panic selling"""
    }

    return recommendations.get(risk_label, "Please consult with a financial advisor for personalized recommendations.")


# ==================== STRAND AGENT ====================

def get_risk_agent():
    """
    Initialize Strand Agent using IAM role credentials (EC2 instance profile)
    This creates a new agent instance with automatic credential management
    """
    # ✅ Use IAM role - boto3 automatically gets credentials from EC2 instance metadata
    bedrock_client = boto3.client(
        "bedrock-runtime",
        region_name=os.getenv('AWS_REGION', 'us-east-1')
    )

    # Create Bedrock model with IAM role credentials
    bedrock_model = BedrockModel(
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        client=bedrock_client,  # ✅ explicitly pass the client
    )

    # Initialize Strand Agent with the configured model
    agent = Agent(
        model=bedrock_model,
        tools=[get_risk_recommendation],
        system_prompt="""You are the Risk Profile Agent for WealthWise AI, a robo-advisor platform.

Your role:
- Explain risk scores in simple, personalized language
- Help investors understand what their risk profile means
- Be encouraging and actionable (2-3 sentences max)
- Focus on how specific factors combine to create their profile

Always be supportive and explain complex concepts in everyday terms."""
    )

    return agent


# ==================== MAIN ANALYSIS FUNCTION ====================

def analyze_user_risk_profile(user_email: str, users_table, portfolios_table) -> Dict[str, Any]:
    """
    Complete risk analysis using Anthropic-based agent
    Calculates risk score and gets agent explanation
    """
    print("=" * 60)
    print(f"🎯 Risk Analysis Agent - Starting")
    print(f"👤 User: {user_email}")
    print("=" * 60)

    try:
        # ✅ Fetch from DynamoDB
        user_response = users_table.get_item(Key={'userId': user_email})
        if 'Item' not in user_response:
            return {'success': False, 'error': 'User not found'}

        user = user_response['Item']
        print(f"✅ User data loaded from DynamoDB")

        portfolio_response = portfolios_table.get_item(Key={'userId': user_email})
        portfolio = portfolio_response.get('Item', {}) if 'Item' in portfolio_response else {}

        # Build allocation
        allocation = []
        stocks_count = len(portfolio.get('stocks', []))
        bonds_count = len(portfolio.get('bonds', []))
        etfs_count = len(portfolio.get('etfs', []))
        total_assets = stocks_count + bonds_count + etfs_count

        if total_assets > 0:
            if stocks_count > 0:
                allocation.append({"name": "stocks", "percentage": (stocks_count / total_assets) * 100})
            if bonds_count > 0:
                allocation.append({"name": "bonds", "percentage": (bonds_count / total_assets) * 100})
            if etfs_count > 0:
                allocation.append({"name": "etfs", "percentage": (etfs_count / total_assets) * 100})

        print(f"📊 Portfolio: {stocks_count} stocks, {bonds_count} bonds, {etfs_count} ETFs")

        # Extract data
        age = int(user.get('age', 30))
        horizon = user.get('investmentHorizon', '5-10')
        tolerance = user.get('riskTolerance', 'moderate')
        monthly_contribution = float(user.get('monthlyContribution', 0))

        # ✅ CALCULATE RISK SCORE (Single Source of Truth)
        risk_result = compute_risk_score_logic(age, horizon, tolerance, allocation, monthly_contribution)

        print(f"📈 Risk Score: {risk_result['riskScore']}/10 ({risk_result['riskLabel']})")

        # ✅ GET AGENT EXPLANATION
        print(f"🤖 Agent: Generating personalized explanation...")

        # Get agent with IAM role credentials
        agent = get_risk_agent()

        prompt = f"""Explain this risk analysis to the investor in 2-3 friendly sentences:

**Their Risk Score:** {risk_result['riskScore']}/10 ({risk_result['riskLabel']})

**Investor Profile:**
- Age: {age} years old
- Investment Horizon: {horizon} years
- Risk Tolerance: {tolerance}
- Monthly Contribution: ₹{monthly_contribution:,.0f}

**How the Score Was Calculated:**
- Age factor contributed: {risk_result['breakdown']['ageContribution']} points
- Investment horizon contributed: {risk_result['breakdown']['horizonContribution']} points
- Risk tolerance contributed: {risk_result['breakdown']['toleranceContribution']} points
- Portfolio allocation contributed: {risk_result['breakdown']['allocationContribution']} points
- Monthly contribution contributed: {risk_result['breakdown']['contributionContribution']} points

Explain what this score means for them personally and how their specific factors combined to create this assessment."""

        agent_response = agent(prompt)

        print(f"✅ Agent response received")

        # ✅ Extract text from AgentResult object
        rationale = "Risk analysis completed successfully."

        try:
            if hasattr(agent_response, 'text'):
                rationale = agent_response.text
            elif hasattr(agent_response, 'content'):
                content = agent_response.content
                if isinstance(content, list) and len(content) > 0:
                    if isinstance(content[0], dict) and 'text' in content[0]:
                        rationale = content[0]['text']
                    else:
                        rationale = str(content[0])
                else:
                    rationale = str(content)
            elif hasattr(agent_response, 'message'):
                message = agent_response.message
                if isinstance(message, dict) and 'content' in message:
                    content = message['content']
                    if isinstance(content, list) and len(content) > 0:
                        if isinstance(content[0], dict) and 'text' in content[0]:
                            rationale = content[0]['text']
                        else:
                            rationale = str(content[0])
                    else:
                        rationale = str(content)
                else:
                    rationale = str(message)
            else:
                rationale = str(agent_response)
        except Exception as e:
            print(f"⚠️ Warning: Could not extract rationale: {e}")
            rationale = f"Your risk score is {risk_result['riskScore']}/10, indicating a {risk_result['riskLabel']} profile. {risk_result['recommendation']}"

        print(f"📝 Rationale: {rationale[:100]}...")

        # ✅ CONVERT TO DECIMAL FOR DYNAMODB
        risk_analysis_result = {
            **risk_result,
            'rationale': rationale,
            'agentType': 'Strand SDK',
            'timestamp': __import__('datetime').datetime.utcnow().isoformat()
        }

        # Convert all floats to Decimal
        risk_analysis_decimal = convert_floats_to_decimal(risk_analysis_result)

        # ✅ STORE IN DYNAMODB
        users_table.update_item(
            Key={'userId': user_email},
            UpdateExpression='SET riskAnalysis = :analysis',
            ExpressionAttributeValues={
                ':analysis': risk_analysis_decimal
            }
        )

        print("💾 Risk analysis saved to DynamoDB")

        print("=" * 60)
        print("✅ Risk Analysis Complete")
        print("=" * 60)
        print()

        return {
            'success': True,
            'userId': user_email,
            'riskAnalysis': risk_analysis_result
        }

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return {'success': False, 'error': str(e)}


# ==================== TESTING ====================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🧪 TESTING STRAND RISK ANALYSIS AGENT")
    print("=" * 60 + "\n")

    # Test the risk calculation directly
    test_age = 35
    test_horizon = "5-10"
    test_tolerance = "moderate"
    test_allocation = [
        {"name": "stocks", "percentage": 60},
        {"name": "bonds", "percentage": 30},
        {"name": "cash", "percentage": 10}
    ]
    test_contribution = 5000

    print("📝 Test Profile:")
    print(f"Age: {test_age}")
    print(f"Horizon: {test_horizon}")
    print(f"Tolerance: {test_tolerance}")
    print(f"Contribution: ₹{test_contribution}")
    print(f"Allocation: {test_allocation}")
    print()

    result = compute_risk_score_logic(test_age, test_horizon, test_tolerance, test_allocation, test_contribution)

    print("📊 Risk Score Result:")
    print(json.dumps(result, indent=2))
    print()

    # Test agent explanation
    print("🤖 Getting Agent Explanation:")
    agent_prompt = f"""Explain this risk analysis in 2-3 friendly sentences:

**Risk Score:** {result['riskScore']}/10 ({result['riskLabel']})
**Profile:** {test_age} years old, {test_horizon} year horizon, {test_tolerance} tolerance, ₹{test_contribution} monthly

The score reflects their balanced approach with moderate growth potential."""

    agent = get_risk_agent()
    agent_response = agent(agent_prompt)
    print(agent_response)
    print()

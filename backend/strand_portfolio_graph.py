"""
Strand Portfolio Analysis Graph

Converts the Portfolio Analysis Agent into a Strand Graph
with conditional logic and state management.
"""

from typing import Dict, Any, TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
import operator


# ==================== STATE DEFINITION ====================

class PortfolioState(TypedDict):
    """State for portfolio analysis workflow"""
    
    # User context
    user_email: str
    user_profile: Dict[str, Any]
    
    # Market data
    market_data: Dict[str, Any]
    holdings: list
    cash_savings: float
    
    # Analysis results
    model_portfolio: Dict[str, Any]
    allocation_analysis: Dict[str, Any]
    health_score: Dict[str, Any]
    rebalancing_plan: Dict[str, Any]
    recommendations: list
    
    # Messages (for conversational context)
    messages: Annotated[list, add_messages]
    
    # Control flow
    next_action: str
    errors: list


# ==================== NODE FUNCTIONS ====================

def initialize_analysis(state: PortfolioState) -> PortfolioState:
    """
    Initialize the analysis workflow
    
    Validates input and prepares state
    """
    print("🔄 [Node: Initialize] Starting portfolio analysis")
    
    # Validate market data
    if not state.get('market_data') or not state['market_data'].get('success'):
        state['errors'] = state.get('errors', [])
        state['errors'].append('Invalid or missing market data')
        state['next_action'] = 'error'
        return state
    
    # Extract holdings and cash
    state['holdings'] = state['market_data'].get('holdings', [])
    state['cash_savings'] = state['market_data'].get('cashSavings', 0)
    
    print(f"✅ [Node: Initialize] Found {len(state['holdings'])} holdings")
    
    state['next_action'] = 'select_model'
    return state


def select_model_portfolio(state: PortfolioState) -> PortfolioState:
    """
    Select appropriate model portfolio based on user profile
    """
    print("🔄 [Node: Model Selection] Analyzing user profile")
    
    user_profile = state.get('user_profile', {}).get('user', {})
    
    age = user_profile.get('age', 35)
    risk = user_profile.get('riskTolerance', 'Moderate').lower()
    
    # Model portfolios
    MODEL_PORTFOLIOS = {
        "Conservative": {
            "stocks": 30,
            "bonds": 60,
            "cash": 10,
            "expectedReturn": 4.5,
            "expectedVolatility": 8,
            "description": "Low risk, capital preservation focus"
        },
        "ModeratelyConservative": {
            "stocks": 45,
            "bonds": 45,
            "cash": 10,
            "expectedReturn": 6.0,
            "expectedVolatility": 11,
            "description": "Below-average risk, some growth potential"
        },
        "Moderate": {
            "stocks": 60,
            "bonds": 30,
            "cash": 10,
            "expectedReturn": 7.5,
            "expectedVolatility": 14,
            "description": "Balanced growth and stability"
        },
        "ModeratelyAggressive": {
            "stocks": 75,
            "bonds": 20,
            "cash": 5,
            "expectedReturn": 8.5,
            "expectedVolatility": 16,
            "description": "Above-average risk, growth focused"
        },
        "Aggressive": {
            "stocks": 85,
            "bonds": 10,
            "cash": 5,
            "expectedReturn": 9.5,
            "expectedVolatility": 18,
            "description": "High risk, maximum growth potential"
        }
    }
    
    # Selection logic
    if age >= 55 or risk == 'conservative':
        model_name = "Conservative"
    elif age >= 45 or risk == 'moderately conservative':
        model_name = "ModeratelyConservative"
    elif age <= 25 and risk == 'aggressive':
        model_name = "Aggressive"
    elif (age <= 35 and risk in ['aggressive', 'moderately aggressive']) or risk == 'moderately aggressive':
        model_name = "ModeratelyAggressive"
    else:
        model_name = "Moderate"
    
    model = MODEL_PORTFOLIOS[model_name]
    
    state['model_portfolio'] = {
        'name': model_name,
        'config': model
    }
    
    print(f"✅ [Node: Model Selection] Selected: {model_name}")
    
    state['next_action'] = 'analyze_allocation'
    return state


def analyze_allocation(state: PortfolioState) -> PortfolioState:
    """
    Analyze current vs target allocation
    """
    print("🔄 [Node: Allocation Analysis] Comparing allocations")
    
    holdings = state['holdings']
    cash_savings = state['cash_savings']
    target_model = state['model_portfolio']['config']
    
    # Calculate total assets
    total_invested = sum(h['currentValue'] for h in holdings)
    total_assets = total_invested + cash_savings
    
    # Categorize holdings
    stocks_value = 0
    bonds_value = 0
    
    for holding in holdings:
        holding_type = holding.get('type', 'stock').lower()
        
        if holding_type == 'bond' or 'bond' in holding.get('sector', '').lower():
            bonds_value += holding['currentValue']
        else:
            stocks_value += holding['currentValue']
    
    # Calculate current allocation
    current_allocation = {
        "stocks": round((stocks_value / total_assets) * 100, 1) if total_assets > 0 else 0,
        "bonds": round((bonds_value / total_assets) * 100, 1) if total_assets > 0 else 0,
        "cash": round((cash_savings / total_assets) * 100, 1) if total_assets > 0 else 0
    }
    
    target_allocation = {
        "stocks": target_model['stocks'],
        "bonds": target_model['bonds'],
        "cash": target_model['cash']
    }
    
    # Calculate drift
    drift = sum(abs(current_allocation[k] - target_allocation[k]) for k in current_allocation.keys())
    drift = round(drift, 1)
    
    # Identify issues
    issues = []
    if drift > 20:
        issues.append("CRITICAL_DRIFT")
    if current_allocation['cash'] > 20:
        issues.append("EXCESS_CASH")
    if bonds_value == 0 and target_allocation['bonds'] > 0:
        issues.append("MISSING_BONDS")
    
    state['allocation_analysis'] = {
        "current": current_allocation,
        "target": target_allocation,
        "drift": drift,
        "issues": issues,
        "totalAssets": round(total_assets, 2)
    }
    
    print(f"✅ [Node: Allocation Analysis] Drift: {drift}%")
    
    state['next_action'] = 'calculate_health'
    return state


def calculate_health_score(state: PortfolioState) -> PortfolioState:
    """
    Calculate portfolio health score (0-100)
    """
    print("🔄 [Node: Health Score] Calculating score")
    
    allocation = state['allocation_analysis']
    holdings = state['holdings']
    
    score = 100
    breakdown = []
    
    # Factor 1: Alignment with target (40 points)
    drift = allocation['drift']
    alignment_penalty = min(drift / 2, 40)
    score -= alignment_penalty
    breakdown.append({
        "factor": "Alignment",
        "penalty": -round(alignment_penalty, 1),
        "reason": f"{drift}% drift from target"
    })
    
    # Factor 2: Concentration risk (15 points)
    max_holding = max([h.get('portfolioWeight', 0) for h in holdings], default=0)
    if max_holding > 50:
        concentration_penalty = 15
    elif max_holding > 30:
        concentration_penalty = 10
    else:
        concentration_penalty = 0
    
    score -= concentration_penalty
    breakdown.append({
        "factor": "Concentration",
        "penalty": -concentration_penalty,
        "reason": f"Largest position: {max_holding}%"
    })
    
    # Factor 3: Cash efficiency (15 points)
    cash_pct = allocation['current']['cash']
    if cash_pct > 30:
        cash_penalty = 15
    elif cash_pct > 20:
        cash_penalty = 10
    elif cash_pct < 5:
        cash_penalty = 5
    else:
        cash_penalty = 0
    
    score -= cash_penalty
    breakdown.append({
        "factor": "Cash",
        "penalty": -cash_penalty,
        "reason": f"{cash_pct}% cash"
    })
    
    # Factor 4: Diversification (30 points)
    num_holdings = len(holdings)
    if num_holdings < 3:
        diversification_penalty = 30
    elif num_holdings < 5:
        diversification_penalty = 20
    elif num_holdings < 8:
        diversification_penalty = 10
    else:
        diversification_penalty = 0
    
    score -= diversification_penalty
    breakdown.append({
        "factor": "Diversification",
        "penalty": -diversification_penalty,
        "reason": f"{num_holdings} holdings"
    })
    
    # Final score
    score = max(0, min(100, round(score, 0)))
    
    # Assign grade
    if score >= 90:
        grade, status = "A", "EXCELLENT"
    elif score >= 80:
        grade, status = "B", "GOOD"
    elif score >= 70:
        grade, status = "C", "FAIR"
    elif score >= 60:
        grade, status = "D", "POOR"
    else:
        grade, status = "F", "CRITICAL"
    
    state['health_score'] = {
        "score": int(score),
        "grade": grade,
        "status": status,
        "breakdown": breakdown
    }
    
    print(f"✅ [Node: Health Score] Score: {score}/100 (Grade {grade})")
    
    # Decide next action based on score
    if score < 70:
        state['next_action'] = 'generate_rebalancing'
    else:
        state['next_action'] = 'generate_recommendations'
    
    return state


def generate_rebalancing_plan(state: PortfolioState) -> PortfolioState:
    """
    Generate specific rebalancing recommendations
    """
    print("🔄 [Node: Rebalancing Plan] Creating plan")
    
    allocation = state['allocation_analysis']
    cash_savings = state['cash_savings']
    target = allocation['target']
    current = allocation['current']
    total_assets = allocation['totalAssets']
    
    plan = {
        "summary": "",
        "cashDeployment": [],
        "sells": [],
        "expectedResult": {}
    }
    
    # Deploy excess cash
    excess_cash = cash_savings - (total_assets * target['cash'] / 100)
    
    if excess_cash > 1000:
        # Calculate needed amounts
        needed_bonds = (total_assets * target['bonds'] / 100) - (total_assets * current['bonds'] / 100)
        needed_stocks = (total_assets * target['stocks'] / 100) - (total_assets * current['stocks'] / 100)
        
        if needed_bonds > 0:
            bond_amount = min(excess_cash, needed_bonds)
            plan['cashDeployment'].append({
                "action": "BUY",
                "symbol": "BND",
                "name": "Vanguard Total Bond Market ETF",
                "amount": round(bond_amount, 2),
                "reason": f"Add bond allocation ({current['bonds']:.0f}% → {target['bonds']:.0f}%)",
                "priority": "HIGH"
            })
            excess_cash -= bond_amount
        
        if excess_cash > 1000 and needed_stocks > 0:
            plan['cashDeployment'].append({
                "action": "BUY",
                "symbol": "VTI",
                "name": "Vanguard Total Stock Market ETF",
                "amount": round(excess_cash * 0.7, 2),
                "reason": "Diversify US stock exposure",
                "priority": "HIGH"
            })
    
    total_to_deploy = sum(item['amount'] for item in plan['cashDeployment'])
    plan['summary'] = f"Deploy ${total_to_deploy:,.0f} from cash reserves" if total_to_deploy > 0 else "No major changes needed"
    
    state['rebalancing_plan'] = plan
    
    print(f"✅ [Node: Rebalancing Plan] {plan['summary']}")
    
    state['next_action'] = 'generate_recommendations'
    return state


def generate_recommendations(state: PortfolioState) -> PortfolioState:
    """
    Generate prioritized actionable recommendations
    """
    print("🔄 [Node: Recommendations] Creating action items")
    
    recommendations = []
    
    allocation = state['allocation_analysis']
    health = state['health_score']
    issues = allocation['issues']
    
    # HIGH PRIORITY: Critical drift
    if allocation['drift'] > 20:
        recommendations.append({
            "priority": "HIGH",
            "category": "REBALANCING",
            "title": "Critical Portfolio Drift Detected",
            "description": f"Your portfolio is {allocation['drift']:.0f}% off target",
            "action": "Review rebalancing plan",
            "impact": "Restore risk profile alignment"
        })
    
    # HIGH PRIORITY: Excess cash
    if "EXCESS_CASH" in issues:
        cash_pct = allocation['current']['cash']
        recommendations.append({
            "priority": "HIGH",
            "category": "CASH",
            "title": "Deploy Idle Cash",
            "description": f"{cash_pct:.0f}% in cash is not working for you",
            "action": "Invest excess cash per rebalancing plan",
            "impact": "Increase potential returns"
        })
    
    # MEDIUM PRIORITY: Low diversification
    if len(state['holdings']) < 5:
        recommendations.append({
            "priority": "MEDIUM",
            "category": "DIVERSIFICATION",
            "title": "Increase Diversification",
            "description": f"Portfolio has only {len(state['holdings'])} holdings",
            "action": "Add 2-3 ETFs across different sectors",
            "impact": "Reduce portfolio risk"
        })
    
    # Sort by priority
    priority_rank = {"HIGH": 1, "MEDIUM": 2, "LOW": 3}
    recommendations.sort(key=lambda x: priority_rank.get(x['priority'], 99))
    
    state['recommendations'] = recommendations
    
    print(f"✅ [Node: Recommendations] Generated {len(recommendations)} recommendations")
    
    state['next_action'] = 'complete'
    return state


def handle_error(state: PortfolioState) -> PortfolioState:
    """
    Handle any errors in the workflow
    """
    print("❌ [Node: Error] Handling workflow errors")
    
    errors = state.get('errors', ['Unknown error occurred'])
    
    print(f"❌ Errors: {', '.join(errors)}")
    
    state['next_action'] = 'end'
    return state


# ==================== ROUTING LOGIC ====================

def route_next_action(state: PortfolioState) -> Literal["select_model", "analyze_allocation", "calculate_health", 
                                                         "generate_rebalancing", "generate_recommendations", 
                                                         "error", "complete"]:
    """
    Route to next node based on state
    """
    next_action = state.get('next_action', 'error')
    
    if next_action == 'error':
        return 'error'
    elif next_action == 'complete':
        return 'complete'
    else:
        return next_action


# ==================== BUILD GRAPH ====================

def create_portfolio_analysis_graph() -> StateGraph:
    """
    Create the Strand portfolio analysis graph
    
    Workflow:
    1. Initialize → 2. Select Model → 3. Analyze Allocation → 
    4. Calculate Health → 5. Generate Rebalancing (if needed) → 
    6. Generate Recommendations → Complete
    """
    
    workflow = StateGraph(PortfolioState)
    
    # Add nodes
    workflow.add_node("initialize", initialize_analysis)
    workflow.add_node("select_model", select_model_portfolio)
    workflow.add_node("analyze_allocation", analyze_allocation)
    workflow.add_node("calculate_health", calculate_health_score)
    workflow.add_node("generate_rebalancing", generate_rebalancing_plan)
    workflow.add_node("generate_recommendations", generate_recommendations)
    workflow.add_node("error", handle_error)
    
    # Set entry point
    workflow.set_entry_point("initialize")
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "initialize",
        route_next_action,
        {
            "select_model": "select_model",
            "error": "error"
        }
    )
    
    workflow.add_conditional_edges(
        "select_model",
        route_next_action,
        {
            "analyze_allocation": "analyze_allocation"
        }
    )
    
    workflow.add_conditional_edges(
        "analyze_allocation",
        route_next_action,
        {
            "calculate_health": "calculate_health"
        }
    )
    
    workflow.add_conditional_edges(
        "calculate_health",
        route_next_action,
        {
            "generate_rebalancing": "generate_rebalancing",
            "generate_recommendations": "generate_recommendations"
        }
    )
    
    workflow.add_conditional_edges(
        "generate_rebalancing",
        route_next_action,
        {
            "generate_recommendations": "generate_recommendations"
        }
    )
    
    workflow.add_conditional_edges(
        "generate_recommendations",
        route_next_action,
        {
            "complete": END
        }
    )
    
    workflow.add_edge("error", END)
    
    print("✅ Portfolio Analysis Graph created")
    
    return workflow.compile()


# ==================== USAGE EXAMPLE ====================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🧪 Testing Portfolio Analysis Graph")
    print("=" * 60 + "\n")
    
    # Create graph
    graph = create_portfolio_analysis_graph()
    
    # Mock state
    mock_state = {
        "user_email": "test@example.com",
        "user_profile": {
            "user": {
                "age": 35,
                "riskTolerance": "Moderate"
            }
        },
        "market_data": {
            "success": True,
            "holdings": [
                {"symbol": "AAPL", "currentValue": 5000, "portfolioWeight": 50, "type": "stock"},
                {"symbol": "GOOGL", "currentValue": 3000, "portfolioWeight": 30, "type": "stock"}
            ],
            "cashSavings": 2000
        },
        "messages": []
    }
    
    # Run graph
    result = graph.invoke(mock_state)
    
    print("\n" + "=" * 60)
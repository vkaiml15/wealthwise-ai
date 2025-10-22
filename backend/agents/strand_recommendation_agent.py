
import os
import json
import boto3
from typing import Dict, Any, List
from decimal import Decimal
from datetime import datetime
from dotenv import load_dotenv
from strands import Agent
from strands.models import BedrockModel

load_dotenv()

bedrock_client = boto3.client(
    service_name='bedrock-runtime',
    region_name=os.getenv('AWS_REGION', 'us-east-1')
)

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


def parse_investment_horizon(horizon_str):
    """
    Safely parse investment horizon string to extract numeric value
    
    Args:
        horizon_str: String like '5-10', '10+', '1-3', etc.
    
    Returns:
        int: The first/lower bound number from the horizon
    """
    if not horizon_str:
        return 5  # Default fallback
    
    horizon_str = str(horizon_str).strip()
    
    # Handle '10+' case
    if '+' in horizon_str:
        return int(horizon_str.replace('+', ''))
    
    # Handle '5-10' case
    if '-' in horizon_str:
        return int(horizon_str.split('-')[0])
    
    # Handle pure number case
    try:
        return int(horizon_str)
    except ValueError:
        return 5  # Default fallback


def analyze_market_context(market_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze current market conditions to contextualize recommendations
    """
    if not market_data:
        return {
            'market_available': False,
            'message': 'Real-time market data not available'
        }
    
    analysis = {
        'market_available': True,
        'timestamp': market_data.get('timestamp', datetime.now().isoformat()),
        'indices': {},
        'volatility': {},
        'sentiment': 'neutral'
    }
    
    # Analyze indices
    indices = market_data.get('indices', {})
    for idx_name, idx_data in indices.items():
        change_pct = float(idx_data.get('changePercent', 0))
        analysis['indices'][idx_name] = {
            'value': float(idx_data.get('value', 0)),
            'change': float(idx_data.get('change', 0)),
            'changePercent': change_pct,
            'trend': 'bullish' if change_pct > 1 else 'bearish' if change_pct < -1 else 'neutral'
        }
    
    # Calculate volatility indicator
    vix = market_data.get('vix', {})
    if vix:
        vix_value = float(vix.get('value', 15))
        analysis['volatility'] = {
            'vix': vix_value,
            'level': 'high' if vix_value > 20 else 'moderate' if vix_value > 15 else 'low',
            'interpretation': 'Market fear is high' if vix_value > 20 else 'Market is calm'
        }
    
    # Overall market sentiment
    avg_change = sum(idx['changePercent'] for idx in analysis['indices'].values()) / len(analysis['indices']) if analysis['indices'] else 0
    analysis['sentiment'] = 'bullish' if avg_change > 0.5 else 'bearish' if avg_change < -0.5 else 'neutral'
    
    return analysis


def generate_recommendations_with_calculations(
    user_profile: Dict[str, Any],
    portfolio: Dict[str, Any],
    market_data: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Generate recommendations with detailed calculations, market context, and reasoning
    """
    
    recommendations = {
        'immediate': [],
        'short_term': [],
        'long_term': [],
        'opportunities': []
    }
    
    # Analyze market context
    market_context = analyze_market_context(market_data)
    
    # Extract user metadata
    required_fields = ['name', 'email', 'age', 'riskTolerance', 'investmentHorizon', 'investmentGoal', 'monthlyContribution']
    filled_fields = sum(1 for field in required_fields if user_profile.get(field))
    has_risk_analysis = bool(user_profile.get('riskAnalysis', {}).get('riskScore'))
    profile_completion = int(((filled_fields / len(required_fields)) * 70) + (30 if has_risk_analysis else 0))

    # Extract user metadata
    user_metadata = {
        'email': user_profile.get('email', 'N/A'),
        'name': user_profile.get('name', 'User'),
        'age': user_profile.get('age', 30),
        'occupation': user_profile.get('occupation', 'Professional'),
        'annual_income': float(user_profile.get('annualIncome', 0)),
        'risk_tolerance': user_profile.get('riskTolerance', 'moderate').lower(),
        'investment_horizon': user_profile.get('investmentHorizon', '5-10'),
        'investment_goals': user_profile.get('investmentGoals', [user_profile.get('investmentGoal', 'wealth_accumulation')]),
        'monthly_contribution': float(user_profile.get('monthlyContribution', 0)),
        'profile_completion': profile_completion  # Use calculated value
    }
    
    # Extract and analyze risk assessment
    risk_analysis = user_profile.get('riskAnalysis', None)
    has_risk_score = risk_analysis is not None
    
    if has_risk_score:
        risk_metadata = {
            'score': float(risk_analysis.get('riskScore', 5.0)),
            'label': risk_analysis.get('riskLabel', 'Moderate'),
            'recommendation': risk_analysis.get('recommendation', ''),
            'capacity': risk_analysis.get('riskCapacity', 'moderate'),
            'willingness': risk_analysis.get('riskWillingness', 'moderate'),
            'assessment_date': risk_analysis.get('assessmentDate', 'Not available'),
            'factors_considered': risk_analysis.get('factorsConsidered', [])
        }
    else:
        risk_metadata = {
            'score': None,
            'label': 'Not Assessed',
            'recommendation': 'Complete risk assessment for personalized advice',
            'capacity': 'unknown',
            'willingness': 'unknown'
        }
    
    # Portfolio metrics with detailed analysis
    stocks = portfolio.get('stocks', [])
    bonds = portfolio.get('bonds', [])
    etfs = portfolio.get('etfs', [])
    cash_savings = float(portfolio.get('cashSavings', 0))
    
    total_holdings = len(stocks) + len(bonds) + len(etfs)
    
    # Calculate portfolio value and allocation
    stock_value = sum(float(s.get('quantity', 0)) * float(s.get('avgPrice', 0)) for s in stocks)
    bond_value = sum(float(b.get('quantity', 0)) * float(b.get('avgPrice', 0)) for b in bonds)
    etf_value = sum(float(e.get('quantity', 0)) * float(e.get('avgPrice', 0)) for e in etfs)
    
    total_invested = stock_value + bond_value + etf_value
    total_value = total_invested + cash_savings
    
    # Calculate allocation percentages
    stock_percent = (stock_value / total_value * 100) if total_value > 0 else 0
    bond_percent = (bond_value / total_value * 100) if total_value > 0 else 0
    etf_percent = (etf_value / total_value * 100) if total_value > 0 else 0
    cash_percent = (cash_savings / total_value * 100) if total_value > 0 else 100
    
    portfolio_metadata = {
        'total_value': total_value,
        'total_holdings': total_holdings,
        'allocation': {
            'stocks': {'count': len(stocks), 'value': stock_value, 'percent': stock_percent},
            'bonds': {'count': len(bonds), 'value': bond_value, 'percent': bond_percent},
            'etfs': {'count': len(etfs), 'value': etf_value, 'percent': etf_percent},
            'cash': {'value': cash_savings, 'percent': cash_percent}
        }
    }
    
    # === DIVERSIFICATION ANALYSIS WITH XAI ===
    if total_holdings < 5:
        target_holdings = 8
        gap = target_holdings - total_holdings
        
        # XAI: Explain the reasoning with user context
        xai_reasoning = f"""
**Why this matters for {user_metadata['name']}:**
- Your current {total_holdings} holdings create concentration risk
- At age {user_metadata['age']} with {user_metadata['investment_horizon']} year horizon, you need more diversification
- With {user_metadata['risk_tolerance']} risk tolerance, optimal range is 8-12 holdings
        
**Market Context:**
- Current market sentiment: {market_context.get('sentiment', 'neutral').upper()}
- Market volatility: {market_context.get('volatility', {}).get('level', 'moderate').upper()}
- {f"This {'volatile' if market_context.get('volatility', {}).get('level') == 'high' else 'stable'} environment makes diversification even more critical" if market_context['market_available'] else 'Market conditions support diversification'}

**Evidence-Based Impact:**
Studies show that portfolios with 8-12 holdings achieve 90% of maximum diversification benefits. 
Your concentration level puts ₹{total_value:,.0f} at higher risk than necessary.
"""
        
        recommendations['immediate'].append({
            'type': 'diversification',
            'priority': 'high',
            'title': 'Increase Portfolio Diversification',
            'description': f'{user_metadata["name"]}, with only {total_holdings} holdings, your ₹{total_value:,.0f} portfolio is highly concentrated.',
            'action': f'Add {gap} more diverse assets across different sectors',
            'impact': 'Reduce volatility by 15-25% while maintaining returns',
            'timeframe': 'Next 2 weeks',
            'user_context': {
                'name': user_metadata['name'],
                'age': user_metadata['age'],
                'risk_profile': f"{risk_metadata['label']} ({risk_metadata['score']}/10)" if has_risk_score else user_metadata['risk_tolerance'],
                'investment_horizon': user_metadata['investment_horizon'],
                'current_exposure': f'₹{total_value:,.0f} spread across only {total_holdings} assets'
            },
            'market_context': market_context,
            'metrics': [
                {'label': 'Current Holdings', 'value': f'{total_holdings}', 'change': None},
                {'label': 'Target Holdings', 'value': f'{target_holdings}', 'change': None},
                {'label': 'Gap', 'value': f'{gap}', 'change': None},
                {'label': 'Risk Reduction', 'value': '20%', 'change': None}
            ],
            'calculation': {
                'currentState': {
                    'Total Holdings': f'{total_holdings} assets',
                    'Stocks': f'{len(stocks)}',
                    'Bonds': f'{len(bonds)}',
                    'ETFs': f'{len(etfs)}',
                    'Total Value': f'₹{total_value:,.0f}',
                    'Concentration Risk': 'HIGH'
                },
                'targetState': {
                    'Recommended Holdings': f'{target_holdings} assets',
                    'Additional Needed': f'{gap} more',
                    'Expected Risk Level': 'MODERATE',
                    'Diversification Benefit': '90% of maximum'
                },
                'formula': 'Optimal Diversification = 8-12 holdings across different sectors and asset classes',
                'gap': f'You need {gap} more holdings to reach minimum diversification threshold',
                'user_specific_impact': f'For {user_metadata["name"]} (Age: {user_metadata["age"]}, Risk: {risk_metadata["label"]}), this concentration level is suboptimal'
            },
            'xai_explanation': xai_reasoning,
            'reasoning': f'With only {total_holdings} holdings representing ₹{total_value:,.0f}, your portfolio faces significant concentration risk. Research shows diversification benefits peak at 8-12 holdings, reducing unsystematic risk by 70%. Given your {risk_metadata["label"]} risk profile and {user_metadata["investment_horizon"]} year horizon, adding {gap} carefully selected holdings is crucial.',
            'steps': [
                f'Analyze your {len(stocks)} current stock(s) - identify missing sectors',
                f'Select {gap} high-quality assets from underrepresented sectors',
                f'Allocate ₹{(total_value * 0.15):,.0f} (15% of portfolio) to each new position',
                'Ensure no single holding exceeds 20% of total portfolio',
                f'Review allocation quarterly given {market_context.get("volatility", {}).get("level", "moderate")} market volatility'
            ],
            'expectedOutcome': f'By diversifying to {target_holdings} holdings, {user_metadata["name"]} will reduce portfolio volatility by ~20% while still capturing market returns. This creates a smoother investment experience aligned with your {risk_metadata["label"]} risk tolerance.'
        })
    
    # === ASSET ALLOCATION WITH MARKET-AWARE XAI ===
    # Calculate target allocation based on risk score
    if has_risk_score:
        risk_score = risk_metadata['score']
        if risk_score >= 7:
            target_stocks, target_bonds = 80, 15
        elif risk_score >= 5:
            target_stocks, target_bonds = 70, 25
        elif risk_score >= 3:
            target_stocks, target_bonds = 50, 40
        else:
            target_stocks, target_bonds = 30, 60
    else:
        # Age-based rule
        target_stocks = max(30, min(90, 100 - user_metadata['age']))
        target_bonds = max(10, min(60, user_metadata['age'] - 10))
    
    # Adjust for market conditions
    market_adjustment = ''
    if market_context['market_available']:
        if market_context['sentiment'] == 'bearish' and market_context['volatility'].get('level') == 'high':
            target_bonds += 5
            target_stocks -= 5
            market_adjustment = f"Adjusted +5% bonds due to high market volatility (Inida VIX: {market_context['volatility'].get('vix', 'N/A')})"
    
    allocation_drift = abs(stock_percent - target_stocks)
    
    if allocation_drift > 15:
        stock_diff = target_stocks - stock_percent
        bond_diff = target_bonds - bond_percent
        
        rebalance_amount_stocks = (total_value * abs(stock_diff) / 100)
        rebalance_amount_bonds = (total_value * abs(bond_diff) / 100)
        
        xai_reasoning_allocation = f"""
**Personalized Analysis for {user_metadata['name']}:**
- Your {stock_percent:.0f}% stocks / {bond_percent:.0f}% bonds allocation is off-target
- Target: {target_stocks}% stocks / {target_bonds}% bonds (based on risk score {risk_metadata['score']}/10)
- Drift: {allocation_drift:.0f}% - this is significant and needs correction

**Your Risk Profile Context:**
- Risk Score: {risk_metadata['score']}/10 ({risk_metadata['label']})
- Risk Capacity: {risk_metadata['capacity'].upper()}
- Risk Willingness: {risk_metadata['willingness'].upper()}
- Investment Horizon: {user_metadata['investment_horizon']} years

**Market Context:**
- Market Sentiment: {market_context.get('sentiment', 'neutral').upper()}
- Volatility (India VIX): {market_context.get('volatility', {}).get('vix', 'N/A')} ({market_context.get('volatility', {}).get('level', 'moderate').upper()})
- {market_adjustment if market_adjustment else 'No market-based adjustments needed'}

**Why This Matters:**
Asset allocation determines 90% of portfolio returns. Your current misalignment could cost you 1-2% annually in risk-adjusted returns (approximately ₹{total_value * 0.015:,.0f}/year).
"""
        
        recommendations['short_term'].append({
            'type': 'rebalancing',
            'priority': 'high' if allocation_drift > 20 else 'medium',
            'title': 'Rebalance Asset Allocation',
            'description': f'{user_metadata["name"]}, your {stock_percent:.0f}%/{bond_percent:.0f}% stock/bond split is {allocation_drift:.0f}% off your optimal {target_stocks}%/{target_bonds}% allocation.',
            'action': f'{"Increase" if stock_diff > 0 else "Decrease"} stocks by ₹{rebalance_amount_stocks:,.0f}, {"increase" if bond_diff > 0 else "decrease"} bonds by ₹{rebalance_amount_bonds:,.0f}',
            'impact': f'Optimize risk-return for {risk_metadata["label"]} profile, potential +1.5% annual returns',
            'timeframe': '1-2 months',
            'user_context': {
                'name': user_metadata['name'],
                'risk_score': risk_metadata['score'],
                'risk_label': risk_metadata['label'],
                'age': user_metadata['age'],
                'portfolio_value': f'₹{total_value:,.0f}',
                'misalignment_cost': f'₹{total_value * 0.015:,.0f}/year'
            },
            'market_context': market_context,
            'metrics': [
                {'label': 'Current Stocks', 'value': f'{stock_percent:.0f}%', 'change': f'{stock_diff:+.0f}%'},
                {'label': 'Target Stocks', 'value': f'{target_stocks}%', 'change': None},
                {'label': 'Allocation Drift', 'value': f'{allocation_drift:.0f}%', 'change': None},
                {'label': 'Rebalance Amount', 'value': f'₹{rebalance_amount_stocks:,.0f}', 'change': None}
            ],
            'calculation': {
                'currentState': {
                    'Stocks': f'{stock_percent:.1f}% (₹{stock_value:,.0f})',
                    'Bonds': f'{bond_percent:.1f}% (₹{bond_value:,.0f})',
                    'Cash': f'{cash_percent:.1f}% (₹{cash_savings:,.0f})',
                    'Total Value': f'₹{total_value:,.0f}'
                },
                'targetState': {
                    'Target Stocks': f'{target_stocks}% (₹{total_value * target_stocks / 100:,.0f})',
                    'Target Bonds': f'{target_bonds}% (₹{total_value * target_bonds / 100:,.0f})',
                    'Target Cash': f'5% (₹{total_value * 0.05:,.0f})'
                },
                'formula': f'Target Allocation = Risk Score Based ({risk_metadata["score"]}/10) + Market Adjustment',
                'gap': f'Stocks: {stock_diff:+.1f}% (₹{rebalance_amount_stocks:,.0f}) | Bonds: {bond_diff:+.1f}% (₹{rebalance_amount_bonds:,.0f})',
                'user_specific_impact': f'For {user_metadata["name"]} with {risk_metadata["label"]} risk tolerance, this {allocation_drift:.0f}% drift creates suboptimal risk-return tradeoff'
            },
            'xai_explanation': xai_reasoning_allocation,
            'reasoning': f'Your current {stock_percent:.0f}/{bond_percent:.0f} allocation deviates {allocation_drift:.0f}% from your optimal {target_stocks}/{target_bonds} split. This misalignment is costing you approximately ₹{total_value * 0.015:,.0f} annually in suboptimal risk-adjusted returns. Given the current {market_context.get("sentiment", "neutral")} market and your {risk_metadata["label"]} risk profile, realignment is crucial.',
            'steps': [
                f'Review current holdings - you have ₹{stock_value:,.0f} in stocks, ₹{bond_value:,.0f} in bonds',
                f'{"Sell" if stock_diff < 0 else "Buy"} ₹{rebalance_amount_stocks:,.0f} worth of {"stocks" if stock_diff > 0 else "bonds"}',
                f'{"Buy" if bond_diff > 0 else "Sell"} ₹{rebalance_amount_bonds:,.0f} worth of bonds',
                f'Consider tax implications - use tax-loss harvesting if selling at loss',
                f'Execute gradually over 4-6 weeks given {market_context.get("volatility", {}).get("level", "moderate")} volatility'
            ],
            'expectedOutcome': f'Realigning to {target_stocks}/{target_bonds} optimizes your portfolio for {risk_metadata["label"]} risk tolerance. Expected improvement: +1.5% annual returns with {"lower" if stock_diff < 0 else "appropriate"} volatility. For your ₹{total_value:,.0f} portfolio, that\'s ₹{total_value * 0.015:,.0f} more per year.'
        })
    
    # === CASH DEPLOYMENT WITH INFLATION CONTEXT ===
    if cash_percent > 20:
        deployable_cash = cash_savings * 0.7
        
        # Get current inflation rate from market data or use default
        inflation_rate = market_data.get('inflation_rate', 6.0) / 100 if market_data else 0.06
        expected_market_return = market_data.get('expected_return', 10.0) / 100 if market_data else 0.10
        
        inflation_loss_annual = cash_savings * inflation_rate
        potential_gain = deployable_cash * expected_market_return
        net_opportunity = potential_gain + (deployable_cash * inflation_rate)
        
        xai_reasoning_cash = f"""
**Your Cash Situation, {user_metadata['name']}:**
- Holding: ₹{cash_savings:,.0f} ({cash_percent:.1f}% of ₹{total_value:,.0f} portfolio)
- Recommended: 5-10% (₹{total_value * 0.075:,.0f})
- Excess: ₹{cash_savings - (total_value * 0.10):,.0f}

**Real Cost of Cash Today:**
- Current Inflation: {inflation_rate * 100:.1f}%
- Annual Purchasing Power Loss: ₹{inflation_loss_annual:,.0f}
- Expected Market Return: {expected_market_return * 100:.1f}%
- Opportunity Cost: ₹{net_opportunity:,.0f}/year

**Market Environment:**
- Market Sentiment: {market_context.get('sentiment', 'neutral').upper()}
- Now is a {"good" if market_context.get('sentiment') != 'bearish' else "strategic"} time to deploy cash
- India VIX: {market_context.get('volatility', {}).get('vix', 'N/A')} - {"Consider dollar-cost averaging" if market_context.get('volatility', {}).get('level') == 'high' else "Market conditions favorable"}

**Impact on Your Goals:**
For your {user_metadata['investment_horizon']} year horizon, keeping this cash idle means missing ₹{net_opportunity * parse_investment_horizon(user_metadata['investment_horizon']):,.0f} in potential compounded gains.
"""
        
        recommendations['immediate'].append({
            'type': 'deployment',
            'priority': 'high',
            'title': 'Deploy Excess Cash Immediately',
            'description': f'{user_metadata["name"]}, your ₹{cash_savings:,.0f} in cash ({cash_percent:.1f}%) is losing ₹{inflation_loss_annual:,.0f}/year to {inflation_rate*100:.1f}% inflation.',
            'action': f'Invest ₹{deployable_cash:,.0f} (70% of cash) in diversified index ETFs',
            'impact': f'Gain ₹{potential_gain:,.0f}/year instead of losing ₹{inflation_loss_annual:,.0f} - net benefit: ₹{net_opportunity:,.0f}/year',
            'timeframe': 'Next 7 days',
            'user_context': {
                'name': user_metadata['name'],
                'age': user_metadata['age'],
                'risk_profile': risk_metadata['label'],
                'cash_amount': f'₹{cash_savings:,.0f}',
                'annual_income': f'₹{user_metadata["annual_income"]:,.0f}',
                'investment_horizon': user_metadata['investment_horizon']
            },
            'market_context': market_context,
            'metrics': [
                {'label': 'Cash %', 'value': f'{cash_percent:.1f}%', 'change': '-15%'},
                {'label': 'To Deploy', 'value': f'₹{deployable_cash:,.0f}', 'change': None},
                {'label': 'Annual Opportunity', 'value': f'₹{net_opportunity:,.0f}', 'change': None},
                {'label': 'Inflation Loss', 'value': f'₹{inflation_loss_annual:,.0f}', 'change': None}
            ],
            'calculation': {
                'currentState': {
                    'Cash Holdings': f'₹{cash_savings:,.0f}',
                    'Cash Percentage': f'{cash_percent:.1f}%',
                    'Annual Inflation Loss': f'₹{inflation_loss_annual:,.0f} ({inflation_rate*100:.1f}% inflation)',
                    'Real Value Next Year': f'₹{cash_savings * (1 - inflation_rate):,.0f}'
                },
                'targetState': {
                    'Recommended Cash %': '5-10%',
                    'Amount to Invest': f'₹{deployable_cash:,.0f}',
                    'Remaining Cash': f'₹{cash_savings - deployable_cash:,.0f}',
                    'Expected Value Next Year': f'₹{(cash_savings - deployable_cash) + (deployable_cash * (1 + expected_market_return)):,.0f}'
                },
                'formula': f'Opportunity Cost = (Deployable × Market Return {expected_market_return*100:.1f}%) - (Cash × Inflation {inflation_rate*100:.1f}%)',
                'gap': f'Excess cash: ₹{cash_savings - (total_value * 0.10):,.0f} above 10% threshold',
                'user_specific_impact': f'For {user_metadata["name"]} earning ₹{user_metadata["annual_income"]:,.0f}/year, this idle cash represents {(cash_savings/user_metadata["annual_income"]*12) if user_metadata["annual_income"] > 0 else 0:.1f} months of income losing value'
            },
            'xai_explanation': xai_reasoning_cash,
            'reasoning': f'You\'re holding {cash_percent:.1f}% in cash - well above the optimal 5-10%. While it feels safe, this ₹{cash_savings:,.0f} is losing ₹{inflation_loss_annual:,.0f} annually to inflation. Given your {user_metadata["investment_horizon"]} year horizon and {risk_metadata["label"]} risk profile, deploying ₹{deployable_cash:,.0f} could generate ₹{net_opportunity:,.0f}/year in net benefits.',
            'steps': [
                f'Keep ₹{cash_savings * 0.3:,.0f} as emergency fund (3-6 months expenses)',
                f'Open low-cost index fund (Nifty 50 ETF - expense ratio <0.1%)',
                f'Given {market_context.get("volatility", {}).get("level", "moderate")} volatility, {"invest in 3 tranches over 4 weeks" if market_context.get("volatility", {}).get("level") == "high" else "invest ₹" + f"{deployable_cash:,.0f} immediately"}',
                f'Set up monthly SIP of ₹{user_metadata["monthly_contribution"]:,.0f} for future savings'
            ],
            'expectedOutcome': f'Deploying ₹{deployable_cash:,.0f} generates ₹{potential_gain:,.0f}/year at {expected_market_return*100:.1f}% returns vs losing ₹{inflation_loss_annual:,.0f} to inflation. Net annual benefit: ₹{net_opportunity:,.0f}. Over {user_metadata["investment_horizon"]} years: ₹{net_opportunity * parse_investment_horizon(user_metadata["investment_horizon"]):,.0f} total!'
        })
    
    elif cash_percent < 5 and total_value > 100000:
        emergency_fund_target = total_value * 0.10
        monthly_savings_needed = (emergency_fund_target - cash_savings) / 6
        
        recommendations['short_term'].append({
            'type': 'emergency_fund',
            'priority': 'medium',
            'title': 'Build Emergency Reserve',
            'description': f'{user_metadata["name"]}, your {cash_percent:.1f}% cash reserve is too low. Build 10% emergency fund.',
            'action': f'Save ₹{monthly_savings_needed:,.0f}/month for 6 months',
            'impact': 'Financial security without forced selling in emergencies',
            'timeframe': '6 months',
            'user_context': user_metadata,
            'market_context': market_context,
            'metrics': [
                {'label': 'Current Cash', 'value': f'₹{cash_savings:,.0f}', 'change': None},
                {'label': 'Target Fund', 'value': f'₹{emergency_fund_target:,.0f}', 'change': None},
                {'label': 'Monthly Saving', 'value': f'₹{monthly_savings_needed:,.0f}', 'change': None}
            ],
            'calculation': {
                'currentState': {
                    'Cash Reserve': f'₹{cash_savings:,.0f}',
                    'Percentage': f'{cash_percent:.1f}%'
                },
                'targetState': {
                    'Target Emergency Fund': f'₹{emergency_fund_target:,.0f} (10% of portfolio)',
                    'Gap to Fill': f'₹{emergency_fund_target - cash_savings:,.0f}'
                },
                'formula': 'Emergency Fund = 10% of Portfolio Value OR 3-6 months expenses',
                'gap': f'Need ₹{emergency_fund_target - cash_savings:,.0f} more in emergency fund',
                'reasoning': 'Without adequate cash reserves, you may be forced to sell investments at unfavorable times during emergencies, crystallizing losses and missing recovery gains.'
            },
            'reasoning': f'Your emergency fund of ₹{cash_savings:,.0f} ({cash_percent:.1f}% of portfolio) is below the recommended 10% minimum. This puts you at risk of having to liquidate investments during market downturns or emergencies, potentially locking in losses.',
            'steps': [
                f'Set monthly auto-transfer of ₹{monthly_savings_needed:,.0f} to liquid fund',
                'Reduce optional expenses to free up savings',
                f'Build to ₹{emergency_fund_target:,.0f} over 6 months',
                'Once complete, redirect excess to investments'
            ],
            'expectedOutcome': f'Building a ₹{emergency_fund_target:,.0f} emergency fund provides a safety net, preventing forced asset sales during downturns. This protects your long-term wealth building strategy.'
        })
    
    # === MONTHLY SIP RECOMMENDATION WITH CALCULATIONS ===
    if user_metadata['monthly_contribution'] == 0 or user_metadata['monthly_contribution'] < 5000:
        recommended_sip = max(5000, total_value * 0.02, user_metadata['annual_income'] * 0.10 / 12 if user_metadata['annual_income'] > 0 else 5000)
        recommended_sip = min(recommended_sip, 50000)  # Cap at 50k
        
        future_value_10y = recommended_sip * 12 * ((pow(1.12, 10) - 1) / 0.12) * 1.12
        future_value_20y = recommended_sip * 12 * ((pow(1.12, 20) - 1) / 0.12) * 1.12
        
        total_invested_10y = recommended_sip * 120
        gains_10y = future_value_10y - total_invested_10y
        
        xai_reasoning_sip = f"""
**SIP Recommendation for {user_metadata['name']}:**
- Current Monthly Investment: ₹{user_metadata["monthly_contribution"]:,.0f}
- Recommended SIP: ₹{recommended_sip:,.0f}/month (based on 10% of annual income)
- Annual Income: ₹{user_metadata["annual_income"]:,.0f}

**Power of Compounding for You:**
- 10 Years: ₹{future_value_10y:,.0f} (invested ₹{total_invested_10y:,.0f}, gained ₹{gains_10y:,.0f})
- 20 Years: ₹{future_value_20y:,.0f}
- Starting today vs 1 year later: ₹{future_value_10y * 0.12:,.0f} difference!

**Your Investment Goals:**
- Primary Goals: {', '.join(user_metadata['investment_goals'])}
- Investment Horizon: {user_metadata['investment_horizon']} years
- Risk Profile: {risk_metadata['label']}

**Why SIP Works:**
1. Rupee Cost Averaging - buy more units when market is down
2. Removes emotion from investing
3. Harnesses compounding
4. Builds discipline

Current {market_context.get('sentiment', 'neutral')} market makes this a {"great" if market_context.get('sentiment') == 'bearish' else "good"} entry point.
"""
        
        recommendations['long_term'].append({
            'type': 'systematic_investment',
            'priority': 'high',
            'title': 'Start Systematic Investment Plan (SIP)',
            'description': f'{user_metadata["name"]}, starting a ₹{recommended_sip:,.0f}/month SIP can build ₹{future_value_10y/100000:.1f}L in 10 years through compounding.',
            'action': f'Start monthly SIP of ₹{recommended_sip:,.0f} in diversified index fund',
            'impact': f'Build ₹{future_value_10y:,.0f} corpus in 10 years (gain ₹{gains_10y:,.0f} from ₹{total_invested_10y:,.0f} investment)',
            'timeframe': 'Start next month',
            'user_context': {
                'name': user_metadata['name'],
                'age': user_metadata['age'],
                'annual_income': f'₹{user_metadata["annual_income"]:,.0f}',
                'current_sip': f'₹{user_metadata["monthly_contribution"]:,.0f}',
                'goals': user_metadata['investment_goals'],
                'horizon': user_metadata['investment_horizon']
            },
            'market_context': market_context,
            'metrics': [
                {'label': 'Monthly SIP', 'value': f'₹{recommended_sip:,.0f}', 'change': None},
                {'label': '10Y Corpus', 'value': f'₹{future_value_10y/100000:.1f}L', 'change': None},
                {'label': 'Total Invested', 'value': f'₹{total_invested_10y/100000:.1f}L', 'change': None},
                {'label': 'Returns Gained', 'value': f'₹{gains_10y/100000:.1f}L', 'change': None}
            ],
            'calculation': {
                'currentState': {
                    'Monthly SIP': f'₹{user_metadata["monthly_contribution"]:,.0f}',
                    'Annual Investment': f'₹{user_metadata["monthly_contribution"] * 12:,.0f}'
                },
                'targetState': {
                    'Recommended SIP': f'₹{recommended_sip:,.0f}/month',
                    'Annual Investment': f'₹{recommended_sip * 12:,.0f}',
                    'Percentage of Income': f'{(recommended_sip * 12 / user_metadata["annual_income"] * 100) if user_metadata["annual_income"] > 0 else 0:.1f}%'
                },
                'formula': 'FV = P × [((1+r)^n - 1) / r] × (1+r), where P=monthly SIP, r=12%/12, n=months',
                'calculations': {
                    '10_year': f'₹{recommended_sip:,.0f} × 120 months @ 12% = ₹{future_value_10y:,.0f}',
                    '20_year': f'₹{recommended_sip:,.0f} × 240 months @ 12% = ₹{future_value_20y:,.0f}',
                    'cost_of_delay_1y': f'₹{future_value_10y * 0.12:,.0f} lost by waiting 1 year'
                },
                'gap': f'Starting today vs delaying = ₹{future_value_10y * 0.12:,.0f} difference',
                'user_specific_impact': f'For {user_metadata["name"]} earning ₹{user_metadata["annual_income"]:,.0f}/year, this {(recommended_sip * 12 / user_metadata["annual_income"] * 100) if user_metadata["annual_income"] > 0 else 0:.1f}% savings rate builds substantial wealth'
            },
            'xai_explanation': xai_reasoning_sip,
            'reasoning': f'You\'re currently investing ₹{user_metadata["monthly_contribution"]:,.0f}/month. A ₹{recommended_sip:,.0f}/month SIP (10% of your ₹{user_metadata["annual_income"]:,.0f} income) can build ₹{future_value_10y:,.0f} in 10 years through compounding at 12% returns. Starting today vs waiting 1 year means ₹{future_value_10y * 0.12:,.0f} more wealth due to compound interest.',
            'steps': [
                f'Choose low-cost index fund (Nifty 50 or Total Market - expense ratio <0.15%)',
                f'Set up auto-debit of ₹{recommended_sip:,.0f} on salary date (5th or 10th)',
                f'Start with ₹{recommended_sip:,.0f}, increase by 10% annually (step-up SIP)',
                'Never stop during market corrections - that\'s when you buy cheap!',
                f'Current {market_context.get("sentiment", "neutral")} market sentiment makes this a {"excellent" if market_context.get("sentiment") == "bearish" else "good"} starting point'
            ],
            'expectedOutcome': f'₹{recommended_sip:,.0f}/month SIP: 10Y = ₹{future_value_10y:,.0f}, 20Y = ₹{future_value_20y:,.0f}. You invest ₹{total_invested_10y:,.0f} but gain ₹{gains_10y:,.0f} from compound returns (12% CAGR). That\'s {(gains_10y/total_invested_10y*100):.0f}% returns on your investment!'
        })
    
    # === RISK ASSESSMENT COMPLETION ===
    if not has_risk_score or profile_completion < 80:
        recommendations['immediate'].append({
            'type': 'profile_completion',
            'priority': 'high',
            'title': 'Complete Risk Assessment for Personalized Advice',
            'description': f'{user_metadata["name"]}, your profile is {user_metadata["profile_completion"]}% complete. Complete risk assessment for truly personalized recommendations.',
            'action': 'Complete the 5-minute risk tolerance questionnaire',
            'impact': 'Get recommendations tailored to YOUR specific risk capacity and willingness',
            'timeframe': 'Today',
            'user_context': user_metadata,
            'market_context': market_context,
            'metrics': [
                {'label': 'Profile Complete', 'value': f'{user_metadata["profile_completion"]}%', 'change': '+20%'},
                {'label': 'Risk Assessment', 'value': 'Incomplete' if not has_risk_score else 'Complete', 'change': None}
            ],
            'xai_explanation': f"""
**Why This Matters, {user_metadata['name']}:**
Without a proper risk assessment, recommendations are based on generic age-based rules rather than YOUR specific:
- Financial capacity to take risk
- Emotional willingness to handle volatility  
- Life circumstances and obligations
- Investment timeline and goals

**Current Recommendations:**
Based on {"age " + str(user_metadata['age']) + " (generic rule)" if not has_risk_score else "your detailed risk profile"}

**With Risk Assessment:**
Recommendations will consider your income, obligations, experience, and personal comfort with market swings.

This 5-minute assessment can optimize your portfolio for YOUR unique situation, potentially improving returns by 1-3% annually through better risk alignment.
""",
            'reasoning': f'Your recommendations are currently based on {"generic age-based rules" if not has_risk_score else "incomplete profile data"}. Completing the risk assessment allows us to optimize your ₹{total_value:,.0f} portfolio for YOUR specific risk capacity and willingness, not just generic guidelines.',
            'steps': [
                'Click on "Complete Risk Assessment" in your profile',
                'Answer 10 questions about your financial situation and comfort with volatility',
                'Takes only 5 minutes to complete',
                'Receive personalized risk score and updated recommendations immediately'
            ],
            'expectedOutcome': 'Personalized recommendations that match your financial capacity and emotional comfort with risk, leading to better investment decisions and outcomes.'
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
        'user_metadata': user_metadata,
        'risk_metadata': risk_metadata,
        'portfolio_metadata': portfolio_metadata,
        'market_context': market_context,
        'explainability': {
            'personalization_factors': [
                f'Age: {user_metadata["age"]} years',
                f'Risk Profile: {risk_metadata["label"]} ({risk_metadata["score"]}/10)' if has_risk_score else 'Risk Profile: Not Assessed',
                f'Investment Horizon: {user_metadata["investment_horizon"]} years',
                f'Income Level: ₹{user_metadata["annual_income"]:,.0f}/year',
                f'Portfolio Size: ₹{total_value:,.0f}',
                f'Current Allocation: {stock_percent:.0f}% stocks, {bond_percent:.0f}% bonds, {cash_percent:.0f}% cash'
            ],
            'market_factors': [
                f'Market Sentiment: {market_context.get("sentiment", "neutral").upper()}',
                f'Volatility: {market_context.get("volatility", {}).get("level", "moderate").upper()}',
                f'India VIX: {market_context.get("volatility", {}).get("vix", "N/A")}'
            ] if market_context['market_available'] else ['Market data not available - using historical averages'],
            'methodology': 'Recommendations combine Nobel Prize-winning Modern Portfolio Theory, behavioral finance principles, and real-time market data to provide personalized, evidence-based advice.'
        }
    }


def get_recommendation_agent():
    """
    Initialize Strand Agent for AI-powered insights with XAI focus
    
    This is the SYSTEM PROMPT that guides the AI agent's behavior.
    Modify this prompt to change how the AI generates insights.
    """
    bedrock_model = BedrockModel(
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        client=bedrock_client
    )
    
    # ============================================================================
    # AGENT SYSTEM PROMPT - Customize AI Behavior Here
    # ============================================================================
    system_prompt = """You are WealthWise AI, an expert financial advisor focused on Explainable AI (XAI).

Your role is to provide a brief, personalized summary (4-5 sentences) that highlights:
1. WHO the user is (name, age, key characteristics)
2. WHAT their biggest opportunity is (with specific numbers)
3. WHY it matters to THEM specifically (personalized reasoning)
4. WHAT impact they can expect (concrete outcomes)

Critical XAI Principles:
- Always mention the user by name
- Reference their specific situation (age, risk profile, income, goals)
- Use actual numbers from their portfolio
- Explain the reasoning chain: Current State → Why Change Needed → Expected Outcome
- Make it relatable with analogies when helpful
- Show how market conditions affect the recommendation

Example tone:
"Hey Rajesh! At 32 with a Moderate risk profile (6/10), your biggest opportunity is deploying that ₹3 lakh sitting in cash - it's losing ₹18,000/year to 6% inflation! Given today's neutral market conditions (India VIX at 15), investing 70% of it (₹2.1L) into a Nifty 50 ETF could generate ₹21,000/year instead. That's a ₹39,000 annual swing from just putting your money to work. For your 10-15 year investment horizon, this delay costs you ₹3.9 lakh over a decade!"

Key Requirements:
- ALWAYS use the user's name
- ALWAYS reference their specific numbers
- ALWAYS explain the "why" behind recommendations
- ALWAYS mention their risk profile
- ALWAYS quantify the impact
- Keep it conversational and encouraging
- Focus on the #1 most impactful action

Tone Guidelines:
- Friendly but professional
- Encouraging and motivating
- Data-driven and specific
- Clear about cause-and-effect relationships
- Transparent about assumptions and reasoning"""
    
    agent = Agent(
        model=bedrock_model,
        system_prompt=system_prompt
    )
    
    return agent


def generate_ai_recommendations(user_email: str, user_profile: Dict, portfolio: Dict, market_data: Dict = None) -> Dict[str, Any]:
    """
    Generate complete recommendations with AI insights, detailed calculations, and XAI
    """
    print("=" * 80)
    print(f"💡 Enhanced AI Recommendation Generation with Explainable AI (XAI)")
    print(f"👤 User: {user_email}")
    print(f"📊 Market Data: {'Available' if market_data else 'Using defaults'}")
    print("=" * 80)
    
    try:
        # 1. Generate structured recommendations with calculations and market context
        structured_recs = generate_recommendations_with_calculations(
            user_profile, 
            portfolio, 
            market_data
        )
        
        print(f"✅ Generated {structured_recs['total_count']} recommendations with detailed calculations")
        print(f"   - Immediate: {structured_recs['summary']['immediate_actions']}")
        print(f"   - Short-term: {structured_recs['summary']['short_term_actions']}")
        print(f"   - Long-term: {structured_recs['summary']['long_term_goals']}")
        
        # 2. Extract metadata for XAI
        user_meta = structured_recs['user_metadata']
        risk_meta = structured_recs['risk_metadata']
        portfolio_meta = structured_recs['portfolio_metadata']
        market_ctx = structured_recs['market_context']
        
        print(f"\n📋 User Profile:")
        print(f"   - Name: {user_meta['name']}, Age: {user_meta['age']}")
        print(f"   - Risk: {risk_meta['label']} ({risk_meta['score']}/10)" if risk_meta['score'] else f"   - Risk: Not Assessed")
        print(f"   - Portfolio: ₹{portfolio_meta['total_value']:,.0f}")
        print(f"   - Allocation: {portfolio_meta['allocation']['stocks']['percent']:.0f}% stocks, {portfolio_meta['allocation']['bonds']['percent']:.0f}% bonds, {portfolio_meta['allocation']['cash']['percent']:.0f}% cash")
        
        if market_ctx['market_available']:
            print(f"\n📈 Market Context:")
            print(f"   - Sentiment: {market_ctx.get('sentiment', 'N/A').upper()}")
            print(f"   - Volatility: {market_ctx.get('volatility', {}).get('level', 'N/A').upper()}")
            print(f"   - India VIX: {market_ctx.get('volatility', {}).get('vix', 'N/A')}")
        
        # 3. Get AI insights from Strands Agent with rich context
        agent = get_recommendation_agent()
        
        # Get top 3 recommendations across all categories
        all_recs = (
            structured_recs['recommendations']['immediate'][:2] +
            structured_recs['recommendations']['short_term'][:1]
        )
        
        # Build comprehensive context for AI with XAI focus
        ai_prompt = f"""Generate a personalized investment summary for this user:

USER PROFILE:
- Name: {user_meta['name']}
- Age: {user_meta['age']} years
- Occupation: {user_meta['occupation']}
- Annual Income: ₹{user_meta['annual_income']:,.0f}
- Risk Profile: {risk_meta['label']} (Score: {risk_meta['score']}/10)
- Risk Capacity: {risk_meta['capacity'].upper()}
- Risk Willingness: {risk_meta['willingness'].upper()}
- Investment Horizon: {user_meta['investment_horizon']} years
- Goals: {', '.join(user_meta['investment_goals'])}

PORTFOLIO DETAILS:
- Total Value: ₹{portfolio_meta['total_value']:,.0f}
- Holdings: {portfolio_meta['total_holdings']} assets
- Allocation:
  * Stocks: {portfolio_meta['allocation']['stocks']['percent']:.0f}% (₹{portfolio_meta['allocation']['stocks']['value']:,.0f})
  * Bonds: {portfolio_meta['allocation']['bonds']['percent']:.0f}% (₹{portfolio_meta['allocation']['bonds']['value']:,.0f})
  * Cash: {portfolio_meta['allocation']['cash']['percent']:.0f}% (₹{portfolio_meta['allocation']['cash']['value']:,.0f})
- Monthly SIP: ₹{user_meta['monthly_contribution']:,.0f}

MARKET ENVIRONMENT:
- Sentiment: {market_ctx.get('sentiment', 'neutral').upper()}
- Volatility (India VIX): {market_ctx.get('volatility', {}).get('vix', 'N/A')} ({market_ctx.get('volatility', {}).get('level', 'moderate').upper()})
- Market Trend: {', '.join([f"{k}: {v['trend']}" for k, v in market_ctx.get('indices', {}).items()])}

TOP RECOMMENDATIONS:
{json.dumps([{
    'priority': r['priority'],
    'title': r['title'],
    'action': r['action'],
    'impact': r['impact'],
    'key_numbers': [m['label'] + ': ' + m['value'] for m in r.get('metrics', [])[:3]]
} for r in all_recs], indent=2) if all_recs else 'Portfolio is well-optimized'}

EXPLAINABILITY FOCUS:
Provide a 4-5 sentence personalized summary that:
1. Addresses {user_meta['name']} by name
2. Highlights their most impactful opportunity with SPECIFIC NUMBERS
3. Explains WHY it matters given their {risk_meta['label']} risk profile and {user_meta['investment_horizon']} year horizon
4. References current market conditions ({market_ctx.get('sentiment', 'neutral')} sentiment)
5. Quantifies the expected financial impact in rupees

Make it conversational, encouraging, and crystal clear about the reasoning behind the recommendation."""
        
        print(f"\n🤖 Calling Strands Agent for XAI insights...")
        agent_result = agent(ai_prompt)
        
        # Extract text from AgentResult
        if hasattr(agent_result, 'content'):
            ai_insights = agent_result.content
        elif hasattr(agent_result, 'output'):
            ai_insights = agent_result.output
        elif hasattr(agent_result, 'text'):
            ai_insights = agent_result.text
        elif isinstance(agent_result, str):
            ai_insights = agent_result
        else:
            ai_insights = str(agent_result)
        
        print(f"✅ XAI insights generated: {len(ai_insights)} characters")
        print(f"\n💬 AI Insights Preview:")
        print(f"   {ai_insights[:200]}...")
        
        # 4. Build comprehensive response with XAI metadata
        response = {
            'success': True,
            'user_email': user_email,
            'timestamp': datetime.now().isoformat(),
            
            # Core recommendations with XAI
            'recommendations': structured_recs['recommendations'],
            'summary': structured_recs['summary'],
            
            # AI-generated insights
            'ai_insights': ai_insights,
            
            # Rich metadata for explainability
            'metadata': {
                'user': user_meta,
                'risk': risk_meta,
                'portfolio': portfolio_meta,
                'market': market_ctx
            },
            
            # Explainability information
            'explainability': structured_recs['explainability'],
            
            # Confidence scores
            'confidence': {
                'data_quality': {
                    'risk_assessment': 'high' if risk_meta['score'] else 'low',
                    'portfolio_data': 'high' if portfolio_meta['total_value'] > 0 else 'medium',
                    'market_data': 'high' if market_ctx['market_available'] else 'medium',
                    'user_profile': 'high' if user_meta['profile_completion'] > 70 else 'medium'
                },
                'recommendation_confidence': 'high' if (risk_meta['score'] and portfolio_meta['total_value'] > 0) else 'medium',
                'explanation': 'Confidence based on completeness of risk assessment, portfolio data, market data, and user profile'
            }
        }
        
        print(f"\n✅ Complete recommendation package generated")
        print(f"   - AI Insights: ✓")
        print(f"   - Detailed Calculations: ✓")
        print(f"   - XAI Explanations: ✓")
        print(f"   - Market Context: ✓")
        print(f"   - User Metadata: ✓")
        print("=" * 80)
        
        return response
        
    except Exception as e:
        print(f"❌ Error generating recommendations: {e}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }


# Utility function for frontend integration
def format_recommendation_for_display(recommendation: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format recommendation for frontend display with XAI highlights
    """
    return {
        'id': recommendation.get('type', 'unknown'),
        'priority': recommendation.get('priority', 'medium'),
        'title': recommendation.get('title', ''),
        'description': recommendation.get('description', ''),
        'action': recommendation.get('action', ''),
        'impact': recommendation.get('impact', ''),
        'timeframe': recommendation.get('timeframe', ''),
        'metrics': recommendation.get('metrics', []),
        
        # XAI-specific fields
        'userContext': recommendation.get('user_context', {}),
        'marketContext': recommendation.get('market_context', {}),
        'xaiExplanation': recommendation.get('xai_explanation', ''),
        'reasoning': recommendation.get('reasoning', ''),
        'calculation': recommendation.get('calculation', {}),
        'steps': recommendation.get('steps', []),
        'expectedOutcome': recommendation.get('expectedOutcome', '')
    }


if __name__ == "__main__":
    # Run example to demonstrate the enhanced system
    print("🚀 Running Enhanced Recommendation System Example\n")
    
    if result['success']:
        print("\n" + "="*80)
        print("📊 RECOMMENDATION SUMMARY")
        print("="*80)
        print(f"\n{result['ai_insights']}")
        print(f"\n📈 Generated {result['summary']['immediate_actions']} immediate, "
              f"{result['summary']['short_term_actions']} short-term, and "
              f"{result['summary']['long_term_goals']} long-term recommendations")
        print(f"\n✅ Full results available in returned object")
    else:
        print(f"\n❌ Error: {result.get('error')}")
"""
Rebalancing Agent
Analyzes portfolio drift and provides rebalancing recommendations
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from .base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)


class RebalancingAgent(BaseAgent):
    """
    Agent responsible for analyzing portfolio allocation drift and 
    providing rebalancing recommendations with tax considerations
    """
    
    def __init__(self):
        super().__init__(
            agent_name="RebalancingAgent",
            model_id="anthropic.claude-3-5-sonnet-20241022-v2:0"
        )
        self.rebalancing_threshold = 5.0  # 5% drift triggers rebalancing
    
    def _get_system_prompt(self) -> str:
        return """You are a Portfolio Rebalancing Agent for WealthWise AI, specialized in 
analyzing portfolio drift and providing tax-efficient rebalancing strategies.

Your responsibilities:
1. Analyze current portfolio allocation vs. target allocation
2. Identify allocation drift and its implications
3. Provide specific rebalancing recommendations
4. Consider tax implications (capital gains)
5. Suggest tax-efficient rebalancing strategies
6. Calculate expected impact of rebalancing

Analysis Framework:
1. **Drift Analysis**: Compare current vs. target allocations
2. **Risk Assessment**: How drift affects overall portfolio risk
3. **Tax Impact**: Estimate capital gains taxes from rebalancing
4. **Rebalancing Strategy**: Specific buy/sell recommendations
5. **Alternative Approaches**: Tax-loss harvesting, new contributions, etc.
6. **Expected Outcomes**: Risk adjustment, return impact

Response Structure:
1. Executive Summary
   - Current vs Target allocation summary
   - Drift severity assessment
   - Recommendation urgency

2. Detailed Drift Analysis
   - Asset-by-asset comparison
   - Over/underweight positions
   - Risk implications

3. Tax Impact Assessment
   - Estimated capital gains
   - Tax-efficient alternatives
   - Optimal timing considerations

4. Rebalancing Recommendations
   - Specific actions (Buy/Sell/Hold)
   - Dollar amounts for each transaction
   - Order of operations

5. Expected Outcomes
   - New allocation percentages
   - Risk score changes
   - Cost-benefit analysis

Guidelines:
- Always consider tax implications first
- Prioritize tax-loss harvesting opportunities
- Consider using new contributions to rebalance
- Explain the reasoning behind each recommendation
- Provide both aggressive and gradual rebalancing options
- Highlight any positions that should NOT be sold due to tax implications

End with actionable next steps and a relevant follow-up question.
"""
    
    def _register_action_groups(self) -> List[Dict[str, Any]]:
        """Register action groups for rebalancing analysis"""
        return [
            {
                'name': 'calculate_allocation_drift',
                'description': 'Calculate drift between current and target allocations',
                'function': self._calculate_allocation_drift
            },
            {
                'name': 'assess_rebalancing_urgency',
                'description': 'Assess how urgently portfolio needs rebalancing',
                'function': self._assess_rebalancing_urgency
            },
            {
                'name': 'calculate_tax_impact',
                'description': 'Calculate tax implications of rebalancing',
                'function': self._calculate_tax_impact
            },
            {
                'name': 'generate_rebalancing_transactions',
                'description': 'Generate specific buy/sell transactions',
                'function': self._generate_rebalancing_transactions
            },
            {
                'name': 'identify_tax_loss_harvest_opportunities',
                'description': 'Find tax-loss harvesting opportunities',
                'function': self._identify_tax_loss_harvest_opportunities
            },
            {
                'name': 'calculate_risk_score_change',
                'description': 'Calculate how rebalancing affects risk score',
                'function': self._calculate_risk_score_change
            }
        ]
    
    def _calculate_allocation_drift(
        self,
        current_holdings: List[Dict[str, Any]],
        target_allocation: Dict[str, float]
    ) -> Dict[str, Any]:
        """Calculate drift between current and target allocations"""
        
        # Calculate total portfolio value
        total_value = sum(h['quantity'] * h['price'] for h in current_holdings)
        
        # Calculate current allocation by type
        current_allocation = {}
        for holding in current_holdings:
            asset_type = holding.get('type', 'Unknown')
            holding_value = holding['quantity'] * holding['price']
            allocation_pct = (holding_value / total_value) * 100
            
            if asset_type in current_allocation:
                current_allocation[asset_type] += allocation_pct
            else:
                current_allocation[asset_type] = allocation_pct
        
        # Calculate drift for each asset type
        drift_analysis = {}
        total_absolute_drift = 0
        
        for asset_type, target_pct in target_allocation.items():
            current_pct = current_allocation.get(asset_type, 0)
            drift = current_pct - target_pct
            drift_analysis[asset_type] = {
                'current': round(current_pct, 2),
                'target': round(target_pct, 2),
                'drift': round(drift, 2),
                'drift_dollars': round((drift / 100) * total_value, 2),
                'status': 'overweight' if drift > 0 else 'underweight' if drift < 0 else 'balanced'
            }
            total_absolute_drift += abs(drift)
        
        return {
            'total_portfolio_value': round(total_value, 2),
            'drift_analysis': drift_analysis,
            'total_absolute_drift': round(total_absolute_drift, 2),
            'needs_rebalancing': total_absolute_drift > self.rebalancing_threshold
        }
    
    def _assess_rebalancing_urgency(
        self,
        drift_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess how urgently portfolio needs rebalancing"""
        
        total_drift = drift_data.get('total_absolute_drift', 0)
        
        if total_drift < 5:
            urgency = 'low'
            recommendation = 'Portfolio is well-balanced. Consider rebalancing with new contributions.'
        elif total_drift < 10:
            urgency = 'moderate'
            recommendation = 'Portfolio has moderate drift. Rebalance within the next 1-2 months.'
        elif total_drift < 15:
            urgency = 'high'
            recommendation = 'Portfolio has significant drift. Rebalance within the next 2-4 weeks.'
        else:
            urgency = 'critical'
            recommendation = 'Portfolio is significantly out of balance. Rebalance as soon as possible.'
        
        return {
            'urgency_level': urgency,
            'total_drift_percentage': total_drift,
            'recommendation': recommendation,
            'risk_of_delay': self._assess_delay_risk(total_drift)
        }
    
    def _assess_delay_risk(self, drift: float) -> str:
        """Assess risk of delaying rebalancing"""
        if drift < 5:
            return 'Minimal risk. Portfolio maintains target risk profile.'
        elif drift < 10:
            return 'Low risk. Minor deviation from intended risk/return profile.'
        elif drift < 15:
            return 'Moderate risk. Portfolio may be exposed to unintended risk levels.'
        else:
            return 'High risk. Portfolio significantly deviates from target strategy.'
    
    def _calculate_tax_impact(
        self,
        holdings: List[Dict[str, Any]],
        transactions: List[Dict[str, Any]],
        tax_bracket: float = 0.15  # 15% capital gains by default
    ) -> Dict[str, Any]:
        """Calculate tax implications of rebalancing transactions"""
        
        total_capital_gains = 0
        total_capital_losses = 0
        taxable_positions = []
        
        for transaction in transactions:
            if transaction['action'] == 'sell':
                symbol = transaction['symbol']
                quantity = transaction['quantity']
                
                # Find the holding
                holding = next((h for h in holdings if h['symbol'] == symbol), None)
                if holding:
                    current_price = holding['price']
                    purchase_price = holding.get('purchasePrice', current_price)
                    
                    gain_per_share = current_price - purchase_price
                    total_gain = gain_per_share * quantity
                    
                    if total_gain > 0:
                        total_capital_gains += total_gain
                        taxable_positions.append({
                            'symbol': symbol,
                            'quantity': quantity,
                            'gain': round(total_gain, 2),
                            'tax_owed': round(total_gain * tax_bracket, 2)
                        })
                    else:
                        total_capital_losses += abs(total_gain)
        
        net_gains = total_capital_gains - total_capital_losses
        estimated_tax = max(0, net_gains * tax_bracket)
        
        return {
            'total_capital_gains': round(total_capital_gains, 2),
            'total_capital_losses': round(total_capital_losses, 2),
            'net_capital_gains': round(net_gains, 2),
            'estimated_tax': round(estimated_tax, 2),
            'tax_bracket': tax_bracket,
            'taxable_positions': taxable_positions,
            'tax_efficiency_score': self._calculate_tax_efficiency(
                total_capital_gains,
                total_capital_losses
            )
        }
    
    def _calculate_tax_efficiency(
        self,
        gains: float,
        losses: float
    ) -> str:
        """Calculate tax efficiency score"""
        if gains == 0:
            return 'excellent'
        elif losses >= gains * 0.5:
            return 'good'
        elif losses >= gains * 0.25:
            return 'moderate'
        else:
            return 'poor'
    
    def _generate_rebalancing_transactions(
        self,
        current_holdings: List[Dict[str, Any]],
        drift_analysis: Dict[str, Any],
        rebalancing_mode: str = 'tax-efficient'  # 'aggressive', 'tax-efficient', 'gradual'
    ) -> List[Dict[str, Any]]:
        """Generate specific buy/sell transactions to rebalance portfolio"""
        
        transactions = []
        total_value = drift_analysis.get('total_portfolio_value', 0)
        
        for asset_type, drift_info in drift_analysis.get('drift_analysis', {}).items():
            drift_dollars = drift_info['drift_dollars']
            
            if abs(drift_dollars) < 500:  # Ignore small drift amounts
                continue
            
            if drift_info['status'] == 'overweight':
                # Need to sell
                # Find holdings of this type
                holdings_to_reduce = [
                    h for h in current_holdings 
                    if h.get('type') == asset_type
                ]
                
                # Prioritize selling positions with losses (tax-loss harvesting)
                if rebalancing_mode == 'tax-efficient':
                    holdings_to_reduce.sort(
                        key=lambda h: h['price'] - h.get('purchasePrice', h['price'])
                    )
                
                remaining_to_sell = abs(drift_dollars)
                for holding in holdings_to_reduce:
                    if remaining_to_sell <= 0:
                        break
                    
                    holding_value = holding['quantity'] * holding['price']
                    sell_value = min(holding_value, remaining_to_sell)
                    sell_quantity = int(sell_value / holding['price'])
                    
                    if sell_quantity > 0:
                        transactions.append({
                            'action': 'sell',
                            'symbol': holding['symbol'],
                            'name': holding['name'],
                            'quantity': sell_quantity,
                            'price': holding['price'],
                            'value': round(sell_quantity * holding['price'], 2),
                            'reason': f'Reduce {asset_type} allocation',
                            'priority': 'high' if abs(drift_info['drift']) > 10 else 'medium'
                        })
                        remaining_to_sell -= sell_value
            
            elif drift_info['status'] == 'underweight':
                # Need to buy
                # Find a representative holding of this type or suggest new one
                sample_holdings = [
                    h for h in current_holdings 
                    if h.get('type') == asset_type
                ]
                
                if sample_holdings:
                    # Buy more of existing holdings
                    holding = sample_holdings[0]
                    buy_value = abs(drift_dollars)
                    buy_quantity = int(buy_value / holding['price'])
                    
                    if buy_quantity > 0:
                        transactions.append({
                            'action': 'buy',
                            'symbol': holding['symbol'],
                            'name': holding['name'],
                            'quantity': buy_quantity,
                            'price': holding['price'],
                            'value': round(buy_quantity * holding['price'], 2),
                            'reason': f'Increase {asset_type} allocation',
                            'priority': 'high' if abs(drift_info['drift']) > 10 else 'medium'
                        })
                else:
                    # Suggest new ETF for this asset type
                    etf_suggestions = {
                        'Stocks': {'symbol': 'VTI', 'name': 'Vanguard Total Stock Market ETF', 'price': 225.00},
                        'Bonds': {'symbol': 'BND', 'name': 'Vanguard Total Bond Market ETF', 'price': 78.00},
                        'ETFs': {'symbol': 'SPY', 'name': 'S&P 500 ETF', 'price': 450.00},
                        'Cash': {'symbol': 'CASH', 'name': 'Cash Reserve', 'price': 1.00}
                    }
                    
                    if asset_type in etf_suggestions:
                        etf = etf_suggestions[asset_type]
                        buy_value = abs(drift_dollars)
                        buy_quantity = int(buy_value / etf['price'])
                        
                        if buy_quantity > 0:
                            transactions.append({
                                'action': 'buy',
                                'symbol': etf['symbol'],
                                'name': etf['name'],
                                'quantity': buy_quantity,
                                'price': etf['price'],
                                'value': round(buy_quantity * etf['price'], 2),
                                'reason': f'Add {asset_type} allocation',
                                'priority': 'high'
                            })
        
        return transactions
    
    def _identify_tax_loss_harvest_opportunities(
        self,
        holdings: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identify positions that can be sold for tax-loss harvesting"""
        
        opportunities = []
        
        for holding in holdings:
            current_price = holding['price']
            purchase_price = holding.get('purchasePrice', current_price)
            
            loss_per_share = purchase_price - current_price
            if loss_per_share > 0:
                total_loss = loss_per_share * holding['quantity']
                loss_percentage = (loss_per_share / purchase_price) * 100
                
                opportunities.append({
                    'symbol': holding['symbol'],
                    'name': holding['name'],
                    'quantity': holding['quantity'],
                    'purchase_price': purchase_price,
                    'current_price': current_price,
                    'loss_per_share': round(loss_per_share, 2),
                    'total_loss': round(total_loss, 2),
                    'loss_percentage': round(loss_percentage, 2),
                    'tax_benefit': round(total_loss * 0.15, 2),  # 15% tax bracket
                    'recommendation': 'Strong candidate' if loss_percentage > 10 else 'Consider'
                })
        
        # Sort by total loss (biggest opportunities first)
        opportunities.sort(key=lambda x: x['total_loss'], reverse=True)
        
        return opportunities
    
    def _calculate_risk_score_change(
        self,
        current_holdings: List[Dict[str, Any]],
        proposed_transactions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate how rebalancing will affect portfolio risk score"""
        
        # Risk weights for different assets
        risk_weights = {
            'AAPL': 6.5, 'MSFT': 6.0, 'GOOGL': 6.8, 'NVDA': 8.5,
            'SPY': 5.5, 'VTI': 5.8, 'QQQ': 7.0,
            'BND': 2.5, 'AGG': 2.3,
            'CASH': 1.0
        }
        
        # Calculate current risk score
        total_value = sum(h['quantity'] * h['price'] for h in current_holdings)
        current_risk = 0
        
        for holding in current_holdings:
            weight = (holding['quantity'] * holding['price']) / total_value
            risk = risk_weights.get(holding['symbol'], 5.0)
            current_risk += weight * risk
        
        # Simulate portfolio after transactions
        simulated_holdings = current_holdings.copy()
        
        for transaction in proposed_transactions:
            if transaction['action'] == 'sell':
                for holding in simulated_holdings:
                    if holding['symbol'] == transaction['symbol']:
                        holding['quantity'] -= transaction['quantity']
                        break
            elif transaction['action'] == 'buy':
                # Add or update holding
                found = False
                for holding in simulated_holdings:
                    if holding['symbol'] == transaction['symbol']:
                        holding['quantity'] += transaction['quantity']
                        found = True
                        break
                if not found:
                    simulated_holdings.append({
                        'symbol': transaction['symbol'],
                        'name': transaction['name'],
                        'quantity': transaction['quantity'],
                        'price': transaction['price'],
                        'type': 'Unknown'
                    })
        
        # Calculate new risk score
        new_total_value = sum(h['quantity'] * h['price'] for h in simulated_holdings if h['quantity'] > 0)
        new_risk = 0
        
        for holding in simulated_holdings:
            if holding['quantity'] > 0:
                weight = (holding['quantity'] * holding['price']) / new_total_value
                risk = risk_weights.get(holding['symbol'], 5.0)
                new_risk += weight * risk
        
        return {
            'current_risk_score': round(current_risk, 2),
            'new_risk_score': round(new_risk, 2),
            'risk_change': round(new_risk - current_risk, 2),
            'improvement': 'decreased' if new_risk < current_risk else 'increased' if new_risk > current_risk else 'unchanged'
        }
    
    def _process_response(
        self,
        raw_response: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Process rebalancing agent response"""
        
        return {
            "text": raw_response,
            "agent_type": self.agent_name,
            "analysis_timestamp": datetime.utcnow().isoformat()
        }
    
    def _generate_follow_ups(
        self,
        response: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Generate follow-up questions for rebalancing"""
        
        return [
            "What are the tax implications of this rebalancing?",
            "Can I rebalance gradually over time instead?",
            "Show me tax-loss harvesting opportunities",
            "How will this change my risk score?",
            "Can I use new contributions to rebalance instead?"
        ]
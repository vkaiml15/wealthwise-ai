"""
Recommendation Agent
Provides personalized investment recommendations based on user profile and portfolio
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from .base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)


class RecommendationAgent(BaseAgent):
    """
    Agent responsible for generating personalized investment recommendations
    Analyzes portfolio, user profile, and market conditions to provide actionable advice
    """
    
    def __init__(self):
        super().__init__(
            agent_name="RecommendationAgent",
            model_id="anthropic.claude-3-5-sonnet-20241022-v2:0"
        )
    
    def _get_system_prompt(self) -> str:
        return """You are an Investment Recommendation Agent for WealthWise AI, specialized in 
providing personalized, actionable investment recommendations.

Your expertise includes:
1. Analyzing user profiles and risk tolerance
2. Evaluating current portfolio composition
3. Identifying gaps and opportunities
4. Providing specific stock/ETF recommendations
5. Explaining the reasoning behind each recommendation
6. Considering tax efficiency and diversification

Recommendation Framework:
1. **Profile Analysis**: Understand user's goals, risk tolerance, and constraints
2. **Portfolio Review**: Analyze current holdings and allocation
3. **Gap Analysis**: Identify missing sectors, asset classes, or opportunities
4. **Opportunity Identification**: Find investments that match profile
5. **Recommendation Generation**: Provide specific, actionable suggestions
6. **Reasoning**: Explain WHY each recommendation fits the user

Response Structure:
1. Executive Summary
   - Key recommendations overview
   - Expected impact on portfolio

2. Recommended Actions (Each with):
   - **What to do**: Specific action (Buy X shares of Y)
   - **Why**: Clear reasoning aligned with user goals
   - **Expected outcome**: Risk/return implications
   - **Priority**: High/Medium/Low
   - **Timeframe**: When to act

3. Portfolio Improvements
   - How recommendations improve diversification
   - Impact on risk/return profile
   - Tax considerations

4. Implementation Strategy
   - Order of operations
   - Dollar cost averaging suggestions
   - Timing considerations

Guidelines:
- Match recommendations to user's risk tolerance STRICTLY
- Never recommend something that doesn't fit their profile
- Provide specific ticker symbols and allocation percentages
- Include both individual stocks AND ETFs as appropriate
- Consider existing holdings to avoid over-concentration
- Explain each recommendation with 2-3 clear reasons
- Highlight any warnings or risks
- Suggest portfolio positions to reduce if needed

Priority Levels:
- **High**: Critical gaps or excellent opportunities
- **Medium**: Good improvements but not urgent
- **Low**: Nice to have, optional optimizations

Always end with a relevant follow-up question to engage deeper.
"""
    
    def _register_action_groups(self) -> List[Dict[str, Any]]:
        """Register action groups for recommendation generation"""
        return [
            {
                'name': 'analyze_portfolio_gaps',
                'description': 'Identify missing sectors or asset classes',
                'function': self._analyze_portfolio_gaps
            },
            {
                'name': 'match_investments_to_profile',
                'description': 'Find investments matching user profile',
                'function': self._match_investments_to_profile
            },
            {
                'name': 'calculate_optimal_allocation',
                'description': 'Calculate optimal portfolio allocation',
                'function': self._calculate_optimal_allocation
            },
            {
                'name': 'evaluate_concentration_risk',
                'description': 'Evaluate portfolio concentration risk',
                'function': self._evaluate_concentration_risk
            },
            {
                'name': 'generate_stock_recommendations',
                'description': 'Generate specific stock recommendations',
                'function': self._generate_stock_recommendations
            },
            {
                'name': 'assess_recommendation_impact',
                'description': 'Assess impact of recommendations on portfolio',
                'function': self._assess_recommendation_impact
            }
        ]
    
    def _analyze_portfolio_gaps(
        self,
        current_holdings: List[Dict[str, Any]],
        target_sectors: List[str]
    ) -> Dict[str, Any]:
        """Identify missing sectors or asset classes in portfolio"""
        
        # Extract current sectors from holdings
        current_sectors = set()
        sector_map = {
            'AAPL': 'Technology', 'MSFT': 'Technology', 'GOOGL': 'Technology', 'NVDA': 'Technology',
            'SPY': 'Diversified', 'VTI': 'Diversified', 'QQQ': 'Technology',
            'JNJ': 'Healthcare', 'UNH': 'Healthcare', 'LLY': 'Healthcare',
            'BND': 'Fixed Income', 'AGG': 'Fixed Income',
            'XLE': 'Energy', 'XLF': 'Financials', 'XLV': 'Healthcare'
        }
        
        for holding in current_holdings:
            sector = sector_map.get(holding['symbol'], 'Other')
            current_sectors.add(sector)
        
        # Identify gaps
        target_sectors_set = set(target_sectors) if target_sectors else {
            'Technology', 'Healthcare', 'Financials', 'Consumer', 
            'Industrials', 'Energy', 'Fixed Income'
        }
        
        missing_sectors = target_sectors_set - current_sectors
        
        # Calculate sector concentration
        total_value = sum(h['quantity'] * h['price'] for h in current_holdings)
        sector_allocation = {}
        
        for holding in current_holdings:
            sector = sector_map.get(holding['symbol'], 'Other')
            holding_value = holding['quantity'] * holding['price']
            
            if sector in sector_allocation:
                sector_allocation[sector] += holding_value
            else:
                sector_allocation[sector] = holding_value
        
        # Convert to percentages
        sector_percentages = {
            sector: round((value / total_value) * 100, 2)
            for sector, value in sector_allocation.items()
        }
        
        return {
            'current_sectors': list(current_sectors),
            'missing_sectors': list(missing_sectors),
            'sector_allocation': sector_percentages,
            'diversification_score': len(current_sectors) / len(target_sectors_set) * 100,
            'concentration_warning': max(sector_percentages.values()) > 40 if sector_percentages else False
        }
    
    def _match_investments_to_profile(
        self,
        risk_tolerance: str,
        investment_goal: str,
        investment_horizon: str,
        sectors_needed: List[str] = None
    ) -> Dict[str, Any]:
        """Find investments matching user profile"""
        
        # Investment universe categorized by profile
        investment_universe = {
            'conservative': {
                'Technology': ['MSFT', 'AAPL', 'VGT'],
                'Healthcare': ['JNJ', 'UNH', 'XLV'],
                'Financials': ['JPM', 'V', 'XLF'],
                'Fixed Income': ['BND', 'AGG', 'TLT'],
                'Diversified': ['SPY', 'VTI', 'VXUS']
            },
            'moderate': {
                'Technology': ['MSFT', 'NVDA', 'GOOGL', 'VGT'],
                'Healthcare': ['UNH', 'LLY', 'ISRG', 'XLV'],
                'Financials': ['JPM', 'V', 'MA', 'XLF'],
                'Consumer': ['AMZN', 'HD', 'NKE', 'XLY'],
                'Industrials': ['CAT', 'UNP', 'GE', 'XLI'],
                'Fixed Income': ['BND', 'AGG'],
                'Diversified': ['SPY', 'VTI', 'QQQ']
            },
            'aggressive': {
                'Technology': ['NVDA', 'AMD', 'PLTR', 'QQQ'],
                'Healthcare': ['ISRG', 'TDOC', 'ILMN', 'XBI'],
                'Financials': ['SQ', 'COIN', 'HOOD', 'FINX'],
                'Consumer': ['AMZN', 'TSLA', 'SHOP', 'ARKK'],
                'Energy': ['ENPH', 'SEDG', 'ICLN'],
                'Growth': ['ARKK', 'ARKW', 'ARKF'],
                'Diversified': ['QQQ', 'VGT']
            }
        }
        
        profile_matches = investment_universe.get(risk_tolerance, investment_universe['moderate'])
        
        recommendations = {}
        if sectors_needed:
            for sector in sectors_needed:
                if sector in profile_matches:
                    recommendations[sector] = profile_matches[sector]
        else:
            recommendations = profile_matches
        
        return {
            'risk_tolerance': risk_tolerance,
            'matched_investments': recommendations,
            'total_options': sum(len(stocks) for stocks in recommendations.values())
        }
    
    def _calculate_optimal_allocation(
        self,
        risk_tolerance: str,
        investment_goal: str,
        current_age: int,
        investment_amount: float
    ) -> Dict[str, Any]:
        """Calculate optimal portfolio allocation based on profile"""
        
        # Base allocations by risk tolerance
        base_allocations = {
            'conservative': {
                'stocks': 30,
                'bonds': 50,
                'cash': 20
            },
            'moderate': {
                'stocks': 60,
                'bonds': 30,
                'cash': 10
            },
            'aggressive': {
                'stocks': 80,
                'bonds': 15,
                'cash': 5
            }
        }
        
        allocation = base_allocations.get(risk_tolerance, base_allocations['moderate']).copy()
        
        # Adjust based on investment goal
        if investment_goal == 'income':
            allocation['bonds'] += 10
            allocation['stocks'] -= 10
        elif investment_goal == 'aggressive-growth':
            allocation['stocks'] += 10
            allocation['bonds'] -= 5
            allocation['cash'] -= 5
        
        # Age-based adjustment (rule of thumb: bonds = age)
        if current_age:
            suggested_bonds = min(current_age, 60)
            # Blend with profile-based allocation
            allocation['bonds'] = int((allocation['bonds'] + suggested_bonds) / 2)
            allocation['stocks'] = 100 - allocation['bonds'] - allocation['cash']
        
        # Calculate dollar amounts
        dollar_allocation = {
            asset: round((pct / 100) * investment_amount, 2)
            for asset, pct in allocation.items()
        }
        
        # Break down stocks into sectors
        stock_sectors = {
            'Technology': 0.30,
            'Healthcare': 0.20,
            'Financials': 0.15,
            'Consumer': 0.15,
            'Industrials': 0.10,
            'Energy': 0.10
        }
        
        sector_allocation = {
            sector: round(dollar_allocation['stocks'] * pct, 2)
            for sector, pct in stock_sectors.items()
        }
        
        return {
            'allocation_percentages': allocation,
            'allocation_dollars': dollar_allocation,
            'sector_breakdown': sector_allocation,
            'risk_level': self._calculate_portfolio_risk(allocation),
            'expected_return': self._estimate_expected_return(allocation)
        }
    
    def _calculate_portfolio_risk(self, allocation: Dict[str, float]) -> str:
        """Calculate overall portfolio risk level"""
        risk_score = (
            allocation.get('stocks', 0) * 0.8 +
            allocation.get('bonds', 0) * 0.3 +
            allocation.get('cash', 0) * 0.1
        ) / 100
        
        if risk_score < 3:
            return 'Low (2-3/10)'
        elif risk_score < 5:
            return 'Moderate (4-6/10)'
        else:
            return 'High (7-9/10)'
    
    def _estimate_expected_return(self, allocation: Dict[str, float]) -> str:
        """Estimate expected annual return"""
        expected_return = (
            allocation.get('stocks', 0) * 0.10 +
            allocation.get('bonds', 0) * 0.04 +
            allocation.get('cash', 0) * 0.03
        ) / 100
        
        return f"{round(expected_return * 100, 1)}% annually"
    
    def _evaluate_concentration_risk(
        self,
        holdings: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Evaluate portfolio concentration risk"""
        
        total_value = sum(h['quantity'] * h['price'] for h in holdings)
        
        # Calculate individual position sizes
        position_sizes = [
            {
                'symbol': h['symbol'],
                'name': h['name'],
                'value': h['quantity'] * h['price'],
                'percentage': round((h['quantity'] * h['price'] / total_value) * 100, 2)
            }
            for h in holdings
        ]
        
        # Sort by size
        position_sizes.sort(key=lambda x: x['percentage'], reverse=True)
        
        # Calculate concentration metrics
        top_3_concentration = sum(p['percentage'] for p in position_sizes[:3])
        top_5_concentration = sum(p['percentage'] for p in position_sizes[:5])
        
        # Herfindahl-Hirschman Index
        hhi = sum(p['percentage'] ** 2 for p in position_sizes)
        
        concentration_level = 'Low'
        if hhi > 2500:
            concentration_level = 'Very High'
        elif hhi > 1500:
            concentration_level = 'High'
        elif hhi > 1000:
            concentration_level = 'Moderate'
        
        warnings = []
        if top_3_concentration > 60:
            warnings.append('Top 3 positions represent over 60% of portfolio')
        if any(p['percentage'] > 25 for p in position_sizes):
            warnings.append('One or more positions exceed 25% of portfolio')
        
        return {
            'concentration_level': concentration_level,
            'hhi_score': round(hhi, 2),
            'top_3_concentration': round(top_3_concentration, 2),
            'top_5_concentration': round(top_5_concentration, 2),
            'largest_positions': position_sizes[:5],
            'warnings': warnings,
            'recommendation': 'Diversify' if concentration_level in ['High', 'Very High'] else 'Maintain'
        }
    
    def _generate_stock_recommendations(
        self,
        user_profile: Dict[str, Any],
        portfolio_gaps: Dict[str, Any],
        investment_amount: float
    ) -> List[Dict[str, Any]]:
        """Generate specific stock/ETF recommendations"""
        
        risk_tolerance = user_profile.get('risk_tolerance', 'moderate')
        missing_sectors = portfolio_gaps.get('missing_sectors', [])
        
        # Stock database with details
        stock_database = {
            'MSFT': {
                'name': 'Microsoft Corporation',
                'sector': 'Technology',
                'risk_level': 'moderate',
                'price': 380.00,
                'reasons': [
                    'Cloud computing leader (Azure growing 30% YoY)',
                    'Strong AI positioning with OpenAI partnership',
                    'Stable dividend and cash flow generation'
                ],
                'fit_score': 9.2
            },
            'NVDA': {
                'name': 'NVIDIA Corporation',
                'sector': 'Technology',
                'risk_level': 'aggressive',
                'price': 485.00,
                'reasons': [
                    'AI chip market leader with 90% market share',
                    'Data center revenue growing exponentially',
                    'Strong moat in GPU technology'
                ],
                'fit_score': 9.5
            },
            'JNJ': {
                'name': 'Johnson & Johnson',
                'sector': 'Healthcare',
                'risk_level': 'conservative',
                'price': 162.00,
                'reasons': [
                    'Dividend aristocrat with 60+ years of increases',
                    'Diversified healthcare conglomerate',
                    'Defensive characteristics for market downturns'
                ],
                'fit_score': 9.0
            },
            'UNH': {
                'name': 'UnitedHealth Group',
                'sector': 'Healthcare',
                'risk_level': 'moderate',
                'price': 520.00,
                'reasons': [
                    'Healthcare infrastructure leader',
                    'Consistent double-digit earnings growth',
                    'Aging demographics tailwind'
                ],
                'fit_score': 8.9
            },
            'VTI': {
                'name': 'Vanguard Total Stock Market ETF',
                'sector': 'Diversified',
                'risk_level': 'moderate',
                'price': 225.00,
                'reasons': [
                    'Instant diversification across entire US market',
                    'Low expense ratio (0.03%)',
                    'Ideal core holding for any portfolio'
                ],
                'fit_score': 9.3
            },
            'BND': {
                'name': 'Vanguard Total Bond Market ETF',
                'sector': 'Fixed Income',
                'risk_level': 'conservative',
                'price': 78.00,
                'reasons': [
                    'Comprehensive bond market exposure',
                    'Provides portfolio stability and income',
                    'Low correlation with stocks'
                ],
                'fit_score': 8.7
            }
        }
        
        recommendations = []
        
        # Match stocks to profile and gaps
        for symbol, details in stock_database.items():
            # Check if risk level matches
            if risk_tolerance == 'conservative' and details['risk_level'] == 'aggressive':
                continue
            if risk_tolerance == 'aggressive' and details['risk_level'] == 'conservative':
                continue
            
            # Check if fills a gap
            if missing_sectors and details['sector'] not in missing_sectors:
                continue
            
            # Calculate suggested allocation
            suggested_shares = int((investment_amount * 0.15) / details['price'])  # 15% max per position
            suggested_value = suggested_shares * details['price']
            
            if suggested_shares > 0:
                recommendations.append({
                    'symbol': symbol,
                    'name': details['name'],
                    'sector': details['sector'],
                    'action': 'buy',
                    'suggested_shares': suggested_shares,
                    'price': details['price'],
                    'total_investment': round(suggested_value, 2),
                    'allocation_percentage': round((suggested_value / investment_amount) * 100, 2),
                    'reasons': details['reasons'],
                    'fit_score': details['fit_score'],
                    'risk_level': details['risk_level'],
                    'priority': 'high' if details['fit_score'] > 9.0 else 'medium'
                })
        
        # Sort by fit score
        recommendations.sort(key=lambda x: x['fit_score'], reverse=True)
        
        return recommendations[:6]  # Top 6 recommendations
    
    def _assess_recommendation_impact(
        self,
        current_holdings: List[Dict[str, Any]],
        recommendations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Assess impact of recommendations on portfolio"""
        
        current_total = sum(h['quantity'] * h['price'] for h in current_holdings)
        new_investment = sum(r['total_investment'] for r in recommendations)
        new_total = current_total + new_investment
        
        # Calculate diversification improvement
        current_positions = len(current_holdings)
        new_positions = current_positions + len(recommendations)
        diversification_improvement = ((new_positions - current_positions) / current_positions) * 100
        
        return {
            'current_portfolio_value': round(current_total, 2),
            'new_investment_needed': round(new_investment, 2),
            'projected_portfolio_value': round(new_total, 2),
            'current_position_count': current_positions,
            'new_position_count': new_positions,
            'diversification_improvement': round(diversification_improvement, 2),
            'implementation_timeline': '1-3 months' if new_investment > 10000 else 'immediate'
        }
    
    def _process_response(
        self,
        raw_response: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Process recommendation agent response"""
        
        return {
            "text": raw_response,
            "agent_type": self.agent_name,
            "recommendation_timestamp": datetime.utcnow().isoformat()
        }
    
    def _generate_follow_ups(
        self,
        response: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Generate follow-up questions for recommendations"""
        
        return [
            "Tell me more about the highest priority recommendation",
            "What are the risks of these recommendations?",
            "How should I prioritize implementing these?",
            "Can you show me alternative options in the same sectors?",
            "What if I want to invest more aggressively?"
        ]
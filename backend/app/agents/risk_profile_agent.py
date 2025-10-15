"""
Risk Profile Agent
Analyzes portfolio risk and provides risk management recommendations
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from .base_agent import BaseAgent
import logging
import math

logger = logging.getLogger(__name__)


class RiskProfileAgent(BaseAgent):
    """
    Agent responsible for:
    1. Calculating comprehensive portfolio risk scores
    2. Analyzing risk-return tradeoffs
    3. Assessing alignment between portfolio and user risk tolerance
    4. Providing risk management recommendations
    """
    
    def __init__(self):
        super().__init__(
            agent_name="RiskProfileAgent",
            model_id="anthropic.claude-3-5-sonnet-20241022-v2:0"
        )
    
    def _get_system_prompt(self) -> str:
        return """You are a Risk Profile Agent for WealthWise AI, specialized in portfolio risk 
analysis and risk management strategies.

Your expertise includes:
1. **Risk Assessment**: Calculating comprehensive risk scores
2. **Risk Analysis**: Evaluating various risk factors (volatility, concentration, correlation)
3. **Risk-Return Tradeoff**: Analyzing if risk level is appropriate for expected returns
4. **Alignment Check**: Determining if portfolio matches user's risk tolerance
5. **Risk Management**: Providing strategies to optimize risk exposure

Risk Dimensions to Analyze:
1. **Market Risk**: Exposure to overall market volatility
2. **Concentration Risk**: Over-reliance on few positions or sectors
3. **Volatility Risk**: Portfolio price fluctuation magnitude
4. **Sector Risk**: Exposure to industry-specific risks
5. **Liquidity Risk**: Ability to exit positions quickly
6. **Interest Rate Risk**: Sensitivity to interest rate changes
7. **Currency Risk**: For international holdings

Risk Score Calculation (0-10 scale):
- 0-2: Very Conservative (Minimal volatility, capital preservation focus)
- 3-4: Conservative (Low volatility, some growth potential)
- 5-6: Moderate (Balanced risk-return profile)
- 7-8: Aggressive (High volatility, strong growth focus)
- 9-10: Very Aggressive (Maximum volatility, speculative)

Response Structure:
1. **Executive Summary**
   - Overall risk score and level
   - Key risk factors
   - Alignment with user profile

2. **Detailed Risk Analysis**
   - Market risk exposure
   - Concentration analysis
   - Volatility assessment
   - Sector risk breakdown

3. **Risk-Return Assessment**
   - Expected return for current risk level
   - Sharpe ratio (risk-adjusted return)
   - Comparison to benchmarks

4. **Alignment Analysis**
   - Does portfolio match stated risk tolerance?
   - Gaps and misalignments
   - Recommended adjustments

5. **Risk Management Recommendations**
   - Specific actions to optimize risk
   - Hedging strategies if needed
   - Diversification improvements

6. **Scenario Analysis**
   - Best case scenario
   - Expected scenario
   - Worst case scenario
   - Portfolio behavior in market stress

Guidelines:
- Be clear and educational about risk concepts
- Provide specific, actionable recommendations
- Explain WHY certain risks exist
- Consider user's capacity to take risk (age, income, goals)
- Highlight both upside and downside risks
- Use plain language, avoid excessive jargon
- Always include reasoning behind risk scores

Warning Indicators:
- Flag if risk score significantly mismatches user tolerance
- Highlight concentration risks above 25% in single position
- Warn about sector over-concentration
- Alert to high correlation risks

End with actionable next steps and relevant follow-up question.
"""
    
    def _register_action_groups(self) -> List[Dict[str, Any]]:
        """Register action groups for risk analysis"""
        return [
            {
                'name': 'calculate_comprehensive_risk_score',
                'description': 'Calculate overall portfolio risk score',
                'function': self._calculate_comprehensive_risk_score
            },
            {
                'name': 'analyze_volatility',
                'description': 'Analyze portfolio volatility',
                'function': self._analyze_volatility
            },
            {
                'name': 'assess_concentration_risk',
                'description': 'Assess portfolio concentration risk',
                'function': self._assess_concentration_risk
            },
            {
                'name': 'calculate_sector_risk',
                'description': 'Calculate sector-level risk exposure',
                'function': self._calculate_sector_risk
            },
            {
                'name': 'evaluate_risk_return_tradeoff',
                'description': 'Evaluate risk-return tradeoff',
                'function': self._evaluate_risk_return_tradeoff
            },
            {
                'name': 'check_profile_alignment',
                'description': 'Check if portfolio aligns with user risk tolerance',
                'function': self._check_profile_alignment
            },
            {
                'name': 'perform_stress_test',
                'description': 'Simulate portfolio performance in stress scenarios',
                'function': self._perform_stress_test
            },
            {
                'name': 'calculate_value_at_risk',
                'description': 'Calculate Value at Risk (VaR)',
                'function': self._calculate_value_at_risk
            },
            {
                'name': 'generate_risk_mitigation_strategies',
                'description': 'Generate strategies to reduce risk',
                'function': self._generate_risk_mitigation_strategies
            }
        ]
    
    def _calculate_comprehensive_risk_score(
        self,
        holdings: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate comprehensive portfolio risk score (0-10)"""
        
        # Asset risk ratings (0-10 scale)
        asset_risk_weights = {
            # Individual Stocks - Higher risk
            'AAPL': 6.5, 'MSFT': 6.0, 'GOOGL': 6.8, 'NVDA': 8.5, 'AMD': 8.2,
            'TSLA': 9.5, 'AMZN': 7.2, 'META': 7.8, 'NFLX': 8.0,
            
            # Broad Market ETFs - Moderate risk
            'SPY': 5.5, 'VTI': 5.8, 'VOO': 5.5, 'IWM': 7.0,
            
            # Tech ETFs - Higher risk
            'QQQ': 7.0, 'VGT': 7.2, 'XLK': 6.8,
            
            # Sector ETFs - Variable risk
            'XLV': 5.0, 'XLF': 6.5, 'XLE': 7.5, 'XLI': 6.0,
            
            # Bond ETFs - Lower risk
            'BND': 2.5, 'AGG': 2.3, 'TLT': 3.5, 'LQD': 3.0,
            
            # International
            'VXUS': 6.5, 'EFA': 6.2, 'VWO': 7.8,
            
            # High Risk
            'ARKK': 9.0, 'COIN': 9.5, 'PLTR': 8.8,
            
            # Cash
            'CASH': 1.0
        }
        
        total_value = sum(h['quantity'] * h['price'] for h in holdings)
        
        # 1. Calculate weighted average risk
        weighted_risk = 0
        for holding in holdings:
            weight = (holding['quantity'] * holding['price']) / total_value
            risk = asset_risk_weights.get(holding['symbol'], 6.0)  # Default 6.0 if not found
            weighted_risk += weight * risk
        
        # 2. Concentration penalty
        concentration_penalty = self._calculate_concentration_penalty(holdings, total_value)
        
        # 3. Sector concentration penalty
        sector_penalty = self._calculate_sector_concentration_penalty(holdings)
        
        # 4. Diversification bonus
        diversification_bonus = self._calculate_diversification_bonus(holdings)
        
        # Final risk score
        base_risk_score = weighted_risk + concentration_penalty + sector_penalty - diversification_bonus
        final_risk_score = max(0, min(10, base_risk_score))  # Clamp between 0-10
        
        # Determine risk level
        risk_level = self._get_risk_level_description(final_risk_score)
        
        # Calculate risk components breakdown
        risk_components = {
            'base_asset_risk': round(weighted_risk, 2),
            'concentration_penalty': round(concentration_penalty, 2),
            'sector_penalty': round(sector_penalty, 2),
            'diversification_bonus': round(diversification_bonus, 2)
        }
        
        return {
            'risk_score': round(final_risk_score, 2),
            'risk_level': risk_level,
            'risk_components': risk_components,
            'assessment_timestamp': datetime.utcnow().isoformat(),
            'factors_analyzed': ['asset_risk', 'concentration', 'sector_exposure', 'diversification']
        }
    
    def _calculate_concentration_penalty(
        self,
        holdings: List[Dict[str, Any]],
        total_value: float
    ) -> float:
        """Calculate penalty for position concentration"""
        
        penalties = 0
        for holding in holdings:
            position_percentage = (holding['quantity'] * holding['price'] / total_value) * 100
            
            if position_percentage > 30:
                penalties += 2.0  # Severe concentration
            elif position_percentage > 20:
                penalties += 1.0  # High concentration
            elif position_percentage > 15:
                penalties += 0.5  # Moderate concentration
        
        return min(penalties, 3.0)  # Cap at 3.0
    
    def _calculate_sector_concentration_penalty(
        self,
        holdings: List[Dict[str, Any]]
    ) -> float:
        """Calculate penalty for sector over-concentration"""
        
        # Sector mapping
        sector_map = {
            'AAPL': 'Technology', 'MSFT': 'Technology', 'GOOGL': 'Technology',
            'NVDA': 'Technology', 'AMD': 'Technology', 'META': 'Technology',
            'TSLA': 'Consumer', 'AMZN': 'Consumer',
            'SPY': 'Diversified', 'VTI': 'Diversified', 'QQQ': 'Technology',
            'XLV': 'Healthcare', 'XLF': 'Financials', 'XLE': 'Energy',
            'BND': 'Fixed Income', 'AGG': 'Fixed Income',
            'CASH': 'Cash'
        }
        
        total_value = sum(h['quantity'] * h['price'] for h in holdings)
        sector_allocations = {}
        
        for holding in holdings:
            sector = sector_map.get(holding['symbol'], 'Other')
            holding_value = holding['quantity'] * holding['price']
            
            if sector in sector_allocations:
                sector_allocations[sector] += holding_value
            else:
                sector_allocations[sector] = holding_value
        
        # Calculate sector percentages
        sector_percentages = {
            sector: (value / total_value) * 100
            for sector, value in sector_allocations.items()
        }
        
        # Penalty for over-concentration
        penalty = 0
        for sector, percentage in sector_percentages.items():
            if sector == 'Diversified':
                continue
            if percentage > 50:
                penalty += 1.5
            elif percentage > 40:
                penalty += 1.0
            elif percentage > 30:
                penalty += 0.5
        
        return min(penalty, 2.0)
    
    def _calculate_diversification_bonus(
        self,
        holdings: List[Dict[str, Any]]
    ) -> float:
        """Calculate bonus for good diversification"""
        
        num_positions = len([h for h in holdings if h['quantity'] > 0])
        
        if num_positions >= 15:
            return 1.0
        elif num_positions >= 10:
            return 0.7
        elif num_positions >= 7:
            return 0.4
        elif num_positions >= 5:
            return 0.2
        else:
            return 0
    
    def _get_risk_level_description(self, score: float) -> str:
        """Get risk level description from score"""
        if score < 2.5:
            return "Very Conservative"
        elif score < 4.5:
            return "Conservative"
        elif score < 6.5:
            return "Moderate"
        elif score < 8.5:
            return "Aggressive"
        else:
            return "Very Aggressive"
    
    def _analyze_volatility(
        self,
        holdings: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze portfolio volatility"""
        
        # Historical volatility estimates (annualized standard deviation %)
        volatility_map = {
            'AAPL': 28, 'MSFT': 25, 'GOOGL': 30, 'NVDA': 45, 'AMD': 50,
            'TSLA': 65, 'META': 35, 'AMZN': 32,
            'SPY': 18, 'VTI': 18, 'QQQ': 25,
            'XLV': 15, 'XLF': 22, 'XLE': 30,
            'BND': 5, 'AGG': 5, 'TLT': 12,
            'ARKK': 50, 'COIN': 80,
            'CASH': 0
        }
        
        total_value = sum(h['quantity'] * h['price'] for h in holdings)
        
        # Calculate weighted volatility
        weighted_volatility = 0
        volatility_breakdown = []
        
        for holding in holdings:
            weight = (holding['quantity'] * holding['price']) / total_value
            vol = volatility_map.get(holding['symbol'], 25)  # Default 25%
            contribution = weight * vol
            weighted_volatility += contribution
            
            volatility_breakdown.append({
                'symbol': holding['symbol'],
                'weight': round(weight * 100, 2),
                'volatility': vol,
                'contribution': round(contribution, 2)
            })
        
        # Sort by contribution
        volatility_breakdown.sort(key=lambda x: x['contribution'], reverse=True)
        
        # Volatility assessment
        if weighted_volatility < 10:
            assessment = "Very Low - Portfolio highly stable"
        elif weighted_volatility < 15:
            assessment = "Low - Portfolio relatively stable"
        elif weighted_volatility < 20:
            assessment = "Moderate - Normal market volatility"
        elif weighted_volatility < 30:
            assessment = "High - Significant price fluctuations expected"
        else:
            assessment = "Very High - Extreme price swings possible"
        
        return {
            'portfolio_volatility': round(weighted_volatility, 2),
            'volatility_percentage': f"{round(weighted_volatility, 1)}% annually",
            'assessment': assessment,
            'top_contributors': volatility_breakdown[:5],
            'interpretation': self._interpret_volatility(weighted_volatility)
        }
    
    def _interpret_volatility(self, volatility: float) -> str:
        """Provide interpretation of volatility level"""
        if volatility < 15:
            return "Your portfolio has below-average volatility, suggesting stable but potentially lower returns."
        elif volatility < 25:
            return "Your portfolio has moderate volatility, typical for balanced stock/bond portfolios."
        else:
            return "Your portfolio has above-average volatility. Expect larger price swings, both up and down."
    
    def _assess_concentration_risk(
        self,
        holdings: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Assess portfolio concentration risk"""
        
        total_value = sum(h['quantity'] * h['price'] for h in holdings)
        
        # Calculate position sizes
        positions = []
        for holding in holdings:
            holding_value = holding['quantity'] * holding['price']
            percentage = (holding_value / total_value) * 100
            
            positions.append({
                'symbol': holding['symbol'],
                'name': holding.get('name', holding['symbol']),
                'value': round(holding_value, 2),
                'percentage': round(percentage, 2),
                'risk_level': 'High' if percentage > 20 else 'Moderate' if percentage > 10 else 'Low'
            })
        
        # Sort by percentage
        positions.sort(key=lambda x: x['percentage'], reverse=True)
        
        # Calculate HHI (Herfindahl-Hirschman Index)
        hhi = sum(p['percentage'] ** 2 for p in positions)
        
        # Concentration metrics
        top_3_concentration = sum(p['percentage'] for p in positions[:3])
        top_5_concentration = sum(p['percentage'] for p in positions[:5])
        
        # Assessment
        if hhi < 1000:
            concentration_level = "Low"
            assessment = "Well-diversified portfolio with no significant concentration risk"
        elif hhi < 1500:
            concentration_level = "Moderate"
            assessment = "Some concentration present but within acceptable limits"
        elif hhi < 2500:
            concentration_level = "High"
            assessment = "Significant concentration risk. Consider diversifying"
        else:
            concentration_level = "Very High"
            assessment = "Dangerous concentration levels. Immediate diversification recommended"
        
        # Warnings
        warnings = []
        for position in positions:
            if position['percentage'] > 25:
                warnings.append(f"{position['symbol']} represents {position['percentage']}% - exceeds recommended 25% maximum")
            elif position['percentage'] > 20:
                warnings.append(f"{position['symbol']} at {position['percentage']}% - approaching concentration limit")
        
        return {
            'concentration_level': concentration_level,
            'hhi_score': round(hhi, 2),
            'assessment': assessment,
            'top_3_concentration': round(top_3_concentration, 2),
            'top_5_concentration': round(top_5_concentration, 2),
            'largest_positions': positions[:5],
            'warnings': warnings,
            'recommendation': self._get_concentration_recommendation(hhi, positions)
        }
    
    def _get_concentration_recommendation(
        self,
        hhi: float,
        positions: List[Dict[str, Any]]
    ) -> str:
        """Generate recommendation based on concentration"""
        if hhi < 1000:
            return "Maintain current diversification. Portfolio is well-balanced."
        elif hhi < 1500:
            return "Consider gradual diversification, especially if any position grows beyond 15%."
        else:
            largest = positions[0]
            return f"Reduce {largest['symbol']} position and reinvest in underrepresented sectors."
    
    def _calculate_sector_risk(
        self,
        holdings: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate sector-level risk exposure"""
        
        sector_map = {
            'AAPL': 'Technology', 'MSFT': 'Technology', 'GOOGL': 'Technology',
            'NVDA': 'Technology', 'AMD': 'Technology', 'META': 'Technology',
            'TSLA': 'Consumer Discretionary', 'AMZN': 'Consumer Discretionary',
            'JNJ': 'Healthcare', 'UNH': 'Healthcare', 'LLY': 'Healthcare',
            'JPM': 'Financials', 'V': 'Financials', 'MA': 'Financials',
            'XLE': 'Energy', 'XLF': 'Financials', 'XLV': 'Healthcare',
            'SPY': 'Diversified', 'VTI': 'Diversified',
            'BND': 'Fixed Income', 'AGG': 'Fixed Income',
            'CASH': 'Cash'
        }
        
        # Sector risk levels
        sector_risk_levels = {
            'Technology': 7.5,
            'Consumer Discretionary': 7.0,
            'Healthcare': 6.0,
            'Financials': 6.5,
            'Energy': 8.0,
            'Industrials': 6.5,
            'Fixed Income': 2.5,
            'Cash': 1.0,
            'Diversified': 5.5
        }
        
        total_value = sum(h['quantity'] * h['price'] for h in holdings)
        sector_exposure = {}
        
        for holding in holdings:
            sector = sector_map.get(holding['symbol'], 'Other')
            holding_value = holding['quantity'] * holding['price']
            
            if sector in sector_exposure:
                sector_exposure[sector]['value'] += holding_value
                sector_exposure[sector]['holdings'].append(holding['symbol'])
            else:
                sector_exposure[sector] = {
                    'value': holding_value,
                    'holdings': [holding['symbol']],
                    'risk_level': sector_risk_levels.get(sector, 6.0)
                }
        
        # Calculate percentages and risk
        sector_analysis = []
        for sector, data in sector_exposure.items():
            percentage = (data['value'] / total_value) * 100
            risk_contribution = (percentage / 100) * data['risk_level']
            
            sector_analysis.append({
                'sector': sector,
                'allocation': round(percentage, 2),
                'value': round(data['value'], 2),
                'risk_level': data['risk_level'],
                'risk_contribution': round(risk_contribution, 2),
                'holdings': data['holdings'],
                'status': 'Overweight' if percentage > 30 else 'Balanced' if percentage > 10 else 'Underweight'
            })
        
        sector_analysis.sort(key=lambda x: x['allocation'], reverse=True)
        
        return {
            'sector_breakdown': sector_analysis,
            'top_sector': sector_analysis[0]['sector'] if sector_analysis else None,
            'sector_count': len(sector_analysis),
            'highest_risk_sector': max(sector_analysis, key=lambda x: x['risk_level'])['sector'],
            'recommendations': self._generate_sector_recommendations(sector_analysis)
        }
    
    def _generate_sector_recommendations(
        self,
        sector_analysis: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate recommendations based on sector analysis"""
        recommendations = []
        
        for sector in sector_analysis:
            if sector['allocation'] > 40:
                recommendations.append(
                    f"Reduce {sector['sector']} allocation from {sector['allocation']}% to under 35%"
                )
            elif sector['allocation'] < 5 and sector['sector'] not in ['Cash', 'Fixed Income']:
                recommendations.append(
                    f"Consider adding {sector['sector']} exposure for better diversification"
                )
        
        return recommendations if recommendations else ["Sector allocation is well-balanced"]
    
    def _evaluate_risk_return_tradeoff(
        self,
        risk_score: float,
        holdings: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Evaluate if risk level is appropriate for expected returns"""
        
        # Expected returns by risk level (historical averages)
        expected_returns = {
            'Very Conservative': 3.5,
            'Conservative': 5.0,
            'Moderate': 7.5,
            'Aggressive': 10.0,
            'Very Aggressive': 12.5
        }
        
        risk_level = self._get_risk_level_description(risk_score)
        expected_return = expected_returns.get(risk_level, 7.5)
        
        # Calculate Sharpe Ratio estimate (simplified)
        risk_free_rate = 4.0  # Current treasury rate
        excess_return = expected_return - risk_free_rate
        
        # Get volatility
        volatility_data = self._analyze_volatility(holdings)
        volatility = volatility_data['portfolio_volatility']
        
        sharpe_ratio = excess_return / volatility if volatility > 0 else 0
        
        # Assessment
        if sharpe_ratio > 0.8:
            assessment = "Excellent risk-return tradeoff"
        elif sharpe_ratio > 0.5:
            assessment = "Good risk-return tradeoff"
        elif sharpe_ratio > 0.3:
            assessment = "Fair risk-return tradeoff"
        else:
            assessment = "Poor risk-return tradeoff - too much risk for expected return"
        
        return {
            'risk_score': risk_score,
            'risk_level': risk_level,
            'expected_annual_return': f"{expected_return}%",
            'portfolio_volatility': f"{volatility}%",
            'sharpe_ratio': round(sharpe_ratio, 2),
            'assessment': assessment,
            'interpretation': self._interpret_sharpe_ratio(sharpe_ratio)
        }
    
    def _interpret_sharpe_ratio(self, sharpe: float) -> str:
        """Interpret Sharpe ratio"""
        if sharpe > 0.8:
            return "Your portfolio has excellent risk-adjusted returns. You're being well-compensated for the risk you're taking."
        elif sharpe > 0.5:
            return "Your portfolio has good risk-adjusted returns, typical of well-constructed portfolios."
        elif sharpe > 0.3:
            return "Your portfolio has acceptable risk-adjusted returns, but there may be room for optimization."
        else:
            return "Your portfolio may be taking on too much risk for the expected returns. Consider rebalancing."
    
    def _check_profile_alignment(
        self,
        portfolio_risk_score: float,
        user_risk_tolerance: str
    ) -> Dict[str, Any]:
        """Check if portfolio aligns with user's stated risk tolerance"""
        
        # Risk tolerance score ranges
        tolerance_ranges = {
            'conservative': (0, 4.5),
            'moderate': (4.0, 7.0),
            'aggressive': (6.5, 10.0)
        }
        
        target_range = tolerance_ranges.get(user_risk_tolerance.lower(), (4.0, 7.0))
        min_risk, max_risk = target_range
        
        # Check alignment
        if min_risk <= portfolio_risk_score <= max_risk:
            alignment = "Aligned"
            message = f"Your portfolio risk level matches your {user_risk_tolerance} risk tolerance"
        elif portfolio_risk_score < min_risk:
            alignment = "Too Conservative"
            gap = min_risk - portfolio_risk_score
            message = f"Your portfolio is {round(gap, 1)} points more conservative than your stated {user_risk_tolerance} tolerance"
        else:
            alignment = "Too Aggressive"
            gap = portfolio_risk_score - max_risk
            message = f"Your portfolio is {round(gap, 1)} points more aggressive than your stated {user_risk_tolerance} tolerance"
        
        # Generate recommendations
        recommendations = []
        if alignment == "Too Conservative":
            recommendations.append("Consider increasing stock allocation")
            recommendations.append("Add growth-oriented investments")
            recommendations.append("Reduce bond/cash positions gradually")
        elif alignment == "Too Aggressive":
            recommendations.append("Increase bond allocation for stability")
            recommendations.append("Reduce high-volatility stock positions")
            recommendations.append("Add defensive sectors (utilities, consumer staples)")
        
        return {
            'alignment_status': alignment,
            'portfolio_risk_score': round(portfolio_risk_score, 2),
            'user_risk_tolerance': user_risk_tolerance,
            'target_range': f"{min_risk}-{max_risk}",
            'message': message,
            'aligned': alignment == "Aligned",
            'recommendations': recommendations if recommendations else ["Portfolio is well-aligned with risk tolerance"]
        }
    
    def _perform_stress_test(
        self,
        holdings: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Simulate portfolio performance in stress scenarios"""
        
        total_value = sum(h['quantity'] * h['price'] for h in holdings)
        
        # Stress scenarios (% decline by asset type)
        scenarios = {
            'market_correction': {
                'description': '10% market correction',
                'impacts': {'Stocks': -10, 'ETFs': -10, 'Bonds': -2, 'Cash': 0}
            },
            'bear_market': {
                'description': '30% bear market',
                'impacts': {'Stocks': -30, 'ETFs': -28, 'Bonds': -5, 'Cash': 0}
            },
            'financial_crisis': {
                'description': 'Severe financial crisis (2008-style)',
                'impacts': {'Stocks': -45, 'ETFs': -42, 'Bonds': -10, 'Cash': 0}
            },
            'tech_crash': {
                'description': 'Technology sector crash',
                'impacts': {'Stocks': -20, 'ETFs': -15, 'Bonds': 0, 'Cash': 0}
            }
        }
        
        scenario_results = {}
        
        for scenario_name, scenario_data in scenarios.items():
            scenario_loss = 0
            
            for holding in holdings:
                asset_type = holding.get('type', 'Stocks')
                holding_value = holding['quantity'] * holding['price']
                impact_pct = scenario_data['impacts'].get(asset_type, -15)
                loss = holding_value * (impact_pct / 100)
                scenario_loss += loss
            
            new_value = total_value + scenario_loss
            loss_percentage = (scenario_loss / total_value) * 100
            
            scenario_results[scenario_name] = {
                'description': scenario_data['description'],
                'portfolio_impact': round(scenario_loss, 2),
                'new_portfolio_value': round(new_value, 2),
                'loss_percentage': round(loss_percentage, 2),
                'severity': 'Low' if loss_percentage > -10 else 'Moderate' if loss_percentage > -20 else 'High'
            }
        
        # Find worst case
        worst_case = min(scenario_results.values(), key=lambda x: x['loss_percentage'])
        
        return {
            'current_portfolio_value': round(total_value, 2),
            'scenarios': scenario_results,
            'worst_case_scenario': worst_case,
            'stress_test_summary': self._generate_stress_test_summary(scenario_results)
        }
    
    def _generate_stress_test_summary(
        self,
        scenario_results: Dict[str, Any]
    ) -> str:
        """Generate summary of stress test results"""
        avg_loss = sum(s['loss_percentage'] for s in scenario_results.values()) / len(scenario_results)
        
        if avg_loss > -10:
            return "Portfolio shows strong resilience to market stress. Well-positioned for downturns."
        elif avg_loss > -20:
            return "Portfolio has moderate downside risk. Consider adding defensive positions."
        else:
            return "Portfolio is vulnerable to significant losses in stress scenarios. Increase diversification and add defensive assets."
    
    def _calculate_value_at_risk(
        self,
        holdings: List[Dict[str, Any]],
        confidence_level: float = 0.95,
        time_horizon_days: int = 30
    ) -> Dict[str, Any]:
        """Calculate Value at Risk (VaR) - potential loss at confidence level"""
        
        total_value = sum(h['quantity'] * h['price'] for h in holdings)
        
        # Get portfolio volatility
        volatility_data = self._analyze_volatility(holdings)
        annual_volatility = volatility_data['portfolio_volatility'] / 100
        
        # Convert to time horizon volatility
        daily_volatility = annual_volatility / math.sqrt(252)  # 252 trading days
        period_volatility = daily_volatility * math.sqrt(time_horizon_days)
        
        # Z-score for confidence level (95% = 1.645, 99% = 2.326)
        z_score = 1.645 if confidence_level == 0.95 else 2.326
        
        # VaR calculation
        var_percentage = z_score * period_volatility * 100
        var_dollar = total_value * (var_percentage / 100)
        
        return {
            'confidence_level': f"{confidence_level * 100}%",
            'time_horizon': f"{time_horizon_days} days",
            'value_at_risk_percentage': round(var_percentage, 2),
            'value_at_risk_dollars': round(var_dollar, 2),
            'interpretation': f"There is a {confidence_level * 100}% chance that your portfolio will not lose more than ${round(var_dollar, 2)} ({round(var_percentage, 1)}%) over the next {time_horizon_days} days",
            'current_portfolio_value': round(total_value, 2)
        }
    
    def _generate_risk_mitigation_strategies(
        self,
        risk_analysis: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Generate specific strategies to reduce risk"""
        
        strategies = []
        
        risk_score = risk_analysis.get('risk_score', 5.0)
        
        if risk_score > 7:
            strategies.append({
                'strategy': 'Increase Bond Allocation',
                'action': 'Shift 10-15% from stocks to bonds',
                'impact': 'Reduce volatility by 3-5%',
                'priority': 'High'
            })
            strategies.append({
                'strategy': 'Add Defensive Stocks',
                'action': 'Invest in utilities, consumer staples, healthcare',
                'impact': 'Lower portfolio beta',
                'priority': 'High'
            })
        
        strategies.append({
            'strategy': 'Dollar-Cost Averaging',
            'action': 'Make regular periodic investments instead of lump sum',
            'impact': 'Reduce timing risk',
            'priority': 'Medium'
        })
        
        strategies.append({
            'strategy': 'Rebalance Regularly',
            'action': 'Review and rebalance quarterly',
            'impact': 'Maintain target risk level',
            'priority': 'Medium'
        })
        
        strategies.append({
            'strategy': 'Diversify Across Asset Classes',
            'action': 'Add REITs, commodities, or international exposure',
            'impact': 'Reduce correlation risk',
            'priority': 'Low'
        })
        
        return strategies
    
    def _process_response(
        self,
        raw_response: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Process risk profile agent response"""
        
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
        """Generate follow-up questions for risk analysis"""
        
        return [
            "How can I reduce my portfolio risk?",
            "What would happen to my portfolio in a market crash?",
            "Does my risk level match my age and goals?",
            "Show me specific ways to make my portfolio safer",
            "What's my risk-adjusted return (Sharpe ratio)?"
        ]
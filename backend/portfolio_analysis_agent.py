import os
import boto3
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from decimal import Decimal


class PortfolioAnalysisAgent:
    """
    Robo-Advisor Portfolio Analysis Agent
    
    Features:
    - 5 Model Portfolio allocation strategies
    - Health score calculation (0-100)
    - Drift analysis
    - Specific rebalancing recommendations
    - Performance attribution vs benchmark
    - Prioritized actionable insights
    
    Usage:
        agent = PortfolioAnalysisAgent()
        analysis = agent.analyze_portfolio(user_email, market_data)
    """
    
    def __init__(self):
        """Initialize DynamoDB connection and model portfolios"""
        # self.dynamodb = boto3.resource(
        #     'dynamodb',
        #     region_name=os.getenv('AWS_REGION', 'us-east-1'),
        #     aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        #     aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        #     aws_session_token=os.getenv('AWS_SESSION_TOKEN')
        # )

        self.dynamodb = boto3.resource("dynamodb", region_name=os.getenv("AWS_REGION", "us-east-1"))
        self.users_table = self.dynamodb.Table('WealthWiseUsers')
        self.portfolios_table = self.dynamodb.Table('WealthWisePortfolios')
        
        # Define 5 Model Portfolios
        self.MODEL_PORTFOLIOS = {
            "Conservative": {
                "stocks": 30,
                "bonds": 60,
                "cash": 10,
                "expectedReturn": 4.5,
                "expectedVolatility": 8,
                "description": "Low risk, capital preservation focus",
                "suitableFor": "Age 55+, Low risk tolerance, Short horizon"
            },
            "ModeratelyConservative": {
                "stocks": 45,
                "bonds": 45,
                "cash": 10,
                "expectedReturn": 6.0,
                "expectedVolatility": 11,
                "description": "Below-average risk, some growth potential",
                "suitableFor": "Age 45-55, Low-Moderate risk, Medium horizon"
            },
            "Moderate": {
                "stocks": 60,
                "bonds": 30,
                "cash": 10,
                "expectedReturn": 7.5,
                "expectedVolatility": 14,
                "description": "Balanced growth and stability",
                "suitableFor": "Age 30-45, Moderate risk, Long horizon"
            },
            "ModeratelyAggressive": {
                "stocks": 75,
                "bonds": 20,
                "cash": 5,
                "expectedReturn": 8.5,
                "expectedVolatility": 16,
                "description": "Above-average risk, growth focused",
                "suitableFor": "Age 25-35, Moderate-High risk, Long horizon"
            },
            "Aggressive": {
                "stocks": 85,
                "bonds": 10,
                "cash": 5,
                "expectedReturn": 9.5,
                "expectedVolatility": 18,
                "description": "High risk, maximum growth potential",
                "suitableFor": "Age <30, High risk tolerance, Very long horizon"
            }
        }
        
        # Recommended ETFs for rebalancing
        self.RECOMMENDED_ETFS = {
            "us_stocks": {"symbol": "VTI", "name": "Vanguard Total Stock Market ETF", "expense": 0.03},
            "bonds": {"symbol": "BND", "name": "Vanguard Total Bond Market ETF", "expense": 0.03},
            "international": {"symbol": "VXUS", "name": "Vanguard Total International Stock ETF", "expense": 0.07},
            "reits": {"symbol": "VNQ", "name": "Vanguard Real Estate ETF", "expense": 0.12}
        }
        
        print("✅ Portfolio Analysis Agent initialized")
    
    # ==================== MODULE 1: MODEL PORTFOLIO SELECTOR ====================
    
    def select_model_portfolio(self, user_profile: Dict) -> Tuple[str, Dict]:
        """
        Map user to one of 5 model portfolios based on age, risk tolerance, and horizon
        
        Args:
            user_profile: Dict with 'age', 'riskTolerance', 'investmentHorizon'
        
        Returns:
            Tuple of (model_name: str, model_config: Dict)
        """
        age = user_profile.get('age', 35)
        risk = user_profile.get('riskTolerance', 'Moderate').lower()
        horizon = user_profile.get('investmentHorizon', '5-10 years').lower()
        
        print(f"📊 User Profile: Age {age}, Risk: {risk.title()}, Horizon: {horizon}")
        
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
            model_name = "Moderate"  # Default
        
        model = self.MODEL_PORTFOLIOS[model_name]
        print(f"✅ Selected Model: {model_name}")
        print(f"   Target: {model['stocks']}% stocks, {model['bonds']}% bonds, {model['cash']}% cash")
        
        return model_name, model
    
    # ==================== MODULE 2: ALLOCATION ANALYZER ====================
    
    def analyze_allocation(self, current_holdings: List[Dict], target_model: Dict, 
                          cash_savings: float) -> Dict:
        """
        Compare current vs target allocation and calculate drift
        
        Args:
            current_holdings: List of holdings with currentValue
            target_model: Dict with target percentages
            cash_savings: Float of cash amount
        
        Returns:
            Dict with current, target, drift, and issues
        """
        # Calculate total assets
        total_invested = sum(h['currentValue'] for h in current_holdings)
        total_assets = total_invested + cash_savings
        
        # Categorize holdings
        stocks_value = 0
        bonds_value = 0
        
        for holding in current_holdings:
            holding_type = holding.get('type', 'stock').lower()
            sector = holding.get('sector', '').upper()
            
            # Classify as stock or bond
            if holding_type == 'bond' or 'BOND' in sector or holding['symbol'].upper() in ['BND', 'AGG', 'TLT']:
                bonds_value += holding['currentValue']
            else:
                stocks_value += holding['currentValue']
        
        # Calculate current allocation percentages
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
        
        # Calculate drift (sum of absolute differences)
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
        
        # Check concentration
        for holding in current_holdings:
            weight = holding.get('portfolioWeight', 0)
            if weight > 30:
                issues.append("CONCENTRATION_RISK")
                break
        
        # Check diversification
        if len(current_holdings) < 5:
            issues.append("LOW_DIVERSIFICATION")
        
        print(f"\n📊 Allocation Analysis:")
        print(f"   Current: {current_allocation['stocks']}% stocks, {current_allocation['bonds']}% bonds, {current_allocation['cash']}% cash")
        print(f"   Target:  {target_allocation['stocks']}% stocks, {target_allocation['bonds']}% bonds, {target_allocation['cash']}% cash")
        print(f"   Drift: {drift}% {'⚠️ CRITICAL' if drift > 20 else '✅ OK'}")
        print(f"   Issues: {', '.join(issues) if issues else 'None'}")
        
        return {
            "current": current_allocation,
            "target": target_allocation,
            "drift": drift,
            "issues": issues,
            "totalAssets": round(total_assets, 2),
            "totalInvested": round(total_invested, 2),
            "cashSavings": round(cash_savings, 2)
        }
    
    # ==================== MODULE 3: HEALTH SCORE CALCULATOR ====================
    
    def calculate_health_score(self, allocation_analysis: Dict, holdings: List[Dict]) -> Dict:
        """
        Calculate portfolio health score (0-100)
        
        Scoring factors:
        - Alignment with target (40 points max)
        - Diversification (30 points max)
        - Cash efficiency (15 points max)
        - Concentration risk (15 points max)
        
        Returns:
            Dict with score, grade, status, breakdown
        """
        score = 100
        breakdown = []
        
        # Factor 1: Alignment with target (40 points max)
        drift = allocation_analysis['drift']
        alignment_penalty = min(drift / 2, 40)  # Max -40 points
        score -= alignment_penalty
        breakdown.append({
            "factor": "Alignment with Target",
            "penalty": -round(alignment_penalty, 1),
            "reason": f"{drift}% drift from target allocation"
        })
        
        # Factor 2: Concentration risk (15 points max)
        max_holding = max([h.get('portfolioWeight', 0) for h in holdings], default=0)
        if max_holding > 50:
            concentration_penalty = 15
            reason = f"One position is {max_holding}% (very high)"
        elif max_holding > 30:
            concentration_penalty = 10
            reason = f"One position is {max_holding}% (high)"
        else:
            concentration_penalty = 0
            reason = f"Largest position is {max_holding}% (acceptable)"
        
        score -= concentration_penalty
        breakdown.append({
            "factor": "Concentration Risk",
            "penalty": -concentration_penalty,
            "reason": reason
        })
        
        # Factor 3: Cash efficiency (15 points max)
        cash_pct = allocation_analysis['current']['cash']
        if cash_pct > 30:
            cash_penalty = 15
            reason = f"{cash_pct}% idle cash (excessive)"
        elif cash_pct > 20:
            cash_penalty = 10
            reason = f"{cash_pct}% idle cash (high)"
        elif cash_pct < 5:
            cash_penalty = 5
            reason = f"{cash_pct}% cash (too low for emergencies)"
        else:
            cash_penalty = 0
            reason = f"{cash_pct}% cash (healthy)"
        
        score -= cash_penalty
        breakdown.append({
            "factor": "Cash Management",
            "penalty": -cash_penalty,
            "reason": reason
        })
        
        # Factor 4: Diversification (30 points max)
        num_holdings = len(holdings)
        if num_holdings < 3:
            diversification_penalty = 30
            reason = f"Only {num_holdings} holdings (very low)"
        elif num_holdings < 5:
            diversification_penalty = 20
            reason = f"Only {num_holdings} holdings (low)"
        elif num_holdings < 8:
            diversification_penalty = 10
            reason = f"{num_holdings} holdings (moderate)"
        else:
            diversification_penalty = 0
            reason = f"{num_holdings} holdings (good)"
        
        score -= diversification_penalty
        breakdown.append({
            "factor": "Diversification",
            "penalty": -diversification_penalty,
            "reason": reason
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
        
        print(f"\n🏥 Health Score: {score}/100 (Grade {grade})")
        for item in breakdown:
            print(f"   {item['factor']}: {item['penalty']} pts - {item['reason']}")
        
        return {
            "score": int(score),
            "grade": grade,
            "status": status,
            "breakdown": breakdown
        }
    
    # ==================== MODULE 4: REBALANCING PLANNER ====================
    
    def generate_rebalancing_plan(self, current_holdings: List[Dict], 
                                   allocation_analysis: Dict,
                                   target_model: Dict) -> Dict:
        """
        Generate specific buy/sell instructions with exact dollar amounts
        
        Returns:
            Dict with cash_deployment, sells, buys, expected_result
        """
        total_assets = allocation_analysis['totalAssets']
        cash_savings = allocation_analysis['cashSavings']
        current = allocation_analysis['current']
        target = allocation_analysis['target']
        
        # Calculate target dollar amounts
        target_amounts = {
            "stocks": total_assets * target['stocks'] / 100,
            "bonds": total_assets * target['bonds'] / 100,
            "cash": total_assets * target['cash'] / 100
        }
        
        # Calculate current dollar amounts
        current_amounts = {
            "stocks": total_assets * current['stocks'] / 100,
            "bonds": total_assets * current['bonds'] / 100,
            "cash": cash_savings
        }
        
        # Calculate needed changes
        needed_changes = {
            "stocks": target_amounts['stocks'] - current_amounts['stocks'],
            "bonds": target_amounts['bonds'] - current_amounts['bonds'],
            "cash": target_amounts['cash'] - current_amounts['cash']
        }
        
        print(f"\n💰 Rebalancing Analysis:")
        print(f"   Need to add ${needed_changes['stocks']:,.0f} in stocks")
        print(f"   Need to add ${needed_changes['bonds']:,.0f} in bonds")
        print(f"   Need to reduce cash by ${-needed_changes['cash']:,.0f}")
        
        # Generate plan
        plan = {
            "summary": "",
            "cashDeployment": [],
            "sells": [],
            "buys": [],
            "expectedResult": {}
        }
        
        # STEP 1: Deploy excess cash
        excess_cash = cash_savings - target_amounts['cash']
        if excess_cash > 1000:
            print(f"\n💵 Step 1: Deploy ${excess_cash:,.0f} excess cash")
            
            # Allocate to bonds if needed
            if needed_changes['bonds'] > 0:
                bond_amount = min(excess_cash, needed_changes['bonds'])
                etf = self.RECOMMENDED_ETFS['bonds']
                plan['cashDeployment'].append({
                    "action": "BUY",
                    "symbol": etf['symbol'],
                    "name": etf['name'],
                    "amount": round(bond_amount, 2),
                    "estimatedShares": int(bond_amount / 80),  # Assume ~$80/share
                    "reason": f"Add bond allocation ({current['bonds']:.0f}% → {target['bonds']:.0f}%)",
                    "priority": "HIGH"
                })
                excess_cash -= bond_amount
            
            # Allocate remaining to stocks
            if excess_cash > 1000 and needed_changes['stocks'] > 0:
                stock_amount = min(excess_cash, needed_changes['stocks'])
                
                # Split between US and International
                us_amount = stock_amount * 0.7
                intl_amount = stock_amount * 0.3
                
                # US Stocks
                etf = self.RECOMMENDED_ETFS['us_stocks']
                plan['cashDeployment'].append({
                    "action": "BUY",
                    "symbol": etf['symbol'],
                    "name": etf['name'],
                    "amount": round(us_amount, 2),
                    "estimatedShares": int(us_amount / 250),  # Assume ~$250/share
                    "reason": "Diversify US stock exposure",
                    "priority": "HIGH"
                })
                
                # International Stocks
                etf = self.RECOMMENDED_ETFS['international']
                plan['cashDeployment'].append({
                    "action": "BUY",
                    "symbol": etf['symbol'],
                    "name": etf['name'],
                    "amount": round(intl_amount, 2),
                    "estimatedShares": int(intl_amount / 67),  # Assume ~$67/share
                    "reason": "Add international diversification",
                    "priority": "MEDIUM"
                })
        
        # STEP 2: Reduce concentration
        for holding in current_holdings:
            weight = holding.get('portfolioWeight', 0)
            if weight > 30:
                # Calculate how much to sell to get to 30%
                target_weight = 30
                current_value = holding['currentValue']
                target_value = total_assets * (target_weight / 100)
                sell_amount = current_value - target_value
                
                if sell_amount > 500:  # Only if meaningful amount
                    plan['sells'].append({
                        "action": "SELL",
                        "symbol": holding['symbol'],
                        "amount": round(sell_amount, 2),
                        "estimatedShares": int(sell_amount / holding['currentPrice']),
                        "reason": f"Reduce concentration from {weight:.0f}% to {target_weight}%",
                        "priority": "HIGH",
                        "proceedsAllocation": "Use to buy underweight positions"
                    })
        
        # Generate summary
        total_to_deploy = sum(item['amount'] for item in plan['cashDeployment'])
        total_to_sell = sum(item['amount'] for item in plan['sells'])
        
        if total_to_deploy > 0 and total_to_sell > 0:
            plan['summary'] = f"Deploy ${total_to_deploy:,.0f} cash and rebalance ${total_to_sell:,.0f}"
        elif total_to_deploy > 0:
            plan['summary'] = f"Deploy ${total_to_deploy:,.0f} from cash reserves"
        elif total_to_sell > 0:
            plan['summary'] = f"Rebalance ${total_to_sell:,.0f} to reduce concentration"
        else:
            plan['summary'] = "Portfolio is well-aligned, no major changes needed"
        
        # Expected result after rebalancing
        plan['expectedResult'] = {
            "newAllocation": target,
            "newHealthScore": 85,  # Estimate
            "improvement": "+25 to +70 points depending on current score"
        }
        
        print(f"\n📋 Rebalancing Plan: {plan['summary']}")
        
        return plan
    
    # ==================== MODULE 5: PERFORMANCE ANALYZER ====================
    
    def analyze_performance(self, holdings: List[Dict], user_profile: Dict) -> Dict:
        """
        Compare performance vs appropriate benchmark
        
        Note: This is simplified - in production, you'd calculate actual returns
        For now, we'll estimate based on market data if available
        
        Returns:
            Dict with performance comparison and attribution
        """
        # For now, return placeholder - will enhance with actual calculation
        # You'd need historical data to calculate true returns
        
        model_name = user_profile.get('modelPortfolio', 'Moderate')
        
        # Benchmark returns (example - would fetch actual data)
        benchmark_returns = {
            "Conservative": {"ytd": 5.2, "name": "30/60 Conservative Portfolio"},
            "ModeratelyConservative": {"ytd": 6.8, "name": "45/45 Moderate-Conservative Portfolio"},
            "Moderate": {"ytd": 8.5, "name": "60/30 Moderate Portfolio"},
            "ModeratelyAggressive": {"ytd": 10.2, "name": "75/20 Moderate-Aggressive Portfolio"},
            "Aggressive": {"ytd": 11.8, "name": "85/10 Aggressive Portfolio"}
        }
        
        benchmark = benchmark_returns.get(model_name, benchmark_returns['Moderate'])
        
        # Calculate user's return (simplified - just use current data)
        # In production, you'd compare initial investment vs current value over time
        total_value = sum(h['currentValue'] for h in holdings)
        
        # Placeholder calculation
        user_return = 0.0  # Would calculate from historical data
        
        attribution = [
            {
                "factor": "Asset Allocation",
                "impact": 0.0,
                "explanation": "Impact of your allocation choices vs benchmark"
            },
            {
                "factor": "Security Selection",
                "impact": 0.0,
                "explanation": "Performance of individual holdings"
            }
        ]
        
        print(f"\n📈 Performance Analysis:")
        print(f"   Benchmark: {benchmark['name']}")
        print(f"   Note: Historical return calculation requires time-series data")
        
        return {
            "userReturn": user_return,
            "benchmarkReturn": benchmark['ytd'],
            "benchmarkName": benchmark['name'],
            "difference": user_return - benchmark['ytd'],
            "attribution": attribution,
            "note": "Performance calculation requires historical portfolio data"
        }
    
    # ==================== MODULE 6: RECOMMENDATION GENERATOR ====================
    
    def generate_recommendations(self, analysis_results: Dict) -> List[Dict]:
        """
        Create prioritized, actionable recommendations
        
        Returns:
            List of recommendations sorted by priority
        """
        recommendations = []
        
        allocation = analysis_results['allocationAnalysis']
        health = analysis_results['portfolioHealth']
        plan = analysis_results['rebalancingPlan']
        issues = allocation['issues']
        
        # HIGH PRIORITY: Critical drift
        if allocation['drift'] > 20:
            recommendations.append({
                "priority": "HIGH",
                "category": "REBALANCING",
                "title": "Critical Portfolio Drift Detected",
                "description": f"Your portfolio is {allocation['drift']:.0f}% off target allocation",
                "action": "Review and implement the rebalancing plan below",
                "impact": "Restore risk profile alignment and reduce portfolio risk",
                "icon": "⚠️"
            })
        
        # HIGH PRIORITY: Excess cash
        if "EXCESS_CASH" in issues:
            cash_pct = allocation['current']['cash']
            cash_amount = allocation['cashSavings']
            deploy_amount = cash_amount - (allocation['totalAssets'] * allocation['target']['cash'] / 100)
            
            if deploy_amount > 1000:
                recommendations.append({
                    "priority": "HIGH",
                    "category": "CASH",
                    "title": "Deploy Idle Cash",
                    "description": f"${cash_amount:,.0f} ({cash_pct:.0f}%) in cash is not working for you",
                    "action": f"Consider investing ${deploy_amount:,.0f} following the rebalancing plan",
                    "impact": f"Potential +${int(deploy_amount * 0.08):,}/year in returns (assuming 8% market return)",
                    "icon": "💰"
                })
        
        # HIGH PRIORITY: Concentration risk
        if "CONCENTRATION_RISK" in issues:
            recommendations.append({
                "priority": "HIGH",
                "category": "CONCENTRATION",
                "title": "High Concentration Risk",
                "description": "One or more positions exceed 30% of your portfolio",
                "action": "Review concentration alerts and consider reducing large positions",
                "impact": "Reduce portfolio volatility by 15-25%",
                "icon": "🎯"
            })
        
        # HIGH PRIORITY: Missing bonds
        if "MISSING_BONDS" in issues and allocation['target']['bonds'] > 0:
            target_bond_amt = allocation['totalAssets'] * allocation['target']['bonds'] / 100
            recommendations.append({
                "priority": "HIGH",
                "category": "DIVERSIFICATION",
                "title": "Add Bond Allocation",
                "description": f"Your portfolio has 0% bonds. Target is {allocation['target']['bonds']:.0f}%",
                "action": f"Consider adding ${target_bond_amt:,.0f} to bond ETFs like BND",
                "impact": "Better downside protection during market corrections",
                "icon": "🛡️"
            })
        
        # MEDIUM PRIORITY: Low diversification
        if "LOW_DIVERSIFICATION" in issues:
            recommendations.append({
                "priority": "MEDIUM",
                "category": "DIVERSIFICATION",
                "title": "Increase Diversification",
                "description": f"Your portfolio has few holdings",
                "action": "Consider adding 2-3 more ETFs across different sectors/regions",
                "impact": "Lower portfolio volatility and reduce single-stock risk",
                "icon": "📊"
            })
        
        # MEDIUM: Monthly contribution reminder
        monthly = analysis_results.get('userProfile', {}).get('monthlyContribution', 0)
        if monthly > 0:
            recommendations.append({
                "priority": "MEDIUM",
                "category": "CONTRIBUTION",
                "title": "Continue Monthly Contributions",
                "description": f"Your planned ${monthly:,.0f}/month contribution",
                "action": "Deploy contributions to underweight positions per rebalancing plan",
                "impact": f"Builds wealth through dollar-cost averaging",
                "icon": "💵"
            })
        
        # Sort by priority
        priority_rank = {"HIGH": 1, "MEDIUM": 2, "LOW": 3}
        recommendations.sort(key=lambda x: priority_rank.get(x['priority'], 99))
        
        print(f"\n💡 Generated {len(recommendations)} recommendations")
        
        return recommendations
    
    # ==================== MAIN ORCHESTRATION METHOD ====================
    
    def analyze_portfolio(self, user_email: str, market_data: Dict) -> Dict:
        """
        Main method - orchestrates all 6 modules
        
        Args:
            user_email: User's email address
            market_data: Output from HybridMarketDataAgent
        
        Returns:
            Complete analysis with recommendations
        """
        print("=" * 60)
        print(f"🤖 Portfolio Analysis Agent - Starting")
        print(f"👤 User: {user_email}")
        print("=" * 60)
        
        try:
            # Validate market data
            if not market_data.get('success'):
                return {
                    'success': False,
                    'error': 'Invalid market data provided'
                }
            
            # Get user profile from DynamoDB
            user_profile = self.get_user_profile(user_email)
            if not user_profile:
                return {
                    'success': False,
                    'error': 'User profile not found'
                }
            
            holdings = market_data.get('holdings', [])
            cash_savings = market_data.get('cashSavings', 0)
            
            # MODULE 1: Select model portfolio
            model_name, target_model = self.select_model_portfolio(user_profile)
            
            # MODULE 2: Analyze allocation
            allocation_analysis = self.analyze_allocation(holdings, target_model, cash_savings)
            
            # MODULE 3: Calculate health score
            health_score = self.calculate_health_score(allocation_analysis, holdings)
            
            # MODULE 4: Generate rebalancing plan
            rebalancing_plan = self.generate_rebalancing_plan(
                holdings, 
                allocation_analysis, 
                target_model
            )
            
            # MODULE 5: Analyze performance
            performance = self.analyze_performance(holdings, {**user_profile, 'modelPortfolio': model_name})
            
            # Package results for Module 6
            analysis_results = {
                'userProfile': user_profile,
                'allocationAnalysis': allocation_analysis,
                'portfolioHealth': health_score,
                'rebalancingPlan': rebalancing_plan,
                'performance': performance
            }
            
            # MODULE 6: Generate recommendations
            recommendations = self.generate_recommendations(analysis_results)
            
            print("\n" + "=" * 60)
            print(f"✅ Analysis Complete!")
            print(f"📊 Health Score: {health_score['score']}/100 (Grade {health_score['grade']})")
            print(f"💡 Recommendations: {len(recommendations)}")
            print("=" * 60)
            
            # Return complete analysis
            return {
                'success': True,
                'timestamp': datetime.utcnow().isoformat(),
                'userId': user_email,
                
                'portfolioHealth': health_score,
                
                'modelPortfolio': {
                    'name': model_name,
                    'description': target_model['description'],
                    'suitableFor': target_model['suitableFor'],
                    'expectedReturn': target_model['expectedReturn'],
                    'expectedVolatility': target_model['expectedVolatility']
                },
                
                'allocationAnalysis': allocation_analysis,
                'rebalancingPlan': rebalancing_plan,
                'performance': performance,
                'recommendations': recommendations,
                
                'disclaimer': (
                    "This analysis provides educational guidance based on modern portfolio theory principles. "
                    "It is not personalized investment advice. Always consult a licensed financial advisor "
                    "before making investment decisions."
                )
            }
            
        except Exception as e:
            print(f"❌ Error in analysis: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e),
                'userId': user_email
            }
    
    # ==================== HELPER METHODS ====================
    
    def get_user_profile(self, user_email: str) -> Optional[Dict]:
        """Fetch user profile from DynamoDB"""
        try:
            response = self.users_table.get_item(Key={'userId': user_email})
            if 'Item' in response:
                user = response['Item']
                # Convert Decimal to float for JSON serialization
                return self.convert_decimal_to_float(user)
            return None
        except Exception as e:
            print(f"❌ Error fetching user profile: {e}")
            return None
    
    def convert_decimal_to_float(self, obj):
        """Convert Decimal to float for JSON serialization"""
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, dict):
            return {k: self.convert_decimal_to_float(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self.convert_decimal_to_float(item) for item in obj]
        return obj


# ==================== TESTING ====================

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    print("\n" + "=" * 60)
    print("🧪 TESTING PORTFOLIO ANALYSIS AGENT")
    print("=" * 60 + "\n")
    
    # Initialize agent
    agent = PortfolioAnalysisAgent()
    
    # Mock market data (simulating output from HybridMarketDataAgent)
    mock_market_data = {
        "success": True,
        "timestamp": "2025-10-18T12:00:00",
        "userId": "shruti@gmail.com",
        "holdings": [
            {
                "symbol": "NVDA",
                "type": "stock",
                "quantity": 20,
                "currentValue": 3636.2,
                "currentPrice": 181.81,
                "portfolioWeight": 16.57,
                "sector": "TECHNOLOGY",
                "beta": 2.12
            },
            {
                "symbol": "AMZN",
                "type": "stock",
                "quantity": 12,
                "currentValue": 2573.64,
                "currentPrice": 214.47,
                "portfolioWeight": 11.73,
                "sector": "Retail",
                "beta": 1.15
            },
            {
                "symbol": "QQQ",
                "type": "etf",
                "quantity": 24,
                "currentValue": 14399.76,
                "currentPrice": 599.99,
                "portfolioWeight": 65.62,
                "sector": "TECHNOLOGY",
                "beta": 1.05
            },
            {
                "symbol": "VEA",
                "type": "etf",
                "quantity": 22,
                "currentValue": 1334.52,
                "currentPrice": 60.66,
                "portfolioWeight": 6.08,
                "sector": "International",
                "beta": 0.85
            }
        ],
        "portfolioMetrics": {
            "totalValue": 21944.12,
            "portfolioBeta": 0.35
        },
        "cashSavings": 40000
    }
    
    # Test with mock user
    test_email = "shruti@gmail.com"
    
    print(f"Testing with user: {test_email}")
    print(f"Mock portfolio value: ${mock_market_data['portfolioMetrics']['totalValue']:,.2f}")
    print(f"Mock cash: ${mock_market_data['cashSavings']:,.2f}")
    print()
    
    # Run analysis
    analysis = agent.analyze_portfolio(test_email, mock_market_data)
    
    # Display results
    print("\n" + "=" * 60)
    print("📊 ANALYSIS RESULTS")
    print("=" * 60)
    
    if analysis['success']:
        print(f"\n✅ SUCCESS!")
        print(f"\n🏥 Portfolio Health:")
        print(f"   Score: {analysis['portfolioHealth']['score']}/100")
        print(f"   Grade: {analysis['portfolioHealth']['grade']}")
        print(f"   Status: {analysis['portfolioHealth']['status']}")
        
        print(f"\n📋 Model Portfolio: {analysis['modelPortfolio']['name']}")
        print(f"   {analysis['modelPortfolio']['description']}")
        
        print(f"\n📊 Allocation:")
        current = analysis['allocationAnalysis']['current']
        target = analysis['allocationAnalysis']['target']
        print(f"   Current: {current['stocks']}% stocks, {current['bonds']}% bonds, {current['cash']}% cash")
        print(f"   Target:  {target['stocks']}% stocks, {target['bonds']}% bonds, {target['cash']}% cash")
        print(f"   Drift: {analysis['allocationAnalysis']['drift']}%")
        
        print(f"\n🔄 Rebalancing Plan:")
        print(f"   {analysis['rebalancingPlan']['summary']}")
        print(f"   Cash Deployment Actions: {len(analysis['rebalancingPlan']['cashDeployment'])}")
        print(f"   Sell Actions: {len(analysis['rebalancingPlan']['sells'])}")
        
        print(f"\n💡 Recommendations: {len(analysis['recommendations'])}")
        for i, rec in enumerate(analysis['recommendations'][:3], 1):  # Show top 3
            print(f"   {i}. [{rec['priority']}] {rec['title']}")
        
        print(f"\n⏰ Timestamp: {analysis['timestamp']}")
        
    else:
        print(f"\n❌ FAILED: {analysis.get('error')}")
    
    print("\n" + "=" * 60)
    print("🧪 TEST COMPLETE")
    print("=" * 60)
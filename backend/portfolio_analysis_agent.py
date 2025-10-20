# strand_portfolio_agent.py
import os
import boto3
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from decimal import Decimal
import traceback

# ---------------------------
# ADAPT: Import STRAND SDK
# ---------------------------
# Replace these imports with the exact objects from your STRAND SDK.
# Common names used in Strand examples: Agent, Tool, Task, Runner, etc.
try:
    # This is a conservative placeholder import. Replace with your real SDK.
    from strand import Agent, Tool, Task, Runner  # ADAPT: change to actual SDK names
except Exception:
    # If the SDK import fails in local environment, we provide lightweight placeholders
    class Tool:
        def __init__(self, fn): self.fn = fn
        def __call__(self, *args, **kwargs): return self.fn(*args, **kwargs)

    class Task(Tool):
        pass

    class Agent:
        def __init__(self, name: str): self.name = name; self.tasks = {}
        def register(self, name, fn): self.tasks[name] = fn
        async def run(self, *args, **kwargs):
            # naive runner that calls .run_entry
            if hasattr(self, 'run_entry'):
                return await self.run_entry(*args, **kwargs)
            raise RuntimeError("No run_entry implemented")

    class Runner:
        def __init__(self, agent): self.agent = agent
        def start(self, *args, **kwargs):
            import asyncio
            return asyncio.run(self.agent.run(*args, **kwargs))


# ---------------------------
# Strand-based Portfolio Agent
# ---------------------------
class PortfolioAnalysisAgent:
    """
    Strand-based agent wrapper around the original PortfolioAnalysisAgent logic.
    Each module is registered as a tool/task so Strand runtime can orchestrate.
    """

    def __init__(self, aws_region: str = None):
        self.aws_region = aws_region or os.getenv("AWS_REGION", "us-east-1")
        self.dynamodb = boto3.resource("dynamodb", region_name=self.aws_region)
        self.users_table = self.dynamodb.Table('WealthWiseUsers')
        self.portfolios_table = self.dynamodb.Table('WealthWisePortfolios')

        # --- Model portfolios and ETFs (unchanged) ---
        self.MODEL_PORTFOLIOS = {
            "Conservative": {
                "stocks": 30, "bonds": 60, "cash": 10,
                "expectedReturn": 4.5, "expectedVolatility": 8,
                "description": "Low risk, capital preservation focus",
                "suitableFor": "Age 55+, Low risk tolerance, Short horizon"
            },
            "ModeratelyConservative": {
                "stocks": 45, "bonds": 45, "cash": 10,
                "expectedReturn": 6.0, "expectedVolatility": 11,
                "description": "Below-average risk, some growth potential",
                "suitableFor": "Age 45-55, Low-Moderate risk, Medium horizon"
            },
            "Moderate": {
                "stocks": 60, "bonds": 30, "cash": 10,
                "expectedReturn": 7.5, "expectedVolatility": 14,
                "description": "Balanced growth and stability",
                "suitableFor": "Age 30-45, Moderate risk, Long horizon"
            },
            "ModeratelyAggressive": {
                "stocks": 75, "bonds": 20, "cash": 5,
                "expectedReturn": 8.5, "expectedVolatility": 16,
                "description": "Above-average risk, growth focused",
                "suitableFor": "Age 25-35, Moderate-High risk, Long horizon"
            },
            "Aggressive": {
                "stocks": 85, "bonds": 10, "cash": 5,
                "expectedReturn": 9.5, "expectedVolatility": 18,
                "description": "High risk, maximum growth potential",
                "suitableFor": "Age <30, High risk tolerance, Very long horizon"
            }
        }

        self.RECOMMENDED_ETFS = {
            "us_stocks": {"symbol": "VTI", "name": "Vanguard Total Stock Market ETF", "expense": 0.03},
            "bonds": {"symbol": "BND", "name": "Vanguard Total Bond Market ETF", "expense": 0.03},
            "international": {"symbol": "VXUS", "name": "Vanguard Total International Stock ETF", "expense": 0.07},
            "reits": {"symbol": "VNQ", "name": "Vanguard Real Estate ETF", "expense": 0.12}
        }

        # Create a Strand Agent instance (or equivalent)
        self.agent = Agent(name="WealthWisePortfolioAgent")  # ADAPT: your SDK's agent creation

        # Register tools/tasks with the Strand agent
        # ADAPT: If your SDK expects decorators, use them instead of this registration style.
        self.agent.register("get_user_profile", Tool(self.get_user_profile))
        self.agent.register("select_model_portfolio", Task(self.select_model_portfolio))
        self.agent.register("analyze_allocation", Task(self.analyze_allocation))
        self.agent.register("calculate_health_score", Task(self.calculate_health_score))
        self.agent.register("generate_rebalancing_plan", Task(self.generate_rebalancing_plan))
        self.agent.register("analyze_performance", Task(self.analyze_performance))
        self.agent.register("generate_recommendations", Task(self.generate_recommendations))

        print("✅ PortfolioAnalysisAgent initialized")

    # -----------------------
    # Core orchestration entry
    # -----------------------
    async def run(self, user_email: str, market_data: Dict) -> Dict:
        """
        Entry point the STRAND runtime should call.
        Orchestrates the steps by invoking registered tasks/tools.
        """
        print("=" * 60)
        print("🤖 PortfolioAnalysisAgent.run - start")
        print(f"👤 user: {user_email}")
        print("=" * 60)

        try:
            # Validate market_data
            if not market_data.get('success'):
                return {'success': False, 'error': 'Invalid market data provided'}

            # Fetch user profile using the registered tool
            user_profile = self.get_user_profile(user_email)
            if not user_profile:
                return {'success': False, 'error': 'User profile not found'}

            holdings = market_data.get('holdings', [])
            cash_savings = market_data.get('cashSavings', 0)

            # MODULE 1 - select model
            model_name, target_model = self.select_model_portfolio(user_profile)

            # MODULE 2 - allocation analysis
            allocation_analysis = self.analyze_allocation(holdings, target_model, cash_savings)

            # MODULE 3 - health score
            health_score = self.calculate_health_score(allocation_analysis, holdings)

            # MODULE 4 - rebalancing plan
            rebalancing_plan = self.generate_rebalancing_plan(holdings, allocation_analysis, target_model)

            # MODULE 5 - performance
            performance = self.analyze_performance(holdings, {**user_profile, 'modelPortfolio': model_name})

            # PACK results for recommendations
            analysis_results = {
                'userProfile': user_profile,
                'allocationAnalysis': allocation_analysis,
                'portfolioHealth': health_score,
                'rebalancingPlan': rebalancing_plan,
                'performance': performance
            }

            # MODULE 6 - generate recommendations
            recommendations = self.generate_recommendations({
                'allocationAnalysis': allocation_analysis,
                'portfolioHealth': health_score,
                'rebalancingPlan': rebalancing_plan,
                'userProfile': user_profile
            })

            # Final response
            response = {
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

            print("✅ PortfolioAnalysisAgent.run - complete")
            return response

        except Exception as e:
            print(f"❌ Error in PortfolioAnalysisAgent.run: {e}")
            traceback.print_exc()
            return {'success': False, 'error': str(e), 'userId': user_email}

    # -----------------------
    # Tools / Tasks (same logic as original)
    # -----------------------
    def get_user_profile(self, user_email: str) -> Optional[Dict]:
        """Fetch user profile from DynamoDB (returns plain py types)."""
        try:
            resp = self.users_table.get_item(Key={'userId': user_email})
            if 'Item' in resp:
                return self.convert_decimal_to_float(resp['Item'])
            return None
        except Exception as e:
            print(f"❌ Error fetching user profile: {e}")
            return None

    def select_model_portfolio(self, user_profile: Dict) -> Tuple[str, Dict]:
        age = user_profile.get('age', 35)
        risk = user_profile.get('riskTolerance', 'Moderate').lower()
        horizon = user_profile.get('investmentHorizon', '5-10 years').lower()

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

        model = self.MODEL_PORTFOLIOS[model_name]
        return model_name, model

    def analyze_allocation(self, current_holdings: List[Dict], target_model: Dict, cash_savings: float) -> Dict:
        total_invested = sum(h['currentValue'] for h in current_holdings)
        total_assets = total_invested + cash_savings

        stocks_value = 0
        bonds_value = 0
        for holding in current_holdings:
            holding_type = holding.get('type', 'stock').lower()
            sector = holding.get('sector', '').upper()
            if holding_type == 'bond' or 'BOND' in sector or holding['symbol'].upper() in ['BND', 'AGG', 'TLT']:
                bonds_value += holding['currentValue']
            else:
                stocks_value += holding['currentValue']

        current_allocation = {
            "stocks": round((stocks_value / total_assets) * 100, 1) if total_assets > 0 else 0,
            "bonds": round((bonds_value / total_assets) * 100, 1) if total_assets > 0 else 0,
            "cash": round((cash_savings / total_assets) * 100, 1) if total_assets > 0 else 0
        }

        target_allocation = {"stocks": target_model['stocks'], "bonds": target_model['bonds'], "cash": target_model['cash']}

        drift = sum(abs(current_allocation[k] - target_allocation[k]) for k in current_allocation.keys())
        drift = round(drift, 1)

        issues = []
        if drift > 20:
            issues.append("CRITICAL_DRIFT")
        if current_allocation['cash'] > 20:
            issues.append("EXCESS_CASH")
        if bonds_value == 0 and target_allocation['bonds'] > 0:
            issues.append("MISSING_BONDS")

        for holding in current_holdings:
            weight = holding.get('portfolioWeight', 0)
            if weight > 30:
                issues.append("CONCENTRATION_RISK")
                break

        if len(current_holdings) < 5:
            issues.append("LOW_DIVERSIFICATION")

        return {
            "current": current_allocation,
            "target": target_allocation,
            "drift": drift,
            "issues": issues,
            "totalAssets": round(total_assets, 2),
            "totalInvested": round(total_invested, 2),
            "cashSavings": round(cash_savings, 2)
        }

    def calculate_health_score(self, allocation_analysis: Dict, holdings: List[Dict]) -> Dict:
        score = 100
        breakdown = []

        drift = allocation_analysis['drift']
        alignment_penalty = min(drift / 2, 40)
        score -= alignment_penalty
        breakdown.append({"factor": "Alignment with Target", "penalty": -round(alignment_penalty, 1),
                          "reason": f"{drift}% drift from target allocation"})

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
        breakdown.append({"factor": "Concentration Risk", "penalty": -concentration_penalty, "reason": reason})

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
        breakdown.append({"factor": "Cash Management", "penalty": -cash_penalty, "reason": reason})

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
        breakdown.append({"factor": "Diversification", "penalty": -diversification_penalty, "reason": reason})

        score = max(0, min(100, round(score, 0)))
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

        return {"score": int(score), "grade": grade, "status": status, "breakdown": breakdown}

    def generate_rebalancing_plan(self, current_holdings: List[Dict], allocation_analysis: Dict, target_model: Dict) -> Dict:
        total_assets = allocation_analysis['totalAssets']
        cash_savings = allocation_analysis['cashSavings']
        current = allocation_analysis['current']
        target = allocation_analysis['target']

        target_amounts = {
            "stocks": total_assets * target['stocks'] / 100,
            "bonds": total_assets * target['bonds'] / 100,
            "cash": total_assets * target['cash'] / 100
        }
        current_amounts = {"stocks": total_assets * current['stocks'] / 100, "bonds": total_assets * current['bonds'] / 100, "cash": cash_savings}
        needed_changes = {k: target_amounts[k] - current_amounts[k] for k in target_amounts.keys()}

        plan = {"summary": "", "cashDeployment": [], "sells": [], "buys": [], "expectedResult": {}}
        excess_cash = cash_savings - target_amounts['cash']

        if excess_cash > 1000:
            if needed_changes['bonds'] > 0:
                bond_amount = min(excess_cash, needed_changes['bonds'])
                etf = self.RECOMMENDED_ETFS['bonds']
                plan['cashDeployment'].append({
                    "action": "BUY", "symbol": etf['symbol'], "name": etf['name'],
                    "amount": round(bond_amount, 2),
                    "estimatedShares": int(bond_amount / 80),
                    "reason": f"Add bond allocation ({current['bonds']:.0f}% → {target['bonds']:.0f}%)",
                    "priority": "HIGH"
                })
                excess_cash -= bond_amount

            if excess_cash > 1000 and needed_changes['stocks'] > 0:
                stock_amount = min(excess_cash, needed_changes['stocks'])
                us_amount = stock_amount * 0.7
                intl_amount = stock_amount * 0.3

                etf = self.RECOMMENDED_ETFS['us_stocks']
                plan['cashDeployment'].append({
                    "action": "BUY", "symbol": etf['symbol'], "name": etf['name'],
                    "amount": round(us_amount, 2), "estimatedShares": int(us_amount / 250),
                    "reason": "Diversify US stock exposure", "priority": "HIGH"
                })
                etf = self.RECOMMENDED_ETFS['international']
                plan['cashDeployment'].append({
                    "action": "BUY", "symbol": etf['symbol'], "name": etf['name'],
                    "amount": round(intl_amount, 2), "estimatedShares": int(intl_amount / 67),
                    "reason": "Add international diversification", "priority": "MEDIUM"
                })

        # Reduce concentration
        for holding in current_holdings:
            weight = holding.get('portfolioWeight', 0)
            if weight > 30:
                target_weight = 30
                current_value = holding['currentValue']
                target_value = total_assets * (target_weight / 100)
                sell_amount = current_value - target_value
                if sell_amount > 500:
                    plan['sells'].append({
                        "action": "SELL",
                        "symbol": holding['symbol'],
                        "amount": round(sell_amount, 2),
                        "estimatedShares": int(sell_amount / holding['currentPrice']),
                        "reason": f"Reduce concentration from {weight:.0f}% to {target_weight}%",
                        "priority": "HIGH",
                        "proceedsAllocation": "Use to buy underweight positions"
                    })

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

        plan['expectedResult'] = {"newAllocation": target, "newHealthScore": 85,
                                  "improvement": "+25 to +70 points depending on current score"}
        return plan

    def analyze_performance(self, holdings: List[Dict], user_profile: Dict) -> Dict:
        model_name = user_profile.get('modelPortfolio', 'Moderate')
        benchmark_returns = {
            "Conservative": {"ytd": 5.2, "name": "30/60 Conservative Portfolio"},
            "ModeratelyConservative": {"ytd": 6.8, "name": "45/45 Moderate-Conservative Portfolio"},
            "Moderate": {"ytd": 8.5, "name": "60/30 Moderate Portfolio"},
            "ModeratelyAggressive": {"ytd": 10.2, "name": "75/20 Moderate-Aggressive Portfolio"},
            "Aggressive": {"ytd": 11.8, "name": "85/10 Aggressive Portfolio"}
        }
        benchmark = benchmark_returns.get(model_name, benchmark_returns['Moderate'])
        total_value = sum(h['currentValue'] for h in holdings)
        user_return = 0.0
        attribution = [
            {"factor": "Asset Allocation", "impact": 0.0, "explanation": "Impact of your allocation choices vs benchmark"},
            {"factor": "Security Selection", "impact": 0.0, "explanation": "Performance of individual holdings"}
        ]
        return {
            "userReturn": user_return,
            "benchmarkReturn": benchmark['ytd'],
            "benchmarkName": benchmark['name'],
            "difference": user_return - benchmark['ytd'],
            "attribution": attribution,
            "note": "Performance calculation requires historical portfolio data"
        }

    def generate_recommendations(self, analysis_results: Dict) -> List[Dict]:
        recommendations = []
        allocation = analysis_results['allocationAnalysis']
        health = analysis_results['portfolioHealth']
        plan = analysis_results.get('rebalancingPlan', {})
        issues = allocation.get('issues', [])

        if allocation['drift'] > 20:
            recommendations.append({
                "priority": "HIGH", "category": "REBALANCING",
                "title": "Critical Portfolio Drift Detected",
                "description": f"Your portfolio is {allocation['drift']:.0f}% off target allocation",
                "action": "Review and implement the rebalancing plan below",
                "impact": "Restore risk profile alignment and reduce portfolio risk", "icon": "⚠️"
            })

        if "EXCESS_CASH" in issues:
            cash_pct = allocation['current']['cash']
            cash_amount = allocation['cashSavings']
            deploy_amount = cash_amount - (allocation['totalAssets'] * allocation['target']['cash'] / 100)
            if deploy_amount > 1000:
                recommendations.append({
                    "priority": "HIGH", "category": "CASH", "title": "Deploy Idle Cash",
                    "description": f"${cash_amount:,.0f} ({cash_pct:.0f}%) in cash is not working for you",
                    "action": f"Consider investing ${deploy_amount:,.0f} following the rebalancing plan",
                    "impact": f"Potential +${int(deploy_amount * 0.08):,}/year in returns (assuming 8% market return)",
                    "icon": "💰"
                })

        if "CONCENTRATION_RISK" in issues:
            recommendations.append({
                "priority": "HIGH", "category": "CONCENTRATION", "title": "High Concentration Risk",
                "description": "One or more positions exceed 30% of your portfolio",
                "action": "Review concentration alerts and consider reducing large positions",
                "impact": "Reduce portfolio volatility by 15-25%", "icon": "🎯"
            })

        if "MISSING_BONDS" in issues and allocation['target']['bonds'] > 0:
            target_bond_amt = allocation['totalAssets'] * allocation['target']['bonds'] / 100
            recommendations.append({
                "priority": "HIGH", "category": "DIVERSIFICATION",
                "title": "Add Bond Allocation",
                "description": f"Your portfolio has 0% bonds. Target is {allocation['target']['bonds']:.0f}%",
                "action": f"Consider adding ${target_bond_amt:,.0f} to bond ETFs like BND",
                "impact": "Better downside protection during market corrections", "icon": "🛡️"
            })

        if "LOW_DIVERSIFICATION" in issues:
            recommendations.append({
                "priority": "MEDIUM", "category": "DIVERSIFICATION", "title": "Increase Diversification",
                "description": f"Your portfolio has few holdings",
                "action": "Consider adding 2-3 more ETFs across different sectors/regions",
                "impact": "Lower portfolio volatility and reduce single-stock risk", "icon": "📊"
            })

        monthly = analysis_results.get('userProfile', {}).get('monthlyContribution', 0)
        if monthly > 0:
            recommendations.append({
                "priority": "MEDIUM", "category": "CONTRIBUTION", "title": "Continue Monthly Contributions",
                "description": f"Your planned ${monthly:,.0f}/month contribution",
                "action": "Deploy contributions to underweight positions per rebalancing plan",
                "impact": f"Builds wealth through dollar-cost averaging", "icon": "💵"
            })

        priority_rank = {"HIGH": 1, "MEDIUM": 2, "LOW": 3}
        recommendations.sort(key=lambda x: priority_rank.get(x['priority'], 99))
        return recommendations

    # -----------------------
    # Helpers
    # -----------------------
    def convert_decimal_to_float(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, dict):
            return {k: self.convert_decimal_to_float(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self.convert_decimal_to_float(i) for i in obj]
        return obj


# -----------------------
# Example local runner
# -----------------------
if __name__ == "__main__":
    import asyncio
    from dotenv import load_dotenv
    load_dotenv()

    agent = PortfolioAnalysisAgent()

    # Mock market data (same sample as you provided)
    mock_market_data = {
        "success": True,
        "timestamp": "2025-10-18T12:00:00",
        "userId": "shruti@gmail.com",
        "holdings": [
            {"symbol": "NVDA", "type": "stock", "quantity": 20, "currentValue": 3636.2, "currentPrice": 181.81, "portfolioWeight": 16.57, "sector": "TECHNOLOGY", "beta": 2.12},
            {"symbol": "AMZN", "type": "stock", "quantity": 12, "currentValue": 2573.64, "currentPrice": 214.47, "portfolioWeight": 11.73, "sector": "Retail", "beta": 1.15},
            {"symbol": "QQQ", "type": "etf", "quantity": 24, "currentValue": 14399.76, "currentPrice": 599.99, "portfolioWeight": 65.62, "sector": "TECHNOLOGY", "beta": 1.05},
            {"symbol": "VEA", "type": "etf", "quantity": 22, "currentValue": 1334.52, "currentPrice": 60.66, "portfolioWeight": 6.08, "sector": "International", "beta": 0.85}
        ],
        "portfolioMetrics": {"totalValue": 21944.12, "portfolioBeta": 0.35},
        "cashSavings": 40000
    }

    # Run the agent locally
    # ADAPT: If your Strand runtime provides Runner.run_agent(agent, ...) use that instead.
    async def local_run():
        result = await agent.run("shruti@gmail.com", mock_market_data)
        import json
        print(json.dumps(result, indent=2, default=str))

    asyncio.run(local_run())

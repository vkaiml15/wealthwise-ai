"""
Market Trend Analysis Agent
Analyzes market trends and provides investment insights for specific industries/sectors
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from .base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)


class MarketTrendAgent(BaseAgent):
    """
    Agent responsible for analyzing market trends and providing investment insights
    Uses market data and AI analysis to identify opportunities
    """
    
    def __init__(self):
        super().__init__(
            agent_name="MarketTrendAgent",
            model_id="anthropic.claude-3-5-sonnet-20241022-v2:0"
        )
        self.supported_industries = [
            'technology', 'healthcare', 'finance', 'energy', 'consumer',
            'industrials', 'real-estate', 'utilities', 'materials',
            'telecommunications', 'renewable-energy', 'ai-ml', 'biotech',
            'e-commerce', 'cybersecurity'
        ]
    
    def _get_system_prompt(self) -> str:
        return """You are a Market Trend Analysis Agent for WealthWise AI, specialized in 
analyzing market trends and providing actionable investment insights.

Your expertise includes:
1. Analyzing current market conditions across various sectors
2. Identifying emerging trends and growth opportunities
3. Evaluating industry-specific risks and catalysts
4. Providing data-driven investment recommendations
5. Explaining complex market dynamics in simple terms

When analyzing market trends:
- Focus on factual, data-driven insights
- Consider both short-term and long-term perspectives
- Highlight key risk factors and growth catalysts
- Provide specific, actionable recommendations
- Include relevant market metrics and indicators

Response Structure:
1. Executive Summary (2-3 sentences)
2. Current Market Conditions
3. Key Trends Analysis
4. Growth Catalysts
5. Risk Factors
6. Investment Opportunities
7. Specific Stock/ETF Recommendations (if applicable)

Always structure your analysis with clear sections and bullet points for easy scanning.
Include reasoning for each recommendation.

When recommending industries or stocks:
- Explain WHY they're good opportunities
- Match recommendations to the user's risk profile
- Consider diversification
- Highlight any warnings or risks

End with a relevant follow-up question to engage the user further.
"""
    
    def _register_action_groups(self) -> List[Dict[str, Any]]:
        """Register action groups for market trend analysis"""
        return [
            {
                'name': 'get_industry_trends',
                'description': 'Get current trends for a specific industry',
                'function': self._get_industry_trends
            },
            {
                'name': 'get_sector_performance',
                'description': 'Get performance metrics for market sectors',
                'function': self._get_sector_performance
            },
            {
                'name': 'identify_emerging_trends',
                'description': 'Identify emerging market trends',
                'function': self._identify_emerging_trends
            },
            {
                'name': 'analyze_market_indicators',
                'description': 'Analyze key market indicators',
                'function': self._analyze_market_indicators
            },
            {
                'name': 'get_top_stocks_by_sector',
                'description': 'Get top performing stocks in a sector',
                'function': self._get_top_stocks_by_sector
            }
        ]
    
    def _get_industry_trends(self, industry: str) -> Dict[str, Any]:
        """Get current trends for a specific industry"""
        
        # Mock data - In production, this would connect to real market data APIs
        industry_data = {
            'technology': {
                'trend': 'bullish',
                'growth_rate': '12.5%',
                'key_drivers': [
                    'AI and Machine Learning adoption',
                    'Cloud computing expansion',
                    'Digital transformation'
                ],
                'risks': [
                    'Regulatory scrutiny',
                    'Market saturation in some segments',
                    'High valuations'
                ],
                'outlook': 'positive',
                'recommended_allocation': '25-30%'
            },
            'healthcare': {
                'trend': 'stable-growth',
                'growth_rate': '8.3%',
                'key_drivers': [
                    'Aging population demographics',
                    'Biotechnology innovations',
                    'Healthcare digitization'
                ],
                'risks': [
                    'Regulatory changes',
                    'Drug pricing pressures',
                    'Clinical trial uncertainties'
                ],
                'outlook': 'positive',
                'recommended_allocation': '15-20%'
            },
            'renewable-energy': {
                'trend': 'strong-growth',
                'growth_rate': '18.7%',
                'key_drivers': [
                    'Climate change initiatives',
                    'Government incentives',
                    'Falling technology costs'
                ],
                'risks': [
                    'Policy changes',
                    'Supply chain issues',
                    'Energy storage challenges'
                ],
                'outlook': 'very-positive',
                'recommended_allocation': '10-15%'
            },
            'ai-ml': {
                'trend': 'explosive-growth',
                'growth_rate': '35.2%',
                'key_drivers': [
                    'Generative AI breakthroughs',
                    'Enterprise AI adoption',
                    'AI infrastructure demand'
                ],
                'risks': [
                    'Market hype vs reality',
                    'Regulatory uncertainties',
                    'High competition'
                ],
                'outlook': 'very-positive',
                'recommended_allocation': '15-20%'
            },
            'finance': {
                'trend': 'moderate-growth',
                'growth_rate': '6.8%',
                'key_drivers': [
                    'Interest rate environment',
                    'Fintech disruption',
                    'Digital banking growth'
                ],
                'risks': [
                    'Economic slowdown',
                    'Credit quality concerns',
                    'Regulatory pressures'
                ],
                'outlook': 'neutral-positive',
                'recommended_allocation': '10-15%'
            }
        }
        
        return industry_data.get(
            industry.lower().replace(' ', '-'),
            {
                'trend': 'data-not-available',
                'message': f'Detailed trend data for {industry} is being compiled'
            }
        )
    
    def _get_sector_performance(self) -> Dict[str, Any]:
        """Get performance metrics for all major sectors"""
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'sectors': {
                'Technology': {
                    'ytd_return': 15.8,
                    'one_month': 3.2,
                    'three_month': 8.5,
                    'momentum': 'strong'
                },
                'Healthcare': {
                    'ytd_return': 8.3,
                    'one_month': 1.5,
                    'three_month': 4.2,
                    'momentum': 'moderate'
                },
                'Financials': {
                    'ytd_return': 6.7,
                    'one_month': 0.8,
                    'three_month': 3.1,
                    'momentum': 'moderate'
                },
                'Energy': {
                    'ytd_return': -2.4,
                    'one_month': -1.2,
                    'three_month': 0.5,
                    'momentum': 'weak'
                },
                'Consumer Discretionary': {
                    'ytd_return': 11.2,
                    'one_month': 2.3,
                    'three_month': 6.8,
                    'momentum': 'strong'
                },
                'Industrials': {
                    'ytd_return': 9.5,
                    'one_month': 1.8,
                    'three_month': 5.2,
                    'momentum': 'moderate'
                }
            },
            'top_performer': 'Technology',
            'bottom_performer': 'Energy'
        }
    
    def _identify_emerging_trends(self) -> Dict[str, Any]:
        """Identify emerging market trends"""
        
        return {
            'emerging_trends': [
                {
                    'name': 'Artificial Intelligence & Machine Learning',
                    'confidence': 'very-high',
                    'timeframe': 'long-term',
                    'investment_potential': 'excellent',
                    'description': 'Generative AI and enterprise AI adoption driving unprecedented growth',
                    'key_players': ['NVDA', 'MSFT', 'GOOGL', 'META']
                },
                {
                    'name': 'Renewable Energy Transition',
                    'confidence': 'high',
                    'timeframe': 'long-term',
                    'investment_potential': 'strong',
                    'description': 'Global shift to clean energy creating massive opportunities',
                    'key_players': ['ENPH', 'SEDG', 'NEE', 'ICLN (ETF)']
                },
                {
                    'name': 'Healthcare Innovation',
                    'confidence': 'high',
                    'timeframe': 'medium-long-term',
                    'investment_potential': 'strong',
                    'description': 'Biotechnology breakthroughs and digital health transformation',
                    'key_players': ['ISRG', 'TDOC', 'ILMN', 'XLV (ETF)']
                },
                {
                    'name': 'Cybersecurity',
                    'confidence': 'high',
                    'timeframe': 'medium-long-term',
                    'investment_potential': 'strong',
                    'description': 'Increasing cyber threats driving security spending',
                    'key_players': ['CRWD', 'ZS', 'PANW', 'HACK (ETF)']
                },
                {
                    'name': 'Electric Vehicles',
                    'confidence': 'moderate',
                    'timeframe': 'medium-term',
                    'investment_potential': 'moderate',
                    'description': 'EV adoption growing but competition intensifying',
                    'key_players': ['TSLA', 'RIVN', 'LCID', 'LIT (ETF)']
                }
            ],
            'recommendation': 'Focus on AI/ML and Renewable Energy for highest growth potential'
        }
    
    def _analyze_market_indicators(self) -> Dict[str, Any]:
        """Analyze key market indicators"""
        
        return {
            'overall_sentiment': 'cautiously-optimistic',
            'indicators': {
                'VIX': {
                    'value': 16.5,
                    'status': 'low',
                    'interpretation': 'Low volatility indicates stable market conditions'
                },
                'SP500_PE_Ratio': {
                    'value': 21.3,
                    'status': 'slightly-elevated',
                    'interpretation': 'Valuations above historical average but not extreme'
                },
                'Treasury_Yield_10Y': {
                    'value': 4.25,
                    'status': 'elevated',
                    'interpretation': 'Higher yields affecting growth stock valuations'
                },
                'Unemployment_Rate': {
                    'value': 3.8,
                    'status': 'healthy',
                    'interpretation': 'Strong labor market supporting economy'
                },
                'GDP_Growth': {
                    'value': 2.4,
                    'status': 'moderate',
                    'interpretation': 'Steady economic growth without overheating'
                }
            },
            'market_phase': 'mid-cycle',
            'risk_level': 'moderate'
        }
    
    def _get_top_stocks_by_sector(self, sector: str, risk_profile: str = 'moderate') -> Dict[str, Any]:
        """Get top performing stocks in a sector matched to risk profile"""
        
        # Mock data - would be real-time in production
        sector_stocks = {
            'technology': {
                'conservative': [
                    {'symbol': 'MSFT', 'name': 'Microsoft', 'score': 9.2, 'reason': 'Strong fundamentals, steady growth'},
                    {'symbol': 'AAPL', 'name': 'Apple', 'score': 9.0, 'reason': 'Market leader, strong cash flow'},
                    {'symbol': 'VGT', 'name': 'Vanguard Tech ETF', 'score': 8.8, 'reason': 'Diversified tech exposure'}
                ],
                'moderate': [
                    {'symbol': 'NVDA', 'name': 'NVIDIA', 'score': 9.5, 'reason': 'AI leader, strong growth'},
                    {'symbol': 'MSFT', 'name': 'Microsoft', 'score': 9.2, 'reason': 'Cloud and AI dominance'},
                    {'symbol': 'GOOGL', 'name': 'Alphabet', 'score': 8.9, 'reason': 'Search monopoly, AI innovation'}
                ],
                'aggressive': [
                    {'symbol': 'NVDA', 'name': 'NVIDIA', 'score': 9.5, 'reason': 'AI chip market leader'},
                    {'symbol': 'AMD', 'name': 'AMD', 'score': 8.7, 'reason': 'High growth, AI opportunity'},
                    {'symbol': 'PLTR', 'name': 'Palantir', 'score': 8.2, 'reason': 'AI software, government contracts'}
                ]
            },
            'healthcare': {
                'conservative': [
                    {'symbol': 'JNJ', 'name': 'Johnson & Johnson', 'score': 9.1, 'reason': 'Dividend aristocrat, diversified'},
                    {'symbol': 'UNH', 'name': 'UnitedHealth', 'score': 8.9, 'reason': 'Healthcare leader, stable growth'},
                    {'symbol': 'XLV', 'name': 'Health Care ETF', 'score': 8.7, 'reason': 'Broad healthcare exposure'}
                ],
                'moderate': [
                    {'symbol': 'ISRG', 'name': 'Intuitive Surgical', 'score': 9.0, 'reason': 'Robotic surgery leader'},
                    {'symbol': 'UNH', 'name': 'UnitedHealth', 'score': 8.9, 'reason': 'Healthcare infrastructure'},
                    {'symbol': 'LLY', 'name': 'Eli Lilly', 'score': 8.8, 'reason': 'Strong drug pipeline'}
                ],
                'aggressive': [
                    {'symbol': 'ISRG', 'name': 'Intuitive Surgical', 'score': 9.0, 'reason': 'Innovation in surgery'},
                    {'symbol': 'TDOC', 'name': 'Teladoc', 'score': 7.8, 'reason': 'Telehealth growth'},
                    {'symbol': 'GILD', 'name': 'Gilead Sciences', 'score': 7.5, 'reason': 'Biotech innovation'}
                ]
            },
            'renewable-energy': {
                'conservative': [
                    {'symbol': 'NEE', 'name': 'NextEra Energy', 'score': 8.8, 'reason': 'Utility with renewable focus'},
                    {'symbol': 'ICLN', 'name': 'Clean Energy ETF', 'score': 8.5, 'reason': 'Diversified renewable exposure'},
                    {'symbol': 'BEP', 'name': 'Brookfield Renewable', 'score': 8.3, 'reason': 'Infrastructure play'}
                ],
                'moderate': [
                    {'symbol': 'ENPH', 'name': 'Enphase Energy', 'score': 8.9, 'reason': 'Solar technology leader'},
                    {'symbol': 'NEE', 'name': 'NextEra Energy', 'score': 8.8, 'reason': 'Largest renewable producer'},
                    {'symbol': 'FSLR', 'name': 'First Solar', 'score': 8.4, 'reason': 'US solar manufacturing'}
                ],
                'aggressive': [
                    {'symbol': 'ENPH', 'name': 'Enphase Energy', 'score': 8.9, 'reason': 'Solar microinverters leader'},
                    {'symbol': 'SEDG', 'name': 'SolarEdge', 'score': 8.2, 'reason': 'Solar optimization tech'},
                    {'symbol': 'PLUG', 'name': 'Plug Power', 'score': 7.5, 'reason': 'Hydrogen fuel cells'}
                ]
            }
        }
        
        sector_key = sector.lower().replace(' ', '-')
        risk_key = risk_profile.lower()
        
        stocks = sector_stocks.get(sector_key, {}).get(risk_key, [])
        
        return {
            'sector': sector,
            'risk_profile': risk_profile,
            'stocks': stocks,
            'total_count': len(stocks)
        }
    
    def _process_response(
        self,
        raw_response: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Process market trend analysis response"""
        
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
        """Generate follow-up questions for market trend analysis"""
        
        user_profile = context.get('user_profile', {}) if context else {}
        risk_tolerance = user_profile.get('risk_tolerance', 'moderate')
        
        return [
            f"Can you recommend specific stocks in this sector for my {risk_tolerance} risk profile?",
            "What are the biggest risks I should be aware of?",
            "How should I allocate my portfolio across these opportunities?",
            "What's the best way to enter this market?",
            "Show me other emerging trends I should consider"
        ]
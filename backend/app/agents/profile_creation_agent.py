"""
Profile Creation Agent
Handles user onboarding and profile creation for new WealthWise AI users
"""

from typing import Dict, List, Any, Optional
from .base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)


class ProfileCreationAgent(BaseAgent):
    """
    Agent responsible for creating comprehensive user investment profiles
    Uses conversational AI to gather information naturally
    """
    
    def __init__(self):
        super().__init__(
            agent_name="ProfileCreationAgent",
            model_id="anthropic.claude-3-5-sonnet-20241022-v2:0"
        )
        self.profile_fields = [
            'risk_tolerance',
            'investment_goal',
            'investment_horizon',
            'annual_income',
            'investment_amount',
            'age',
            'employment_status',
            'investment_experience',
            'liquidity_needs'
        ]
    
    def _get_system_prompt(self) -> str:
        return """You are a friendly and professional Profile Creation Agent for WealthWise AI, 
an intelligent investment advisory platform. Your role is to help new users create their investment 
profile through natural, conversational interactions.

Your responsibilities:
1. Gather essential information about the user's financial situation and investment goals
2. Ask questions in a friendly, non-intimidating manner
3. Explain why each piece of information is important
4. Provide guidance on investment concepts when needed
5. Create a comprehensive user profile

Information to gather:
- Risk Tolerance (conservative, moderate, aggressive)
- Investment Goals (preservation, income, growth, aggressive growth)
- Investment Horizon (0-2 years, 3-5 years, 5-10 years, 10+ years)
- Annual Income Range
- Initial Investment Amount
- Age Range
- Employment Status
- Investment Experience Level
- Liquidity Needs

Guidelines:
- Be conversational and warm, not robotic
- Ask one or two questions at a time, don't overwhelm
- Provide brief explanations when introducing financial concepts
- Validate user inputs and provide gentle corrections if needed
- Summarize the profile before finalizing
- Never make the user feel inadequate about their financial knowledge

Response format:
- Provide your question/response naturally
- If you have all the information needed, structure it in JSON format within <profile_data> tags
- Always end with a relevant follow-up question unless the profile is complete

Example profile data format:
<profile_data>
{
  "risk_tolerance": "moderate",
  "investment_goal": "growth",
  "investment_horizon": "5-10 years",
  "annual_income": "75000-100000",
  "investment_amount": "25000",
  "age": "35",
  "employment_status": "employed",
  "investment_experience": "intermediate",
  "liquidity_needs": "low"
}
</profile_data>
"""
    
    def _register_action_groups(self) -> List[Dict[str, Any]]:
        """Register action groups for profile creation"""
        return [
            {
                'name': 'validate_risk_tolerance',
                'description': 'Validate user risk tolerance input',
                'function': self._validate_risk_tolerance
            },
            {
                'name': 'validate_investment_goal',
                'description': 'Validate investment goal',
                'function': self._validate_investment_goal
            },
            {
                'name': 'calculate_recommended_allocation',
                'description': 'Calculate recommended portfolio allocation',
                'function': self._calculate_recommended_allocation
            },
            {
                'name': 'assess_profile_completeness',
                'description': 'Check if profile has all required fields',
                'function': self._assess_profile_completeness
            }
        ]
    
    def _validate_risk_tolerance(self, risk_tolerance: str) -> Dict[str, Any]:
        """Validate risk tolerance input"""
        valid_options = ['conservative', 'moderate', 'aggressive']
        
        if risk_tolerance.lower() in valid_options:
            return {
                'valid': True,
                'value': risk_tolerance.lower(),
                'description': self._get_risk_description(risk_tolerance.lower())
            }
        
        return {
            'valid': False,
            'message': f'Please choose from: {", ".join(valid_options)}'
        }
    
    def _validate_investment_goal(self, goal: str) -> Dict[str, Any]:
        """Validate investment goal"""
        valid_goals = ['preservation', 'income', 'growth', 'aggressive-growth']
        
        if goal.lower().replace(' ', '-') in valid_goals:
            return {
                'valid': True,
                'value': goal.lower().replace(' ', '-')
            }
        
        return {
            'valid': False,
            'message': 'Please choose a valid investment goal'
        }
    
    def _calculate_recommended_allocation(
        self,
        risk_tolerance: str,
        age: int,
        investment_horizon: str
    ) -> Dict[str, Any]:
        """Calculate recommended portfolio allocation"""
        
        # Base allocation on risk tolerance
        allocations = {
            'conservative': {'stocks': 30, 'bonds': 50, 'cash': 20},
            'moderate': {'stocks': 60, 'bonds': 30, 'cash': 10},
            'aggressive': {'stocks': 80, 'bonds': 15, 'cash': 5}
        }
        
        base_allocation = allocations.get(risk_tolerance, allocations['moderate'])
        
        # Adjust based on age (rule of thumb: 100 - age = stock allocation)
        age_based_stock_allocation = max(20, 100 - age)
        
        # Average the two approaches
        adjusted_stocks = int((base_allocation['stocks'] + age_based_stock_allocation) / 2)
        adjusted_bonds = int((100 - adjusted_stocks) * 0.8)
        adjusted_cash = 100 - adjusted_stocks - adjusted_bonds
        
        return {
            'stocks': adjusted_stocks,
            'bonds': adjusted_bonds,
            'cash': adjusted_cash,
            'rationale': f'Based on {risk_tolerance} risk tolerance and age {age}'
        }
    
    def _assess_profile_completeness(
        self,
        profile_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check if profile has all required fields"""
        
        missing_fields = []
        for field in self.profile_fields:
            if field not in profile_data or not profile_data[field]:
                missing_fields.append(field)
        
        return {
            'complete': len(missing_fields) == 0,
            'missing_fields': missing_fields,
            'completion_percentage': int(
                ((len(self.profile_fields) - len(missing_fields)) / len(self.profile_fields)) * 100
            )
        }
    
    def _get_risk_description(self, risk_tolerance: str) -> str:
        """Get description for risk tolerance level"""
        descriptions = {
            'conservative': 'Focuses on capital preservation with minimal volatility. Suitable for those who prioritize stability over high returns.',
            'moderate': 'Balances growth potential with reasonable risk. Good for investors seeking steady returns with moderate market exposure.',
            'aggressive': 'Aims for maximum growth with higher volatility tolerance. Appropriate for those comfortable with significant market fluctuations.'
        }
        return descriptions.get(risk_tolerance, '')
    
    def _process_response(
        self,
        raw_response: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Process response and extract profile data if available"""
        
        # Check if profile data is present in response
        profile_data = None
        if '<profile_data>' in raw_response:
            try:
                import json
                import re
                pattern = r'<profile_data>(.*?)</profile_data>'
                match = re.search(pattern, raw_response, re.DOTALL)
                if match:
                    profile_data = json.loads(match.group(1).strip())
            except:
                pass
        
        # Remove profile_data tags from visible response
        visible_response = raw_response.replace('<profile_data>', '').replace('</profile_data>', '')
        
        return {
            "text": visible_response.strip(),
            "agent_type": self.agent_name,
            "profile_data": profile_data,
            "profile_complete": profile_data is not None
        }
    
    def _generate_follow_ups(
        self,
        response: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Generate follow-up questions for profile creation"""
        
        if response.get('profile_complete'):
            return [
                "Can you review my profile summary?",
                "I'd like to change something",
                "Let's proceed to my dashboard"
            ]
        
        # Generate contextual follow-ups based on what's been asked
        return [
            "I'm not sure about my risk tolerance",
            "Can you explain investment horizons?",
            "What's the difference between growth and income investing?"
        ]
"""
Strand Tools - Wrapping existing agents as Strand-compatible tools

These tools allow Strand agents to interact with your existing
market data and portfolio analysis infrastructure.
"""

from typing import Dict, Any, Optional
import json
# Updated to use new Strands SDK agents
from agents.market_agent import create_market_agent
from agents.portfolio_agent import create_portfolio_agent


class MarketDataTool:
    """
    Strand Tool for fetching real-time market data
    
    Wraps HybridMarketDataAgent to work with Strand SDK
    """
    
    def __init__(self):
        self.agent = create_market_agent()
        
        # Tool metadata for Strand
        self.name = "get_market_data"
        self.description = """
        Fetch real-time market data for a user's portfolio.
        
        This tool provides:
        - Current prices for all holdings (stocks, ETFs, bonds)
        - Day changes and percentages
        - Sector information
        - Beta values
        - Portfolio metrics (total value, sector breakdown, top holdings)
        - Support for both US and Indian markets
        
        Args:
            user_email: User's email address
        
        Returns:
            Dictionary with holdings, portfolioMetrics, and cashSavings
        """
    
    async def execute(self, user_email: str) -> Dict[str, Any]:
        """
        Execute the market data fetch
        
        Args:
            user_email: User's email address
            
        Returns:
            Market report with live data
        """
        print(f"🔧 [MarketDataTool] Fetching data for {user_email}")
        
        try:
            report = self.agent.generate_report(user_email)
            
            if not report['success']:
                return {
                    'success': False,
                    'error': report.get('error', 'Failed to fetch market data')
                }
            
            print(f"✅ [MarketDataTool] Retrieved {len(report['holdings'])} holdings")
            return report
            
        except Exception as e:
            print(f"❌ [MarketDataTool] Error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def to_strand_tool(self):
        """Convert to Strand SDK tool format"""
        return {
            'name': self.name,
            'description': self.description,
            'function': self.execute,
            'parameters': {
                'user_email': {
                    'type': 'string',
                    'description': 'User email address',
                    'required': True
                }
            }
        }


class PortfolioAnalysisTool:
    """
    Strand Tool for portfolio analysis and recommendations
    
    Wraps PortfolioAnalysisAgent to work with Strand SDK
    """
    
    def __init__(self):
        self.agent = create_portfolio_agent()
        
        # Tool metadata for Strand
        self.name = "analyze_portfolio"
        self.description = """
        Analyze a user's portfolio and provide robo-advisor recommendations.
        
        This tool provides:
        - Portfolio health score (0-100)
        - Model portfolio assignment (Conservative to Aggressive)
        - Allocation analysis (current vs target)
        - Drift calculation
        - Specific rebalancing recommendations with $ amounts
        - Performance vs benchmark
        - Prioritized actionable insights
        
        Args:
            user_email: User's email address
            market_data: Market data from get_market_data tool
        
        Returns:
            Complete portfolio analysis with recommendations
        """
    
    async def execute(self, user_email: str, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute portfolio analysis
        
        Args:
            user_email: User's email address
            market_data: Market data dictionary
            
        Returns:
            Portfolio analysis with recommendations
        """
        print(f"🔧 [PortfolioAnalysisTool] Analyzing portfolio for {user_email}")
        
        try:
            if not market_data.get('success'):
                return {
                    'success': False,
                    'error': 'Invalid market data provided'
                }
            
            analysis = self.agent.analyze_portfolio(user_email, market_data)
            
            if not analysis['success']:
                return {
                    'success': False,
                    'error': analysis.get('error', 'Analysis failed')
                }
            
            score = analysis['portfolioHealth']['score']
            print(f"✅ [PortfolioAnalysisTool] Health Score: {score}/100")
            return analysis
            
        except Exception as e:
            print(f"❌ [PortfolioAnalysisTool] Error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def to_strand_tool(self):
        """Convert to Strand SDK tool format"""
        return {
            'name': self.name,
            'description': self.description,
            'function': self.execute,
            'parameters': {
                'user_email': {
                    'type': 'string',
                    'description': 'User email address',
                    'required': True
                },
                'market_data': {
                    'type': 'object',
                    'description': 'Market data from get_market_data tool',
                    'required': True
                }
            }
        }


class UserProfileTool:
    """
    Strand Tool for fetching user profile information
    
    Retrieves user preferences, risk tolerance, investment goals, etc.
    """
    
    def __init__(self, dynamodb_resource):
        self.dynamodb = dynamodb_resource
        self.users_table = self.dynamodb.Table('WealthWiseUsers')
        
        self.name = "get_user_profile"
        self.description = """
        Fetch user profile information from database.
        
        Provides:
        - Age and risk tolerance
        - Investment goals and horizon
        - Monthly contribution plans
        - Account creation date
        
        Args:
            user_email: User's email address
        
        Returns:
            User profile dictionary
        """
    
    async def execute(self, user_email: str) -> Dict[str, Any]:
        """
        Fetch user profile
        
        Args:
            user_email: User's email address
            
        Returns:
            User profile data
        """
        print(f"🔧 [UserProfileTool] Fetching profile for {user_email}")
        
        try:
            response = self.users_table.get_item(Key={'userId': user_email})
            
            if 'Item' not in response:
                return {
                    'success': False,
                    'error': 'User not found'
                }
            
            user = response['Item']
            
            # Remove sensitive data
            if 'passwordHash' in user:
                del user['passwordHash']
            
            # Convert Decimal to float
            user = self._convert_decimal_to_float(user)
            
            print(f"✅ [UserProfileTool] Retrieved profile for {user.get('name', 'Unknown')}")
            
            return {
                'success': True,
                'user': user
            }
            
        except Exception as e:
            print(f"❌ [UserProfileTool] Error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _convert_decimal_to_float(self, obj):
        """Convert Decimal to float for JSON serialization"""
        from decimal import Decimal
        
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, dict):
            return {k: self._convert_decimal_to_float(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_decimal_to_float(item) for item in obj]
        return obj
    
    def to_strand_tool(self):
        """Convert to Strand SDK tool format"""
        return {
            'name': self.name,
            'description': self.description,
            'function': self.execute,
            'parameters': {
                'user_email': {
                    'type': 'string',
                    'description': 'User email address',
                    'required': True
                }
            }
        }


# Factory function to create all tools
def create_strand_tools(dynamodb_resource=None) -> Dict[str, Any]:
    """
    Create all Strand tools
    
    Args:
        dynamodb_resource: Optional DynamoDB resource for UserProfileTool
    
    Returns:
        Dictionary of tool name -> tool instance
    """
    tools = {
        'market_data': MarketDataTool(),
        'portfolio_analysis': PortfolioAnalysisTool()
    }
    
    if dynamodb_resource:
        tools['user_profile'] = UserProfileTool(dynamodb_resource)
    
    print(f"✅ Created {len(tools)} Strand tools")
    
    return tools
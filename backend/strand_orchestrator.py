# """
# Strand Orchestrator Agent - Main Conversational Robo-Advisor

# This is the brain of your robo-advisor. It:
# - Accepts natural language queries from users
# - Calls appropriate tools (market data, portfolio analysis)
# - Generates natural language explanations
# - Maintains conversation context
# - Provides personalized financial advice

# Usage:
#     orchestrator = StrandOrchestrator()
#     response = await orchestrator.chat(
#         user_id="user@example.com",
#         message="Should I rebalance my portfolio?"
#     )
# """

# import os
# from typing import Dict, Any, Optional, List
# from anthropic import Anthropic
# from datetime import datetime
# import json


# class StrandOrchestrator:
#     """
#     Main conversational agent for robo-advisor
    
#     Orchestrates all portfolio analysis tools and provides
#     natural language explanations of financial recommendations.
#     """
    
#     def __init__(self, tools: Dict[str, Any], anthropic_api_key: Optional[str] = None):
#         """
#         Initialize the orchestrator
        
#         Args:
#             tools: Dictionary of available tools (from strand_tools.py)
#             anthropic_api_key: Anthropic API key (defaults to env var)
#         """
#         self.tools = tools
#         self.anthropic_api_key = anthropic_api_key or os.getenv('ANTHROPIC_API_KEY')
        
#         if not self.anthropic_api_key:
#             raise ValueError("ANTHROPIC_API_KEY not found in environment")
        
#         self.client = Anthropic(api_key=self.anthropic_api_key)
        
#         # Conversation memory (simple in-memory for now)
#         # In production, store in Redis or DynamoDB
#         self.conversation_history: Dict[str, List[Dict]] = {}
        
#         print("✅ Strand Orchestrator initialized")
    
#     def _get_system_prompt(self) -> str:
#         """
#         Get the system prompt for Claude
        
#         This defines the robo-advisor's personality and capabilities
#         """
#         return """You are WealthWise AI, an expert robo-advisor and portfolio analyst.

# Your role is to:
# 1. Analyze user portfolios and provide data-driven insights
# 2. Explain complex financial concepts in simple, accessible language
# 3. Give specific, actionable recommendations with dollar amounts
# 4. Be encouraging but honest about portfolio health
# 5. Always consider the user's risk tolerance and investment horizon

# Available tools:
# - get_market_data: Fetch real-time market prices and portfolio values
# - analyze_portfolio: Comprehensive portfolio analysis with health score
# - get_user_profile: Retrieve user preferences and risk tolerance

# Guidelines:
# - Use tools when you need data (don't make up numbers)
# - Explain recommendations in terms of expected impact
# - Use analogies to explain complex concepts
# - Be conversational but professional
# - Focus on actionable insights, not just data
# - If health score is below 70, emphasize urgency of rebalancing
# - If health score is 80+, praise the user and suggest minor optimizations
# - Always disclose that this is educational guidance, not personalized advice

# Example tone:
# "Your portfolio health score is 67/100 (Grade D). Think of it like a car that needs maintenance - it'll still run, but you're risking bigger problems down the road. The good news? We can fix this with a few simple moves."
# """
    
#     async def chat(self, user_id: str, message: str, 
#                    force_refresh: bool = False) -> Dict[str, Any]:
#         """
#         Main chat interface
        
#         Args:
#             user_id: User's email address
#             message: User's message
#             force_refresh: If True, fetch fresh market data
            
#         Returns:
#             Dictionary with response and metadata
#         """
#         print(f"\n💬 [Orchestrator] Chat request from {user_id}")
#         print(f"📝 Message: {message}")
        
#         # Initialize conversation history if needed
#         if user_id not in self.conversation_history:
#             self.conversation_history[user_id] = []
        
#         # Add user message to history
#         self.conversation_history[user_id].append({
#             "role": "user",
#             "content": message
#         })
        
#         # Determine if we need to fetch data
#         needs_data = self._needs_market_data(message) or force_refresh
        
#         try:
#             # Execute workflow
#             if needs_data:
#                 print("🔄 Fetching market data...")
#                 response = await self._execute_full_analysis(user_id, message)
#             else:
#                 print("💭 Generating conversational response...")
#                 response = await self._generate_response(user_id, message)
            
#             # Add assistant response to history
#             self.conversation_history[user_id].append({
#                 "role": "assistant",
#                 "content": response['response']
#             })
            
#             return response
            
#         except Exception as e:
#             print(f"❌ Error in chat: {e}")
#             return {
#                 'success': False,
#                 'error': str(e),
#                 'response': "I apologize, but I encountered an error processing your request. Please try again."
#             }
    
#     def _needs_market_data(self, message: str) -> bool:
#         """
#         Determine if message requires fetching market data
        
#         Args:
#             message: User's message
            
#         Returns:
#             True if market data is needed
#         """
#         triggers = [
#             'rebalance', 'portfolio', 'holdings', 'value', 'worth',
#             'analysis', 'health', 'score', 'allocation', 'drift',
#             'recommend', 'should i', 'what should', 'performance',
#             'how is my', "how's my", 'current', 'price'
#         ]
        
#         message_lower = message.lower()
#         return any(trigger in message_lower for trigger in triggers)
    
#     async def _execute_full_analysis(self, user_id: str, message: str) -> Dict[str, Any]:
#         """
#         Execute full portfolio analysis workflow
        
#         This calls:
#         1. get_user_profile
#         2. get_market_data
#         3. analyze_portfolio
#         4. Generate natural language explanation
        
#         Args:
#             user_id: User's email
#             message: User's message
            
#         Returns:
#             Complete response with data and explanation
#         """
#         print("🔄 [Full Analysis] Starting...")
        
#         # Step 1: Get user profile
#         user_profile_tool = self.tools.get('user_profile')
#         user_profile = await user_profile_tool.execute(user_id) if user_profile_tool else None
        
#         # Step 2: Get market data
#         market_tool = self.tools['market_data']
#         market_data = await market_tool.execute(user_id)
        
#         if not market_data.get('success'):
#             return {
#                 'success': False,
#                 'error': 'Failed to fetch market data',
#                 'response': "I couldn't fetch your current portfolio data. Please try again in a moment."
#             }
        
#         # Step 3: Analyze portfolio
#         analysis_tool = self.tools['portfolio_analysis']
#         analysis = await analysis_tool.execute(user_id, market_data)
        
#         if not analysis.get('success'):
#             return {
#                 'success': False,
#                 'error': 'Portfolio analysis failed',
#                 'response': "I had trouble analyzing your portfolio. Please try again."
#             }
        
#         # Step 4: Generate natural language explanation
#         explanation = await self._generate_explanation(
#             user_id=user_id,
#             message=message,
#             market_data=market_data,
#             analysis=analysis,
#             user_profile=user_profile
#         )
        
#         return {
#             'success': True,
#             'response': explanation,
#             'data': {
#                 'marketData': market_data,
#                 'analysis': analysis,
#                 'userProfile': user_profile
#             },
#             'timestamp': datetime.utcnow().isoformat()
#         }
    
#     async def _generate_explanation(self, user_id: str, message: str,
#                                     market_data: Dict, analysis: Dict,
#                                     user_profile: Optional[Dict]) -> str:
#         """
#         Generate natural language explanation using Claude
        
#         Args:
#             user_id: User's email
#             message: Original user message
#             market_data: Market data results
#             analysis: Portfolio analysis results
#             user_profile: User profile data
            
#         Returns:
#             Natural language explanation
#         """
#         print("🧠 Generating explanation with Claude...")
        
#         # Build context for Claude
#         context = self._build_context(market_data, analysis, user_profile)
        
#         # Get conversation history (last 5 messages for context)
#         history = self.conversation_history.get(user_id, [])[-5:]
        
#         # Create messages for Claude
#         messages = history + [{
#             "role": "user",
#             "content": f"""User question: {message}

# Here's the current portfolio data and analysis:

# {context}

# Please provide a helpful, conversational response that:
# 1. Directly answers their question
# 2. Highlights key insights from the data
# 3. Explains any concerning issues in simple terms
# 4. Gives specific, actionable recommendations
# 5. Is encouraging but honest

# Remember: Use analogies, be conversational, and focus on what they should DO, not just what the numbers say."""
#         }]
        
#         # Call Claude
#         response = self.client.messages.create(
#             model="claude-sonnet-4-20250514",
#             max_tokens=2000,
#             system=self._get_system_prompt(),
#             messages=messages
#         )
        
#         explanation = response.content[0].text
        
#         print(f"✅ Generated {len(explanation)} character explanation")
        
#         return explanation
    
#     async def _generate_response(self, user_id: str, message: str) -> Dict[str, Any]:
#         """
#         Generate response without fetching new data
        
#         For follow-up questions or general queries
        
#         Args:
#             user_id: User's email
#             message: User's message
            
#         Returns:
#             Response dictionary
#         """
#         print("💭 Generating conversational response...")
        
#         # Get conversation history
#         history = self.conversation_history.get(user_id, [])[-5:]
        
#         messages = history + [{
#             "role": "user",
#             "content": message
#         }]
        
#         # Call Claude
#         response = self.client.messages.create(
#             model="claude-sonnet-4-20250514",
#             max_tokens=1500,
#             system=self._get_system_prompt(),
#             messages=messages
#         )
        
#         text = response.content[0].text
        
#         return {
#             'success': True,
#             'response': text,
#             'timestamp': datetime.utcnow().isoformat()
#         }
    
#     def _build_context(self, market_data: Dict, analysis: Dict, 
#                       user_profile: Optional[Dict]) -> str:
#         """
#         Build context string for Claude
        
#         Args:
#             market_data: Market data
#             analysis: Portfolio analysis
#             user_profile: User profile
            
#         Returns:
#             Formatted context string
#         """
#         context_parts = []
        
#         # Portfolio summary
#         total_value = market_data['portfolioMetrics']['totalValue']
#         num_holdings = len(market_data['holdings'])
        
#         context_parts.append(f"PORTFOLIO SUMMARY:")
#         context_parts.append(f"- Total Value: ${total_value:,.2f}")
#         context_parts.append(f"- Number of Holdings: {num_holdings}")
#         context_parts.append(f"- Cash Savings: ${market_data.get('cashSavings', 0):,.2f}")
        
#         # Health score
#         health = analysis['portfolioHealth']
#         context_parts.append(f"\nHEALTH SCORE: {health['score']}/100 (Grade {health['grade']}, Status: {health['status']})")
        
#         # Breakdown
#         context_parts.append("\nScore Breakdown:")
#         for item in health['breakdown']:
#             context_parts.append(f"  - {item['factor']}: {item['penalty']} pts ({item['reason']})")
        
#         # Model portfolio
#         model = analysis['modelPortfolio']
#         context_parts.append(f"\nMODEL PORTFOLIO: {model['name']}")
#         context_parts.append(f"Description: {model['description']}")
        
#         # Allocation
#         alloc = analysis['allocationAnalysis']
#         current = alloc['current']
#         target = alloc['target']
        
#         context_parts.append(f"\nALLOCATION:")
#         context_parts.append(f"- Current: {current['stocks']}% stocks, {current['bonds']}% bonds, {current['cash']}% cash")
#         context_parts.append(f"- Target:  {target['stocks']}% stocks, {target['bonds']}% bonds, {target['cash']}% cash")
#         context_parts.append(f"- Drift: {alloc['drift']}%")
        
#         if alloc['issues']:
#             context_parts.append(f"- Issues: {', '.join(alloc['issues'])}")
        
#         # Top recommendations
#         recs = analysis['recommendations']
#         if recs:
#             context_parts.append(f"\nTOP RECOMMENDATIONS ({len(recs)} total):")
#             for i, rec in enumerate(recs[:3], 1):
#                 context_parts.append(f"{i}. [{rec['priority']}] {rec['title']}")
#                 context_parts.append(f"   Action: {rec['action']}")
#                 context_parts.append(f"   Impact: {rec['impact']}")
        
#         # Rebalancing plan
#         plan = analysis['rebalancingPlan']
#         if plan['cashDeployment']:
#             context_parts.append(f"\nREBALANCING PLAN:")
#             context_parts.append(f"Summary: {plan['summary']}")
#             for action in plan['cashDeployment']:
#                 context_parts.append(f"  - {action['action']} ${action['amount']:,.2f} of {action['symbol']} ({action['name']})")
#                 context_parts.append(f"    Reason: {action['reason']}")
        
#         # User profile
#         if user_profile and user_profile.get('success'):
#             user = user_profile['user']
#             context_parts.append(f"\nUSER PROFILE:")
#             context_parts.append(f"- Age: {user.get('age', 'Unknown')}")
#             context_parts.append(f"- Risk Tolerance: {user.get('riskTolerance', 'Unknown')}")
#             context_parts.append(f"- Investment Goal: {user.get('investmentGoal', 'Unknown')}")
#             context_parts.append(f"- Investment Horizon: {user.get('investmentHorizon', 'Unknown')}")
        
#         return "\n".join(context_parts)
    
#     def clear_history(self, user_id: str):
#         """Clear conversation history for a user"""
#         if user_id in self.conversation_history:
#             del self.conversation_history[user_id]
#             print(f"🗑️  Cleared conversation history for {user_id}")
    
#     def get_conversation_summary(self, user_id: str) -> Dict[str, Any]:
#         """Get summary of conversation history"""
#         history = self.conversation_history.get(user_id, [])
        
#         return {
#             'user_id': user_id,
#             'message_count': len(history),
#             'last_message': history[-1] if history else None,
#             'conversation_started': datetime.utcnow().isoformat()
#         }


# # ==================== USAGE EXAMPLE ====================

# async def example_usage():
#     """Example of how to use the orchestrator"""
    
#     print("\n" + "=" * 60)
#     print("🧪 Testing Strand Orchestrator")
#     print("=" * 60 + "\n")
    
#     # This would be imported from strand_tools.py in real usage
#     from strand_tools import create_strand_tools
    
#     # Create tools (you'd pass DynamoDB resource here)
#     tools = create_strand_tools()
    
#     # Create orchestrator
#     orchestrator = StrandOrchestrator(tools)
    
#     # Example conversations
#     test_messages = [
#         "What's my portfolio health score?",
#         "Should I rebalance my portfolio?",
#         "Why is my score low?",
#         "What specific ETFs should I buy?"
#     ]
    
#     test_user = "test@example.com"
    
#     for message in test_messages:
#         print(f"\n💬 User: {message}")
#         response = await orchestrator.chat(test_user, message)
        
#         if response['success']:
#             print(f"🤖 Assistant: {response['response'][:200]}...")
#         else:
#             print(f"❌ Error: {response['error']}")
        
#         print("\n" + "-" * 60)


# if __name__ == "__main__":
#     import asyncio
#     asyncio.run(example_usage())

"""
Strand Orchestrator Agent - AWS Bedrock Version

Modified to use AWS Bedrock instead of Anthropic API
"""

import os
from typing import Dict, Any, Optional, List
from anthropic import AnthropicBedrock
from datetime import datetime
import json


class StrandOrchestrator:
    """
    Main conversational agent for robo-advisor
    Uses AWS Bedrock for Claude access
    """
    
    def __init__(self, tools: Dict[str, Any]):
        """
        Initialize the orchestrator with AWS Bedrock
        
        Args:
            tools: Dictionary of available tools (from strand_tools.py)
        """
        self.tools = tools
        
        # Initialize AWS Bedrock client
        try:
            self.client = AnthropicBedrock(
                aws_region=os.getenv('AWS_REGION', 'us-east-1'),
                aws_access_key=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                aws_session_token=os.getenv('AWS_SESSION_TOKEN')
            )
            print("✅ Strand Orchestrator initialized with AWS Bedrock")
        except Exception as e:
            print(f"❌ Failed to initialize Bedrock: {e}")
            raise
        
        # Conversation memory
        self.conversation_history: Dict[str, List[Dict]] = {}
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for Claude"""
        return """You are WealthWise AI, an expert robo-advisor and portfolio analyst.

Your role is to:
1. Analyze user portfolios and provide data-driven insights
2. Explain complex financial concepts in simple, accessible language
3. Give specific, actionable recommendations with dollar amounts
4. Be encouraging but honest about portfolio health
5. Always consider the user's risk tolerance and investment horizon

Available tools:
- get_market_data: Fetch real-time market prices and portfolio values
- analyze_portfolio: Comprehensive portfolio analysis with health score
- get_user_profile: Retrieve user preferences and risk tolerance

Guidelines:
- Use tools when you need data (don't make up numbers)
- Explain recommendations in terms of expected impact
- Use analogies to explain complex concepts
- Be conversational but professional
- Focus on actionable insights, not just data
- If health score is below 70, emphasize urgency of rebalancing
- If health score is 80+, praise the user and suggest minor optimizations
- Always disclose that this is educational guidance, not personalized advice

Example tone:
"Your portfolio health score is 67/100 (Grade D). Think of it like a car that needs maintenance - it'll still run, but you're risking bigger problems down the road. The good news? We can fix this with a few simple moves."
"""
    
    async def chat(self, user_id: str, message: str, 
                   force_refresh: bool = False) -> Dict[str, Any]:
        """
        Main chat interface
        
        Args:
            user_id: User's email address
            message: User's message
            force_refresh: If True, fetch fresh market data
            
        Returns:
            Dictionary with response and metadata
        """
        print(f"\n💬 [Orchestrator] Chat request from {user_id}")
        print(f"📝 Message: {message}")
        
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        self.conversation_history[user_id].append({
            "role": "user",
            "content": message
        })
        
        needs_data = self._needs_market_data(message) or force_refresh
        
        try:
            if needs_data:
                print("🔄 Fetching market data...")
                response = await self._execute_full_analysis(user_id, message)
            else:
                print("💭 Generating conversational response...")
                response = await self._generate_response(user_id, message)
            
            self.conversation_history[user_id].append({
                "role": "assistant",
                "content": response['response']
            })
            
            return response
            
        except Exception as e:
            print(f"❌ Error in chat: {e}")
            return {
                'success': False,
                'error': str(e),
                'response': "I apologize, but I encountered an error processing your request. Please try again."
            }
    
    def _needs_market_data(self, message: str) -> bool:
        """Determine if message requires fetching market data"""
        triggers = [
            'rebalance', 'portfolio', 'holdings', 'value', 'worth',
            'analysis', 'health', 'score', 'allocation', 'drift',
            'recommend', 'should i', 'what should', 'performance',
            'how is my', "how's my", 'current', 'price'
        ]
        
        message_lower = message.lower()
        return any(trigger in message_lower for trigger in triggers)
    
    async def _execute_full_analysis(self, user_id: str, message: str) -> Dict[str, Any]:
        """Execute full portfolio analysis workflow"""
        print("🔄 [Full Analysis] Starting...")
        
        # Get user profile
        user_profile_tool = self.tools.get('user_profile')
        user_profile = await user_profile_tool.execute(user_id) if user_profile_tool else None
        
        # Get market data
        market_tool = self.tools['market_data']
        market_data = await market_tool.execute(user_id)
        
        if not market_data.get('success'):
            return {
                'success': False,
                'error': 'Failed to fetch market data',
                'response': "I couldn't fetch your current portfolio data. Please try again in a moment."
            }
        
        # Analyze portfolio
        analysis_tool = self.tools['portfolio_analysis']
        analysis = await analysis_tool.execute(user_id, market_data)
        
        if not analysis.get('success'):
            return {
                'success': False,
                'error': 'Portfolio analysis failed',
                'response': "I had trouble analyzing your portfolio. Please try again."
            }
        
        # Generate explanation
        explanation = await self._generate_explanation(
            user_id=user_id,
            message=message,
            market_data=market_data,
            analysis=analysis,
            user_profile=user_profile
        )
        
        return {
            'success': True,
            'response': explanation,
            'data': {
                'marketData': market_data,
                'analysis': analysis,
                'userProfile': user_profile
            },
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def _generate_explanation(self, user_id: str, message: str,
                                    market_data: Dict, analysis: Dict,
                                    user_profile: Optional[Dict]) -> str:
        """Generate natural language explanation using Claude via Bedrock"""
        print("🧠 Generating explanation with Claude (Bedrock)...")
        
        context = self._build_context(market_data, analysis, user_profile)
        history = self.conversation_history.get(user_id, [])[-5:]
        
        messages = history + [{
            "role": "user",
            "content": f"""User question: {message}

Here's the current portfolio data and analysis:

{context}

Please provide a helpful, conversational response that:
1. Directly answers their question
2. Highlights key insights from the data
3. Explains any concerning issues in simple terms
4. Gives specific, actionable recommendations
5. Is encouraging but honest

Remember: Use analogies, be conversational, and focus on what they should DO, not just what the numbers say."""
        }]
        
        # Call Claude via Bedrock
        response = self.client.messages.create(
            model="anthropic.claude-sonnet-4-20250514-v1:0",  # Bedrock model ID
            max_tokens=2000,
            system=self._get_system_prompt(),
            messages=messages
        )
        
        explanation = response.content[0].text
        print(f"✅ Generated {len(explanation)} character explanation")
        
        return explanation
    
    async def _generate_response(self, user_id: str, message: str) -> Dict[str, Any]:
        """Generate response without fetching new data"""
        print("💭 Generating conversational response...")
        
        history = self.conversation_history.get(user_id, [])[-5:]
        messages = history + [{"role": "user", "content": message}]
        
        response = self.client.messages.create(
            model="anthropic.claude-sonnet-4-20250514-v1:0",
            max_tokens=1500,
            system=self._get_system_prompt(),
            messages=messages
        )
        
        text = response.content[0].text
        
        return {
            'success': True,
            'response': text,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _build_context(self, market_data: Dict, analysis: Dict, 
                      user_profile: Optional[Dict]) -> str:
        """Build context string for Claude"""
        context_parts = []
        
        total_value = market_data['portfolioMetrics']['totalValue']
        num_holdings = len(market_data['holdings'])
        
        context_parts.append(f"PORTFOLIO SUMMARY:")
        context_parts.append(f"- Total Value: ${total_value:,.2f}")
        context_parts.append(f"- Number of Holdings: {num_holdings}")
        context_parts.append(f"- Cash Savings: ${market_data.get('cashSavings', 0):,.2f}")
        
        health = analysis['portfolioHealth']
        context_parts.append(f"\nHEALTH SCORE: {health['score']}/100 (Grade {health['grade']}, Status: {health['status']})")
        
        context_parts.append("\nScore Breakdown:")
        for item in health['breakdown']:
            context_parts.append(f"  - {item['factor']}: {item['penalty']} pts ({item['reason']})")
        
        model = analysis['modelPortfolio']
        context_parts.append(f"\nMODEL PORTFOLIO: {model['name']}")
        
        alloc = analysis['allocationAnalysis']
        current = alloc['current']
        target = alloc['target']
        
        context_parts.append(f"\nALLOCATION:")
        context_parts.append(f"- Current: {current['stocks']}% stocks, {current['bonds']}% bonds, {current['cash']}% cash")
        context_parts.append(f"- Target:  {target['stocks']}% stocks, {target['bonds']}% bonds, {target['cash']}% cash")
        context_parts.append(f"- Drift: {alloc['drift']}%")
        
        if user_profile and user_profile.get('success'):
            user = user_profile['user']
            context_parts.append(f"\nUSER PROFILE:")
            context_parts.append(f"- Age: {user.get('age', 'Unknown')}")
            context_parts.append(f"- Risk Tolerance: {user.get('riskTolerance', 'Unknown')}")
        
        return "\n".join(context_parts)
    
    def clear_history(self, user_id: str):
        """Clear conversation history for a user"""
        if user_id in self.conversation_history:
            del self.conversation_history[user_id]
            print(f"🗑️ Cleared conversation history for {user_id}")
    
    def get_conversation_summary(self, user_id: str) -> Dict[str, Any]:
        """Get summary of conversation history"""
        history = self.conversation_history.get(user_id, [])
        
        return {
            'user_id': user_id,
            'message_count': len(history),
            'last_message': history[-1] if history else None,
            'conversation_started': datetime.utcnow().isoformat()
        }
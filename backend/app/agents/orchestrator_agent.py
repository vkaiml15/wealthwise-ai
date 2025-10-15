"""
Orchestrator Agent
Master agent that routes queries to appropriate specialized agents
"""

from typing import Dict, List, Any, Optional
from .base_agent import BaseAgent
from .profile_creation_agent import ProfileCreationAgent
from .market_trend_agent import MarketTrendAgent
from .rebalancing_agent import RebalancingAgent
from .recommendation_agent import RecommendationAgent
import logging
import re

logger = logging.getLogger(__name__)


class OrchestratorAgent(BaseAgent):
    """
    Master orchestrator that:
    1. Classifies user intent
    2. Routes to appropriate specialized agent(s)
    3. Coordinates multi-agent workflows
    4. Synthesizes responses from multiple agents
    """
    
    def __init__(self):
        super().__init__(
            agent_name="OrchestratorAgent",
            model_id="anthropic.claude-3-5-sonnet-20241022-v2:0"
        )
        
        # Initialize specialized agents
        self.profile_agent = ProfileCreationAgent()
        self.market_agent = MarketTrendAgent()
        self.rebalancing_agent = RebalancingAgent()
        self.recommendation_agent = RecommendationAgent()
        
        self.agent_map = {
            'profile_creation': self.profile_agent,
            'market_trends': self.market_agent,
            'rebalancing': self.rebalancing_agent,
            'recommendations': self.recommendation_agent
        }
    
    def _get_system_prompt(self) -> str:
        return """You are the Orchestrator Agent for WealthWise AI, responsible for understanding 
user intent and coordinating specialized agents to provide comprehensive investment advisory services.

Your responsibilities:
1. **Intent Classification**: Determine what the user is asking for
2. **Agent Routing**: Select the appropriate specialized agent(s)
3. **Context Management**: Maintain conversation context
4. **Response Coordination**: Combine outputs from multiple agents
5. **Follow-up Generation**: Create engaging follow-up questions

Available Specialized Agents:
- **ProfileCreationAgent**: User onboarding and profile creation
- **MarketTrendAgent**: Market analysis, sector trends, industry insights
- **RebalancingAgent**: Portfolio rebalancing analysis and recommendations
- **RecommendationAgent**: Personalized investment recommendations

Intent Categories:
1. **Portfolio Analysis**: General portfolio review, performance, composition
2. **Market Research**: Industry trends, sector performance, emerging opportunities
3. **Rebalancing**: Portfolio drift analysis, rebalancing strategies
4. **Recommendations**: Specific investment suggestions, stock picks
5. **Profile Management**: Update preferences, risk tolerance, goals
6. **General Inquiry**: Questions about investing, terminology, strategies

Routing Rules:
- Profile/onboarding questions → ProfileCreationAgent
- "What's trending", "Industry analysis", "Sector performance" → MarketTrendAgent
- "Rebalance", "allocation drift", "portfolio adjustment" → RebalancingAgent
- "Recommend stocks", "what should I buy", "investment ideas" → RecommendationAgent
- Complex queries may require MULTIPLE agents in sequence

For complex queries requiring multiple agents:
1. Break down the query into sub-tasks
2. Route each sub-task to appropriate agent
3. Synthesize results into coherent response
4. Ensure logical flow and connections

Response Format:
- Provide direct, conversational answers
- Don't mention agent names to the user
- Synthesize information naturally
- Always end with a relevant follow-up question

Guidelines:
- Be conversational and helpful
- Understand implicit intent (e.g., "portfolio" likely means their own portfolio)
- Maintain context from previous messages
- Provide comprehensive answers that anticipate follow-up questions
- Generate engaging, contextual follow-ups
"""
    
    def _register_action_groups(self) -> List[Dict[str, Any]]:
        """Register action groups for orchestration"""
        return [
            {
                'name': 'classify_intent',
                'description': 'Classify user query intent',
                'function': self._classify_intent
            },
            {
                'name': 'route_to_agent',
                'description': 'Route query to appropriate agent',
                'function': self._route_to_agent
            },
            {
                'name': 'coordinate_multi_agent',
                'description': 'Coordinate multiple agents for complex queries',
                'function': self._coordinate_multi_agent
            },
            {
                'name': 'synthesize_responses',
                'description': 'Combine responses from multiple agents',
                'function': self._synthesize_responses
            }
        ]
    
    def _classify_intent(self, user_query: str) -> Dict[str, Any]:
        """Classify user query intent to determine routing"""
        
        query_lower = user_query.lower()
        
        # Intent patterns
        intents = {
            'profile_creation': [
                'create profile', 'onboarding', 'risk tolerance', 'investment goal',
                'getting started', 'new user', 'set up', 'profile'
            ],
            'market_trends': [
                'market', 'trend', 'industry', 'sector', 'emerging', 'booming',
                'performance', 'opportunities', 'what\'s hot', 'growth areas',
                'ai industry', 'tech sector', 'healthcare trends'
            ],
            'rebalancing': [
                'rebalance', 'allocation', 'drift', 'adjust portfolio',
                'reallocate', 'portfolio balance', 'too much', 'overweight'
            ],
            'recommendations': [
                'recommend', 'should i buy', 'what stocks', 'suggest',
                'investment ideas', 'where to invest', 'good stocks',
                'personalized', 'for my portfolio'
            ],
            'portfolio_analysis': [
                'analyze portfolio', 'portfolio review', 'how is my portfolio',
                'portfolio performance', 'comprehensive analysis', 'evaluate'
            ],
            'general_inquiry': [
                'what is', 'how does', 'explain', 'tell me about', 'help'
            ]
        }
        
        # Score each intent
        intent_scores = {}
        for intent, keywords in intents.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            if score > 0:
                intent_scores[intent] = score
        
        # Determine primary and secondary intents
        if not intent_scores:
            primary_intent = 'general_inquiry'
            confidence = 0.5
        else:
            sorted_intents = sorted(intent_scores.items(), key=lambda x: x[1], reverse=True)
            primary_intent = sorted_intents[0][0]
            confidence = min(sorted_intents[0][1] / 3, 1.0)  # Normalize confidence
        
        # Determine if multi-agent coordination needed
        requires_multi_agent = len(intent_scores) > 1 and confidence < 0.8
        
        return {
            'primary_intent': primary_intent,
            'confidence': round(confidence, 2),
            'all_intents': intent_scores,
            'requires_multi_agent': requires_multi_agent,
            'query_complexity': 'complex' if requires_multi_agent else 'simple'
        }
    
    def _route_to_agent(
        self,
        intent: str,
        user_query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Route query to appropriate specialized agent"""
        
        agent_routing = {
            'profile_creation': 'profile_creation',
            'market_trends': 'market_trends',
            'rebalancing': 'rebalancing',
            'recommendations': 'recommendations',
            'portfolio_analysis': 'recommendations',  # Can analyze and recommend
            'general_inquiry': None  # Handle directly
        }
        
        target_agent = agent_routing.get(intent)
        
        if not target_agent:
            # Handle general inquiries directly
            return {
                'agent': 'orchestrator',
                'response': self._handle_general_inquiry(user_query),
                'follow_ups': self._generate_general_follow_ups(user_query)
            }
        
        # Invoke specialized agent
        agent = self.agent_map[target_agent]
        response = agent.invoke(user_query, context)
        
        return response
    
    def _coordinate_multi_agent(
        self,
        user_query: str,
        intents: Dict[str, int],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Coordinate multiple agents for complex queries"""
        
        logger.info(f"Coordinating multi-agent workflow for query: {user_query}")
        
        # Example: "Analyze my portfolio and recommend stocks in the AI industry"
        # This requires: portfolio_analysis + market_trends + recommendations
        
        agent_responses = []
        
        # Sort intents by score to determine execution order
        sorted_intents = sorted(intents.items(), key=lambda x: x[1], reverse=True)
        
        for intent, score in sorted_intents:
            if score > 0:
                agent_key = self._map_intent_to_agent(intent)
                if agent_key and agent_key in self.agent_map:
                    agent = self.agent_map[agent_key]
                    
                    # Enrich context with previous agent responses
                    enriched_context = context.copy() if context else {}
                    if agent_responses:
                        enriched_context['previous_agent_outputs'] = agent_responses
                    
                    response = agent.invoke(user_query, enriched_context)
                    agent_responses.append({
                        'agent': agent_key,
                        'intent': intent,
                        'response': response
                    })
        
        # Synthesize all responses
        synthesized = self._synthesize_responses(agent_responses, user_query)
        
        return synthesized
    
    def _map_intent_to_agent(self, intent: str) -> Optional[str]:
        """Map intent category to agent key"""
        mapping = {
            'profile_creation': 'profile_creation',
            'market_trends': 'market_trends',
            'rebalancing': 'rebalancing',
            'recommendations': 'recommendations',
            'portfolio_analysis': 'recommendations'
        }
        return mapping.get(intent)
    
    def _synthesize_responses(
        self,
        agent_responses: List[Dict[str, Any]],
        original_query: str
    ) -> Dict[str, Any]:
        """Combine responses from multiple agents into coherent response"""
        
        if not agent_responses:
            return {
                'response': {
                    'text': "I apologize, but I couldn't process your request. Could you please rephrase?"
                },
                'follow_ups': ["What would you like to know about your portfolio?"]
            }
        
        if len(agent_responses) == 1:
            # Single agent, return as-is
            return agent_responses[0]['response']
        
        # Multiple agents - synthesize
        synthesis_parts = []
        all_follow_ups = []
        
        for idx, agent_data in enumerate(agent_responses):
            response = agent_data['response']
            agent_name = agent_data['agent']
            
            # Add section for each agent's contribution
            if 'response' in response and 'text' in response['response']:
                text = response['response']['text']
            elif 'text' in response:
                text = response['text']
            else:
                continue
            
            synthesis_parts.append(text)
            
            # Collect follow-ups
            if 'follow_ups' in response:
                all_follow_ups.extend(response['follow_ups'])
        
        # Combine into coherent response
        synthesized_text = "\n\n".join(synthesis_parts)
        
        # Deduplicate follow-ups
        unique_follow_ups = list(dict.fromkeys(all_follow_ups))[:5]
        
        return {
            'agent': 'orchestrator',
            'response': {
                'text': synthesized_text,
                'agent_type': 'multi_agent_synthesis',
                'agents_involved': [a['agent'] for a in agent_responses]
            },
            'follow_ups': unique_follow_ups,
            'timestamp': agent_responses[-1]['response'].get('timestamp')
        }
    
    def _handle_general_inquiry(self, query: str) -> Dict[str, Any]:
        """Handle general inquiries directly without specialized agents"""
        
        # Use base Bedrock model for general questions
        prompt = f"""You are a helpful investment advisor assistant. Answer this general question 
about investing or finance in a clear, educational manner:

Question: {query}

Provide a concise, informative answer suitable for someone learning about investing."""
        
        response_text = self._invoke_bedrock_model(prompt)
        
        return {
            'text': response_text,
            'agent_type': 'general_inquiry'
        }
    
    def _generate_general_follow_ups(self, query: str) -> List[str]:
        """Generate follow-up questions for general inquiries"""
        return [
            "Can you explain this in more detail?",
            "How does this apply to my portfolio?",
            "What should I do with this information?",
            "Are there any risks I should know about?"
        ]
    
    def invoke(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Override invoke to add orchestration logic
        """
        try:
            logger.info(f"Orchestrator received query: {user_input}")
            
            # Classify intent
            intent_analysis = self._classify_intent(user_input)
            logger.info(f"Intent analysis: {intent_analysis}")
            
            # Route based on complexity
            if intent_analysis['query_complexity'] == 'simple':
                # Single agent routing
                response = self._route_to_agent(
                    intent_analysis['primary_intent'],
                    user_input,
                    context
                )
            else:
                # Multi-agent coordination
                response = self._coordinate_multi_agent(
                    user_input,
                    intent_analysis['all_intents'],
                    context
                )
            
            logger.info(f"Orchestrator completed routing and synthesis")
            
            return response
            
        except Exception as e:
            logger.error(f"Error in orchestrator: {str(e)}")
            return {
                "agent": "orchestrator",
                "error": str(e),
                "response": {
                    "text": "I apologize, but I encountered an error processing your request. Please try rephrasing your question."
                },
                "follow_ups": ["What would you like to know about your investments?"]
            }
    
    def _process_response(
        self,
        raw_response: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Process orchestrator response"""
        return {
            "text": raw_response,
            "agent_type": "orchestrator"
        }
    
    def _generate_follow_ups(
        self,
        response: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Generate contextual follow-up questions"""
        return [
            "Can you analyze my portfolio?",
            "What market trends should I know about?",
            "Do I need to rebalance?",
            "What stocks do you recommend for me?"
        ]
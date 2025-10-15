"""
WealthWise AI Agents Package
Multi-agent system for investment advisory using AWS Bedrock AgentCore
"""

from .base_agent import BaseAgent
from .profile_creation_agent import ProfileCreationAgent
from .market_trend_agent import MarketTrendAgent
from .risk_profile_agent import RiskProfileAgent
from .rebalancing_agent import RebalancingAgent
from .recommendation_agent import RecommendationAgent
from .orchestrator_agent import OrchestratorAgent

__all__ = [
    'BaseAgent',
    'ProfileCreationAgent',
    'MarketTrendAgent',
    'RiskProfileAgent',
    'RebalancingAgent',
    'RecommendationAgent',
    'OrchestratorAgent'
]
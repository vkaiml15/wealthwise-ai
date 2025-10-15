"""
Base Agent Class for WealthWise AI
Provides common functionality for all Bedrock AgentCore implementations
"""

import json
import boto3
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Abstract base class for all WealthWise AI agents
    Implements common Bedrock AgentCore functionality
    """
    
    def __init__(
        self,
        agent_name: str,
        model_id: str = "anthropic.claude-3-5-sonnet-20241022-v2:0",
        region_name: str = "us-east-1"
    ):
        """
        Initialize base agent with AWS Bedrock
        
        Args:
            agent_name: Name of the agent
            model_id: Bedrock model identifier
            region_name: AWS region
        """
        self.agent_name = agent_name
        self.model_id = model_id
        self.region_name = region_name
        
        # Initialize AWS clients
        self.bedrock_runtime = boto3.client(
            'bedrock-runtime',
            region_name=region_name
        )
        
        self.bedrock_agent_runtime = boto3.client(
            'bedrock-agent-runtime',
            region_name=region_name
        )
        
        # Agent configuration
        self.system_prompt = self._get_system_prompt()
        self.action_groups = self._register_action_groups()
        
        logger.info(f"Initialized {agent_name} with model {model_id}")
    
    @abstractmethod
    def _get_system_prompt(self) -> str:
        """
        Define the system prompt for this agent
        Must be implemented by each agent
        """
        pass
    
    @abstractmethod
    def _register_action_groups(self) -> List[Dict[str, Any]]:
        """
        Register action groups (tools) for this agent
        Must be implemented by each agent
        """
        pass
    
    def invoke(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Invoke the agent with user input
        
        Args:
            user_input: User's query or input
            context: Additional context (user profile, portfolio, etc.)
            conversation_history: Previous messages in conversation
            
        Returns:
            Agent response with generated text and metadata
        """
        try:
            # Prepare the full prompt with context
            full_prompt = self._prepare_prompt(user_input, context, conversation_history)
            
            # Invoke Bedrock model
            response = self._invoke_bedrock_model(full_prompt)
            
            # Process and structure the response
            structured_response = self._process_response(response, context)
            
            # Generate follow-up questions if applicable
            follow_ups = self._generate_follow_ups(structured_response, context)
            
            return {
                "agent": self.agent_name,
                "response": structured_response,
                "follow_ups": follow_ups,
                "timestamp": datetime.utcnow().isoformat(),
                "context_used": context is not None
            }
            
        except Exception as e:
            logger.error(f"Error in {self.agent_name}: {str(e)}")
            return {
                "agent": self.agent_name,
                "error": str(e),
                "response": "I apologize, but I encountered an error processing your request. Please try again.",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _prepare_prompt(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]],
        conversation_history: Optional[List[Dict[str, str]]]
    ) -> str:
        """
        Prepare the complete prompt with system instructions and context
        """
        prompt_parts = [self.system_prompt]
        
        # Add context if available
        if context:
            prompt_parts.append("\n<context>")
            prompt_parts.append(json.dumps(context, indent=2))
            prompt_parts.append("</context>\n")
        
        # Add conversation history if available
        if conversation_history:
            prompt_parts.append("\n<conversation_history>")
            for msg in conversation_history[-5:]:  # Last 5 messages
                role = msg.get("role", "user")
                content = msg.get("content", "")
                prompt_parts.append(f"{role}: {content}")
            prompt_parts.append("</conversation_history>\n")
        
        # Add current user input
        prompt_parts.append(f"\nUser: {user_input}\n\nAssistant:")
        
        return "\n".join(prompt_parts)
    
    def _invoke_bedrock_model(self, prompt: str) -> str:
        """
        Invoke AWS Bedrock model with the prepared prompt
        """
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4000,
            "temperature": 0.7,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        response = self.bedrock_runtime.invoke_model(
            modelId=self.model_id,
            body=json.dumps(request_body)
        )
        
        response_body = json.loads(response['body'].read())
        return response_body['content'][0]['text']
    
    def _process_response(
        self,
        raw_response: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Process raw model response into structured format
        Can be overridden by specific agents
        """
        return {
            "text": raw_response,
            "agent_type": self.agent_name
        }
    
    def _generate_follow_ups(
        self,
        response: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> List[str]:
        """
        Generate follow-up questions based on response
        Can be overridden by specific agents
        """
        return []
    
    def execute_action(
        self,
        action_name: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a specific action/tool
        
        Args:
            action_name: Name of the action to execute
            parameters: Parameters for the action
            
        Returns:
            Result of the action execution
        """
        # Find the action in registered action groups
        for action_group in self.action_groups:
            if action_group['name'] == action_name:
                function = action_group['function']
                return function(**parameters)
        
        raise ValueError(f"Action {action_name} not found in {self.agent_name}")
    
    def stream_response(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Stream responses from the agent (for real-time UX)
        """
        prompt = self._prepare_prompt(user_input, context, None)
        
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4000,
            "temperature": 0.7,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        response = self.bedrock_runtime.invoke_model_with_response_stream(
            modelId=self.model_id,
            body=json.dumps(request_body)
        )
        
        for event in response['body']:
            chunk = json.loads(event['chunk']['bytes'])
            if chunk['type'] == 'content_block_delta':
                yield chunk['delta']['text']
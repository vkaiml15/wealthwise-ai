"""
Amazon Q Business Integration Service
For Anonymous Mode (No TVM needed)
"""

import os
import boto3
from typing import Dict, Any, Optional
import json

class QBusinessService:
    """Service to interact with Amazon Q Business"""

    def __init__(self):
        """Initialize Q Business client using IAM role"""
        self.application_id = os.getenv('Q_BUSINESS_APPLICATION_ID')
        self.region = os.getenv('AWS_REGION', 'us-east-1')

        # ✅ Use IAM role - boto3 automatically gets credentials from EC2 instance metadata
        self.client = boto3.client(
            'qbusiness',
            region_name=self.region
        )

        print(f"✅ Q Business Service initialized (App ID: {self.application_id})")


    def chat_sync(
        self,
        user_message: str,
        user_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        parent_message_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a message to Q Business and get response

        Args:
            user_message: The user's message
            user_id: User identifier (not used in anonymous mode)
            conversation_id: Optional conversation ID to continue a conversation
            parent_message_id: Optional parent message ID

        Returns:
            Dictionary with response
        """
        try:
            print(f"📤 Sending to Q Business: {user_message[:50]}...")

            # Prepare request parameters
            # For ANONYMOUS mode, DO NOT include userId
            request_params = {
                'applicationId': self.application_id,
                'userMessage': user_message
            }

            # Add optional parameters if provided
            if conversation_id:
                request_params['conversationId'] = conversation_id
            if parent_message_id:
                request_params['parentMessageId'] = parent_message_id

            # Call Q Business ChatSync API
            response = self.client.chat_sync(**request_params)

            print(f"✅ Q Business responded successfully")

            return {
                'success': True,
                'systemMessage': response.get('systemMessage', ''),
                'conversationId': response.get('conversationId'),
                'systemMessageId': response.get('systemMessageId'),
                'userMessageId': response.get('userMessageId'),
                'sourceAttributions': response.get('sourceAttributions', [])
            }

        except Exception as e:
            print(f"❌ Q Business error: {e}")
            return {
                'success': False,
                'error': str(e),
                'systemMessage': f"Sorry, I encountered an error: {str(e)}"
            }


    def list_conversations(self, user_id: Optional[str] = None, max_results: int = 10) -> Dict[str, Any]:
        """List conversations (for anonymous mode)"""
        try:
            # For anonymous mode, don't pass userId
            response = self.client.list_conversations(
                applicationId=self.application_id,
                maxResults=max_results
            )

            return {
                'success': True,
                'conversations': response.get('conversations', [])
            }
        except Exception as e:
            print(f"❌ Error listing conversations: {e}")
            return {
                'success': False,
                'error': str(e),
                'conversations': []
            }

    def delete_conversation(self, conversation_id: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Delete a conversation (for anonymous mode)"""
        try:
            # For anonymous mode, don't pass userId
            self.client.delete_conversation(
                applicationId=self.application_id,
                conversationId=conversation_id
            )

            return {'success': True}
        except Exception as e:
            print(f"❌ Error deleting conversation: {e}")
            return {
                'success': False,
                'error': str(e)
            }


# Singleton instance
_qbusiness_service = None

def get_qbusiness_service() -> QBusinessService:
    """Get or create Q Business service instance"""
    global _qbusiness_service
    if _qbusiness_service is None:
        _qbusiness_service = QBusinessService()
    return _qbusiness_service

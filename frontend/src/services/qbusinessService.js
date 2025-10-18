/**
 * Q Business Service
 * Handles communication with Q Business backend
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
export class QBusinessService {
    constructor() {
        this.conversationId = null;
        this.parentMessageId = null;
    }

    /**
     * Send a message to Q Business
     */
    async sendMessage(message, userEmail = 'user@wealthwise.com') {
        try {
            const requestBody = {
                message
            };

            // Only include IDs if they exist and are valid (36+ characters)
            if (this.conversationId && this.conversationId.length >= 36) {
                requestBody.conversation_id = this.conversationId;
            }

            if (this.parentMessageId && this.parentMessageId.length >= 36) {
                requestBody.parent_message_id = this.parentMessageId;
            }

            console.log('📤 Sending to Q Business:', {
                message: message.substring(0, 50) + '...',
                hasConversationId: !!requestBody.conversation_id,
                hasParentMessageId: !!requestBody.parent_message_id
            });

            const response = await fetch(
                `${API_BASE_URL}/api/qbusiness/chat?user_email=${encodeURIComponent(userEmail)}`,
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(requestBody)
                }
            );

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            if (data.success) {
                // Store conversation context for next message
                // Only store if they're valid UUIDs (36+ characters)
                if (data.conversation_id && data.conversation_id.length >= 36) {
                    this.conversationId = data.conversation_id;
                }
                
                if (data.system_message_id && data.system_message_id.length >= 36) {
                    this.parentMessageId = data.system_message_id;
                }

                console.log('✅ Q Business response received:', {
                    conversationId: this.conversationId,
                    messageLength: data.system_message?.length || 0
                });

                return {
                    success: true,
                    message: data.system_message || 'No response received',
                    conversationId: data.conversation_id,
                    sources: data.source_attributions || []
                };
            } else {
                console.error('❌ Q Business API error:', data.error);
                return {
                    success: false,
                    message: data.system_message || 'An error occurred',
                    error: data.error
                };
            }
        } catch (error) {
            console.error('❌ Q Business connection error:', error);
            return {
                success: false,
                message: 'Failed to connect to Q Business. Please check if the backend is running.',
                error: error.message
            };
        }
    }

    /**
     * Start a new conversation
     */
    startNewConversation() {
        console.log('🆕 Starting new Q Business conversation');
        this.conversationId = null;
        this.parentMessageId = null;
    }

    /**
     * Get current conversation ID
     */
    getConversationId() {
        return this.conversationId;
    }

    /**
     * Get conversation history
     */
    async getConversations(userEmail = 'user@wealthwise.com') {
        try {
            const response = await fetch(
                `${API_BASE_URL}/api/qbusiness/conversations?user_email=${encodeURIComponent(userEmail)}`
            );
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            return data.conversations || [];
        } catch (error) {
            console.error('Error fetching conversations:', error);
            return [];
        }
    }

    /**
     * Delete a conversation
     */
    async deleteConversation(conversationId, userEmail = 'user@wealthwise.com') {
        try {
            // Validate conversation ID before attempting to delete
            if (!conversationId || conversationId.length < 36) {
                console.error('Invalid conversation ID for deletion:', conversationId);
                return false;
            }

            const response = await fetch(
                `${API_BASE_URL}/api/qbusiness/conversations/${conversationId}?user_email=${encodeURIComponent(userEmail)}`,
                { method: 'DELETE' }
            );
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return true;
        } catch (error) {
            console.error('Error deleting conversation:', error);
            return false;
        }
    }
}

// Singleton instance
let qBusinessService = null;

export const getQBusinessService = () => {
    if (!qBusinessService) {
        qBusinessService = new QBusinessService();
    }
    return qBusinessService;
};

import React, { createContext, useContext, useState } from 'react';
import { useAuth } from './AuthContext';
import { mockChatResponses, detectIntent } from '../data/mockChatResponses';

const ChatContext = createContext();

export const useChat = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
};

export const ChatProvider = ({ children }) => {
  const { currentUser, portfolio } = useAuth();
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const [conversationContext, setConversationContext] = useState({
    lastTopic: null,
    lastIntent: null,
    mentionedStocks: [],
    portfolioAnalyzed: false
  });

  // Send user message and get AI response
  const sendMessage = (content) => {
    // Add user message
    const userMessage = {
      role: 'user',
      content: content,
      timestamp: Date.now()
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsTyping(true);

    // Detect intent based on message and context
    const intent = detectIntent(content, conversationContext);

    // Update conversation context
    setConversationContext((prev) => ({
      ...prev,
      lastIntent: intent,
      lastTopic: intent
    }));

    // Simulate AI thinking delay
    setTimeout(() => {
      const response = mockChatResponses[intent] || mockChatResponses.general;
      
      // Customize response based on user's portfolio
      let customizedContent = response.message;
      
      // Replace placeholders with actual data
      if (portfolio) {
        customizedContent = customizedContent
          .replace(/\$X{1,}/g, `$${portfolio.totalValue?.toLocaleString()}`)
          .replace(/Y\.Y/g, portfolio.riskScore?.toString());
      }

      const assistantMessage = {
        role: 'assistant',
        content: customizedContent,
        followUp: response.followUp,
        timestamp: Date.now(),
        agent: getAgentName(intent)
      };

      setMessages((prev) => [...prev, assistantMessage]);
      setIsTyping(false);

      // Update context based on the response
      if (intent === 'portfolioAnalysis') {
        setConversationContext((prev) => ({
          ...prev,
          portfolioAnalyzed: true
        }));
      }
    }, 1500 + Math.random() * 1000); // Random delay between 1.5-2.5 seconds
  };

  // Get agent name based on intent
  const getAgentName = (intent) => {
    const agentMap = {
      portfolioAnalysis: 'Portfolio Analysis',
      recommendations: 'Recommendation',
      marketTrends: 'Market Trend',
      industryRecommendation: 'Market Trend',
      rebalancing: 'Rebalancing',
      riskAnalysis: 'Risk Profile',
      contextual_recommendation: 'Recommendation',
      general: 'Orchestrator'
    };
    return agentMap[intent] || 'Orchestrator';
  };

  // Clear chat
  const clearChat = () => {
    setMessages([]);
    setConversationContext({
      lastTopic: null,
      lastIntent: null,
      mentionedStocks: [],
      portfolioAnalyzed: false
    });
  };

  // Add a message directly (for follow-up clicks, etc.)
  const addMessage = (message) => {
    setMessages((prev) => [...prev, message]);
  };

  const value = {
    messages,
    isTyping,
    conversationContext,
    sendMessage,
    clearChat,
    addMessage
  };

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
};

export default ChatContext;
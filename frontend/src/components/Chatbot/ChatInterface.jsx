import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useChat } from '../../context/ChatContext';
import { 
  Send, 
  Sparkles, 
  TrendingUp, 
  BarChart3, 
  Shield, 
  Target,
  Loader2,
  AlertCircle,
  RefreshCw,
  MessageSquare
} from 'lucide-react';
import Message from './Message';
import FollowUpChips from './FollowUpChips';

const ChatInterface = () => {
  const { currentUser, portfolio } = useAuth();
  const { messages, sendMessage, isTyping, clearChat } = useChat();
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Quick action queries
  const quickActions = [
    {
      icon: BarChart3,
      label: 'Analyze Portfolio',
      query: 'Analyze my portfolio',
      color: 'indigo'
    },
    {
      icon: TrendingUp,
      label: 'Market Trends',
      query: 'What are the current market trends?',
      color: 'purple'
    },
    {
      icon: Shield,
      label: 'Risk Analysis',
      query: 'Analyze my risk profile',
      color: 'green'
    },
    {
      icon: Target,
      label: 'Recommendations',
      query: 'Give me stock recommendations',
      color: 'blue'
    }
  ];

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputValue.trim() && !isTyping) {
      sendMessage(inputValue.trim());
      setInputValue('');
    }
  };

  const handleQuickAction = (query) => {
    if (!isTyping) {
      sendMessage(query);
    }
  };

  const handleFollowUpClick = (query) => {
    if (!isTyping) {
      sendMessage(query);
    }
  };

  const handleClearChat = () => {
    if (window.confirm('Are you sure you want to clear the chat history?')) {
      clearChat();
      setInputValue('');
    }
  };

  return (
    <div className="flex flex-col h-full bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg flex items-center justify-center">
            <Sparkles className="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-gray-900">AI Investment Advisor</h2>
            <p className="text-sm text-gray-500">Ask me anything about your investments</p>
          </div>
        </div>
        
        {messages.length > 0 && (
          <button
            onClick={handleClearChat}
            className="flex items-center space-x-2 px-4 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Clear Chat</span>
          </button>
        )}
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto px-6 py-6 space-y-6">
        {messages.length === 0 ? (
          // Empty State
          <div className="h-full flex flex-col items-center justify-center text-center px-4">
            <div className="w-20 h-20 bg-gradient-to-br from-indigo-100 to-purple-100 rounded-full flex items-center justify-center mb-6">
              <MessageSquare className="w-10 h-10 text-indigo-600" />
            </div>
            <h3 className="text-2xl font-bold text-gray-900 mb-3">
              Welcome back, {currentUser?.name || 'Investor'}!
            </h3>
            <p className="text-gray-600 mb-8 max-w-md">
              I'm your AI investment advisor. Ask me about portfolio analysis, market trends, 
              recommendations, or any investment-related questions.
            </p>

            {/* Quick Actions */}
            <div className="w-full max-w-2xl">
              <p className="text-sm font-medium text-gray-700 mb-4">Quick Actions:</p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {quickActions.map((action, index) => (
                  <button
                    key={index}
                    onClick={() => handleQuickAction(action.query)}
                    className={`flex items-center space-x-3 p-4 bg-white border-2 border-gray-200 rounded-xl hover:border-${action.color}-500 hover:bg-${action.color}-50 transition-all group`}
                  >
                    <div className={`w-10 h-10 bg-${action.color}-100 rounded-lg flex items-center justify-center group-hover:bg-${action.color}-200 transition-colors`}>
                      <action.icon className={`w-5 h-5 text-${action.color}-600`} />
                    </div>
                    <div className="flex-1 text-left">
                      <p className="font-medium text-gray-900">{action.label}</p>
                      <p className="text-xs text-gray-500 mt-0.5">{action.query}</p>
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Portfolio Context */}
            {portfolio && (
              <div className="mt-8 p-4 bg-indigo-50 rounded-lg border border-indigo-100 max-w-md">
                <p className="text-sm text-indigo-900 font-medium mb-2">
                  📊 Your Portfolio at a Glance
                </p>
                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div>
                    <p className="text-indigo-600">Total Value</p>
                    <p className="font-semibold text-indigo-900">
                      ${portfolio.totalValue?.toLocaleString()}
                    </p>
                  </div>
                  <div>
                    <p className="text-indigo-600">Risk Score</p>
                    <p className="font-semibold text-indigo-900">
                      {portfolio.riskScore}/10
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        ) : (
          // Messages
          <>
            {messages.map((message, index) => (
              <Message key={index} message={message} />
            ))}

            {/* Typing Indicator */}
            {isTyping && (
              <div className="flex items-start space-x-3">
                <div className="w-8 h-8 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full flex items-center justify-center flex-shrink-0">
                  <Sparkles className="w-4 h-4 text-white" />
                </div>
                <div className="bg-white rounded-2xl rounded-tl-none px-4 py-3 shadow-sm border border-gray-200">
                  <div className="flex items-center space-x-2">
                    <Loader2 className="w-4 h-4 text-indigo-600 animate-spin" />
                    <span className="text-sm text-gray-600">Analyzing...</span>
                  </div>
                </div>
              </div>
            )}

            {/* Follow-up Chips */}
            {messages.length > 0 && 
             messages[messages.length - 1]?.role === 'assistant' && 
             messages[messages.length - 1]?.followUp && 
             !isTyping && (
              <FollowUpChips 
                followUp={messages[messages.length - 1].followUp}
                onChipClick={handleFollowUpClick}
              />
            )}

            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Input Area */}
      <div className="bg-white border-t border-gray-200 px-6 py-4">
        {/* Context Indicator */}
        {portfolio && messages.length > 0 && (
          <div className="mb-3 flex items-center space-x-2 text-xs text-gray-500">
            <AlertCircle className="w-3 h-3" />
            <span>I have context of your portfolio and previous conversation</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="flex items-end space-x-3">
          <div className="flex-1">
            <textarea
              ref={inputRef}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit(e);
                }
              }}
              placeholder="Ask about portfolio analysis, market trends, recommendations..."
              className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all outline-none resize-none"
              rows="1"
              style={{
                minHeight: '48px',
                maxHeight: '120px',
              }}
              disabled={isTyping}
            />
          </div>
          <button
            type="submit"
            disabled={!inputValue.trim() || isTyping}
            className="px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl font-medium hover:from-indigo-700 hover:to-purple-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2 shadow-lg hover:shadow-xl"
          >
            {isTyping ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
            <span className="hidden sm:inline">Send</span>
          </button>
        </form>

        {/* Quick Tips */}
        {messages.length === 0 && (
          <div className="mt-3 flex flex-wrap gap-2">
            <span className="text-xs text-gray-500">Try asking:</span>
            {['Portfolio analysis', 'Market trends', 'Rebalancing'].map((tip, index) => (
              <button
                key={index}
                onClick={() => setInputValue(tip)}
                className="text-xs px-3 py-1 bg-gray-100 text-gray-600 rounded-full hover:bg-gray-200 transition-colors"
              >
                {tip}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatInterface;
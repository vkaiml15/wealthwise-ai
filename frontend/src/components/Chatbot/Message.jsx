import React from 'react';
import { User, Sparkles, TrendingUp, TrendingDown, AlertTriangle, CheckCircle } from 'lucide-react';

const Message = ({ message }) => {
  const isUser = message.role === 'user';

  // Parse message content for special formatting
  const renderContent = (content) => {
    // Split by lines
    const lines = content.split('\n');
    
    return lines.map((line, index) => {
      // Check for headers (lines starting with ##)
      if (line.startsWith('## ')) {
        return (
          <h3 key={index} className="text-lg font-bold text-gray-900 mt-4 mb-2">
            {line.replace('## ', '')}
          </h3>
        );
      }

      // Check for bold text wrapped in **
      if (line.includes('**')) {
        const parts = line.split(/(\*\*.*?\*\*)/g);
        return (
          <p key={index} className="mb-2">
            {parts.map((part, i) => {
              if (part.startsWith('**') && part.endsWith('**')) {
                return <strong key={i} className="font-semibold text-gray-900">{part.slice(2, -2)}</strong>;
              }
              return <span key={i}>{part}</span>;
            })}
          </p>
        );
      }

      // Check for bullet points
      if (line.trim().startsWith('•') || line.trim().startsWith('-')) {
        return (
          <li key={index} className="ml-4 mb-1">
            {line.trim().replace(/^[•-]\s*/, '')}
          </li>
        );
      }

      // Check for numbered lists
      if (/^\d+\./.test(line.trim())) {
        return (
          <li key={index} className="ml-4 mb-1">
            {line.trim().replace(/^\d+\.\s*/, '')}
          </li>
        );
      }

      // Check for icons/emojis at start
      const iconMatch = line.match(/^(✅|⚠️|📊|🎯|💰|📈|📉|🏭|🎲|⚖️|🌍)/);
      if (iconMatch) {
        return (
          <div key={index} className="flex items-start space-x-2 mb-2">
            <span className="text-xl">{iconMatch[1]}</span>
            <span className="flex-1">{line.replace(iconMatch[1], '').trim()}</span>
          </div>
        );
      }

      // Regular paragraph
      if (line.trim()) {
        return <p key={index} className="mb-2">{line}</p>;
      }

      return <br key={index} />;
    });
  };

  return (
    <div className={`flex items-start space-x-3 ${isUser ? 'flex-row-reverse space-x-reverse' : ''}`}>
      {/* Avatar */}
      <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
        isUser 
          ? 'bg-gradient-to-br from-gray-600 to-gray-700' 
          : 'bg-gradient-to-br from-indigo-500 to-purple-600'
      }`}>
        {isUser ? (
          <User className="w-4 h-4 text-white" />
        ) : (
          <Sparkles className="w-4 h-4 text-white" />
        )}
      </div>

      {/* Message Content */}
      <div className={`flex-1 max-w-3xl ${isUser ? 'flex justify-end' : ''}`}>
        <div className={`rounded-2xl px-4 py-3 ${
          isUser 
            ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-tr-none' 
            : 'bg-white text-gray-800 shadow-sm border border-gray-200 rounded-tl-none'
        }`}>
          {/* Message Text */}
          <div className={`text-sm leading-relaxed ${isUser ? 'text-white' : 'text-gray-800'}`}>
            {renderContent(message.content)}
          </div>

          {/* Timestamp */}
          <div className={`text-xs mt-2 ${isUser ? 'text-indigo-200' : 'text-gray-400'}`}>
            {new Date(message.timestamp).toLocaleTimeString('en-US', { 
              hour: 'numeric', 
              minute: '2-digit' 
            })}
          </div>
        </div>

        {/* Agent Indicator (for assistant messages) */}
        {!isUser && message.agent && (
          <div className="mt-2 flex items-center space-x-2 text-xs text-gray-500">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span>{message.agent} agent</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default Message;
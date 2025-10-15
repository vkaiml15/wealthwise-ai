import React from 'react';
import { ArrowRight } from 'lucide-react';

const FollowUpChips = ({ followUp, onChipClick }) => {
  if (!followUp) return null;

  // Parse follow-up text into clickable chip
  // Can be a single question or multiple suggestions
  const suggestions = Array.isArray(followUp) ? followUp : [followUp];

  return (
    <div className="flex items-start space-x-3">
      {/* Empty space for alignment with messages */}
      <div className="w-8"></div>
      
      <div className="flex-1 max-w-3xl">
        <p className="text-xs font-medium text-gray-500 mb-2">Suggested follow-up:</p>
        <div className="flex flex-wrap gap-2">
          {suggestions.map((suggestion, index) => (
            <button
              key={index}
              onClick={() => onChipClick(suggestion)}
              className="group flex items-center space-x-2 px-4 py-2 bg-white border-2 border-indigo-200 rounded-full text-sm text-indigo-700 hover:bg-indigo-50 hover:border-indigo-400 transition-all shadow-sm hover:shadow-md"
            >
              <span>{suggestion}</span>
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default FollowUpChips;
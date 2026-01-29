// frontend/src/components/ChatWidget/ChatInput.jsx
import React from 'react';
import { Send } from 'lucide-react';

const ChatInput = ({ value, onChange, onSend, disabled }) => {
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSend(value);
    }
  };

  return (
    <div className="p-[15px] border-t border-[#e0e0e0] flex gap-[10px] bg-white">
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyPress={handleKeyPress}
        placeholder="Type your question..."
        disabled={disabled}
        className="flex-1 px-[15px] py-3 border border-[#e0e0e0] rounded-[25px] outline-none text-[0.95rem] transition-all duration-200 focus:border-[#667eea] disabled:bg-gray-100 disabled:cursor-not-allowed"
        autoComplete="off"
      />
      <button
        onClick={() => onSend(value)}
        disabled={disabled || !value.trim()}
        className="w-[45px] h-[45px] rounded-full border-none bg-gradient-to-br from-[#667eea] to-[#764ba2] text-white cursor-pointer flex items-center justify-center transition-all duration-200 hover:scale-105 disabled:opacity-60 disabled:cursor-not-allowed"
        aria-label="Send message"
      >
        <Send size={20} />
      </button>
    </div>
  );
};

export default ChatInput;
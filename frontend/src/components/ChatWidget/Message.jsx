// frontend/src/components/ChatWidget/Message.jsx
import React from 'react';

const Message = ({ message }) => {
  const { content, isUser, sources, isError } = message;

  return (
    <div
      className={`mb-[15px] flex animate-fadeIn ${
        isUser ? 'justify-end' : 'justify-start'
      }`}
    >
      <div
        className={`max-w-[75%] px-4 py-3 rounded-[15px] break-words ${
          isUser
            ? 'bg-gradient-to-br from-[#667eea] to-[#764ba2] text-white rounded-br-[5px]'
            : isError
            ? 'bg-red-50 text-red-600 rounded-bl-[5px] shadow-[0_2px_5px_rgba(0,0,0,0.1)]'
            : 'bg-white text-[#333] rounded-bl-[5px] shadow-[0_2px_5px_rgba(0,0,0,0.1)]'
        }`}
      >
        <p className="text-sm leading-relaxed whitespace-pre-wrap">{content}</p>

        {/* Sources */}
        {!isUser && sources && sources.length > 0 && (
          <div className="mt-3 space-y-1">
            <p className="text-xs font-semibold text-gray-500 mb-2">Sources:</p>
            {sources.slice(0, 3).map((source, idx) => (
              <div
                key={idx}
                className="text-xs bg-blue-50 text-blue-700 px-2.5 py-1.5 rounded-full inline-block mr-1.5 mb-1"
              >
                📄 {source.source} · Page {source.page}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Message;
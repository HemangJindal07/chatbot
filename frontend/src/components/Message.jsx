// frontend/src/components/Message.jsx
import React from "react";
import { Bot, User } from "lucide-react";

const Message = ({ message, isUser }) => {
  return (
    <div
      className={`flex gap-3 ${
        isUser ? "flex-row-reverse" : "flex-row"
      }`}
    >
      <div
        className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
          isUser ? "bg-blue-500" : "bg-gray-700"
        }`}
      >
        {isUser ? (
          <User size={20} className="text-white" />
        ) : (
          <Bot size={20} className="text-white" />
        )}
      </div>

      <div className={`flex-1 ${isUser ? "text-right" : "text-left"}`}>
        <div
          className={`inline-block max-w-[80%] p-4 rounded-lg ${
            isUser
              ? "bg-blue-500 text-white"
              : "bg-gray-100 text-gray-800 border border-gray-200"
          }`}
        >
          <p className="whitespace-pre-wrap">{message.content}</p>
        </div>

        {/*
        {!isUser && message.sources && message.sources.length > 0 && (
          <div className="mt-2 text-sm text-gray-600">
            <details className="cursor-pointer">
              <summary className="font-medium hover:text-blue-600">
                Sources ({message.sources.length})
              </summary>

              <ul className="mt-2 space-y-1 pl-4">
                {message.sources.map((source, idx) => (
                  <li key={idx} className="text-xs">
                    • {source.source}, Page {source.page}
                    <span className="text-gray-400">
                      {" "}
                      ({(source.score * 100).toFixed(1)}% relevant)
                    </span>
                  </li>
                ))}
              </ul>
            </details>
          </div>
        )}
        */}
      </div>
    </div>
  );
};

export default Message;

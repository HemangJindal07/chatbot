// frontend/src/components/ChatWidget/ChatWindow.jsx
import React, { useState, useRef, useEffect } from 'react';
import { chatAPI } from '../../services/api';

const ChatWindow = ({ onClose }) => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Hello! I'm your Policy Bot. Ask me anything about company policies, and I'll help you find the information you need.",
      isUser: false,
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState(null);
  const messagesEndRef = useRef(null);
  const chatMessagesRef = useRef(null);

  const scrollToBottom = () => {
    if (chatMessagesRef.current) {
      chatMessagesRef.current.scrollTop = chatMessagesRef.current.scrollHeight;
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSend = async () => {
    const message = input.trim();
    if (!message || loading) return;

    // Add user message
    setMessages((prev) => [...prev, { id: Date.now(), text: message, isUser: true }]);
    setInput('');
    setLoading(true);

    try {
      const response = await chatAPI.sendMessage(message, conversationId);
      
      // Add bot response
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          text: response.answer,
          isUser: false,
          sources: response.sources || [],
        },
      ]);
      setConversationId(response.conversation_id);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          text: 'Sorry, I encountered an error. Please try again later.',
          isUser: false,
          isError: true,
        },
      ]);
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSend();
    }
  };

  return (
    <div
      style={{
        position: 'fixed',
        bottom: '100px',
        right: '30px',
        width: '380px',
        height: '550px',
        background: 'white',
        borderRadius: '15px',
        boxShadow: '0 10px 40px rgba(0, 0, 0, 0.3)',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
        zIndex: 999,
        animation: 'slideUp 0.3s ease',
      }}
    >
      <style>
        {`
          @keyframes slideUp {
            from {
              opacity: 0;
              transform: translateY(20px);
            }
            to {
              opacity: 1;
              transform: translateY(0);
            }
          }
          @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
          }
          @keyframes typing {
            0%, 60%, 100% { transform: translateY(0); }
            30% { transform: translateY(-10px); }
          }
          @media (max-width: 480px) {
            .chat-window-responsive {
              width: 100% !important;
              height: 100% !important;
              bottom: 0 !important;
              right: 0 !important;
              border-radius: 0 !important;
            }
          }
        `}
      </style>

      {/* Chat Header */}
      <div
        style={{
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          padding: '20px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}
      >
        <h3 style={{ fontSize: '1.2rem', fontWeight: 600, margin: 0 }}>Policy Bot</h3>
        <button
          onClick={onClose}
          style={{
            background: 'none',
            border: 'none',
            color: 'white',
            fontSize: '1.5rem',
            cursor: 'pointer',
            width: '30px',
            height: '30px',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            borderRadius: '50%',
            transition: 'background 0.2s ease',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = 'rgba(255, 255, 255, 0.2)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = 'none';
          }}
        >
          ×
        </button>
      </div>

      {/* Chat Messages */}
      <div
        ref={chatMessagesRef}
        style={{
          flex: 1,
          padding: '20px',
          overflowY: 'auto',
          background: '#f8f9fa',
        }}
        className="custom-scrollbar"
      >
        {messages.map((message) => (
          <div
            key={message.id}
            style={{
              marginBottom: '15px',
              display: 'flex',
              justifyContent: message.isUser ? 'flex-end' : 'flex-start',
              animation: 'fadeIn 0.3s ease',
            }}
          >
            <div
              style={{
                maxWidth: '75%',
                padding: '12px 16px',
                borderRadius: '15px',
                wordWrap: 'break-word',
                background: message.isUser
                  ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                  : message.isError
                  ? '#fee'
                  : 'white',
                color: message.isUser ? 'white' : message.isError ? '#c00' : '#333',
                borderBottomLeftRadius: message.isUser ? '15px' : '5px',
                borderBottomRightRadius: message.isUser ? '5px' : '15px',
                boxShadow: !message.isUser ? '0 2px 5px rgba(0, 0, 0, 0.1)' : 'none',
              }}
            >
              {message.text}
              
              {/* Sources */}
              {message.sources && message.sources.length > 0 && (
                <div style={{ marginTop: '10px' }}>
                  {message.sources.slice(0, 3).map((source, idx) => (
                    <div
                      key={idx}
                      style={{
                        display: 'inline-block',
                        fontSize: '0.75rem',
                        background: '#e3f2fd',
                        color: '#1976d2',
                        padding: '4px 10px',
                        borderRadius: '12px',
                        marginRight: '5px',
                        marginBottom: '5px',
                      }}
                    >
                      📄 {source.source} · Page {source.page}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {/* Typing Indicator */}
        {loading && (
          <div
            style={{
              display: 'flex',
              justifyContent: 'flex-start',
              marginBottom: '15px',
            }}
          >
            <div
              style={{
                padding: '12px 16px',
                background: 'white',
                borderRadius: '15px',
                width: 'fit-content',
                boxShadow: '0 2px 5px rgba(0, 0, 0, 0.1)',
              }}
            >
              <span style={{
                height: '8px',
                width: '8px',
                background: '#999',
                borderRadius: '50%',
                display: 'inline-block',
                margin: '0 2px',
                animation: 'typing 1.4s infinite',
              }}></span>
              <span style={{
                height: '8px',
                width: '8px',
                background: '#999',
                borderRadius: '50%',
                display: 'inline-block',
                margin: '0 2px',
                animation: 'typing 1.4s infinite 0.2s',
              }}></span>
              <span style={{
                height: '8px',
                width: '8px',
                background: '#999',
                borderRadius: '50%',
                display: 'inline-block',
                margin: '0 2px',
                animation: 'typing 1.4s infinite 0.4s',
              }}></span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Chat Input */}
      <div
        style={{
          padding: '15px',
          borderTop: '1px solid #e0e0e0',
          display: 'flex',
          gap: '10px',
          background: 'white',
        }}
      >
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your question..."
          disabled={loading}
          autoComplete="off"
          style={{
            flex: 1,
            padding: '12px 15px',
            border: '1px solid #e0e0e0',
            borderRadius: '25px',
            outline: 'none',
            fontSize: '0.95rem',
            transition: 'border 0.2s ease',
          }}
          onFocus={(e) => {
            e.target.style.borderColor = '#667eea';
          }}
          onBlur={(e) => {
            e.target.style.borderColor = '#e0e0e0';
          }}
        />
        <button
          onClick={handleSend}
          disabled={loading || !input.trim()}
          style={{
            width: '45px',
            height: '45px',
            borderRadius: '50%',
            border: 'none',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            cursor: loading || !input.trim() ? 'not-allowed' : 'pointer',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            transition: 'all 0.2s ease',
            opacity: loading || !input.trim() ? 0.6 : 1,
          }}
          onMouseEnter={(e) => {
            if (!loading && input.trim()) {
              e.currentTarget.style.transform = 'scale(1.05)';
            }
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'scale(1)';
          }}
        >
          <svg 
            xmlns="http://www.w3.org/2000/svg" 
            width="20" 
            height="20" 
            viewBox="0 0 24 24" 
            fill="white"
          >
            <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
          </svg>
        </button>
      </div>
    </div>
  );
};

export default ChatWindow;
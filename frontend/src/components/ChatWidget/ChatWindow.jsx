// frontend/src/components/ChatWidget/ChatWindow.jsx
import React, { useState, useRef, useEffect } from 'react';
import { chatAPI } from '../../services/api';

const ChatWindow = ({ onClose }) => {
  const [messages, setMessages] = useState(() => {
    const saved = sessionStorage.getItem('chatMessages');
    return saved ? JSON.parse(saved) : [
      {
        id: 1,
        content: "Hello! I'm your Policy Assistant. Here are some common questions I can help you with:",
        isUser: false,
        timestamp: new Date().toISOString(),
      },
    ];
  });
  
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState(() => {
    const saved = sessionStorage.getItem('conversationId');
    return saved || null;
  });
  
  // Suggestions state
  const [suggestions, setSuggestions] = useState([]);
  const [loadingSuggestions, setLoadingSuggestions] = useState(false);
  
  const messagesEndRef = useRef(null);
  const chatMessagesRef = useRef(null);

  // Load suggestions when component mounts
  useEffect(() => {
    loadSuggestions();
  }, []);

  const loadSuggestions = async () => {
    setLoadingSuggestions(true);
    try {
      const response = await chatAPI.getSuggestions(5);
      setSuggestions(response.suggestions || []);
      console.log('💡 Loaded suggestions:', response.suggestions);
    } catch (error) {
      console.error('Failed to load suggestions:', error);
      // Fallback suggestions
      setSuggestions([
        { question: 'What is the password policy?', category: 'IT Security' },
        { question: 'What is POSH?', category: 'Workplace Safety' },
        { question: 'Can I work from home?', category: 'Remote Work' },
        { question: 'What is the VPN policy?', category: 'Network Access' },
        { question: 'How do I report harassment?', category: 'HR' },
      ]);
    } finally {
      setLoadingSuggestions(false);
    }
  };

  useEffect(() => {
    sessionStorage.setItem('chatMessages', JSON.stringify(messages));
  }, [messages]);

  useEffect(() => {
    if (conversationId) {
      sessionStorage.setItem('conversationId', conversationId);
    }
  }, [conversationId]);

  const scrollToBottom = () => {
    if (chatMessagesRef.current) {
      chatMessagesRef.current.scrollTop = chatMessagesRef.current.scrollHeight;
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSend = async (messageText = null) => {
    const message = messageText || input.trim();
    if (!message || loading) return;

    const userMessage = {
      id: Date.now(),
      content: message,
      isUser: true,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const conversationHistory = messages
        .filter(msg => msg.id !== 1)
        .map(msg => ({
          content: msg.content,
          isUser: msg.isUser,
          timestamp: msg.timestamp,
        }));

      const response = await chatAPI.sendMessage(
        message, 
        conversationId,
        conversationHistory
      );

      const botMessage = {
        id: Date.now() + 1,
        content: response.answer,
        isUser: false,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, botMessage]);
      setConversationId(response.conversation_id);
    } catch (error) {
      const errorMessage = {
        id: Date.now() + 1,
        content: 'Sorry, I encountered an error. Please try again later.',
        isUser: false,
        isError: true,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSuggestionClick = (question) => {
    handleSend(question);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSend();
    }
  };

  const handleClearConversation = () => {
    sessionStorage.removeItem('chatMessages');
    sessionStorage.removeItem('conversationId');
    setMessages([
      {
        id: 1,
        content: "Hello! I'm your Policy Assistant. Here are some common questions I can help you with:",
        isUser: false,
        timestamp: new Date().toISOString(),
      },
    ]);
    setConversationId(null);
    loadSuggestions(); // Reload suggestions
  };

  // Show suggestions only when conversation just started
  const showSuggestions = messages.length === 1;

  // Icon mapping for categories
  const categoryIcons = {
    'IT Security': '',
    'Workplace Safety': '',
    'Remote Work': '',
    'Network Access': '',
    'HR': '',
    'IT Policy': '',
    'Security': '',
    'Email': '',
    'Data Protection': '',
  };

  return (
    <div
      style={{
        position: 'fixed',
        bottom: '100px',
        right: '30px',
        width: '500px',
        height: '700px',
        maxWidth: 'calc(100vw - 40px)',
        maxHeight: 'calc(100vh - 120px)',
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
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
          }
          @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
          }
          @keyframes typing {
            0%, 60%, 100% { transform: translateY(0); }
            30% { transform: translateY(-10px); }
          }
        `}
      </style>

      {/* Header */}
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
        <div>
          <h3 style={{ fontSize: '1.2rem', fontWeight: 600, margin: 0 }}>Tx Policy Assistant</h3>
          <p style={{ fontSize: '0.7rem', margin: '4px 0 0 0', opacity: 0.8 }}>
            {/* 💬 {messages.length - 1} messages */}
          </p>
        </div>
        <div style={{ display: 'flex', gap: '5px' }}>
          <button
            onClick={handleClearConversation}
            title="New conversation"
            style={{
              background: 'none',
              border: 'none',
              color: 'white',
              fontSize: '1.2rem',
              cursor: 'pointer',
              width: '30px',
              height: '30px',
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              borderRadius: '50%',
              transition: 'background 0.2s ease',
            }}
            onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(255, 255, 255, 0.2)'}
            onMouseLeave={(e) => e.currentTarget.style.background = 'none'}
          >
            ⟳
          </button>
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
            onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(255, 255, 255, 0.2)'}
            onMouseLeave={(e) => e.currentTarget.style.background = 'none'}
          >
            ×
          </button>
        </div>
      </div>

      {/* Messages */}
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
                whiteSpace: 'pre-wrap',
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
              {message.content}
            </div>
          </div>
        ))}

        {/* Smart Suggestions - Professional UI */}


{/* Smart Suggestions - Clean Text Only */}
{showSuggestions && (
  <div style={{ marginTop: '20px', animation: 'fadeIn 0.5s ease' }}>
    <p style={{ 
      fontSize: '0.7rem', 
      color: '#a0aec0', 
      marginBottom: '12px',
      fontWeight: 500,
      letterSpacing: '0.8px',
      textTransform: 'uppercase'
    }}>
      Popular Questions
    </p>
    
    {loadingSuggestions ? (
      <div style={{ 
        textAlign: 'center', 
        padding: '30px 20px', 
        color: '#a0aec0',
        fontSize: '0.8rem'
      }}>
        Generating suggestions...
      </div>
    ) : (
      <div style={{ 
        display: 'flex',
        flexWrap: 'wrap',      
        gap: '8px',         
        alignItems: 'flex-start'
      }}>
        {suggestions.map((suggestion, idx) => (
          <button
            key={idx}
            onClick={() => handleSuggestionClick(suggestion.question)}
            style={{
              background: 'white',
              border: '1px solid #e2e8f0',
              borderRadius: '10px',
              padding: '12px 14px',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
              textAlign: 'left',
              boxShadow: '0 1px 2px rgba(0, 0, 0, 0.04)',
              fontSize: '0.85rem',
              color: '#4a5568',
              fontWeight: 400,
              lineHeight: '1.4',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = '#667eea';
              e.currentTarget.style.background = '#f7fafc';
              e.currentTarget.style.transform = 'translateX(4px)';
              e.currentTarget.style.boxShadow = '0 2px 8px rgba(102, 126, 234, 0.1)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = '#e2e8f0';
              e.currentTarget.style.background = 'white';
              e.currentTarget.style.transform = 'translateX(0)';
              e.currentTarget.style.boxShadow = '0 1px 2px rgba(0, 0, 0, 0.04)';
            }}
          >
            {suggestion.question}
          </button>
        ))}
      </div>
    )}
  </div>
)}
        {/* Typing Indicator */}
        {loading && (
          <div style={{ display: 'flex', justifyContent: 'flex-start', marginBottom: '15px' }}>
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

      {/* Input */}
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
          onFocus={(e) => e.target.style.borderColor = '#667eea'}
          onBlur={(e) => e.target.style.borderColor = '#e0e0e0'}
        />
        <button
          onClick={() => handleSend()}
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
          onMouseLeave={(e) => e.currentTarget.style.transform = 'scale(1)'}
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="white">
            <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
          </svg>
        </button>
      </div>
    </div>
  );
};

export default ChatWindow;
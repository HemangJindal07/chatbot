// frontend/src/components/ChatWidget/ChatWindow.jsx
import React, { useState, useRef, useEffect } from 'react';
import { chatAPI } from '../../services/api';

const ChatWindow = ({ onClose }) => {
  const [messages, setMessages] = useState(() => {
    const saved = sessionStorage.getItem('chatMessages');
    return saved ? JSON.parse(saved) : [
      {
        id: 1,
        content: "Hello! I'm your Policy Bot. Select a policy document to see what you can ask about.",
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
  
  // NEW: States for policies and suggestions
  const [policies, setPolicies] = useState([]);
  const [loadingPolicies, setLoadingPolicies] = useState(false);
  const [selectedPolicy, setSelectedPolicy] = useState(null);
  const [suggestions, setSuggestions] = useState([]);
  const [loadingSuggestions, setLoadingSuggestions] = useState(false);
  
  const messagesEndRef = useRef(null);
  const chatMessagesRef = useRef(null);

  // Load policies when component mounts
  useEffect(() => {
    loadPolicies();
  }, []);

  const loadPolicies = async () => {
    setLoadingPolicies(true);
    try {
    const response = await chatAPI.getPolicies();
    setPolicies(response.policies || []);
    console.log('Loaded policies:', response.policies);
    } catch (error) {
      console.error('Failed to load policies:', error);
    } finally {
      setLoadingPolicies(false);
    }
  };

  const handlePolicyClick = async (policy) => {
    setSelectedPolicy(policy);
    setLoadingSuggestions(true);
    
    try {
    const response = await chatAPI.getPolicySuggestions(policy.filename);
    setSuggestions(response.suggestions || []);
    console.log('Generated suggestions:', response.suggestions);
    } catch (error) {
      console.error('Failed to load suggestions:', error);
      setSuggestions([]);
    } finally {
      setLoadingSuggestions(false);
    }
  };

  const handleBackToPolicies = () => {
    setSelectedPolicy(null);
    setSuggestions([]);
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

    // Hide suggestions after first message
    setSelectedPolicy(null);
    setSuggestions([]);

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
        content: "Hello! I'm your Policy Bot. Select a policy document to see what you can ask about.",
        isUser: false,
        timestamp: new Date().toISOString(),
      },
    ]);
    setConversationId(null);
    setSelectedPolicy(null);
    setSuggestions([]);
    loadPolicies(); // Reload policies
  };

  // Show suggestions only when conversation just started
  const showSuggestions = messages.length === 1;

  return (
  <div
    style={{
      position: 'fixed',
      bottom: '100px',
      right: '30px',
      width: '1050px',           // Increased from 380px
      height: '550px',          // Increased from 550px
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
          <h3 style={{ fontSize: '1.2rem', fontWeight: 600, margin: 0 }}>Policy Bot</h3>
          <p style={{ fontSize: '0.7rem', margin: '4px 0 0 0', opacity: 0.8 }}>
            {/* {messages.length - 1} messages */}
          </p>
        </div>
        <div style={{ display: 'flex', gap: '5px' }}>
          <button
            onClick={handleClearConversation}
            title="Clear conversation"
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

        {/* Policy Selection - Show only at start */}
        {showSuggestions && !selectedPolicy && (
          <div style={{ marginTop: '20px', animation: 'fadeIn 0.5s ease' }}>
              <p style={{ 
              fontSize: '0.85rem', 
              color: '#666', 
              marginBottom: '12px',
              fontWeight: 500 
            }}>
              Available Policies:
            </p>
            
            {loadingPolicies ? (
              <div style={{ textAlign: 'center', padding: '20px', color: '#999' }}>
                Loading policies...
              </div>
            ) : policies.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '20px', color: '#999' }}>
                No policies found. Please add PDF files to the backend.
              </div>
            ) : (
              <div style={{ 
                display: 'grid', 
                gridTemplateColumns: '1fr',
                gap: '8px' 
              }}>
                {policies.map((policy, idx) => (
                  <button
                    key={idx}
                    onClick={() => handlePolicyClick(policy)}
                    style={{
                      background: 'white',
                      border: '1px solid #e0e0e0',
                      borderRadius: '10px',
                      padding: '12px',
                      fontSize: '0.85rem',
                      color: '#333',
                      cursor: 'pointer',
                      transition: 'all 0.2s ease',
                      textAlign: 'left',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '10px',
                      boxShadow: '0 2px 4px rgba(0, 0, 0, 0.05)',
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.borderColor = '#667eea';
                      e.currentTarget.style.background = '#f0f4ff';
                      e.currentTarget.style.transform = 'translateX(4px)';
                      e.currentTarget.style.boxShadow = '0 4px 8px rgba(102, 126, 234, 0.15)';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.borderColor = '#e0e0e0';
                      e.currentTarget.style.background = 'white';
                      e.currentTarget.style.transform = 'translateX(0)';
                      e.currentTarget.style.boxShadow = '0 2px 4px rgba(0, 0, 0, 0.05)';
                    }}
                  >
                    <span style={{ fontSize: '1.5rem' }}>{policy.icon}</span>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontWeight: 600, marginBottom: '2px' }}>
                        {policy.display_name}
                      </div>
                      <div style={{ fontSize: '0.7rem', color: '#999' }}>
                        Click to see topics
                      </div>
                    </div>
                    <span style={{ color: '#667eea', fontSize: '1.2rem' }}>→</span>
                  </button>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Suggestions - Show after policy selected */}
        {showSuggestions && selectedPolicy && (
          <div style={{ marginTop: '20px', animation: 'fadeIn 0.5s ease' }}>
            <div style={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: '8px',
              marginBottom: '12px'
            }}>
              <button
                onClick={handleBackToPolicies}
                style={{
                  background: 'none',
                  border: 'none',
                  color: '#667eea',
                  cursor: 'pointer',
                  fontSize: '1.2rem',
                  padding: '4px',
                }}
              >
                ←
              </button>
              <p style={{ 
                fontSize: '0.85rem', 
                color: '#666',
                fontWeight: 500,
                margin: 0
              }}>
                {selectedPolicy.icon} {selectedPolicy.display_name}
              </p>
            </div>
            
            {loadingSuggestions ? (
              <div style={{ textAlign: 'center', padding: '20px', color: '#999' }}>
                Generating suggestions...
              </div>
            ) : (
              <div style={{ 
                display: 'flex',
                flexDirection: 'column',
                gap: '8px' 
              }}>
                {suggestions.map((suggestion, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSuggestionClick(suggestion.question)}
                    style={{
                      background: 'white',
                      border: '1px solid #e0e0e0',
                      borderRadius: '10px',
                      padding: '12px',
                      fontSize: '0.85rem',
                      color: '#333',
                      cursor: 'pointer',
                      transition: 'all 0.2s ease',
                      textAlign: 'left',
                      boxShadow: '0 2px 4px rgba(0, 0, 0, 0.05)',
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.borderColor = '#667eea';
                      e.currentTarget.style.background = '#f0f4ff';
                      e.currentTarget.style.transform = 'translateX(4px)';
                      e.currentTarget.style.boxShadow = '0 4px 8px rgba(102, 126, 234, 0.15)';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.borderColor = '#e0e0e0';
                      e.currentTarget.style.background = 'white';
                      e.currentTarget.style.transform = 'translateX(0)';
                      e.currentTarget.style.boxShadow = '0 2px 4px rgba(0, 0, 0, 0.05)';
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
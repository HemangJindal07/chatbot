// frontend/src/App.jsx
import React, { useState, useRef, useEffect } from 'react';
import { chatAPI } from './services/api';
import Message from './components/Message';
import ChatInput from './components/ChatInput';
import Sidebar from './components/Sidebar';
import { Loader2 } from 'lucide-react';

function App() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState(null);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (content) => {
    setError(null);
    
    // Add user message
    const userMessage = {
      id: Date.now(),
      content,
      isUser: true,
    };
    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);

    try {
      const response = await chatAPI.sendMessage(content, conversationId);
      
      // Add bot response
      const botMessage = {
        id: Date.now() + 1,
        content: response.answer,
        isUser: false,
        sources: response.sources,
      };
      
      setMessages((prev) => [...prev, botMessage]);
      setConversationId(response.conversation_id);
    } catch (err) {
      setError('Failed to get response. Please try again.');
      console.error('Chat error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleClearChat = () => {
    setMessages([]);
    setConversationId(null);
    setError(null);
  };

  return (
    <div className="flex h-screen bg-white">
      <Sidebar onClearChat={handleClearChat} />
      
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="border-b border-gray-200 p-4 bg-white">
          <h1 className="text-2xl font-bold text-gray-800">
            🤖 TestingXperts Policy Chatbot
          </h1>
          <p className="text-sm text-gray-600 mt-1">
            Ask me anything about our IT policies
          </p>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 && (
            <div className="text-center text-gray-500 mt-20">
              <p className="text-lg">👋 Hi! I'm your policy assistant.</p>
              <p className="mt-2">Ask me anything about TestingXperts policies!</p>
            </div>
          )}
          
          {messages.map((message) => (
            <Message
              key={message.id}
              message={message}
              isUser={message.isUser}
            />
          ))}
          
          {loading && (
            <div className="flex items-center gap-2 text-gray-600">
              <Loader2 className="animate-spin" size={20} />
              <span>Thinking...</span>
            </div>
          )}
          
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <ChatInput onSend={handleSendMessage} disabled={loading} />
      </div>
    </div>
  );
}

export default App;
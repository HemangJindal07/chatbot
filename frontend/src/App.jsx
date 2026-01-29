// frontend/src/App.jsx
import React, { useState } from 'react';
import ChatButton from './components/ChatWidget/ChatButton';
import ChatWindow from './components/ChatWidget/ChatWindow';

function App() {
  const [isChatOpen, setIsChatOpen] = useState(false);

  return (
    <div 
      style={{
        fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
        background: '#ffffff',
        minHeight: '100vh',
        width: '100vw',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
      }}
    >
      {/* Header with Logo */}
      <div style={{
        position: 'absolute',
        top: '20px',
        left: '30px',
        zIndex: 100,
      }}>
        <img 
          src="/tx.png" 
          alt="TestingXperts" 
          style={{
            height: '80px',
            width: 'auto',
            objectFit: 'contain',
          }}
        />
      </div>

      {/* TxMinds Logo - Right */}
      <div style={{
        position: 'absolute',
        top: '20px',
        right: '30px',
        zIndex: 100,
      }}>
        <img 
          src="/txminds.png" 
          alt="TxMinds" 
          style={{
            height: '80px',
            width: 'auto',
            objectFit: 'contain',
          }}
        />
      </div>
      
      {/* Page Content */}
      <div style={{
        textAlign: 'center',
        color: '#0a0a0a',
        padding: '20px',
      }}>
        <h1 style={{
          fontSize: '3rem',
          marginBottom: '1rem',
          fontWeight: 'bold',
        }}>
          Welcome to Policy Bot
        </h1>
        <p style={{
          fontSize: '1.2rem',
          opacity: 0.9,
        }}>
          Your AI assistant for employee policy questions
        </p>
        <p style={{
          marginTop: '10px',
          fontSize: '1rem',
          opacity: 0.9,
        }}>
          Click the chat button below to get started!
        </p>
      </div>

      {/* Chat Window */}
      {isChatOpen && <ChatWindow onClose={() => setIsChatOpen(false)} />}

      {/* Chat Button */}
      <ChatButton 
        onClick={() => setIsChatOpen(!isChatOpen)} 
        isOpen={isChatOpen}
      />
    </div>
  );
}

export default App;
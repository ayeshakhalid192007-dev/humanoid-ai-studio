import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '@site/src/context/AuthContext';

// Styles for the chatbot
const chatStyles = {
  chatWidget: {
    position: 'fixed',
    bottom: '20px',
    right: '20px',
    zIndex: 10000,
    display: 'flex',
    flexDirection: 'column',
    fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
  },
  chatButton: {
    width: '60px',
    height: '60px',
    borderRadius: '50%',
    backgroundColor: '#4F46E5',
    color: 'white',
    border: 'none',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    cursor: 'pointer',
    boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
    fontSize: '24px',
    transition: 'all 0.3s ease',
  },
  chatButtonOpen: {
    transform: 'translateY(-10px)',
    boxShadow: '0 6px 16px rgba(0, 0, 0, 0.2)',
  },
  chatContainer: {
    width: '400px',
    height: '500px',
    borderRadius: '12px',
    backgroundColor: 'white',
    boxShadow: '0 10px 25px rgba(0, 0, 0, 0.15)',
    display: 'flex',
    flexDirection: 'column',
    overflow: 'hidden',
    transition: 'all 0.3s ease',
    transform: 'translateY(20px)',
  },
  chatContainerOpen: {
    transform: 'translateY(0)',
  },
  chatHeader: {
    backgroundColor: '#4F46E5',
    color: 'white',
    padding: '16px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  chatMessages: {
    flex: 1,
    padding: '16px',
    overflowY: 'auto',
    backgroundColor: '#f9fafb',
  },
  chatInput: {
    display: 'flex',
    padding: '12px',
    backgroundColor: 'white',
    borderTop: '1px solid #e5e7eb',
  },
  messageInput: {
    flex: 1,
    padding: '12px',
    border: '1px solid #d1d5db',
    borderRadius: '8px',
    marginRight: '8px',
    fontSize: '14px',
  },
  sendMessageButton: {
    padding: '12px 16px',
    backgroundColor: '#4F46E5',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
  },
  message: {
    marginBottom: '12px',
    padding: '8px 12px',
    borderRadius: '8px',
    maxWidth: '80%',
    wordWrap: 'break-word',
  },
  userMessage: {
    backgroundColor: '#dbeafe',
    marginLeft: 'auto',
    textAlign: 'right',
  },
  botMessage: {
    backgroundColor: '#f3f4f6',
  },
  loadingIndicator: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '8px',
  },
  typingDots: {
    display: 'flex',
  },
  dot: {
    width: '8px',
    height: '8px',
    borderRadius: '50%',
    backgroundColor: '#6b7280',
    margin: '0 2px',
    animation: 'bounce 1.5s infinite',
  },
};

// Chat message bubble component
const MessageBubble = ({ message, isUser }) => {
  const baseStyles = { ...chatStyles.message };
  if (isUser) {
    Object.assign(baseStyles, chatStyles.userMessage);
  } else {
    Object.assign(baseStyles, chatStyles.botMessage);
  }

  return (
    <div style={baseStyles}>
      {message}
    </div>
  );
};

// Loading indicator component
const LoadingIndicator = () => {
  return (
    <div style={chatStyles.loadingIndicator}>
      <div style={chatStyles.typingDots}>
        <div style={{ ...chatStyles.dot, animationDelay: '0s' }}></div>
        <div style={{ ...chatStyles.dot, animationDelay: '0.2s' }}></div>
        <div style={{ ...chatStyles.dot, animationDelay: '0.4s' }}></div>
      </div>
    </div>
  );
};

// Main Chatbot component
const Chatbot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    { id: 1, text: 'Hello! I\'m your AI assistant for the ROS 2 curriculum. How can I help you with robotics today?', isUser: false },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  // Use AuthContext to get auth state
  const authContext = useAuth();
  const isAuthenticated = authContext?.isAuthenticated || false;
  const user = authContext?.user || null;

  // Scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!inputValue.trim() || loading) return;

    // Add user message
    const userMessage = {
      id: Date.now(),
      text: inputValue.trim(),
      isUser: true,
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setLoading(true);

    try {
      // Determine API endpoint based on auth status
      const apiEndpoint = process.env.BACKEND_URL || 'http://localhost:8000';

      // Prepare request payload
      const payload = {
        query: inputValue.trim(),
        session_id: user?.session_id || Date.now().toString(),
        user_id: isAuthenticated ? user?.id : null,  // Only send user_id if authenticated
      };

      // Use the authenticated user's session for requests
      const response = await fetch(`${apiEndpoint}/api/ai/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(isAuthenticated /*&& authContext?.authToken ? {
            'Authorization': `Bearer ${authContext.authToken}`
          } : {}*/),
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();

      // Add bot response
      const botMessage = {
        id: Date.now() + 1,
        text: data?.data?.content || 'I encountered an error processing your request',
        isUser: false,
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage = {
        id: Date.now() + 1,
        text: 'Sorry, I encountered an error. Please try again.',
        isUser: false,
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div style={chatStyles.chatWidget}>
      {/* Chat button */}
      <button
        style={{
          ...chatStyles.chatButton,
          ...(isOpen ? chatStyles.chatButtonOpen : {})
        }}
        onClick={() => setIsOpen(!isOpen)}
      >
        💬
      </button>

      {/* Chat container */}
      {isOpen && (
        <div
          style={{
            ...chatStyles.chatContainer,
            ...(isOpen ? chatStyles.chatContainerOpen : {})
          }}
        >
          <div style={chatStyles.chatHeader}>
            <h3>Curriculum Assistant</h3>
            <button
              onClick={() => setIsOpen(false)}
              style={{
                background: 'none',
                border: 'none',
                color: 'white',
                fontSize: '20px',
                cursor: 'pointer',
              }}
            >
              ×
            </button>
          </div>

          <div style={chatStyles.chatMessages}>
            {messages.map((msg) => (
              <MessageBubble key={msg.id} message={msg.text} isUser={msg.isUser} />
            ))}
            {loading && <LoadingIndicator />}
            <div ref={messagesEndRef} />
          </div>

          <div style={chatStyles.chatInput}>
            <textarea
              style={chatStyles.messageInput}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask about ROS, Gazebo, perception..."
              rows="1"
            />
            <button
              style={chatStyles.sendMessageButton}
              onClick={handleSend}
              disabled={loading || !inputValue.trim()}
            >
              Send
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Chatbot;
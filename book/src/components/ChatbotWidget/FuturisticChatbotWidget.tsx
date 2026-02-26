/**
 * Futuristic Chatbot Widget - Embedded RAG Chatbot Component
 *
 * Features:
 * - Collapsible widget (bottom-right corner)
 * - sessionStorage persistence across page navigation
 * - Text selection integration
 * - Citation links with smooth scroll
 * - Typing indicators
 * - Accessibility (keyboard nav, ARIA labels)
 * - Context-aware suggested questions (T035)
 *
 * Author: Physical AI Platform Team
 * Date: 2026-02-22
 */
import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../../context/AuthContext';
import { AuthModal } from '../Auth/AuthModal';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  citations?: Citation[];
  timestamp: string;
}

interface Citation {
  module: string;
  lesson: string;
  section: string;
  url: string;
}

const BACKEND_URL = 'http://localhost:8000';
const SESSION_STORAGE_KEY = 'chatbot_conversation';
const SESSION_ID_KEY = 'chatbot_session_id';

// Add position prop to allow upper placement
interface FuturisticChatbotWidgetProps {
  position?: 'floating' | 'upper';
}

export default function FuturisticChatbotWidget({ position = 'floating' }: FuturisticChatbotWidgetProps = {}): JSX.Element {
  const { isAuthenticated } = useAuth();
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState('');
  const [error, setError] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Initialize session ID and load conversation history
  useEffect(() => {
    // Get or create session ID
    let sid = null;
    try {
      sid = sessionStorage.getItem(SESSION_ID_KEY);
      if (!sid) {
        sid = (typeof crypto !== 'undefined' && crypto.randomUUID)
          ? crypto.randomUUID()
          : Math.random().toString(36).substring(2) + Date.now().toString(36);
        sessionStorage.setItem(SESSION_ID_KEY, sid);
      }
    } catch (e) {
      console.error('Failed to access sessionStorage:', e);
      sid = 'fallback-session-' + Date.now();
    }
    setSessionId(sid);

    // Load conversation history
    try {
      const savedConversation = sessionStorage.getItem(SESSION_STORAGE_KEY);
      if (savedConversation) {
        setMessages(JSON.parse(savedConversation));
      }
    } catch (e) {
      console.error('Failed to load conversation history:', e);
    }
  }, []);

  // Save conversation to sessionStorage
  useEffect(() => {
    if (messages.length > 0) {
      sessionStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(messages));
    }
  }, [messages]);

  // Auto-scroll to bottom
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  // Handle text selection (FR-052)
  const getSelectedText = (): string => {
    return window.getSelection()?.toString() || '';
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!inputValue.trim() || isLoading) return;

    const query = inputValue.trim();
    const selectionText = getSelectedText();
    setInputValue('');
    setError(null);

    // Add user message
    const userMessage: Message = {
      role: 'user',
      content: query,
      timestamp: new Date().toISOString()
    };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Call backend API
      const response = await fetch(`${BACKEND_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query,
          session_id: sessionId,
          page_context: window.location.href,
          selection_text: selectionText || undefined
        })
      });

      if (response.status === 429) {
        throw new Error('Rate limit exceeded: 20 queries per hour. Try again later.');
      }

      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`);
      }

      const data = await response.json();

      // Add assistant message
      const assistantMessage: Message = {
        role: 'assistant',
        content: data.answer,
        citations: data.citations,
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, assistantMessage]);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to get response');
      console.error('Chat error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  const handleCitationClick = (url: string) => {
    // Navigate to citation URL with smooth scroll
    if (url.includes('#')) {
      const [path, anchor] = url.split('#');
      if (window.location.href.includes(path)) {
        // Same page - just scroll
        const element = document.getElementById(anchor);
        if (element) {
          element.scrollIntoView({ behavior: 'smooth' });
        }
      } else {
        // Different page - navigate
        window.location.href = url;
      }
    }
  };

  if (!isAuthenticated) {
    if (position === 'upper') {
      return (
        <div className="fm-chatbot-upper-container">
          <button
            className="fm-chatbot-icon fm-chatbot-icon--locked"
            onClick={() => setShowAuthModal(true)}
            aria-label="Login to access chatbot"
            title="Login to access the AI assistant"
          >
            <span>💬</span>
            <span className="fm-chatbot-icon-lock">🔒</span>
          </button>
          <AuthModal
            isOpen={showAuthModal}
            onClose={() => setShowAuthModal(false)}
          />
        </div>
      );
    } else {
      return (
        <>
          <button
            className="fm-chatbot-icon fm-chatbot-icon--locked"
            onClick={() => setShowAuthModal(true)}
            aria-label="Login to access chatbot"
            title="Login to access the AI assistant"
          >
            <span>💬</span>
            <span className="fm-chatbot-icon-lock">🔒</span>
          </button>
          <AuthModal
            isOpen={showAuthModal}
            onClose={() => setShowAuthModal(false)}
          />
        </>
      );
    }
  }

  if (!isExpanded) {
    if (position === 'upper') {
      return (
        <div className="fm-chatbot-upper-container">
          <button
            className="fm-chatbot-icon"
            onClick={() => setIsExpanded(true)}
            aria-label="Open chatbot"
            title="Ask questions about the curriculum"
          >
            💬
          </button>
        </div>
      );
    } else {
      return (
        <button
          className="fm-chatbot-icon"
          onClick={() => setIsExpanded(true)}
          aria-label="Open chatbot"
          title="Ask questions about the curriculum"
        >
          💬
        </button>
      );
    }
  }

  // Handle suggested question selection
  const handleSuggestedQuestion = (question: string) => {
    setInputValue(question);
  };

  if (position === 'upper') {
    return (
      <div className="fm-chatbot fm-chatbot--upper" role="dialog" aria-label="Curriculum chatbot">
        <div className="fm-chatbot__header">
          <span>AI Assistant</span>
          <button
            onClick={() => setIsExpanded(false)}
            aria-label="Close chatbot"
            className="fm-chatbot__close-button"
          >
            ✕
          </button>
        </div>

        <div className="fm-chatbot__messages">
          {messages.map((msg, idx) => (
            <div key={idx} className={`fm-chatbot__message fm-chatbot__message--${msg.role}`}>
              <div className="fm-chatbot__message-content">
                {msg.content}
                {msg.role === 'assistant' && (
                  <button
                    onClick={() => copyToClipboard(msg.content)}
                    className="fm-chatbot__copy-button"
                    title="Copy to clipboard"
                    aria-label="Copy message"
                  >
                    📋
                  </button>
                )}
              </div>

              {msg.citations && msg.citations.length > 0 && (
                <div className="fm-chatbot__citations">
                  <strong>Sources:</strong>
                  {msg.citations.map((citation, i) => (
                    <button
                      key={i}
                      onClick={() => handleCitationClick(citation.url)}
                      className="fm-chatbot__citation-link"
                    >
                      Module {citation.module}: {citation.section}
                    </button>
                  ))}
                </div>
              )}
            </div>
          ))}

          {isLoading && (
            <div className="fm-chatbot__message fm-chatbot__message--bot">
              <div className="fm-chatbot__typing-indicator">
                <span></span><span></span><span></span>
              </div>
            </div>
          )}

          {error && (
            <div className="fm-chatbot__error">
              {error}
              <button onClick={() => setError(null)}>Dismiss</button>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={handleSubmit} className="fm-chatbot__input">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Ask about the curriculum..."
            maxLength={500}
            disabled={isLoading}
            aria-label="Chat input"
            className="fm-chatbot__input-field"
          />
          <button
            type="submit"
            disabled={isLoading || !inputValue.trim()}
            aria-label="Send message"
            className="fm-chatbot__send-button"
          >
            ➤
          </button>
        </form>
      </div>
    );
  }

  return (
    <div className="fm-chatbot" role="dialog" aria-label="Curriculum chatbot">
      <div className="fm-chatbot__header">
        <span>AI Assistant</span>
        <button
          onClick={() => setIsExpanded(false)}
          aria-label="Close chatbot"
          className="fm-chatbot__close-button"
        >
          ✕
        </button>
      </div>

      <div className="fm-chatbot__messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`fm-chatbot__message fm-chatbot__message--${msg.role}`}>
            <div className="fm-chatbot__message-content">
              {msg.content}
              {msg.role === 'assistant' && (
                <button
                  onClick={() => copyToClipboard(msg.content)}
                  className="fm-chatbot__copy-button"
                  title="Copy to clipboard"
                  aria-label="Copy message"
                >
                  📋
                </button>
              )}
            </div>

            {msg.citations && msg.citations.length > 0 && (
              <div className="fm-chatbot__citations">
                <strong>Sources:</strong>
                {msg.citations.map((citation, i) => (
                  <button
                    key={i}
                    onClick={() => handleCitationClick(citation.url)}
                    className="fm-chatbot__citation-link"
                  >
                    Module {citation.module}: {citation.section}
                  </button>
                ))}
              </div>
            )}
          </div>
        ))}

        {isLoading && (
          <div className="fm-chatbot__message fm-chatbot__message--bot">
            <div className="fm-chatbot__typing-indicator">
              <span></span><span></span><span></span>
            </div>
          </div>
        )}

        {error && (
          <div className="fm-chatbot__error">
            {error}
            <button onClick={() => setError(null)}>Dismiss</button>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="fm-chatbot__input">
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="Ask about the curriculum..."
          maxLength={500}
          disabled={isLoading}
          aria-label="Chat input"
          className="fm-chatbot__input-field"
        />
        <button
          type="submit"
          disabled={isLoading || !inputValue.trim()}
          aria-label="Send message"
          className="fm-chatbot__send-button"
        >
          ➤
        </button>
      </form>
    </div>
  );
}
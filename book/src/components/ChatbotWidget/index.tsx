/**
 * ChatbotWidget - Embedded RAG Chatbot Component
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
 * Date: 2026-02-09
 */
import React, { useState, useEffect, useRef } from 'react';
import styles from './styles.module.css';
import SuggestedQuestions from './SuggestedQuestions';
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

export default function ChatbotWidget(): JSX.Element {
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
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
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
        document.getElementById(anchor)?.scrollIntoView({ behavior: 'smooth' });
      } else {
        // Different page - navigate
        window.location.href = url;
      }
    }
  };

  if (!isAuthenticated) {
    return (
      <>
        <button
          className={`${styles.chatbotIcon} ${styles.lockedFab}`}
          onClick={() => setShowAuthModal(true)}
          aria-label="Login to access chatbot"
          title="Login to access the AI assistant"
        >
          <span>💬</span>
          <span className={styles.lockOverlay}>🔒</span>
        </button>
        <AuthModal
          isOpen={showAuthModal}
          onClose={() => setShowAuthModal(false)}
        />
      </>
    );
  }

  if (!isExpanded) {
    return (
      <button
        className={styles.chatbotIcon}
        onClick={() => setIsExpanded(true)}
        aria-label="Open chatbot"
        title="Ask questions about the curriculum"
      >
        💬
      </button>
    );
  }

  // Handle suggested question selection
  const handleSuggestedQuestion = (question: string) => {
    setInputValue(question);
  };

  return (
    <div className={styles.chatbotContainer} role="dialog" aria-label="Curriculum chatbot">
      <div className={styles.chatbotHeader}>
        <span>AI Assistant</span>
        <button
          onClick={() => setIsExpanded(false)}
          aria-label="Close chatbot"
          className={styles.closeButton}
        >
          ✕
        </button>
      </div>

      {/* Show suggested questions when no conversation started */}
      {messages.length === 0 && (
        <SuggestedQuestions
          onSelectQuestion={handleSuggestedQuestion}
          disabled={isLoading}
        />
      )}

      <div className={styles.messagesContainer}>
        {messages.map((msg, idx) => (
          <div key={idx} className={`${styles.message} ${styles[msg.role]}`}>
            <div className={styles.messageContent}>
              {msg.content}
              {msg.role === 'assistant' && (
                <button
                  onClick={() => copyToClipboard(msg.content)}
                  className={styles.copyButton}
                  title="Copy to clipboard"
                  aria-label="Copy message"
                >
                  📋
                </button>
              )}
            </div>

            {msg.citations && msg.citations.length > 0 && (
              <div className={styles.citations}>
                <strong>Sources:</strong>
                {msg.citations.map((citation, i) => (
                  <button
                    key={i}
                    onClick={() => handleCitationClick(citation.url)}
                    className={styles.citationLink}
                  >
                    Module {citation.module}: {citation.section}
                  </button>
                ))}
              </div>
            )}
          </div>
        ))}

        {isLoading && (
          <div className={`${styles.message} ${styles.assistant}`}>
            <div className={styles.typingIndicator}>
              <span></span><span></span><span></span>
            </div>
          </div>
        )}

        {error && (
          <div className={styles.error}>
            {error}
            <button onClick={() => setError(null)}>Dismiss</button>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className={styles.inputForm}>
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="Ask about the curriculum..."
          maxLength={500}
          disabled={isLoading}
          aria-label="Chat input"
          className={styles.input}
        />
        <button
          type="submit"
          disabled={isLoading || !inputValue.trim()}
          aria-label="Send message"
          className={styles.sendButton}
        >
          ➤
        </button>
      </form>
    </div>
  );
}

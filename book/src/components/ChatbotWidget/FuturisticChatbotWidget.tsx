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
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';

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

const SESSION_STORAGE_KEY = 'chatbot_conversation';
const SESSION_ID_KEY = 'chatbot_session_id';

// Add position prop to allow upper placement
interface FuturisticChatbotWidgetProps {
  position?: 'floating' | 'upper';
}

export default function FuturisticChatbotWidget({ position = 'floating' }: FuturisticChatbotWidgetProps = {}): JSX.Element {
  const { siteConfig } = useDocusaurusContext();
  const BACKEND_URL = (siteConfig.customFields?.backendUrl as string) || 'https://backend-production-52d2.up.railway.app';
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

  // Handle suggested question selection
  const handleSuggestedQuestion = (question: string) => {
    setInputValue(question);
  };

  // Upper/inline variant (used in navbar etc.)
  if (position === 'upper') {
    if (!isAuthenticated) {
      return (
        <div className="fm-chatbot-upper-container">
          <button
            className="fm-chatbot-icon fm-chatbot-icon--locked"
            onClick={() => setShowAuthModal(true)}
            aria-label="Login to access chatbot"
          >
            <span>💬</span>
            <span className="fm-chatbot-icon-lock">🔒</span>
          </button>
          <AuthModal isOpen={showAuthModal} onClose={() => setShowAuthModal(false)} />
        </div>
      );
    }
    if (!isExpanded) {
      return (
        <div className="fm-chatbot-upper-container">
          <button className="fm-chatbot-icon" onClick={() => setIsExpanded(true)} aria-label="Open chatbot">
            💬
          </button>
        </div>
      );
    }
    return (
      <div className="fm-chatbot fm-chatbot--upper" role="dialog" aria-label="Curriculum chatbot">
        <ChatPanel
          messages={messages}
          isLoading={isLoading}
          error={error}
          inputValue={inputValue}
          messagesEndRef={messagesEndRef}
          onInputChange={(v) => setInputValue(v)}
          onSubmit={handleSubmit}
          onClose={() => setIsExpanded(false)}
          onCopy={copyToClipboard}
          onCitationClick={handleCitationClick}
          onDismissError={() => setError(null)}
        />
      </div>
    );
  }

  // Default floating variant — fixed bottom-right corner
  return (
    <div className="fm-chatbot-float-anchor">
      <AuthModal isOpen={showAuthModal} onClose={() => setShowAuthModal(false)} />

      {!isExpanded ? (
        <button
          className={`fm-chatbot-fab${!isAuthenticated ? ' fm-chatbot-fab--locked' : ''}`}
          onClick={() => isAuthenticated ? setIsExpanded(true) : setShowAuthModal(true)}
          aria-label={isAuthenticated ? 'Open AI assistant' : 'Sign in to use AI assistant'}
          title={isAuthenticated ? 'Ask the AI assistant' : 'Sign in to use AI assistant'}
        >
          {/* Pulse ring */}
          <span className="fm-chatbot-fab__ring" aria-hidden="true" />
          {/* Icon */}
          <span className="fm-chatbot-fab__icon" aria-hidden="true">
            {isAuthenticated ? (
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                <circle cx="9" cy="10" r="1" fill="currentColor" stroke="none"/>
                <circle cx="12" cy="10" r="1" fill="currentColor" stroke="none"/>
                <circle cx="15" cy="10" r="1" fill="currentColor" stroke="none"/>
              </svg>
            ) : (
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
              </svg>
            )}
          </span>
          {/* Label tooltip */}
          <span className="fm-chatbot-fab__label">
            {isAuthenticated ? 'AI Assistant' : 'Sign in to chat'}
          </span>
        </button>
      ) : (
        <div className="fm-chatbot fm-chatbot--float" role="dialog" aria-label="AI Curriculum Assistant">
          <div className="fm-chatbot__header">
            <div className="fm-chatbot__header-left">
              <span className="fm-chatbot__status-dot" aria-hidden="true" />
              <span className="fm-chatbot__title">AI Assistant</span>
            </div>
            <button
              onClick={() => setIsExpanded(false)}
              aria-label="Close chatbot"
              className="fm-chatbot__close-button"
            >
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
                <line x1="1" y1="1" x2="13" y2="13"/>
                <line x1="13" y1="1" x2="1" y2="13"/>
              </svg>
            </button>
          </div>

          <ChatPanel
            messages={messages}
            isLoading={isLoading}
            error={error}
            inputValue={inputValue}
            messagesEndRef={messagesEndRef}
            onInputChange={(v) => setInputValue(v)}
            onSubmit={handleSubmit}
            onClose={() => setIsExpanded(false)}
            onCopy={copyToClipboard}
            onCitationClick={handleCitationClick}
            onDismissError={() => setError(null)}
            hideHeader
          />
        </div>
      )}
    </div>
  );
}

// ── Shared panel sub-component ──────────────────────────────────────────────
interface ChatPanelProps {
  messages: Array<{ role: string; content: string; citations?: Array<{ module: string; lesson: string; section: string; url: string }>; timestamp: string }>;
  isLoading: boolean;
  error: string | null;
  inputValue: string;
  messagesEndRef: React.RefObject<HTMLDivElement>;
  onInputChange: (v: string) => void;
  onSubmit: (e: React.FormEvent) => void;
  onClose: () => void;
  onCopy: (text: string) => void;
  onCitationClick: (url: string) => void;
  onDismissError: () => void;
  hideHeader?: boolean;
}

function ChatPanel({
  messages, isLoading, error, inputValue, messagesEndRef,
  onInputChange, onSubmit, onCopy, onCitationClick, onDismissError, hideHeader
}: ChatPanelProps) {
  return (
    <>
      {!hideHeader && (
        <div className="fm-chatbot__header">
          <span>AI Assistant</span>
        </div>
      )}
      <div className="fm-chatbot__messages">
        {messages.length === 0 && (
          <div className="fm-chatbot__empty">
            <div className="fm-chatbot__empty-icon">✦</div>
            <p>Ask anything about the curriculum</p>
          </div>
        )}
        {messages.map((msg, idx) => (
          <div key={idx} className={`fm-chatbot__message fm-chatbot__message--${msg.role}`}>
            <div className="fm-chatbot__message-content">
              {msg.content}
              {msg.role === 'assistant' && (
                <button
                  onClick={() => onCopy(msg.content)}
                  className="fm-chatbot__copy-button"
                  title="Copy"
                  aria-label="Copy message"
                >
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                    <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
                  </svg>
                </button>
              )}
            </div>
            {msg.citations && msg.citations.length > 0 && (
              <div className="fm-chatbot__citations">
                {msg.citations.map((citation, i) => (
                  <button key={i} onClick={() => onCitationClick(citation.url)} className="fm-chatbot__citation-link">
                    ↗ {citation.section}
                  </button>
                ))}
              </div>
            )}
          </div>
        ))}
        {isLoading && (
          <div className="fm-chatbot__message fm-chatbot__message--assistant">
            <div className="fm-chatbot__typing-indicator">
              <span /><span /><span />
            </div>
          </div>
        )}
        {error && (
          <div className="fm-chatbot__error">
            {error}
            <button onClick={onDismissError} className="fm-chatbot__error-dismiss">✕</button>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <form onSubmit={onSubmit} className="fm-chatbot__input">
        <input
          type="text"
          value={inputValue}
          onChange={(e) => onInputChange(e.target.value)}
          placeholder="Ask about the curriculum…"
          maxLength={500}
          disabled={isLoading}
          aria-label="Chat input"
          className="fm-chatbot__input-field"
        />
        <button
          type="submit"
          disabled={isLoading || !inputValue.trim()}
          aria-label="Send"
          className="fm-chatbot__send-button"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <line x1="22" y1="2" x2="11" y2="13"/>
            <polygon points="22 2 15 22 11 13 2 9 22 2"/>
          </svg>
        </button>
      </form>
    </>
  );
}
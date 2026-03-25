/**
 * ChatKit Widget Component
 *
 * React component that implements the ChatKit UI for the Physical AI platform,
 * integrating with the backend ChatKit endpoints and handling authentication.
 *
 * Features:
 * - Embedded ChatKit-style UI
 * - Authentication integration with AuthContext
 * - Text selection "Ask" feature
 * - Proper error handling and graceful degradation
 *
 * Author: Physical AI Platform Team
 * Date: 2026-02-18
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import BrowserOnly from '@docusaurus/BrowserOnly';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import { useAuth } from '../../context/AuthContext';
import styles from './ChatkitWidget.module.css';

export interface ChatKitProps {
  pageContext?: {
    title: string;
    url: string;
    moduleId?: string;
    sectionTitle?: string;
  };
  initialExpanded?: boolean;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export interface Thread {
  id: string;
  createdAt: Date;
  messages: Message[];
}

const ChatKitWidget: React.FC<ChatKitProps> = ({ pageContext, initialExpanded = false }) => {
  const { siteConfig } = useDocusaurusContext();
  const backendUrl: string = (siteConfig.customFields?.backendUrl as string) || 'http://localhost:8000';
  const [isOpen, setIsOpen] = useState(initialExpanded);
  const [isMinimized, setIsMinimized] = useState(!initialExpanded);
  const [threadId, setThreadId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { isAuthenticated, user, profile } = useAuth(); // Adjust based on your actual AuthContext
  const [selectedText, setSelectedText] = useState<string>('');
  const [isClient, setIsClient] = useState(false);

  // Initialize client-side only
  useEffect(() => {
    setIsClient(true);
  }, []);

  // Scroll to bottom of messages when they change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Check if we have selected text on the page
  const checkSelection = useCallback((e: MouseEvent) => {
    const selection = window.getSelection()?.toString();
    if (selection && selection.trim().length > 0 && selection.trim().length < 500) { // Prevent very long selections
      setSelectedText(selection.trim());
    }
  }, []);

  // Add event listeners for text selection
  useEffect(() => {
    if (!isClient) return;

    document.addEventListener('mouseup', checkSelection);
    return () => {
      document.removeEventListener('mouseup', checkSelection);
    };
  }, [isClient, checkSelection]);

  // Initialize thread on component mount
  useEffect(() => {
    const initThread = async () => {
      if (!isClient) return;

      try {
        // Create or get thread from backend
        const response = await fetch(`${backendUrl}/api/chatkit/threads`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            // Note: Physical AI uses session cookie authentication instead of Bearer token
            ...(isAuthenticated ? {
              'X-Requested-With': 'XMLHttpRequest'  // Common header to identify AJAX requests
            } : {})
          },
          credentials: 'include', // Ensure cookies are sent for session-based auth
          body: JSON.stringify({
            initial_messages: [],
            metadata: {
              page_context: pageContext
            },
            page_context: pageContext || undefined,
            page_url: typeof window !== 'undefined' ? window.location.href : '',
            page_title: typeof window !== 'undefined' ? document.title : ''
          })
        });

        if (!response.ok) {
          const errorData = await response.text();
          throw new Error(`Failed to initialize thread: ${response.statusText} - ${errorData}`);
        }

        const data = await response.json();
        setThreadId(data.id);

        // Load existing messages if any
        await loadThreadMessages(data.id);
      } catch (err) {
        console.error('Error initializing thread:', err);
        setError(err instanceof Error ? err.message : 'Failed to initialize conversation. Using temporary thread.');
        setThreadId(`temp_${Date.now()}`);
      }
    };

    if (!threadId) {
      initThread();
    }
  }, [threadId, pageContext, isClient, isAuthenticated]);

  // Load thread messages
  const loadThreadMessages = async (threadId: string) => {
    try {
      const response = await fetch(`${backendUrl}/api/chatkit/threads/${threadId}/messages`, {
        headers: {
          'Content-Type': 'application/json',
          ...(isAuthenticated ? {
            'X-Requested-With': 'XMLHttpRequest'
          } : {})
        },
        credentials: 'include'
      });

      if (response.ok) {
        const data = await response.json();
        if (data.data && Array.isArray(data.data)) {
          // Convert API messages to internal format
          const convertedMessages: Message[] = data.data
            .filter((msg: any) => msg.role && msg.content && msg.content[0] && msg.content[0].text) // Only valid messages
            .map((msg: any) => ({
              id: msg.id,
              role: msg.role as 'user' | 'assistant',
              content: msg.content[0].text.value,
              timestamp: new Date(msg.created_at * 1000) // Convert from Unix timestamp if present
            }));

          setMessages(convertedMessages);
        }
      }
    } catch (err) {
      console.error('Error loading thread messages:', err);
      // Don't set error here as we don't want to prevent the user from starting a conversation
    }
  };

  // Function to format the page context for the backend
  const getPageContextForBackend = () => {
    if (!isClient) return {};

    return {
      page_title: pageContext?.title || document.title,
      page_url: pageContext?.url || window?.location?.href,
      page_context: {
        module: pageContext?.moduleId,
        section: pageContext?.sectionTitle
      }
    };
  };

  // Handle sending a message
  const handleSendMessage = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();

    if (!inputValue.trim() && !selectedText.trim()) return;

    const userMessage = inputValue.trim() || selectedText.trim();
    if (!userMessage) return;

    setIsLoading(true);
    setError(null);

    // Add user message to UI immediately
    const userMessageObj: Message = {
      id: `temp_${Date.now()}`,
      role: 'user',
      content: userMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessageObj]);
    setInputValue('');
    setSelectedText('');

    try {
      const response = await fetch(`${backendUrl}/api/chatkit/threads/${threadId}/messages`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          // Note: Physical AI uses session cookie authentication instead of Bearer token
          ...(isAuthenticated ? {
            'X-Requested-With': 'XMLHttpRequest'
          } : {})
        },
        credentials: 'include', // Ensure cookies are sent for session-based authentication
        body: JSON.stringify({
          content: userMessage,
          page_context: getPageContextForBackend(),
          selected_text: selectedText, // Include selected text info
          page_url: getPageContextForBackend().page_url,
          page_title: getPageContextForBackend().page_title
        })
      });

      if (!response.ok) {
        const errorData = await response.text();
        throw new Error(`Failed to send message: ${response.statusText} - ${errorData}`);
      }

      // Handle server-sent events streaming
      if (response.body) {
        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        let assistantContent = '';
        let assistantMessage: Message = {
          id: `temp_assistant_${Date.now()}`,
          role: 'assistant',
          content: assistantContent,
          timestamp: new Date()
        };

        try {
          while (true) {
            const { done, value } = await reader.read();

            if (done) {
              break;
            }

            const chunk = decoder.decode(value, { stream: true });
            const lines = chunk.split('\n');

            for (const line of lines) {
              if (line.startsWith('data: ')) {
                try {
                  const data = JSON.parse(line.slice(6)); // Remove 'data: ' prefix

                  if (data.type === 'chunk') {
                    assistantContent += data.content || '';
                    assistantMessage.content = assistantContent;

                    // Update the assistant message in state
                    setMessages(prev => {
                      const last = prev[prev.length - 1];
                      if (last?.role === 'assistant' && last.id === assistantMessage.id) {
                        return [...prev.slice(0, -1), assistantMessage];
                      } else {
                        return [...prev, assistantMessage];
                      }
                    });
                  }
                  else if (data.type === 'done') {
                    // Assistant message is complete
                    break;
                  }
                  else if (data.type === 'error') {
                    throw new Error(data.content || data.data?.message || data.message || 'Error occurred while streaming response');
                  }
                } catch (parseError) {
                  console.error('Error parsing message data:', parseError);
                }
              }
            }
          }
        } finally {
          reader.releaseLock();
        }
      }
    } catch (err) {
      console.error('Error sending message:', err);
      setError(err instanceof Error ? err.message : 'Failed to send message. Please try again.');

      // Remove the temporary user message only if the failure happened during actual sending
      setMessages(prev => prev.slice(0, -1));
    } finally {
      setIsLoading(false);
    }
  };

  // If not on the client, render nothing (component will be handled by BrowserOnly)
  if (!isClient) {
    return (
      <div className={styles.placeholder}>
        Loading chat widget...
      </div>
    );
  }

  // Component to render only on browser
  const ChatKitContent = () => (
    <div className={`${styles.chatkitWidget} ${isMinimized ? styles.minimized : ''}`}>
      {/* Header */}
      <div className={styles.header} onClick={() => setIsMinimized(!isMinimized)}>
        <div className={styles.headerContent}>
          <h3>Physical AI Assistant</h3>
          <div className={styles.headerActions}>
            <button
              className={styles.toggleButton}
              onClick={(e) => { e.stopPropagation(); setIsOpen(!isOpen); }}
              aria-label={isOpen ? "Collapse chat" : "Expand chat"}
            >
              {isOpen ? '−' : '+'}
            </button>
            <button
              className={styles.closeButton}
              onClick={() => setIsMinimized(true)}
              aria-label="Minimize chat"
            >
              ×
            </button>
          </div>
        </div>
      </div>

      {/* Chat Container */}
      {!isMinimized && isOpen && (
        <div className={styles.chatContainer}>
          {/* Messages Area */}
          <div className={styles.messages}>
            {messages.length === 0 && (
              <div className={styles.welcomeMessage}>
                <p>Hello! I'm your Physical AI Assistant.</p>
                <p>Ask me anything about the robotics curriculum, or select text on the page and ask about it.</p>
                {selectedText && (
                  <p className={styles.selectedTextPreview}>
                    <strong>Selected:</strong> {selectedText.substring(0, 100)}{selectedText.length > 100 ? '...' : ''}
                  </p>
                )}
              </div>
            )}

            {messages.map((message) => (
              <div
                key={message.id}
                className={`${styles.message} ${styles[message.role]}`}
              >
                <div className={styles.messageContent}>
                  {message.content}
                </div>
                <div className={styles.messageTimestamp}>
                  {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </div>
              </div>
            ))}
            {isLoading && (
              <div className={`${styles.message} ${styles.assistant}`}>
                <div className={styles.messageContent}>
                  <div className={styles.typingIndicator}>
                    <div></div><div></div><div></div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <form onSubmit={handleSendMessage} className={styles.inputForm}>
            {selectedText && (
              <div className={styles.selectedText}>
                <p><strong>Selected text:</strong> "{selectedText.substring(0, 70)}{selectedText.length > 70 ? '...' : ''}"</p>
              </div>
            )}

            <div className={styles.inputContainer}>
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder={selectedText ? "Ask about selected text..." : "Ask about the curriculum..."}
                disabled={isLoading}
                className={styles.inputField}
              />
              <button
                type="submit"
                disabled={isLoading || (!inputValue.trim() && !selectedText.trim())}
                className={styles.sendButton}
              >
                {isLoading ? 'Sending...' : 'Send'}
              </button>
            </div>

            {error && (
              <div className={styles.errorMessage}>
                {error}
              </div>
            )}
          </form>
        </div>
      )}

      {/* Floating action button when minimized */}
      {isMinimized && !isOpen && (
        <div
          className={styles.minimizedButton}
          onClick={() => { setIsMinimized(false); setIsOpen(true); }}
          title="Open Chat"
        >
          💬
        </div>
      )}
    </div>
  );

  return (
    <BrowserOnly>
      {() => <ChatKitContent />}
    </BrowserOnly>
  );
};

export default ChatKitWidget;
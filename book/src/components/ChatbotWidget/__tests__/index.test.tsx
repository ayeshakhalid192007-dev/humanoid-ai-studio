/**
 * Unit tests for ChatbotWidget component.
 *
 * Tests:
 * - Widget rendering (collapsed/expanded states)
 * - sessionStorage persistence
 * - Message display
 * - Input handling
 *
 * Task: T101
 */
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';

// Mock fetch globally
global.fetch = jest.fn();

// Mock crypto.randomUUID
Object.defineProperty(global, 'crypto', {
  value: {
    randomUUID: () => 'test-uuid-1234-5678-9012'
  }
});

// Mock sessionStorage
const mockSessionStorage = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => { store[key] = value; },
    removeItem: (key: string) => { delete store[key]; },
    clear: () => { store = {}; }
  };
})();
Object.defineProperty(window, 'sessionStorage', { value: mockSessionStorage });

// Import component after mocks
import ChatbotWidget from '../index';

describe('ChatbotWidget', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockSessionStorage.clear();
    (global.fetch as jest.Mock).mockReset();
  });

  describe('Collapsed State', () => {
    it('renders collapsed icon by default', () => {
      render(<ChatbotWidget />);

      const iconButton = screen.getByRole('button', { name: /open chatbot/i });
      expect(iconButton).toBeInTheDocument();
    });

    it('does not render chat container when collapsed', () => {
      render(<ChatbotWidget />);

      expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    });

    it('expands when icon is clicked', () => {
      render(<ChatbotWidget />);

      const iconButton = screen.getByRole('button', { name: /open chatbot/i });
      fireEvent.click(iconButton);

      expect(screen.getByRole('dialog')).toBeInTheDocument();
    });
  });

  describe('Expanded State', () => {
    it('renders header with title', () => {
      render(<ChatbotWidget />);
      fireEvent.click(screen.getByRole('button', { name: /open chatbot/i }));

      expect(screen.getByText('AI Assistant')).toBeInTheDocument();
    });

    it('renders close button', () => {
      render(<ChatbotWidget />);
      fireEvent.click(screen.getByRole('button', { name: /open chatbot/i }));

      expect(screen.getByRole('button', { name: /close chatbot/i })).toBeInTheDocument();
    });

    it('collapses when close button clicked', () => {
      render(<ChatbotWidget />);
      fireEvent.click(screen.getByRole('button', { name: /open chatbot/i }));

      const closeButton = screen.getByRole('button', { name: /close chatbot/i });
      fireEvent.click(closeButton);

      expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    });

    it('renders input field', () => {
      render(<ChatbotWidget />);
      fireEvent.click(screen.getByRole('button', { name: /open chatbot/i }));

      expect(screen.getByRole('textbox', { name: /chat input/i })).toBeInTheDocument();
    });

    it('renders send button', () => {
      render(<ChatbotWidget />);
      fireEvent.click(screen.getByRole('button', { name: /open chatbot/i }));

      expect(screen.getByRole('button', { name: /send message/i })).toBeInTheDocument();
    });
  });

  describe('Session Storage', () => {
    it('generates session ID on mount', () => {
      render(<ChatbotWidget />);

      expect(mockSessionStorage.getItem('chatbot_session_id')).toBe('test-uuid-1234-5678-9012');
    });

    it('reuses existing session ID', () => {
      mockSessionStorage.setItem('chatbot_session_id', 'existing-session-id');

      render(<ChatbotWidget />);

      expect(mockSessionStorage.getItem('chatbot_session_id')).toBe('existing-session-id');
    });

    it('loads conversation history from sessionStorage', () => {
      const savedMessages = JSON.stringify([
        { role: 'user', content: 'Hello', timestamp: '2024-01-01T00:00:00Z' },
        { role: 'assistant', content: 'Hi there!', timestamp: '2024-01-01T00:00:01Z' }
      ]);
      mockSessionStorage.setItem('chatbot_conversation', savedMessages);

      render(<ChatbotWidget />);
      fireEvent.click(screen.getByRole('button', { name: /open chatbot/i }));

      expect(screen.getByText('Hello')).toBeInTheDocument();
      expect(screen.getByText('Hi there!')).toBeInTheDocument();
    });
  });

  describe('Input Handling', () => {
    it('updates input value on change', () => {
      render(<ChatbotWidget />);
      fireEvent.click(screen.getByRole('button', { name: /open chatbot/i }));

      const input = screen.getByRole('textbox', { name: /chat input/i });
      fireEvent.change(input, { target: { value: 'What is ROS?' } });

      expect(input).toHaveValue('What is ROS?');
    });

    it('send button is disabled when input is empty', () => {
      render(<ChatbotWidget />);
      fireEvent.click(screen.getByRole('button', { name: /open chatbot/i }));

      const sendButton = screen.getByRole('button', { name: /send message/i });
      expect(sendButton).toBeDisabled();
    });

    it('send button is enabled when input has text', () => {
      render(<ChatbotWidget />);
      fireEvent.click(screen.getByRole('button', { name: /open chatbot/i }));

      const input = screen.getByRole('textbox', { name: /chat input/i });
      fireEvent.change(input, { target: { value: 'Test query' } });

      const sendButton = screen.getByRole('button', { name: /send message/i });
      expect(sendButton).not.toBeDisabled();
    });

    it('input has maxLength of 500', () => {
      render(<ChatbotWidget />);
      fireEvent.click(screen.getByRole('button', { name: /open chatbot/i }));

      const input = screen.getByRole('textbox', { name: /chat input/i });
      expect(input).toHaveAttribute('maxLength', '500');
    });
  });

  describe('Message Submission', () => {
    beforeEach(() => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => ({
          answer: 'ROS is a robotics middleware.',
          citations: [
            { module: '1', lesson: 'intro', section: 'Overview', url: 'https://example.com#overview' }
          ]
        })
      });
    });

    it('adds user message to conversation on submit', async () => {
      render(<ChatbotWidget />);
      fireEvent.click(screen.getByRole('button', { name: /open chatbot/i }));

      const input = screen.getByRole('textbox', { name: /chat input/i });
      fireEvent.change(input, { target: { value: 'What is ROS?' } });

      const form = input.closest('form')!;
      fireEvent.submit(form);

      await waitFor(() => {
        expect(screen.getByText('What is ROS?')).toBeInTheDocument();
      });
    });

    it('clears input after submission', async () => {
      render(<ChatbotWidget />);
      fireEvent.click(screen.getByRole('button', { name: /open chatbot/i }));

      const input = screen.getByRole('textbox', { name: /chat input/i });
      fireEvent.change(input, { target: { value: 'What is ROS?' } });

      const form = input.closest('form')!;
      fireEvent.submit(form);

      await waitFor(() => {
        expect(input).toHaveValue('');
      });
    });

    it('calls backend API with correct payload', async () => {
      render(<ChatbotWidget />);
      fireEvent.click(screen.getByRole('button', { name: /open chatbot/i }));

      const input = screen.getByRole('textbox', { name: /chat input/i });
      fireEvent.change(input, { target: { value: 'What is ROS?' } });

      const form = input.closest('form')!;
      fireEvent.submit(form);

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          expect.stringContaining('/chat'),
          expect.objectContaining({
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: expect.stringContaining('What is ROS?')
          })
        );
      });
    });

    it('displays assistant response', async () => {
      render(<ChatbotWidget />);
      fireEvent.click(screen.getByRole('button', { name: /open chatbot/i }));

      const input = screen.getByRole('textbox', { name: /chat input/i });
      fireEvent.change(input, { target: { value: 'What is ROS?' } });

      const form = input.closest('form')!;
      fireEvent.submit(form);

      await waitFor(() => {
        expect(screen.getByText('ROS is a robotics middleware.')).toBeInTheDocument();
      });
    });
  });

  describe('Accessibility', () => {
    it('has correct ARIA role for dialog', () => {
      render(<ChatbotWidget />);
      fireEvent.click(screen.getByRole('button', { name: /open chatbot/i }));

      const dialog = screen.getByRole('dialog');
      expect(dialog).toHaveAttribute('aria-label', 'Curriculum chatbot');
    });

    it('input has accessible label', () => {
      render(<ChatbotWidget />);
      fireEvent.click(screen.getByRole('button', { name: /open chatbot/i }));

      expect(screen.getByRole('textbox', { name: /chat input/i })).toBeInTheDocument();
    });

    it('buttons have accessible labels', () => {
      render(<ChatbotWidget />);

      expect(screen.getByRole('button', { name: /open chatbot/i })).toBeInTheDocument();

      fireEvent.click(screen.getByRole('button', { name: /open chatbot/i }));

      expect(screen.getByRole('button', { name: /close chatbot/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /send message/i })).toBeInTheDocument();
    });
  });
});

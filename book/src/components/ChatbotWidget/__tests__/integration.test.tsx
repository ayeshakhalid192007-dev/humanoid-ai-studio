/**
 * Integration tests for ChatbotWidget.
 *
 * Tests the full flow:
 * - Text selection → query submission → response with citations
 *
 * Task: T104
 */
import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import '@testing-library/jest-dom';

// Mock fetch
global.fetch = jest.fn();

// Mock crypto.randomUUID
Object.defineProperty(global, 'crypto', {
  value: {
    randomUUID: () => 'test-session-uuid'
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

// Mock window.getSelection for text selection tests
const mockSelection = {
  toString: () => ''
};
Object.defineProperty(window, 'getSelection', {
  value: () => mockSelection,
  writable: true
});

import ChatbotWidget from '../index';

describe('ChatbotWidget Integration', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockSessionStorage.clear();
    mockSelection.toString = () => '';
    (global.fetch as jest.Mock).mockReset();
  });

  describe('Text Selection Flow', () => {
    const mockResponse = {
      answer: 'Joint limits in URDF define the range of motion using lower and upper attributes.',
      citations: [
        {
          module: '1',
          lesson: 'lesson2-urdf-models',
          section: 'Joint Limits',
          url: 'https://example.com/docs/module1/lesson2#joint-limits'
        }
      ]
    };

    beforeEach(() => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => mockResponse
      });
    });

    it('captures selected text and includes in query', async () => {
      // Simulate text selection
      mockSelection.toString = () => '<limit lower="-1.57" upper="1.57"/>';

      render(<ChatbotWidget />);
      fireEvent.click(screen.getByRole('button', { name: /open chatbot/i }));

      const input = screen.getByRole('textbox', { name: /chat input/i });
      fireEvent.change(input, { target: { value: 'Explain this code' } });

      const form = input.closest('form')!;
      fireEvent.submit(form);

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          expect.any(String),
          expect.objectContaining({
            body: expect.stringContaining('selection_text')
          })
        );
      });

      // Verify the body contains the selection
      const callBody = JSON.parse((global.fetch as jest.Mock).mock.calls[0][1].body);
      expect(callBody.selection_text).toBe('<limit lower="-1.57" upper="1.57"/>');
    });

    it('sends undefined selection_text when nothing selected', async () => {
      mockSelection.toString = () => '';

      render(<ChatbotWidget />);
      fireEvent.click(screen.getByRole('button', { name: /open chatbot/i }));

      const input = screen.getByRole('textbox', { name: /chat input/i });
      fireEvent.change(input, { target: { value: 'What is ROS?' } });

      const form = input.closest('form')!;
      fireEvent.submit(form);

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalled();
      });

      const callBody = JSON.parse((global.fetch as jest.Mock).mock.calls[0][1].body);
      expect(callBody.selection_text).toBeUndefined();
    });
  });

  describe('Full Query-Response Flow', () => {
    const mockResponse = {
      answer: 'ROS 2 (Robot Operating System 2) is a robotics middleware that provides tools and libraries for building robot applications.',
      citations: [
        {
          module: '1',
          lesson: 'lesson1-ros2-basics',
          section: 'Introduction to ROS 2',
          url: 'https://example.com/docs/module1/lesson1#intro'
        },
        {
          module: '1',
          lesson: 'intro',
          section: 'Course Overview',
          url: 'https://example.com/docs/module1/intro#overview'
        }
      ]
    };

    beforeEach(() => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => mockResponse
      });
    });

    it('displays user message immediately', async () => {
      render(<ChatbotWidget />);
      fireEvent.click(screen.getByRole('button', { name: /open chatbot/i }));

      const input = screen.getByRole('textbox', { name: /chat input/i });
      fireEvent.change(input, { target: { value: 'What is ROS 2?' } });

      const form = input.closest('form')!;
      fireEvent.submit(form);

      // User message should appear immediately
      expect(screen.getByText('What is ROS 2?')).toBeInTheDocument();
    });

    it('displays assistant response after API call', async () => {
      render(<ChatbotWidget />);
      fireEvent.click(screen.getByRole('button', { name: /open chatbot/i }));

      const input = screen.getByRole('textbox', { name: /chat input/i });
      fireEvent.change(input, { target: { value: 'What is ROS 2?' } });

      const form = input.closest('form')!;
      fireEvent.submit(form);

      await waitFor(() => {
        expect(screen.getByText(/ROS 2.*is a robotics middleware/)).toBeInTheDocument();
      });
    });

    it('displays citations with response', async () => {
      render(<ChatbotWidget />);
      fireEvent.click(screen.getByRole('button', { name: /open chatbot/i }));

      const input = screen.getByRole('textbox', { name: /chat input/i });
      fireEvent.change(input, { target: { value: 'What is ROS 2?' } });

      const form = input.closest('form')!;
      fireEvent.submit(form);

      await waitFor(() => {
        expect(screen.getByText(/sources/i)).toBeInTheDocument();
      });
    });

    it('persists conversation to sessionStorage', async () => {
      render(<ChatbotWidget />);
      fireEvent.click(screen.getByRole('button', { name: /open chatbot/i }));

      const input = screen.getByRole('textbox', { name: /chat input/i });
      fireEvent.change(input, { target: { value: 'What is ROS 2?' } });

      const form = input.closest('form')!;
      fireEvent.submit(form);

      await waitFor(() => {
        expect(screen.getByText(/ROS 2/)).toBeInTheDocument();
      });

      // Check sessionStorage
      const savedConversation = mockSessionStorage.getItem('chatbot_conversation');
      expect(savedConversation).not.toBeNull();

      const parsed = JSON.parse(savedConversation!);
      expect(parsed.length).toBe(2); // user + assistant
      expect(parsed[0].role).toBe('user');
      expect(parsed[1].role).toBe('assistant');
    });

    it('includes page_context in request', async () => {
      // Mock window.location.href
      Object.defineProperty(window, 'location', {
        value: {
          ...window.location,
          href: 'https://example.com/docs/module1/lesson1'
        },
        writable: true
      });

      render(<ChatbotWidget />);
      fireEvent.click(screen.getByRole('button', { name: /open chatbot/i }));

      const input = screen.getByRole('textbox', { name: /chat input/i });
      fireEvent.change(input, { target: { value: 'Explain this page' } });

      const form = input.closest('form')!;
      fireEvent.submit(form);

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalled();
      });

      const callBody = JSON.parse((global.fetch as jest.Mock).mock.calls[0][1].body);
      expect(callBody.page_context).toContain('module1');
    });
  });

  describe('Error Handling Flow', () => {
    it('displays error message on API failure', async () => {
      (global.fetch as jest.Mock).mockRejectedValue(new Error('Network error'));

      render(<ChatbotWidget />);
      fireEvent.click(screen.getByRole('button', { name: /open chatbot/i }));

      const input = screen.getByRole('textbox', { name: /chat input/i });
      fireEvent.change(input, { target: { value: 'What is ROS?' } });

      const form = input.closest('form')!;
      fireEvent.submit(form);

      await waitFor(() => {
        expect(screen.getByText(/failed to get response/i)).toBeInTheDocument();
      });
    });

    it('displays rate limit message on 429', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: false,
        status: 429,
        statusText: 'Too Many Requests'
      });

      render(<ChatbotWidget />);
      fireEvent.click(screen.getByRole('button', { name: /open chatbot/i }));

      const input = screen.getByRole('textbox', { name: /chat input/i });
      fireEvent.change(input, { target: { value: 'What is ROS?' } });

      const form = input.closest('form')!;
      fireEvent.submit(form);

      await waitFor(() => {
        expect(screen.getByText(/rate limit exceeded/i)).toBeInTheDocument();
      });
    });

    it('allows dismissing error message', async () => {
      (global.fetch as jest.Mock).mockRejectedValue(new Error('Network error'));

      render(<ChatbotWidget />);
      fireEvent.click(screen.getByRole('button', { name: /open chatbot/i }));

      const input = screen.getByRole('textbox', { name: /chat input/i });
      fireEvent.change(input, { target: { value: 'What is ROS?' } });

      const form = input.closest('form')!;
      fireEvent.submit(form);

      await waitFor(() => {
        expect(screen.getByText(/failed/i)).toBeInTheDocument();
      });

      const dismissButton = screen.getByText(/dismiss/i);
      fireEvent.click(dismissButton);

      expect(screen.queryByText(/failed/i)).not.toBeInTheDocument();
    });
  });

  describe('Multiple Queries Flow', () => {
    it('maintains conversation history across queries', async () => {
      const responses = [
        { answer: 'First answer', citations: [] },
        { answer: 'Second answer', citations: [] }
      ];

      let callCount = 0;
      (global.fetch as jest.Mock).mockImplementation(() => {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: async () => responses[callCount++]
        });
      });

      render(<ChatbotWidget />);
      fireEvent.click(screen.getByRole('button', { name: /open chatbot/i }));

      // First query
      const input = screen.getByRole('textbox', { name: /chat input/i });
      fireEvent.change(input, { target: { value: 'First question' } });
      fireEvent.submit(input.closest('form')!);

      await waitFor(() => {
        expect(screen.getByText('First answer')).toBeInTheDocument();
      });

      // Second query
      fireEvent.change(input, { target: { value: 'Second question' } });
      fireEvent.submit(input.closest('form')!);

      await waitFor(() => {
        expect(screen.getByText('Second answer')).toBeInTheDocument();
      });

      // Both messages should be visible
      expect(screen.getByText('First question')).toBeInTheDocument();
      expect(screen.getByText('First answer')).toBeInTheDocument();
      expect(screen.getByText('Second question')).toBeInTheDocument();
      expect(screen.getByText('Second answer')).toBeInTheDocument();
    });
  });

  describe('Suggested Questions Integration', () => {
    beforeEach(() => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => ({
          answer: 'Test answer',
          citations: []
        })
      });

      // Set pathname for module context
      Object.defineProperty(window, 'location', {
        value: {
          pathname: '/',
          href: 'http://localhost/'
        },
        writable: true,
        configurable: true
      });
    });

    it('shows suggested questions when conversation empty', () => {
      render(<ChatbotWidget />);
      fireEvent.click(screen.getByRole('button', { name: /open chatbot/i }));

      expect(screen.getByText(/try asking/i)).toBeInTheDocument();
    });

    it('hides suggested questions after first message', async () => {
      render(<ChatbotWidget />);
      fireEvent.click(screen.getByRole('button', { name: /open chatbot/i }));

      // Verify suggested questions are shown
      expect(screen.getByText(/try asking/i)).toBeInTheDocument();

      // Submit a message
      const input = screen.getByRole('textbox', { name: /chat input/i });
      fireEvent.change(input, { target: { value: 'What is ROS?' } });
      fireEvent.submit(input.closest('form')!);

      await waitFor(() => {
        expect(screen.getByText('What is ROS?')).toBeInTheDocument();
      });

      // Suggested questions should be hidden
      expect(screen.queryByText(/try asking/i)).not.toBeInTheDocument();
    });

    it('clicking suggested question populates input', () => {
      render(<ChatbotWidget />);
      fireEvent.click(screen.getByRole('button', { name: /open chatbot/i }));

      // Find and click a suggested question
      const suggestedButtons = screen.getAllByRole('button').filter(
        btn => btn.getAttribute('aria-label')?.startsWith('Ask:')
      );

      if (suggestedButtons.length > 0) {
        const questionText = suggestedButtons[0].textContent;
        fireEvent.click(suggestedButtons[0]);

        const input = screen.getByRole('textbox', { name: /chat input/i });
        expect(input).toHaveValue(questionText);
      }
    });
  });
});

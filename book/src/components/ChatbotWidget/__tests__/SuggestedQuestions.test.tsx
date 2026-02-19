/**
 * Unit tests for SuggestedQuestions component.
 *
 * Tests:
 * - Question rendering
 * - Context-aware question selection
 * - Click handling
 * - URL parsing
 *
 * Task: T101 (part of widget tests)
 */
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';

import SuggestedQuestions, {
  getPageContext,
  getSuggestedQuestions,
  QUESTIONS_BY_MODULE,
  DEFAULT_QUESTIONS
} from '../SuggestedQuestions';

describe('SuggestedQuestions', () => {
  describe('Component Rendering', () => {
    it('renders suggested questions section', () => {
      const mockHandler = jest.fn();
      render(<SuggestedQuestions onSelectQuestion={mockHandler} />);

      expect(screen.getByRole('region', { name: /suggested questions/i })).toBeInTheDocument();
    });

    it('renders "Try asking" header', () => {
      const mockHandler = jest.fn();
      render(<SuggestedQuestions onSelectQuestion={mockHandler} />);

      expect(screen.getByText(/try asking/i)).toBeInTheDocument();
    });

    it('renders question buttons', () => {
      const mockHandler = jest.fn();
      render(<SuggestedQuestions onSelectQuestion={mockHandler} />);

      const buttons = screen.getAllByRole('button');
      expect(buttons.length).toBeGreaterThan(0);
    });

    it('displays default questions when no module context', () => {
      const mockHandler = jest.fn();

      // Mock window.location for root page
      Object.defineProperty(window, 'location', {
        value: { pathname: '/' },
        writable: true
      });

      render(<SuggestedQuestions onSelectQuestion={mockHandler} />);

      // Should show at least one default question
      expect(screen.getByText(DEFAULT_QUESTIONS[0])).toBeInTheDocument();
    });
  });

  describe('Click Handling', () => {
    it('calls onSelectQuestion when question clicked', () => {
      const mockHandler = jest.fn();
      render(<SuggestedQuestions onSelectQuestion={mockHandler} />);

      const firstButton = screen.getAllByRole('button')[0];
      fireEvent.click(firstButton);

      expect(mockHandler).toHaveBeenCalledTimes(1);
      expect(mockHandler).toHaveBeenCalledWith(expect.any(String));
    });

    it('passes question text to handler', () => {
      const mockHandler = jest.fn();

      Object.defineProperty(window, 'location', {
        value: { pathname: '/' },
        writable: true
      });

      render(<SuggestedQuestions onSelectQuestion={mockHandler} />);

      const button = screen.getByText(DEFAULT_QUESTIONS[0]);
      fireEvent.click(button);

      expect(mockHandler).toHaveBeenCalledWith(DEFAULT_QUESTIONS[0]);
    });

    it('disables buttons when disabled prop is true', () => {
      const mockHandler = jest.fn();
      render(<SuggestedQuestions onSelectQuestion={mockHandler} disabled={true} />);

      const buttons = screen.getAllByRole('button');
      buttons.forEach(button => {
        expect(button).toBeDisabled();
      });
    });

    it('does not call handler when disabled', () => {
      const mockHandler = jest.fn();
      render(<SuggestedQuestions onSelectQuestion={mockHandler} disabled={true} />);

      const firstButton = screen.getAllByRole('button')[0];
      fireEvent.click(firstButton);

      expect(mockHandler).not.toHaveBeenCalled();
    });
  });

  describe('Accessibility', () => {
    it('has accessible region label', () => {
      const mockHandler = jest.fn();
      render(<SuggestedQuestions onSelectQuestion={mockHandler} />);

      expect(screen.getByRole('region')).toHaveAttribute('aria-label', 'Suggested questions');
    });

    it('buttons have aria-label with question text', () => {
      const mockHandler = jest.fn();

      Object.defineProperty(window, 'location', {
        value: { pathname: '/' },
        writable: true
      });

      render(<SuggestedQuestions onSelectQuestion={mockHandler} />);

      const button = screen.getByText(DEFAULT_QUESTIONS[0]);
      expect(button).toHaveAttribute('aria-label', `Ask: ${DEFAULT_QUESTIONS[0]}`);
    });
  });
});

describe('getPageContext', () => {
  beforeEach(() => {
    // Reset location before each test
    Object.defineProperty(window, 'location', {
      value: { pathname: '/' },
      writable: true,
      configurable: true
    });
  });

  it('returns null for root page', () => {
    window.location.pathname = '/';
    const context = getPageContext();

    expect(context.module).toBeNull();
    expect(context.lesson).toBeNull();
  });

  it('extracts module1 from URL', () => {
    window.location.pathname = '/docs/module1/intro';
    const context = getPageContext();

    expect(context.module).toBe('module1');
  });

  it('extracts module2 from URL', () => {
    window.location.pathname = '/docs/module2/lesson1-gazebo-setup';
    const context = getPageContext();

    expect(context.module).toBe('module2');
  });

  it('extracts lesson from URL', () => {
    window.location.pathname = '/docs/module1/lesson2-nodes-topics';
    const context = getPageContext();

    expect(context.lesson).toBe('nodes-topics');
  });

  it('extracts capstone module', () => {
    window.location.pathname = '/docs/capstone/intro';
    const context = getPageContext();

    expect(context.module).toBe('capstone');
  });

  it('detects exercises page', () => {
    window.location.pathname = '/docs/module1/exercises';
    const context = getPageContext();

    expect(context.module).toBe('module1');
    expect(context.lesson).toBe('exercises');
  });

  it('detects intro page', () => {
    window.location.pathname = '/docs/module3/intro';
    const context = getPageContext();

    expect(context.module).toBe('module3');
    expect(context.lesson).toBe('intro');
  });
});

describe('getSuggestedQuestions', () => {
  it('returns default questions for null module', () => {
    const questions = getSuggestedQuestions(null, null);
    expect(questions).toEqual(DEFAULT_QUESTIONS);
  });

  it('returns default questions for unknown module', () => {
    const questions = getSuggestedQuestions('module99', null);
    expect(questions).toEqual(DEFAULT_QUESTIONS);
  });

  it('returns module1 general questions', () => {
    const questions = getSuggestedQuestions('module1', null);
    expect(questions).toEqual(QUESTIONS_BY_MODULE.module1.general);
  });

  it('returns lesson-specific questions when available', () => {
    const questions = getSuggestedQuestions('module1', 'ros2-basics');
    expect(questions).toEqual(QUESTIONS_BY_MODULE.module1.lessons['ros2-basics']);
  });

  it('falls back to general when lesson not found', () => {
    const questions = getSuggestedQuestions('module1', 'unknown-lesson');
    expect(questions).toEqual(QUESTIONS_BY_MODULE.module1.general);
  });

  it('returns module2 questions for gazebo-setup', () => {
    const questions = getSuggestedQuestions('module2', 'gazebo-setup');
    expect(questions).toEqual(QUESTIONS_BY_MODULE.module2.lessons['gazebo-setup']);
  });

  it('returns capstone questions', () => {
    const questions = getSuggestedQuestions('capstone', null);
    expect(questions).toEqual(QUESTIONS_BY_MODULE.capstone.general);
  });
});

describe('QUESTIONS_BY_MODULE', () => {
  it('has questions for all 4 modules', () => {
    expect(QUESTIONS_BY_MODULE).toHaveProperty('module1');
    expect(QUESTIONS_BY_MODULE).toHaveProperty('module2');
    expect(QUESTIONS_BY_MODULE).toHaveProperty('module3');
    expect(QUESTIONS_BY_MODULE).toHaveProperty('module4');
  });

  it('has capstone questions', () => {
    expect(QUESTIONS_BY_MODULE).toHaveProperty('capstone');
  });

  it('each module has general questions', () => {
    Object.values(QUESTIONS_BY_MODULE).forEach(module => {
      expect(module.general).toBeDefined();
      expect(module.general.length).toBeGreaterThan(0);
    });
  });

  it('each module has lesson-specific questions', () => {
    Object.values(QUESTIONS_BY_MODULE).forEach(module => {
      expect(module.lessons).toBeDefined();
      expect(Object.keys(module.lessons).length).toBeGreaterThan(0);
    });
  });

  it('all questions are non-empty strings', () => {
    Object.values(QUESTIONS_BY_MODULE).forEach(module => {
      module.general.forEach(q => {
        expect(typeof q).toBe('string');
        expect(q.length).toBeGreaterThan(10);
      });

      Object.values(module.lessons).forEach(lessonQuestions => {
        lessonQuestions.forEach(q => {
          expect(typeof q).toBe('string');
          expect(q.length).toBeGreaterThan(10);
        });
      });
    });
  });
});

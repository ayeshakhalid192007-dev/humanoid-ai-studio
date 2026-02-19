import React from 'react';
import styles from './Logo.module.css';

interface LogoProps {
  className?: string;
  size?: number;
}

export default function Logo({ className, size = 32 }: LogoProps): JSX.Element {
  return (
    <svg
      className={`${styles.logo} ${className || ''}`}
      width={size}
      height={size}
      viewBox="0 0 64 64"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-label="Physical AI Platform Logo"
    >
      {/* Robot Head Outline */}
      <rect
        x="12"
        y="20"
        width="40"
        height="36"
        rx="6"
        className={styles.head}
        strokeWidth="2.5"
      />

      {/* Antenna */}
      <line
        x1="32"
        y1="20"
        x2="32"
        y2="8"
        className={styles.antenna}
        strokeWidth="2.5"
        strokeLinecap="round"
      />

      {/* Antenna Signal Dot */}
      <circle
        cx="32"
        cy="5"
        r="3"
        className={styles.signalDot}
      />

      {/* Left Eye */}
      <circle
        cx="24"
        cy="34"
        r="5"
        className={styles.eye}
      />

      {/* Right Eye */}
      <circle
        cx="40"
        cy="34"
        r="5"
        className={styles.eye}
      />

      {/* Mouth / Speaker Grille */}
      <rect
        x="22"
        y="44"
        width="20"
        height="6"
        rx="2"
        className={styles.mouth}
      />

      {/* Neural Network Lines - Left */}
      <path
        d="M8 28 L12 32"
        className={styles.neural}
        strokeWidth="1.5"
        strokeLinecap="round"
      />
      <path
        d="M8 38 L12 38"
        className={styles.neural}
        strokeWidth="1.5"
        strokeLinecap="round"
      />
      <path
        d="M8 48 L12 44"
        className={styles.neural}
        strokeWidth="1.5"
        strokeLinecap="round"
      />

      {/* Neural Network Lines - Right */}
      <path
        d="M56 28 L52 32"
        className={styles.neural}
        strokeWidth="1.5"
        strokeLinecap="round"
      />
      <path
        d="M56 38 L52 38"
        className={styles.neural}
        strokeWidth="1.5"
        strokeLinecap="round"
      />
      <path
        d="M56 48 L52 44"
        className={styles.neural}
        strokeWidth="1.5"
        strokeLinecap="round"
      />

      {/* Neural Nodes */}
      <circle cx="6" cy="28" r="2" className={styles.node} />
      <circle cx="6" cy="38" r="2" className={styles.node} />
      <circle cx="6" cy="48" r="2" className={styles.node} />
      <circle cx="58" cy="28" r="2" className={styles.node} />
      <circle cx="58" cy="38" r="2" className={styles.node} />
      <circle cx="58" cy="48" r="2" className={styles.node} />
    </svg>
  );
}

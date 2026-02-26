/**
 * ContentSkeleton Component
 *
 * Displays skeleton loaders while content is being fetched.
 * Provides visual feedback during personalization and translation.
 */

import React from 'react';
import styles from './ContentSkeleton.module.css';

interface ContentSkeletonProps {
  type?: 'full' | 'partial';
}

export default function ContentSkeleton({ type = 'full' }: ContentSkeletonProps) {
  return (
    <div className={styles.skeleton}>
      {/* Title skeleton */}
      <div className={styles.skeletonTitle} />

      {/* Paragraph skeletons */}
      <div className={styles.skeletonParagraph}>
        <div className={styles.skeletonLine} />
        <div className={styles.skeletonLine} />
        <div className={styles.skeletonLine} style={{ width: '80%' }} />
      </div>

      {type === 'full' && (
        <>
          {/* Heading skeleton */}
          <div className={styles.skeletonHeading} />

          {/* More paragraphs */}
          <div className={styles.skeletonParagraph}>
            <div className={styles.skeletonLine} />
            <div className={styles.skeletonLine} />
            <div className={styles.skeletonLine} style={{ width: '90%' }} />
          </div>

          {/* Code block skeleton */}
          <div className={styles.skeletonCodeBlock}>
            <div className={styles.skeletonCodeLine} style={{ width: '60%' }} />
            <div className={styles.skeletonCodeLine} style={{ width: '80%' }} />
            <div className={styles.skeletonCodeLine} style={{ width: '70%' }} />
            <div className={styles.skeletonCodeLine} style={{ width: '50%' }} />
          </div>

          {/* Another heading */}
          <div className={styles.skeletonHeading} />

          {/* Final paragraph */}
          <div className={styles.skeletonParagraph}>
            <div className={styles.skeletonLine} />
            <div className={styles.skeletonLine} />
            <div className={styles.skeletonLine} style={{ width: '75%' }} />
          </div>
        </>
      )}
    </div>
  );
}

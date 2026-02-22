import React from 'react';
import Layout from '@theme/Layout';
import styles from './testimonials.module.css';

const testimonials = [
  {
    name: 'Sarah Chen',
    role: 'Robotics Engineer at Boston Dynamics',
    initials: 'SC',
    quote:
      'The Predict-Execute-Reflect methodology completely changed how I approach learning. After completing the curriculum, I landed my dream job working on humanoid locomotion. The hands-on Gazebo projects were invaluable.',
  },
  {
    name: 'Marcus Johnson',
    role: 'AI Research Scientist',
    initials: 'MJ',
    quote:
      'As someone transitioning from pure ML to robotics, this platform bridged the gap perfectly. The VLA module showed me how to connect large language models to real-world robot actions safely and effectively.',
  },
  {
    name: 'Elena Rodriguez',
    role: 'Graduate Student, Stanford',
    initials: 'ER',
    quote:
      'The AI assistant is a game-changer for learning. Being able to highlight confusing concepts and get instant explanations with citations saved me countless hours. Worth every minute spent on this curriculum.',
  },
];

function TestimonialCard({
  name,
  role,
  initials,
  quote,
}: {
  name: string;
  role: string;
  initials: string;
  quote: string;
}) {
  return (
    <div className={styles.testimonialCard}>
      <blockquote className={styles.quote}>"{quote}"</blockquote>
      <div className={styles.author}>
        <div className={styles.avatar}>{initials}</div>
        <div className={styles.authorInfo}>
          <span className={styles.name}>{name}</span>
          <span className={styles.role}>{role}</span>
        </div>
      </div>
    </div>
  );
}

export default function Testimonials(): JSX.Element {
  return (
    <Layout title="Testimonials" description="What learners say about the Physical AI Platform">
      <header className={styles.hero}>
        <div className={styles.heroInner}>
          <h1>What Learners Say</h1>
          <p className={styles.heroSubtitle}>
            Join hundreds of students and professionals advancing their robotics careers.
          </p>
        </div>
      </header>
      <main className={styles.main}>
        <section className={styles.testimonialsSection}>
          <div className={styles.testimonialsGrid}>
            {testimonials.map((testimonial, idx) => (
              <TestimonialCard key={idx} {...testimonial} />
            ))}
          </div>
        </section>
        <section className={styles.ctaSection}>
          <h2>Ready to Unlock Bonus Features?</h2>
          <p>Create an account to access personalized content, advanced AI features, and exclusive learning tools.</p>
          <a href="/auth/signup" className={styles.ctaButton}>
            Sign Up for Free
          </a>
        </section>
      </main>
    </Layout>
  );
}

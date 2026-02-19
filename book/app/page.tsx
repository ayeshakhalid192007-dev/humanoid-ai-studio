import { HeroSection } from '@/components/homepage/HeroSection';
import { AboutSection } from '@/components/homepage/AboutSection';
import { LearningPillars } from '@/components/homepage/LearningPillars';
import { FeaturesOverview } from '@/components/homepage/FeaturesOverview';
import { Footer } from '@/components/homepage/Footer';

export default function HomePage() {
  return (
    <div className="min-h-screen bg-[#0f0f14]">
      <HeroSection />
      <AboutSection />
      <LearningPillars />
      <FeaturesOverview />
      <Footer />
    </div>
  );
}
# Data Model: Modern Frontend Homepage

## Core Entities

### 1. Homepage (Root Entity)
- **Fields**:
  - title: string (e.g., "Master Physical AI & Humanoid Robotics")
  - tagline: string (e.g., "Learn ROS 2, simulation, perception, and voice-to-action pipelines")
  - description: string (main description content)
  - theme: HomepageTheme (dark/light mode preference)

**Validation Rules**:
- title must be 20-100 characters
- tagline must be 10-50 words

**Relationships**:
- Contains HeroSection
- Contains AboutSection
- Contains LearningPillarsGrid
- Contains FeaturesOverview
- Contains FooterSection

## 2. HomepageTheme
- **Fields**:
  - primaryColor: Color
  - gradient: Gradient
  - fontFamily: string
  - isDarkMode: boolean (default: true)

## 3. HeroSection
- **Fields**:
  - title: string
  - subtitle: string
  - ctaButtons: CTAButton[]
  - backgroundImage: BackgroundStyle
  - animation: AnimationConfig

**Validation Rules**:
- title max length: 60 characters
- subtitle max length: 150 characters
- Requires at least 1 ctaButton and maximum 2

**Relationships**:
- Belongs to Homepage (1-to-1)

## 4. CTAButton
- **Fields**:
  - label: string
  - href: string | null
  - onClick: function | null
  - variant: 'primary' | 'secondary' | 'ghost'
  - animation: AnimationConfig
  - glowEffect: boolean (default: true)

**Validation Rules**:
- label max length: 25 characters
- Must have either href or onClick defined

## 5. BackgroundStyle
- **Fields**:
  - type: 'gradient' | 'image' | 'glass'
  - gradientColors: string[] | null
  - imageSrc: string | null
  - opacity: number (default: 1.0)
  - animated: boolean (default: true)

## 6. AnimationConfig
- **Fields**:
  - type: 'fadeIn' | 'slideIn' | 'stagger' | 'spring'
  - duration: number
  - delay: number (default: 0)
  - springConfig: SpringConfig | null

## 7. SpringConfig
- **Fields**:
  - stiffness: number (default: 300)
  - damping: number (default: 25)
  - mass: number (default: 1)

## 8. AboutSection
- **Fields**:
  - title: string
  - content: string
  - containerStyle: ContainerStyle
  - animation: AnimationConfig

**Validation Rules**:
- title max length: 50 characters
- content max length: 1000 characters

**Relationships**:
- Belongs to Homepage (1-to-1)

## 9. ContainerStyle
- **Fields**:
  - backgroundType: 'glass' | 'solid' | 'transparent'
  - backdropBlur: string (default: 'blur-md')
  - padding: string (default: 'p-8')
  - rounded: string (default: 'rounded-2xl')
  - boxShadow: string (default: 'shadow-xl')

## 10. LearningPillarsGrid
- **Fields**:
  - title: string
  - pillars: LearningPillar[]
  - gridColumnConfig: { desktop: number, tablet: number, mobile: number }
  - layoutType: 'grid' | 'carousel'
  - staggerConfig: StaggerConfig

**Validation Rules**:
- Must have 6 LearningPillar items as specified in feature spec
- gridColumnConfig values: 1-3 for mobile, 2-6 for desktop

**Relationships**:
- Contains multiple LearningPillar (1-to-many)

## 11. LearningPillar
- **Fields**:
  - id: string (auto-generated)
  - title: string
  - description: string
  - icon: string
  - style: PillarStyle
  - animation: AnimationConfig

**Validation Rules**:
- title max length: 30 characters
- description max length: 100 characters

### Known Learning Pillar Titles:
- "AI Tutor"
- "Interactive Simulations"
- "Structured Curriculum"
- "Personalized Chapters"
- "Urdu Translation"
- "Intelligent RAG Chatbot"

## 12. PillarStyle
- **Fields**:
  - backgroundColor: string (default: 'bg-white/10')
  - backdropBlur: string (default: 'blur-sm')
  - borderRadius: string (default: 'rounded-2xl')
  - boxShadow: string (default: 'shadow-lg')
  - hoverEffects: HoverStyle

## 13. HoverStyle
- **Fields**:
  - translateY: string (default: '-translate-y-1')
  - scale: number (default: 1.03)
  - glowingBorder: boolean (default: true)
  - boxShadow: string (default: 'shadow-2xl')

## 14. FeaturesOverview
- **Fields**:
  - title: string
  - features: FeatureItem[]
  - layoutType: 'grid' | 'list'
  - scrollAnimation: boolean (default: true)
  - staggerConfig: StaggerConfig

**Validation Rules**:
- Must have minimum 5 FeatureItem items
- title max length: 60 characters

**Relationships**:
- Contains multiple FeatureItem (1-to-many)

## 15. FeatureItem
- **Fields**:
  - id: string (auto-generated)
  - title: string
  - description: string
  - icon: string | null

**Validation Rules**:
- title max length: 40 characters
- description max length: 150 characters

### Known Feature Titles:
- "ROS 2 Fundamentals"
- "Simulation Environments"
- "NVIDIA Isaac Integration"
- "Vision-Language-Action Systems"
- "Reinforcement Learning"
- "Sim-to-Real Transfer"
- "AI Orchestrator Architecture"
- "Reusable Agent Skills"
- "Modular AI System Design"
- "Authentication & Personalization"
- "Observability & Logging"

## 16. FooterSection
- **Fields**:
  - projectName: string
  - tagline: string
  - externalLinks: Link[]
  - backgroundColor: string (default: 'bg-gray-900')

**Validation Rules**:
- projectName max length: 50 characters
- tagline max length: 60 characters

**Relationships**:
- Contains multiple Link (1-to-many)

## 17. Link
- **Fields**:
  - text: string
  - url: string
  - icon: string | null
  - target: '_blank' | '_self' (default: '_blank')

**Validation Rules**:
- text max length: 30 characters
- url must be valid URL format

## 18. StaggerConfig
- **Fields**:
  - delay: number (default: 0.1)
  - damping: number (default: 15)
  - stiffness: number (default: 100)

## State Transitions

### FeatureCard Hover State
1. Normal State → Hover State (when mouse enters)
2. Hover State → Active State (when clicked)
3. Active State → Normal State (when mouse leaves)

### Page Scroll States
1. Unobserved → In Viewport (when component enters viewport)
2. In Viewport → Animate (when animation triggers)
3. Animate → Complete (when animation finishes)

## Validation Rules Summary

1. **Length Validations**:
   - Text fields have proper max lengths
   - Arrays have required min/max counts

2. **Required Field Validations**:
   - All entities have required fields defined
   - Links have valid URL format

3. **Business Logic Validations**:
   - LearningPillarsGrid has exactly 6 pillars
   - FeaturesOverview has 11 features as specified
   - CTAButton has either href or onClick defined
   - Animation configs have valid values
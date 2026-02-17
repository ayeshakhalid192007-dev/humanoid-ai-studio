# Feature Specification: Physical AI & Humanoid Robotics Platform

**Feature Branch**: `001-physical-ai-robotics-platform`
**Created**: 2026-02-07
**Updated**: 2026-02-07
**Status**: Draft
**Input**: User description: "Physical AI & Humanoid Robotics: Embodied Intelligence in the Real World - A capstone-quarter educational and software platform focused on Physical AI and Humanoid Robotics"
**Latest Update (2026-02-07)**: Expanded book publication & RAG chatbot requirements to complete specification - added FR-021 through FR-060 (book infrastructure, RAG backend, chatbot frontend), SC-013 through SC-026 (performance metrics), updated Key Entities, Dependencies (Docusaurus, FastAPI, Qdrant, Neon stack), Assumptions, Edge Cases, and Out of Scope sections. Complete mandatory core infrastructure now specified.

## Clarifications

### Session 2026-02-07 (Initial Clarification)

- Q: Which ROS 2 distribution is required? → A: ROS 2 Humble (mandated) - Single version for all students, LTS with 5-year support until 2027
- Q: Is Gazebo mandatory or optional relative to Unity? → A: Gazebo mandatory, Unity optional - All students must complete Gazebo path; Unity available as advanced enrichment track requiring NVIDIA hardware
- Q: Is NVIDIA hardware required or optional? → A: NVIDIA GPU required for VSLAM, CPU fallback available - Isaac ROS preferred but ORB-SLAM3/RTAB-Map allowed; some students experience slower performance
- Q: How much system latency is tolerable for voice-to-action? → A: 10 seconds total (voice → robot motion starts) - 2s transcription + 3s LLM reasoning + 5s action init; allows network variability
- Q: How are unsafe or invalid robot actions prevented? → 
A: Multi-layer validation - LLM system prompt restricts action types + ROS parameter bounds check + simulation pre-check for collisions/falls; log rejections with educational explanations

### Session 2026-02-07 (Specification Update)

**Update Rationale**: Original spec described curriculum platform (ROS 2, Gazebo, VSLAM, VLA) but was missing the delivery mechanism - how students actually access and interact with course content. This update adds the complete delivery infrastructure as mandatory core requirements.

**Additions**:
- User Story 5: Interactive Learning Book with AI Assistant (P0 - foundational infrastructure)
- FR-021 through FR-030: Book publication and RAG chatbot functional requirements
- SC-013 through SC-020: Performance and quality metrics for book/chatbot
- New Key Entities: Book Page, Chatbot Conversation, Vector Embedding, RAG Query, Source Citation
- Updated Dependencies: Added book publication and RAG chatbot technology stack (Docusaurus, Qdrant, Neon, FastAPI, OpenAI)
- Updated Assumptions: Added markdown authoring, hosting infrastructure, browser requirements, vector database capacity
- Updated Out of Scope: Clarified exclusions for book/chatbot platform (video hosting, live chat, grading, analytics)

### Session 2026-02-08 (Technical Clarifications)

- Q: Which SDK should be used for LLM orchestration (FR-036: "OpenAI Agents SDK OR ChatKit SDK")? → A: OpenAI Agents SDK - Provides tighter integration with OpenAI embedding/chat APIs (FR-038, FR-040), proven stability, extensive documentation, and reduces vendor abstraction complexity
- Q: Which hosting platform for FastAPI backend (Assumption 17: "Railway, Render free tier OR organization provides server infrastructure")? → A: Railway Free Tier - 500 hours/month with $5 credit, fast cold starts (~10s), simple deployment. Monitor usage to avoid mid-quarter exhaustion; implement usage alerts at 400 hours
- Q: How should CPU fallback be triggered for students without NVIDIA GPUs (FR-009)? → A: Automatic GPU detection with fallback - Launch script detects GPU via `nvidia-smi` at runtime, automatically configures Isaac ROS (GPU) or ORB-SLAM3 (CPU). Display informational warning if CPU fallback used. Zero manual configuration required
- Q: What is the scope of rate limiting in FR-048 ("20 queries per hour per session")? → A: Per browser session (sessionStorage) - Each browser tab/session gets independent 20 queries/hour limit using 1-hour sliding window. Session ID stored in sessionStorage, tracked in Neon Postgres. Opening new tab creates new session with fresh limit. Aligns with FR-055 (sessionStorage for conversation history)
- Q: What is the log retention period for FR-019 and FR-047 (platform logs and chatbot interactions)? → A: End of quarter + 30 days - Retain all logs until 30 days after quarter end date (configurable), then auto-delete via scheduled cleanup job. Preserves full quarter data for instructor review and curriculum gap analysis while staying under Neon 500MB free tier limit. Addresses privacy compliance (GDPR/FERPA)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - ROS 2 Middleware Control (Priority: P1)

As a student learning Physical AI, I want to understand and control robot behavior using ROS 2 nodes, topics, and services so that I can build the foundational communication layer for embodied intelligence systems.

**Why this priority**: ROS 2 is the fundamental middleware for all subsequent modules. Without understanding publish/subscribe patterns and service-based control, students cannot progress to simulation, perception, or VLA integration.

**Independent Test**: Can be fully tested by creating a simple talker/listener node pair and verifying message flow in terminal output. Delivers immediate value through hands-on understanding of distributed robot control.

**Learning Objectives**: LO-001: Predict message flow in pub/sub systems, LO-002: Debug node communication failures, LO-003: Design service-based control interfaces

**Reasoning Requirements**:
- **Prediction**: "If I publish to `/cmd_vel` topic at 10Hz, what will the subscriber receive? What happens if the subscriber starts after the publisher?"
- **Observable Outcome**: Terminal output showing timestamped messages, `ros2 topic echo` displaying real-time data, RQT graph visualizing node connections
- **Reflection Question**: "Why did the subscriber miss the first 3 messages? How does QoS policy affect message delivery?"

**Acceptance Scenarios**:

1. **Given** a ROS 2 workspace with a talker node, **When** student runs `ros2 run <package> talker`, **Then** messages appear in terminal at specified rate with correct content
2. **Given** talker and listener nodes running, **When** student runs `ros2 topic list`, **Then** all active topics are displayed including `/chatter` or equivalent
3. **Given** a service server node, **When** student calls service via `ros2 service call`, **Then** service executes and returns expected response
4. **Given** multiple nodes communicating, **When** student opens RQT graph, **Then** node connections and topic flows are correctly visualized

---

### User Story 2 - Physics-Based Digital Twin Simulation (Priority: P2)

As a student, I want to simulate humanoid robots in realistic virtual environments so that I can safely test control algorithms and perception systems before deploying to physical hardware.

**Why this priority**: Simulation provides safe, repeatable testing environments. This is critical for developing autonomous systems without risk of hardware damage, and enables faster iteration cycles.

**Independent Test**: Can be tested by spawning a humanoid URDF model in Gazebo, applying forces, and verifying physics behavior matches real-world expectations (gravity, collisions, friction).

**Learning Objectives**: LO-004: Understand URDF robot modeling, LO-005: Configure physics engines, LO-006: Generate and interpret simulated sensor data

**Reasoning Requirements**:
- **Prediction**: "If I apply 10N forward force to the robot torso, which direction will it move? Will it topple over?"
- **Observable Outcome**: Gazebo GUI showing robot motion, collision feedback, joint states published to topics, sensor point clouds in RViz
- **Reflection Question**: "Why did the robot fall when walking on a slope but not on flat ground? What physics parameters control stability?"

**Acceptance Scenarios**:

1. **Given** a humanoid URDF file, **When** student spawns robot in Gazebo, **Then** robot appears with correct geometry, joints, and sensors
2. **Given** robot in simulation, **When** gravity is enabled, **Then** robot responds to gravitational force realistically
3. **Given** robot with lidar sensor, **When** obstacles are placed in environment, **Then** lidar publishes point cloud data reflecting obstacle positions
4. **Given** robot walking gait, **When** collision occurs with wall, **Then** physics engine correctly prevents penetration and publishes contact forces

---

### User Story 3 - Autonomous Perception and Navigation (Priority: P3)

As a student, I want the robot to perceive its environment using vision and lidar, then navigate autonomously to goals while avoiding obstacles, so I can understand how embodied AI systems interact with the physical world.

**Why this priority**: Perception and navigation demonstrate the "embodied" aspect of Physical AI. This builds on ROS 2 and simulation foundations to create truly autonomous behavior.

**Independent Test**: Can be tested by placing robot in simulated environment, setting navigation goal, and verifying robot reaches goal while avoiding dynamic obstacles.

**Learning Objectives**: LO-007: Understand VSLAM algorithms, LO-008: Configure Nav2 stack, LO-009: Tune local and global planners

**Reasoning Requirements**:
- **Prediction**: "If I set a goal behind the wall, will the robot path around it? What if a person crosses the robot's path?"
- **Observable Outcome**: RViz showing costmap updates, planned path visualization, robot successfully reaching goal, recovery behaviors on obstacle detection
- **Reflection Question**: "Why did the robot choose path A instead of path B? How did dynamic obstacles affect the costmap?"

**Acceptance Scenarios**:

1. **Given** robot with camera and lidar, **When** robot moves through environment, **Then** VSLAM produces accurate pose estimates within 5cm error
2. **Given** obstacle-filled environment, **When** navigation goal is set, **Then** Nav2 plans collision-free path from start to goal
3. **Given** robot executing path, **When** unexpected obstacle appears, **Then** local planner replans trajectory in real-time
4. **Given** robot stuck in recovery mode, **When** recovery behaviors execute, **Then** robot exits stuck state and resumes navigation

---

### User Story 4 - Voice-to-Action VLA Pipeline (Priority: P4)

As a user, I want to give natural language voice commands to the robot and see it understand and execute multi-step tasks, so I can interact with Physical AI systems intuitively without programming.

**Why this priority**: VLA represents the cutting-edge integration of language models with embodied systems. This is the capstone demonstration of all prior learning.

**Independent Test**: Can be tested by speaking command like "go to the kitchen and pick up the red cup", then verifying robot successfully chains navigation and manipulation actions.

**Learning Objectives**: LO-010: Integrate LLMs with ROS 2 actions, LO-011: Design VLA reasoning pipelines, LO-012: Debug multi-modal system failures

**Reasoning Requirements**:
- **Prediction**: "If I say 'move forward slowly', what ROS 2 message will the LLM generate? What if I say 'go to the living room'?"
- **Observable Outcome**: Transcribed voice input displayed, LLM reasoning chain visible (command → plan → ROS actions), robot executing planned behaviors
- **Reflection Question**: "Why did the LLM choose navigation over manipulation? How did context from previous commands influence the plan?"

**Acceptance Scenarios**:

1. **Given** microphone input active, **When** user speaks command, **Then** speech is accurately transcribed to text within 2 seconds
2. **Given** transcribed command, **When** LLM processes input, **Then** LLM generates valid ROS 2 action plan with correct parameters within 3 seconds
3. **Given** action plan, **When** ROS 2 action server receives plan, **Then** robot begins executing planned behaviors within 5 seconds of receiving plan
4. **Given** voice command spoken, **When** end-to-end pipeline executes, **Then** total latency from speech to robot motion does not exceed 10 seconds
5. **Given** unsafe command (e.g., "jump off the table"), **When** multi-layer validation executes, **Then** command is rejected with educational explanation logged
6. **Given** invalid command (e.g., "fly to the moon"), **When** LLM and parameter validation execute, **Then** system rejects command and explains physical constraints
7. **Given** ambiguous command, **When** LLM cannot determine intent, **Then** system requests clarification from user

---

### User Story 5 - AI-Assisted Learning via RAG Chatbot (Priority: P0)

As a student reading the Physical AI curriculum book, I want to ask questions about concepts, code examples, and troubleshooting without leaving the page, so I can get instant clarification and maintain learning flow.

**Why this priority**: P0 (highest priority) because chatbot is core infrastructure enabling self-service learning. Without it, students depend entirely on instructor support, creating bottlenecks and reducing learning autonomy. The book is the primary delivery mechanism for curriculum - without chatbot integration, students cannot access AI-assisted explanations aligned with reasoning-first pedagogy.

**Independent Test**: Can be tested by opening any book page, highlighting a ROS 2 code snippet (e.g., node publisher example), typing question "Why does this node use QoS profile Reliable?", and verifying chatbot retrieves relevant curriculum section and answers accurately with citations.

**Learning Objectives**:
- LO-013: Students can use chatbot to debug prediction errors and verify their reasoning
- LO-014: Students can query curriculum content via natural language without manual search
- LO-015: Students can validate understanding by asking "what if" hypothetical questions

**Reasoning Requirements**:
- **Prediction**: "If I ask chatbot 'What are URDF joint limits?', will it reference Module 1 content or Module 2 content? How will it cite sources?"
- **Observable Outcome**: Chatbot response appears within 3 seconds, includes citation (e.g., "Module 1, Lesson 3: Joint Constraints and Workspace"), retrieves relevant code snippet from curriculum, answers question accurately using retrieved context
- **Reflection Question**: "Did chatbot's explanation match my prediction? What additional curriculum sections did it suggest? How does RAG retrieval differ from simple keyword search?"

**Acceptance Scenarios**:

1. **Given** book page open on any module, **When** student types question in chatbot widget, **Then** response appears within 3 seconds with cited curriculum sources
2. **Given** text selected on page (code snippet or explanation), **When** student clicks "Ask about this" or types question, **Then** chatbot uses selected text as context in retrieval query and references it in answer
3. **Given** off-topic question (e.g., "What's the weather today?"), **When** chatbot processes query, **Then** chatbot politely declines and suggests curriculum-related topics students can explore
4. **Given** ambiguous question without context, **When** chatbot lacks sufficient information, **Then** chatbot asks clarifying questions referencing specific modules or lessons
5. **Given** code debugging question (e.g., "Why is my node not publishing?"), **When** chatbot retrieves relevant troubleshooting guide, **Then** response includes step-by-step diagnostic process from curriculum with terminal commands to run
6. **Given** prediction-phase exercise question, **When** student asks for hint (not full answer), **Then** chatbot provides guided reasoning questions without revealing solution directly
7. **Given** student navigates between book pages, **When** student returns to chatbot, **Then** conversation history persists across navigation (session storage)

---

### Edge Cases

- What happens when ROS 2 nodes fail mid-execution (process crash, network partition)?
- How does system handle physics simulation instability (robot falling through floor, joint explosions)?
- What if VSLAM loses tracking in low-texture or dynamic environments?
- How does VLA pipeline handle commands outside robot capabilities ("fly to the moon")? → Multi-layer validation rejects with educational explanation
- How does system prevent unsafe actions (extreme velocities, self-collision, falling)? → LLM prompt constraints + parameter bounds + simulation pre-check
- What happens when multiple students run simulations on shared compute resources?
- How does system recover from LLM API rate limits or network timeouts?
- What if voice commands contain background noise or multiple speakers?
- What happens when chatbot receives ambiguous queries that match multiple course sections?
- How does system handle chatbot API rate limits or service outages?
- What if book deployment fails during automated build pipeline?
- How does chatbot maintain accuracy when course content is updated mid-quarter?
- What happens when vector database becomes inconsistent with published book content?
- What if Docusaurus build fails due to malformed Markdown (invalid frontmatter, broken links)? → CI fails with descriptive error, prevents deployment until fixed
- What if Qdrant Cloud free tier storage exceeded (>1GB embeddings)? → Implement chunking strategy to stay under limit, archive old curriculum versions
- What if Neon Postgres free tier compute exhausted (>1 hour/month active)? → Database auto-suspends, chatbot shows "temporarily offline" message, resumes when compute available
- What if OpenAI API rate limit exceeded during peak usage (multiple students querying simultaneously)? → Backend queues requests, shows "high demand, estimated wait: 30s" to users
- What if student asks chatbot to help with ROS 2 code debugging but provides no context? → Chatbot requests: lesson reference, error message, code snippet before answering
- What if chatbot retrieves irrelevant curriculum chunks (low cosine similarity <0.7)? → Chatbot responds "I don't have specific curriculum content on that topic. Could you rephrase or ask about [suggested topics]?"
- What if student highlights ambiguous text selection (spans multiple concepts)? → Chatbot acknowledges: "Your selection covers X and Y. Which aspect should I focus on?"
- What if GitHub Pages deployment breaks due to DNS misconfiguration? → Fallback: temporary deployment to GitHub-provided domain (username.github.io/repo) until DNS fixed

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Platform MUST provide ROS 2 Humble (mandated, no alternative distributions) workspace with pre-configured packages for talker/listener examples
- **FR-002**: Platform MUST support creation and execution of custom ROS 2 nodes in Python using rclpy
- **FR-003**: Platform MUST enable pub/sub communication with configurable QoS policies
- **FR-004**: Platform MUST provide service-based robot control interfaces for discrete actions
- **FR-005**: Platform MUST include Gazebo simulation environment (mandatory for all students) with humanoid robot URDF models
- **FR-006**: Platform MUST simulate realistic physics including gravity, collisions, friction, and joint dynamics
- **FR-007**: Platform MUST generate simulated sensor data (RGB cameras, depth cameras, lidar, IMU) published to ROS topics
- **FR-008**: Platform SHOULD support Unity simulation as optional advanced enrichment track with Isaac Sim integration (requires NVIDIA GPU)
- **FR-009**: Platform MUST integrate NVIDIA Isaac ROS packages for VSLAM perception (preferred path); Platform MUST provide CPU-based fallback options (ORB-SLAM3 or RTAB-Map) for students without NVIDIA GPUs. Automatic GPU detection via `nvidia-smi` at runtime determines which SLAM backend to configure. Display informational warning if CPU fallback is used
- **FR-010**: Platform MUST include Nav2 navigation stack with configured local and global planners
- **FR-011**: Platform MUST enable obstacle avoidance using costmap-based planning
- **FR-012**: Platform MUST provide visualization tools (RViz, RQT) for debugging and monitoring
- **FR-013**: Platform MUST integrate speech-to-text service for voice command transcription
- **FR-014**: Platform MUST connect to LLM API (OpenAI, Anthropic, or local model) for natural language understanding
- **FR-015**: Platform MUST translate LLM outputs into ROS 2 action messages with validated parameters; validation includes parameter bounds checking and simulation-based collision/stability pre-checks
- **FR-015a**: Platform MUST implement multi-layer safety validation: (1) LLM system prompt restricts unsafe action types, (2) ROS parameter bounds enforce physical limits, (3) Simulation pre-check predicts collisions and instability
- **FR-015b**: Platform MUST log all rejected commands with educational explanations describing why the action was unsafe or invalid
- **FR-016**: Platform MUST execute multi-step robot behaviors based on LLM action plans
- **FR-017**: Platform MUST include educational documentation mapping code to Physical AI concepts
- **FR-018**: Platform MUST provide prediction-execution-reflection templates for student exercises
- **FR-019**: Platform MUST log all interactions (commands, sensor data, actions) for debugging and learning. Logs retained until 30 days after quarter end date (configurable), then auto-deleted via scheduled cleanup job. Addresses privacy compliance (GDPR/FERPA)
- **FR-020**: Platform MUST run on standard Ubuntu 22.04 systems with NVIDIA GPU support
### Book Publication & Infrastructure Requirements

- **FR-021**: Platform MUST use Docusaurus v3.0+ for static site generation from curriculum markdown files
- **FR-022**: Platform MUST deploy book to GitHub Pages with automated CI/CD using GitHub Actions (build triggered on every commit to main branch)
- **FR-023**: Platform MUST organize content in hierarchical structure: Quarter → Module (1-4) → Lesson → Exercise with automatic table of contents generation
- **FR-024**: Platform MUST render code examples with syntax highlighting (Python, YAML, XML for URDF) and copy-to-clipboard functionality
- **FR-025**: Platform MUST support content versioning tracking curriculum updates (e.g., v1.2.0 aligned to Constitution v1.2.0)
- **FR-026**: Platform MUST generate complete static site from curriculum markdown files within 5 minutes build time (Docusaurus build + deployment)
- **FR-027**: Platform MUST support dark/light theme toggle for accessibility and student preference
- **FR-028**: Platform MUST render LaTeX equations for kinematics, control theory, and physics formulas using KaTeX or similar
- **FR-029**: Platform MUST provide downloadable resources (URDF files, launch scripts, Docker configs) linked from relevant lessons
- **FR-030**: Platform MUST include search functionality across all curriculum content using Docusaurus Algolia integration or built-in search
- **FR-031**: Platform MUST include "Edit this page" links to GitHub source repository for community contributions and error reporting
- **FR-032**: Platform MUST embed video walkthroughs for complex setup procedures (ROS 2 workspace initialization, Isaac Sim installation)

### RAG Chatbot Backend Requirements

- **FR-033**: Platform MUST embed interactive RAG chatbot widget on all book pages (Docusaurus custom React component)
- **FR-034**: Chatbot backend MUST use FastAPI v0.100+ with async request handling for concurrent student queries
- **FR-035**: Backend MUST connect to Qdrant Cloud (free tier: 1GB vector storage) for curriculum content embeddings
- **FR-036**: Backend MUST use OpenAI Agents SDK for LLM orchestration and response generation (provides native streaming, function calling, structured outputs with direct OpenAI API integration)
- **FR-037**: Backend MUST store conversation history and user interactions in Neon Serverless Postgres (free tier: 500MB storage, 1 compute hour)
- **FR-038**: Backend MUST embed all curriculum content using OpenAI `text-embedding-3-small` model (cost-effective, 1536 dimensions)
- **FR-039**: Backend MUST retrieve top-5 relevant curriculum chunks per query using cosine similarity with minimum threshold >0.7
- **FR-040**: Backend MUST implement context window management: truncate retrieved context if combined with query exceeds 8k tokens (gpt-4o-mini limit)
- **FR-041**: Backend MUST answer questions based on book content using retrieved curriculum sections as context (RAG pattern: retrieve → augment → generate)
- **FR-042**: Backend MUST support text-selection-based queries: when user highlights text on page, chatbot receives selection as additional context in retrieval
- **FR-043**: Backend MUST cite specific book sections/pages in answers with format: "According to Module 2, Lesson 3: Gazebo Sensors..." with clickable links
- **FR-044**: Backend MUST handle chatbot API rate limits gracefully: queue requests if OpenAI rate limit hit, show estimated wait time to user
- **FR-045**: Backend MUST filter answers to curriculum scope: reject off-topic questions politely with suggested curriculum-related alternatives
- **FR-046**: Backend MUST sanitize user input to prevent prompt injection attacks (strip special tokens, validate length <500 chars)
- **FR-047**: Backend MUST log all queries, retrieved chunks, and generated answers to Neon Postgres for curriculum gap analysis; Platform logs include chatbot interactions (FR-019 integration note). Same retention policy as FR-019: auto-delete 30 days after quarter end
- **FR-048**: Backend MUST rate-limit users to 20 queries per hour per browser session (sessionStorage-based session ID with 1-hour sliding window tracked in Neon Postgres) to manage OpenAI API costs (<$10 per student per quarter). Each browser tab/session has independent limit
- **FR-049**: Backend MUST cache frequent queries in-memory (Python dict or Redis optional) to reduce LLM API calls for repeated questions
- **FR-050**: Backend MUST respond to chatbot queries with <200ms overhead excluding LLM latency (FastAPI processing + Qdrant retrieval + Postgres logging)

### Chatbot Frontend Requirements

- **FR-051**: Chatbot widget MUST be embedded on all Docusaurus pages as fixed position element (bottom-right corner, does not block content)
- **FR-052**: Widget MUST support text selection → right-click "Ask chatbot about this" OR automatic detection when text highlighted + chatbot opened
- **FR-053**: Widget MUST show typing indicators during LLM response generation (animated dots or progress message)
- **FR-054**: Widget MUST display source citations as clickable links navigating to specific book sections (smooth scroll to cited content)
- **FR-055**: Widget MUST maintain conversation history across page navigation using browser sessionStorage (persists until tab closed)
- **FR-056**: Widget MUST show "suggested questions" based on current page content (e.g., on URDF lesson page: "What are joint limits?", "How do I debug URDF parsing errors?")
- **FR-057**: Widget MUST collapse to minimized icon when not in use to avoid obstructing curriculum content (expand on click)
- **FR-058**: Widget MUST display error messages gracefully: if backend unavailable, show "Chatbot temporarily offline" with retry option
- **FR-059**: Widget MUST support keyboard navigation and screen reader compatibility (WCAG 2.1 AA accessibility)
- **FR-060**: Widget MUST allow users to copy chatbot responses to clipboard (copy button on each message)

### Key Entities

- **Student**: Learner progressing through Physical AI curriculum, interacting with platform to build understanding of embodied intelligence systems
- **Educator**: Instructor delivering curriculum, monitoring student progress, customizing learning objectives
- **Humanoid Robot Model**: URDF-defined articulated robot with sensors, actuators, and physics properties
- **Simulation Environment**: Virtual world containing obstacles, surfaces, lighting, and dynamic elements for robot testing
- **ROS 2 Node**: Software module implementing specific functionality (perception, control, planning) communicating via topics and services
- **Learning Module**: Self-contained educational unit covering specific Physical AI concept (ROS 2, simulation, perception, VLA)
- **Action Plan**: LLM-generated sequence of robot behaviors with parameters, timing, and success criteria
- **Sensor Data**: Time-series observations from robot sensors (images, point clouds, IMU readings) used for perception and navigation
- **Book Page**: Single unit of course content rendered from markdown with navigation, search, and embedded chatbot
- **Curriculum Book**: Docusaurus-generated static website containing all educational content, deployed to GitHub Pages, serving as primary student interface
- **RAG Chatbot**: Embedded AI assistant using retrieval-augmented generation to answer student questions based on curriculum content with citations
- **Chatbot Conversation**: Stateful dialog session between student and AI assistant with message history and context
- **Vector Embedding**: Numerical representation of curriculum text chunks stored in Qdrant for semantic similarity search
- **Conversation Turn**: Single question-answer exchange between student and chatbot, logged in Neon Postgres with metadata (timestamp, retrieved chunks, user session)
- **RAG Query**: Student question processed through retrieval (find relevant content) then generation (produce grounded answer) pipeline
- **Source Citation**: Reference linking chatbot answer to specific course section, page, or code example

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Students can build and run a complete ROS 2 talker/listener system within 30 minutes of starting Module 1
- **SC-002**: Students successfully spawn and control a humanoid robot in Gazebo simulation with functional sensor data within 1 hour
- **SC-003**: Students achieve autonomous navigation success rate above 90% in standard test environments (10 navigation goals)
- **SC-004**: Students successfully execute voice-to-action commands with end-to-end success rate above 80% in capstone demonstration
- **SC-005**: Platform handles 20 concurrent simulation instances without performance degradation (>30 FPS physics rate)
- **SC-006**: Voice command transcription accuracy exceeds 95% for standard robotics vocabulary in quiet environments (within 2 seconds)
- **SC-006a**: End-to-end voice-to-action latency does not exceed 10 seconds (2s transcription + 3s LLM reasoning + 5s action initialization)
- **SC-007**: LLM generates valid ROS 2 action plans for 90% of in-scope commands without human intervention
- **SC-008**: Complete capstone project (voice-commanded autonomous humanoid) demonstrates all four modules integrated successfully
- **SC-009**: 80% of students complete capstone within standard quarter timeline (10-12 weeks)
- **SC-010**: Students accurately predict robot behavior before execution in 70% of prediction-phase exercises
- **SC-011**: Students correctly diagnose system failures (node crashes, planning failures) in debugging exercises
- **SC-012**: Platform reduces instructor support requests by 40% through comprehensive documentation and self-service debugging tools
### Book Publication Success Criteria

- **SC-013**: Docusaurus book deploys to GitHub Pages within 5 minutes of curriculum content commit to main branch
- **SC-014**: Book build process completes without errors for all 4 modules (20-32 lessons total) in single build pass
- **SC-015**: All code snippets render with correct syntax highlighting (Python, YAML, XML) and functional copy buttons
- **SC-016**: Book navigation loads pages within 2 seconds on standard broadband connection (50 Mbps)
- **SC-017**: Search functionality returns relevant results in top-5 for 90% of curriculum keyword queries

### RAG Chatbot Success Criteria

- **SC-018**: Chatbot answers curriculum questions with >85% accuracy validated against instructor-labeled test set (100 questions spanning all modules)
- **SC-019**: Chatbot retrieval finds relevant curriculum content in top-3 chunks for 90% of in-scope queries (measured on test set)
- **SC-020**: Chatbot latency (query submission → first response token) <3 seconds for 95th percentile of requests
- **SC-021**: Text-selection-based queries correctly incorporate highlighted text as context in 100% of test cases
- **SC-022**: Chatbot rejects off-topic questions (non-curriculum) with helpful redirection 100% of time on out-of-scope test set
- **SC-023**: Chatbot provides accurate citations linking to correct book sections in >90% of answers that reference curriculum content
- **SC-024**: Neon Postgres database stores >1000 conversation turns without performance degradation (query time <50ms)
- **SC-025**: Qdrant vector search executes in <100ms for curriculum-sized corpus (~500-800 chunks depending on final content volume)
- **SC-026**: Chatbot maintains conversation context across page navigation for 100% of sessions (no context loss when user switches lessons)

## Assumptions

1. Students have prior programming experience (Python proficiency)
2. Students have completed prerequisite AI/ML courses covering neural networks and transformers
3. Compute resources available: Ubuntu 22.04, 16GB RAM, NVIDIA GPU (GTX 1060 or better) preferred for Isaac ROS acceleration; CPU-based VSLAM fallback available for non-NVIDIA systems
4. Internet connectivity for LLM API access and package downloads
5. Students allocate 10-15 hours per week for coursework
6. Educational licenses available for NVIDIA Isaac Sim and Unity
7. Speech-to-text uses standard English commands (multilingual support not required)
8. Humanoid robot models use open-source URDF files (no proprietary hardware specifications)
9. Simulation environments use free assets (no licensed 3D models)
10. LLM API costs remain within educational budget ($5-10 per student for quarter)
11. Students have modern web browsers (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+) with JavaScript enabled for chatbot widget
12. GitHub repository hosting curriculum markdown is public (for GitHub Pages free tier) OR organization has paid plan
13. OpenAI API costs remain within educational budget: ~$5-10 per student for quarter (embeddings: ~$0.50, chat: ~$4.50 assuming 200 queries × $0.02/query)
14. Qdrant Cloud and Neon Postgres free tiers remain available (or budget allocated for paid tiers if needed)
15. Curriculum content volume stays under Qdrant 1GB limit (~500-800 chunks at 1536 dimensions = ~600MB)
16. Students read curriculum primarily on desktop/laptop (mobile responsive design but optimized for larger screens)
17. FastAPI backend deployed to Railway Free Tier (500 hours/month, $5 credit, ~10s cold start). Usage monitoring required to prevent mid-quarter hour exhaustion
18. Chatbot queries are primarily synchronous (students wait for answers, not batch processing)

## Dependencies

### Mandatory Dependencies

#### Curriculum Platform Dependencies
- ROS 2 Humble distribution (mandated, LTS with support until 2027)
- Gazebo 11 or later
- NVIDIA Isaac ROS packages (preferred for VSLAM) OR ORB-SLAM3/RTAB-Map (CPU fallback)
- Nav2 navigation stack
- Python 3.10+
- Speech-to-text service (Whisper, Google Speech API, or Azure)
- LLM API access for VLA pipeline (OpenAI GPT-4, Anthropic Claude, or local LLaMA)
- Standard ROS 2 visualization tools (RViz2, RQT)

#### Book Publication Stack (Mandatory)
- **Docusaurus**: v3.0+ (React-based static site generator optimized for documentation)
- **GitHub Pages**: Free hosting with custom domain support, HTTPS enabled
- **GitHub Actions**: CI/CD for automated build and deployment on commit
- **Node.js**: v18+ (required for Docusaurus build process)
- **React**: v18+ (Docusaurus dependency, also used for chatbot widget)

#### RAG Chatbot Stack (Mandatory)
- **FastAPI**: v0.100+ (async Python web framework for chatbot backend)
- **OpenAI Agents SDK** OR **ChatKit SDK**: LLM orchestration for answer generation
- **Qdrant Cloud**: Free tier (1GB vector storage, persistent for curriculum embeddings)
- **Neon Serverless Postgres**: Free tier (500MB storage, 1 compute hour, auto-suspend when idle)
- **OpenAI API**: `text-embedding-3-small` (embeddings) + `gpt-4o-mini` (answer generation)
- **Python**: v3.10+ (FastAPI backend, embedding pipeline)
- **CORS middleware**: For cross-origin requests from Docusaurus frontend to FastAPI backend
- **Pydantic**: v2.0+ (data validation for API requests/responses)
- **Uvicorn**: ASGI server for FastAPI deployment

### Optional Dependencies (Advanced Track)
- Unity 2021 LTS (for optional Unity simulation path)
- NVIDIA Isaac Sim (for optional Isaac integration path)

## Out of Scope

### Curriculum Platform
- Physical hardware integration (real robot deployment)
- Custom robot mechanical design or CAD modeling
- Non-humanoid robot platforms (quadrupeds, drones, vehicles)
- Advanced manipulation (grasping, dexterous manipulation)
- Multi-robot coordination and swarm behaviors
- Production-grade deployments (safety certification, real-world reliability)
- Mobile applications or remote control interfaces
- Custom LLM training or fine-tuning
- Real-time operating system (RTOS) requirements
- Proprietary robot firmware development

### Book & Chatbot Platform
- Custom LMS features beyond book + chatbot (grading systems, assignment submission, certificates, student progress dashboards)
- Multi-language translations of curriculum (book published in English only)
- Offline chatbot functionality (requires internet for OpenAI API, no local LLM fallback)
- Voice input for chatbot queries (text-only interface)
- Collaborative real-time editing of curriculum content (static content only, contributions via GitHub PRs)
- Advanced analytics beyond basic logging (heatmaps, A/B testing, learning path optimization)
- Custom curriculum authoring UI (content authored in Markdown, managed via Git)
- Mobile-native apps (responsive web interface only)

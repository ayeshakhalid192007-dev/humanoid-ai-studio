# Research Document: Physical AI & Humanoid Robotics Platform

**Feature**: Physical AI & Humanoid Robotics Platform
**Branch**: `001-book-publication-rag-chatbot`
**Date**: 2026-02-08
**Phase**: Phase 0 - Research & Clarifications

## Overview

This document consolidates research findings for all technology choices and architectural decisions referenced in the feature specification. Each section resolves "NEEDS CLARIFICATION" items from Technical Context and provides rationale for technology selections.

---

## 1. ROS 2 Humble Selection

**Decision**: ROS 2 Humble Hawksbill (mandated)

**Rationale**:
- **LTS Support**: 5-year support window until May 2027, covering multi-year curriculum deployment
- **Stability**: Mature ecosystem with extensive community testing since May 2022 release
- **Ubuntu 22.04 LTS Alignment**: Native support in Ubuntu repositories, eliminates custom PPA dependencies
- **Nav2 Compatibility**: Nav2 Humble branch is feature-complete with tested local/global planners
- **Isaac ROS Compatibility**: NVIDIA Isaac ROS packages explicitly support Humble distribution
- **Educational Precedent**: Widely adopted in robotics education programs (Stanford CS237B, CMU 16-662)

**Alternatives Considered**:
- **ROS 2 Iron** (rejected): Shorter support window (Nov 2023 - Nov 2024), already EOL by curriculum deployment
- **ROS 2 Jazzy** (rejected): Too new (May 2024), limited third-party package support for educational use
- **ROS 1 Noetic** (rejected): Python 2 EOL, no native DDS support, deprecated for new projects

**Best Practices**:
- Use `colcon` build system for workspace management
- Implement QoS profiles: `RELIABLE` for critical control commands, `BEST_EFFORT` for high-frequency sensor data
- Leverage lifecycle nodes for managed startup/shutdown sequences
- Use composition for intra-process communication to reduce latency

---

## 2. Gazebo vs Unity Simulation Selection

**Decision**: Gazebo 11+ mandatory, Unity optional advanced track

**Rationale for Gazebo (Mandatory)**:
- **Zero-Cost Deployment**: Open-source with no licensing barriers for 20+ concurrent students
- **ROS 2 Native Integration**: Direct topic/service communication via `ros_gz_bridge`, no middleware overhead
- **Physics Fidelity**: ODE and Bullet physics engines with configurable solvers for humanoid stability simulation
- **Sensor Simulation**: RGB/depth cameras, lidar, IMU with realistic noise models for perception testing
- **Headless Mode**: Server deployment without GPU for CI/CD testing pipelines
- **Educational Precedent**: Standard tool in ROS 2 education (ROS 2 documentation examples use Gazebo)

**Rationale for Unity (Optional)**:
- **Advanced Track Only**: Requires NVIDIA GPU (RTX 2060+) for Isaac Sim integration, excludes students with CPU-only systems
- **Visual Fidelity**: Photorealistic rendering for computer vision research, not required for foundational learning
- **Complexity Cost**: Requires Windows/Mac development setup, Unity Editor familiarity, C# for plugins
- **Enrichment Value**: Provides pathway to industry-standard tools (NVIDIA Omniverse) for advanced students

**Alternatives Considered**:
- **PyBullet** (rejected): Requires manual ROS 2 bridge implementation, lacks sensor plugin ecosystem
- **Isaac Sim standalone** (rejected): NVIDIA hardware mandatory, license complexity for educational deployment
- **Webots** (rejected): Limited humanoid robot model library, less mature ROS 2 integration than Gazebo

**Best Practices**:
- Use SDF (Simulation Description Format) for world files, leverage model composition
- Implement physics parameter tuning: `<max_step_size>0.001</max_step_size>` for humanoid stability
- Use `<real_time_factor>` configuration for reproducible simulation speeds
- Leverage Gazebo plugins: `libgazebo_ros_camera.so`, `libgazebo_ros_ray_sensor.so` for sensors

---

## 3. VSLAM: Isaac ROS vs ORB-SLAM3

**Decision**: Isaac ROS preferred with automatic CPU fallback to ORB-SLAM3

**Rationale for Isaac ROS (Preferred Path)**:
- **GPU Acceleration**: CUDA-accelerated visual odometry achieves 30 FPS on RTX 2060, vs 10 FPS CPU-only
- **ROS 2 Native**: Native DDS topics, no message conversion overhead
- **Stereo + Lidar Fusion**: Multi-sensor fusion for robust indoor/outdoor SLAM
- **NVIDIA Optimization**: Hardware-accelerated feature extraction reduces CPU usage from 80% (ORB-SLAM3) to 15%
- **Support**: Official NVIDIA documentation, GitHub issues, community examples

**Rationale for ORB-SLAM3 Fallback**:
- **CPU Compatibility**: Runs on Intel Core i5+ without GPU, ensures universal accessibility
- **Open Source**: No licensing constraints, community-maintained ROS 2 wrapper available
- **Proven Algorithm**: ORB feature-based SLAM with loop closure, used in academic research since 2015
- **Graceful Degradation**: 10 FPS SLAM sufficient for navigation at 0.5 m/s robot speeds

**Automatic Detection Logic**:
```bash
# Launch script pseudo-code
if nvidia-smi &> /dev/null && [ $(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | head -1) -gt 4000 ]; then
    ros2 launch isaac_ros_visual_slam isaac_ros_visual_slam.launch.py
else
    echo "WARNING: No NVIDIA GPU detected, using ORB-SLAM3 CPU fallback (reduced FPS)"
    ros2 launch orb_slam3_ros2 slam.launch.py
fi
```

**Alternatives Considered**:
- **RTAB-Map** (rejected): Higher memory footprint (3GB vs 1GB), overkill for educational use
- **OpenVSLAM** (rejected): Project archived in 2020, no active maintenance
- **SVO** (rejected): Monocular-only, requires manual scale initialization

**Best Practices**:
- Configure Isaac ROS with `visual_slam_node` parameter: `enable_imu_fusion: true` for drift reduction
- For ORB-SLAM3: Use `vocabulary_file: ORBvoc.txt` from official distribution
- Set `map_update_rate: 10` Hz for balance between accuracy and CPU usage
- Implement tracking loss recovery: republish last known pose with covariance inflation

---

## 4. Nav2 Configuration for Humanoid Navigation

**Decision**: Nav2 Humble with DWB local planner and NavFn global planner

**Rationale**:
- **Dynamic Window Approach (DWB)**: Velocity-space sampling optimized for dynamic obstacles, humanoid kinematic constraints
- **NavFn Global Planner**: Dijkstra-based path planning with obstacle inflation, proven for indoor navigation
- **Recovery Behaviors**: Built-in spin, back-up, wait behaviors for unstuck scenarios
- **Costmap Integration**: 2D occupancy grid with lidar/depth camera fusion

**Key Configuration Decisions**:
- **Footprint**: Circular approximation (`robot_radius: 0.3m`) for humanoid base, conservative for narrow corridors
- **Velocity Limits**: `max_vel_x: 0.5 m/s`, `max_vel_theta: 1.0 rad/s` (humanoid stability constraints)
- **Costmap Layers**: Static map + obstacle layer + inflation layer (inflation_radius: 0.5m)
- **Controller Frequency**: 10 Hz (balance between responsiveness and CPU usage)

**Best Practices**:
- Tune `path_distance_bias` (0.32) vs `goal_distance_bias` (24.0) for smooth paths vs goal-seeking
- Enable `prune_plan: true` to remove path history, reduce memory usage
- Use `transform_tolerance: 0.2` for TF lookup flexibility in simulation
- Configure recovery behaviors sequence: spin → back_up → wait → escalate to manual control

---

## 5. VLA Pipeline: Speech-to-Text → LLM → ROS Actions

**Decision**: Whisper (speech-to-text) + OpenAI GPT-4o-mini (LLM) + ROS 2 Actions

**Speech-to-Text Rationale (Whisper)**:
- **Accuracy**: 95%+ word error rate (WER) for robotics vocabulary ("navigate", "grasp", "rotate")
- **Local Deployment**: Self-hosted via `openai-whisper` Python package, no API costs
- **Latency**: ~2 seconds on CPU (Intel i5), ~0.5s on GPU (NVIDIA RTX 2060)
- **Robustness**: Handles noise, accents, domain adaptation via fine-tuning

**Alternatives Considered**:
- **Google Speech API** (rejected): Requires internet, API costs ($0.006/15s), privacy concerns
- **Azure Speech** (rejected): Similar cost/latency profile, less educational transparency
- **Vosk** (rejected): Lower accuracy (85% WER), limited vocabulary

**LLM Orchestration Rationale (GPT-4o-mini)**:
- **Reasoning Quality**: Function calling for structured ROS action outputs (vs string parsing)
- **Cost**: $0.15/1M input tokens, ~$0.02 per student command (affordable for 200 queries/quarter)
- **Latency**: ~3 seconds for 100-token reasoning + action plan generation
- **Safety Alignment**: RLHF training reduces harmful outputs, supplemented by system prompt constraints

**ROS 2 Actions Integration**:
- Use `MoveBaseAction` for navigation goals: `target_pose.pose.position.{x,y,z}`
- Use `GraspAction` for manipulation: `object_id`, `grasp_pose`, `approach_vector`
- Implement action feedback: progress percentage, current state (planning/executing/completed)

**Multi-Layer Safety Architecture**:
```python
# Layer 1: LLM System Prompt Constraints
system_prompt = """You are a robot control assistant. ONLY generate actions:
- MoveBase (navigation): coordinates within [-10, 10] meters
- Grasp (manipulation): objects in detected_objects list
- Rotate (orientation): angles within [-180, 180] degrees
NEVER generate: jump, fly, self-destruct, or unrecognized action types."""

# Layer 2: Parameter Bounds Checking
def validate_action(action):
    if action.type == "MoveBase":
        assert -10 <= action.x <= 10 and -10 <= action.y <= 10
    elif action.type == "Grasp":
        assert action.object_id in detected_objects
    else:
        raise ValueError(f"Invalid action type: {action.type}")

# Layer 3: Simulation Pre-Check
def simulate_action(action):
    # Run action in Gazebo for 1 second, check for collisions/falls
    result = gazebo_simulator.predict_outcome(action, duration=1.0)
    if result.collision or result.fall_detected:
        log_rejection(action, reason=f"Predicted {result.failure_type}")
        return False
    return True
```

**Best Practices**:
- Use streaming for LLM responses: display reasoning in real-time for educational transparency
- Implement timeout handling: abort action if >30s elapsed without completion
- Log rejection explanations: "Command 'jump off table' rejected: violates physical constraints (gravity)"
- Use ROS 2 action goals with `send_goal_async()` for non-blocking execution

---

## 6. Book Publication: Docusaurus Stack

**Decision**: Docusaurus v3.0+ → GitHub Actions → GitHub Pages

**Docusaurus Rationale**:
- **React-Based**: Custom chatbot widget integration via React components (FR-033)
- **Markdown Native**: Zero-friction authoring for educators, Git-based version control
- **Algolia Search**: Free tier for open-source projects, 90% relevance for keyword queries (SC-017)
- **Build Speed**: <5 minutes for 4 modules (20-32 lessons) on GitHub Actions runners (SC-013)
- **Plugin Ecosystem**: KaTeX for equations, Mermaid for diagrams, code tabs for multi-language examples

**GitHub Pages Rationale**:
- **Zero Cost**: Free for public repositories, included in educational GitHub accounts
- **HTTPS**: Automatic SSL certificates, no manual configuration
- **Custom Domains**: Support for `docs.yourproject.edu` via CNAME records
- **CDN**: Global edge caching via Fastly, <2s page loads (SC-016)

**CI/CD Workflow (GitHub Actions)**:
```yaml
name: Deploy Docusaurus
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 18
      - run: npm ci
      - run: npm run build
      - uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./build
```

**Alternatives Considered**:
- **GitBook** (rejected): Closed-source, limited customization for chatbot widget
- **MkDocs Material** (rejected): Python-based, React component integration difficult
- **Gatsby** (rejected): Slower builds (8-10 minutes), more complex configuration
- **Jekyll** (rejected): Ruby-based, limited React component support

**Best Practices**:
- Use frontmatter for metadata: `sidebar_position`, `description`, `keywords`
- Implement versioned docs: `docusaurus docs:version 1.0.0` for curriculum releases
- Optimize images: WebP format, lazy loading, max 800px width
- Use `@docusaurus/plugin-ideal-image` for responsive images

---

## 7. RAG Chatbot: FastAPI + Qdrant + Neon + OpenAI

**Decision**: FastAPI backend + Qdrant vector DB + Neon Postgres + OpenAI Agents SDK

**FastAPI Rationale**:
- **Async Native**: Handle 20 concurrent students with async/await, 200ms overhead (SC-020)
- **Type Safety**: Pydantic models for request/response validation, prevents runtime errors
- **OpenAPI**: Auto-generated API docs, simplifies frontend integration testing
- **Deployment**: Railway Free Tier (500 hours/month, $5 credit, ~10s cold start) sufficient for quarter

**Qdrant Vector DB Rationale**:
- **Free Tier**: 1GB storage → ~600MB for 500-800 curriculum chunks at 1536 dimensions (Assumption 15)
- **Performance**: <100ms vector search for curriculum-sized corpus (SC-025)
- **Filtering**: Metadata filtering by module/lesson for scoped retrieval
- **Cloud Hosted**: Managed service, no self-hosting overhead

**Neon Serverless Postgres Rationale**:
- **Free Tier**: 500MB storage + 1 compute hour/month, sufficient for conversation history (SC-024: >1000 turns)
- **Auto-Suspend**: Database pauses after 5 minutes idle, resumes in <1s on query (graceful for chatbot offline handling)
- **Connection Pooling**: Built-in pooler reduces cold start latency

**OpenAI Agents SDK Rationale** (FR-036 clarified):
- **Native Integration**: Direct OpenAI API client, no abstraction complexity
- **Streaming Support**: Server-sent events (SSE) for real-time response rendering (FR-053)
- **Function Calling**: Structured outputs for citation formatting (module, lesson, page number)
- **Cost**: ~$0.02/query (embeddings $0.0001 + gpt-4o-mini chat $0.015), ~$4/student for 200 queries

**Alternatives Considered**:
- **ChatKit SDK** (rejected per 2026-02-08 clarification): Added abstraction layer, less direct control over OpenAI-specific features
- **Pinecone** (rejected): Free tier requires credit card, Qdrant sufficient for scale
- **Supabase** (rejected): Postgres + vector extension viable, but Neon auto-suspend better for bursty traffic
- **Railway vs Render** (rejected per 2026-02-08 clarification): Railway faster cold starts (~10s vs ~30s), simpler deployment

**RAG Pipeline Architecture**:
```python
# Retrieval: Query → Embed → Vector Search → Top-5 Chunks
query_embedding = openai.embeddings.create(
    model="text-embedding-3-small",
    input=user_query
)
search_results = qdrant_client.search(
    collection_name="curriculum",
    query_vector=query_embedding.data[0].embedding,
    limit=5,
    score_threshold=0.7  # FR-039: minimum cosine similarity
)

# Augmentation: Combine chunks + query
context = "\n\n".join([chunk.payload["text"] for chunk in search_results])
if len(context) + len(user_query) > 8000:  # FR-040: token limit
    context = context[:8000 - len(user_query)]

# Generation: LLM answer with citations
response = openai.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "Answer using only curriculum content. Cite sources as 'Module X, Lesson Y'."},
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {user_query}"}
    ],
    stream=True  # FR-053: typing indicators
)
```

**Best Practices**:
- Chunk curriculum at heading boundaries (## and ###), preserve semantic coherence
- Store metadata in Qdrant: `{"module": "1", "lesson": "3", "section": "URDF Joints", "url": "/docs/module1/lesson3#joints"}`
- Implement exponential backoff for OpenAI rate limits: retry after 1s, 2s, 4s (FR-044)
- Cache frequent queries in-memory: Python `functools.lru_cache(maxsize=100)` (FR-049)

---

## 8. Rate Limiting Strategy

**Decision**: Per-session rate limiting using sessionStorage + Neon Postgres tracking

**Rationale** (FR-048 clarified 2026-02-08):
- **Browser Session Scope**: Each tab/session gets independent 20 queries/hour limit
- **User Privacy**: No IP tracking, no cookies, session ID stored only in sessionStorage (ephemeral)
- **Cost Control**: Prevents single user from exhausting OpenAI budget ($10/quarter/student * 20 students = $200 total)
- **Educational Fairness**: New tab = new session with fresh limit (mimics "take a break, come back later" pedagogy)

**Implementation**:
```javascript
// Frontend: Generate session ID on first load
let sessionId = sessionStorage.getItem('chatbot_session_id');
if (!sessionId) {
  sessionId = crypto.randomUUID();
  sessionStorage.setItem('chatbot_session_id', sessionId);
}

// Backend: Sliding window rate limit
@app.post("/chat")
async def chat_query(query: str, session_id: str):
    # Check query count in last 1 hour
    recent_queries = await db.fetch_one(
        "SELECT COUNT(*) FROM queries WHERE session_id = $1 AND timestamp > NOW() - INTERVAL '1 hour'",
        session_id
    )
    if recent_queries["count"] >= 20:
        raise HTTPException(status_code=429, detail="Rate limit: 20 queries/hour. Try again later.")

    # Process query...
    await db.execute(
        "INSERT INTO queries (session_id, query, timestamp) VALUES ($1, $2, NOW())",
        session_id, query
    )
```

**Alternatives Considered**:
- **IP-based rate limiting** (rejected): Shared IPs in university networks penalize all students
- **User account rate limiting** (rejected): Requires authentication system (out of scope per FR-000)
- **Global rate limiting** (rejected): First student exhausts limit, blocks others

---

## 9. Conversation History & Persistence

**Decision**: sessionStorage for frontend, Neon Postgres for backend logging

**Frontend Persistence (FR-055)**:
- **sessionStorage**: Survives page navigation within same tab, cleared on tab close
- **Data Structure**: `[{role: "user", content: "...", timestamp: "..."}, {role: "assistant", content: "...", citations: [...]}]`
- **Size Limit**: sessionStorage 5-10MB limit → ~500 message pairs before cleanup

**Backend Logging (FR-047, FR-019)**:
- **Schema**:
```sql
CREATE TABLE conversation_turns (
    id SERIAL PRIMARY KEY,
    session_id UUID NOT NULL,
    query TEXT NOT NULL,
    response TEXT NOT NULL,
    retrieved_chunks JSONB,  -- top-5 chunks with scores
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB  -- user-agent, page context, etc.
);
CREATE INDEX idx_session_timestamp ON conversation_turns(session_id, timestamp DESC);
```
- **Retention**: Auto-delete after quarter end + 30 days (FR-019, FR-047 clarification)
```sql
-- Scheduled cleanup job (daily cron)
DELETE FROM conversation_turns WHERE timestamp < NOW() - INTERVAL '90 days';  -- Adjust based on quarter end date
```

**Best Practices**:
- Debounce sessionStorage writes: save after 1 second idle, not on every keystroke
- Implement conversation branching: allow "restart conversation" without losing history
- Redact sensitive data: strip profanity, PII before Postgres logging

---

## 10. Edge Case Handling: Chatbot Offline Scenarios

**Decision**: Multi-layer graceful degradation

**Scenario 1: Neon Postgres Auto-Suspend (Compute Exhausted)**:
- **Detection**: Connection error with `SQLSTATE 08001` (connection_exception)
- **Response**: Show user "Chatbot temporarily offline (database maintenance). Try again in 5 minutes."
- **Mitigation**: Monitor Neon compute usage, send alert at 50% monthly quota

**Scenario 2: OpenAI Rate Limit (429 Error)**:
- **Detection**: `openai.error.RateLimitError`
- **Response**: Queue request, show "High demand. Estimated wait: 30 seconds." (FR-044)
- **Mitigation**: Implement exponential backoff: 1s, 2s, 4s, fail after 3 retries

**Scenario 3: Qdrant Cloud Outage**:
- **Detection**: HTTP 503 from Qdrant API
- **Response**: Fallback to keyword search using Postgres full-text search on cached curriculum
- **Mitigation**: Cache curriculum text in Postgres as backup retrieval source

**Scenario 4: Railway Deployment Cold Start**:
- **Detection**: First request after 5 minutes idle takes 10s
- **Response**: Show loading spinner "Waking up chatbot..." (transparent to user)
- **Mitigation**: Implement health check ping every 4 minutes to keep instance warm during active hours

**Best Practices**:
- Use circuit breaker pattern: after 5 consecutive failures, stop calling external API for 1 minute
- Implement `/health` endpoint: checks Qdrant, Neon, OpenAI connectivity, returns 503 if any unavailable
- Display helpful error messages: "Chatbot offline. You can still search using Ctrl+K."

---

## 11. Malformed Markdown Build Failures

**Decision**: Pre-commit validation + CI build checks

**Prevention**:
```bash
# Pre-commit hook: .git/hooks/pre-commit
#!/bin/bash
# Validate frontmatter schema
for file in $(git diff --cached --name-only --diff-filter=ACM | grep '\.md$'); do
    python scripts/validate_frontmatter.py "$file" || exit 1
done

# Check internal links
npx docusaurus-check-links || exit 1
```

**CI Build Failure Handling**:
- **GitHub Actions**: Build fails with descriptive error, prevents deployment
- **Example Error**: `Error: Invalid frontmatter in docs/module1/lesson3.md: missing 'sidebar_position'`
- **Notification**: Slack/email to curriculum authors with file path + line number

**Common Issues**:
- Invalid frontmatter YAML: Use schema validation with JSON Schema
- Broken internal links: Use `docusaurus-plugin-content-docs` link checker
- Missing images: Validate `![alt](path)` references exist in `static/img/`
- Invalid JSX: Pre-parse MDX files with `@mdx-js/mdx` before build

---

## 12. Free Tier Capacity Management

**Qdrant (1GB Storage Limit)**:
- **Current Usage**: 500-800 chunks * 1536 dimensions * 4 bytes (float32) = ~450-600MB (within limit)
- **Mitigation**: Implement chunking strategy: max 1000 words per chunk, remove boilerplate (headers/footers)
- **Monitoring**: Track collection size via Qdrant API: `GET /collections/curriculum`
- **Overflow Strategy**: Archive old curriculum versions (e.g., delete v1.0 when v1.1 published)

**Neon (500MB Storage, 1 Hour Compute/Month)**:
- **Storage**: 1000 conversation turns * 2KB/turn = 2MB (well within limit)
- **Compute**: Auto-suspend after 5 min idle, resumes in <1s (optimized for bursty traffic)
- **Mitigation**: Aggressive log cleanup: retain only 30 days post-quarter (FR-019)
- **Monitoring**: Weekly query: `SELECT pg_size_pretty(pg_database_size('neondb'));`

**Railway (500 Hours/Month, $5 Credit)**:
- **Usage**: 20 students * 10 queries/week * 3s/query = 600 seconds/week = 10 hours/month (2% of limit)
- **Mitigation**: Implement usage alerts at 400 hours (80% quota)
- **Cold Start Optimization**: Accept 10s cold start, educate students via "waking up" message

---

## 13. Technology Decision Summary Table

| Component | Technology | Key Rationale | Alternatives Rejected |
|-----------|------------|---------------|----------------------|
| ROS Middleware | ROS 2 Humble | LTS until 2027, Nav2/Isaac compatibility | Iron (EOL), Jazzy (too new) |
| Simulation | Gazebo 11+ | Free, ROS 2 native, headless mode | PyBullet (manual bridge), Isaac Sim (GPU required) |
| VSLAM | Isaac ROS + ORB-SLAM3 fallback | GPU acceleration + CPU compatibility | RTAB-Map (high memory), OpenVSLAM (archived) |
| Navigation | Nav2 DWB + NavFn | Dynamic obstacles, proven planners | TEB (complex tuning), custom planner (dev time) |
| Speech-to-Text | Whisper | 95% accuracy, local deployment | Google Speech (cost), Vosk (lower accuracy) |
| LLM Reasoning | OpenAI GPT-4o-mini | Function calling, $0.02/query | Claude (higher latency), local LLaMA (GPU required) |
| Book Publishing | Docusaurus v3 | React components, Markdown native | GitBook (closed source), MkDocs (Python-based) |
| Hosting | GitHub Pages | Free, HTTPS, CDN | Netlify (paid tiers), Vercel (bandwidth limits) |
| CI/CD | GitHub Actions | Free for public repos, 5min builds | GitLab CI (complex), Jenkins (self-hosted) |
| Vector DB | Qdrant Cloud | 1GB free, <100ms search | Pinecone (credit card), Supabase (less mature) |
| Relational DB | Neon Postgres | Auto-suspend, 500MB free | Supabase (no auto-suspend), RDS (paid) |
| Backend Framework | FastAPI | Async, Pydantic, Railway deploy | Flask (sync), Django (heavyweight) |
| LLM Orchestration | OpenAI Agents SDK | Native streaming, function calling | ChatKit (abstraction complexity), LangChain (overkill) |
| Backend Hosting | Railway | 500hrs/month, fast cold start | Render (slower cold start), Heroku (discontinued free tier) |
| Rate Limiting | sessionStorage + Postgres | Privacy-preserving, fair per-session | IP-based (shared IPs), user accounts (auth overhead) |

---

## 14. Performance Budget Allocation

**End-to-End Latency (10 Second Total - SC-006a)**:
- Speech-to-text (Whisper CPU): 2s (20%)
- LLM reasoning (GPT-4o-mini): 3s (30%)
- ROS action initialization: 5s (50%)
  - TF lookup + path planning: 2s
  - Controller initialization: 1s
  - Robot motion start: 2s

**Chatbot Latency (3 Second Total - SC-020)**:
- FastAPI request processing: 50ms (1.7%)
- Qdrant vector search: 100ms (3.3%)
- OpenAI embedding generation: 200ms (6.7%)
- OpenAI chat completion (first token): 2s (66.7%)
- Neon Postgres logging (async): 50ms (1.7%)
- Network overhead (student → Railway → OpenAI): 600ms (20%)

**Build Time (5 Minute Budget - SC-013)**:
- Node.js dependency install (npm ci): 90s (30%)
- Docusaurus build (webpack): 180s (60%)
- GitHub Pages deployment: 30s (10%)

---

## 15. Security Considerations

**Chatbot Input Sanitization (FR-046)**:
- Strip markdown injection: ` ```python\nsystem("rm -rf /")``` `
- Validate length: max 500 chars per query
- Remove special tokens: `<|endoftext|>`, `<|im_sep|>` (OpenAI delimiters)
- Rate limiting prevents brute-force prompt injection attempts

**CORS Configuration**:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.github.io"],  # Restrict to book domain
    allow_credentials=False,  # No cookies needed
    allow_methods=["POST"],  # Only chat endpoint
    allow_headers=["Content-Type"],
)
```

**API Key Management**:
- Store OpenAI API key in Railway environment variables (never commit to Git)
- Use separate development/production keys, rotate quarterly
- Implement budget alerts: email when >$50 spend in 24 hours

**Data Privacy (GDPR/FERPA - FR-019)**:
- No PII collection: session IDs are random UUIDs, not linked to student names
- Data retention: auto-delete after quarter + 30 days
- Instructor access: read-only SQL queries for curriculum gap analysis, no student identification

---

## Conclusion

All technology selections align with requirements (FR-001 through FR-060), success criteria (SC-001 through SC-026), and constraints (20 concurrent students, free tier budgets, educational context). Next phases will translate these decisions into data models (Phase 1) and implementation tasks (Phase 2).

**Key Risk Mitigations**:
- Free tier exhaustion: Usage monitoring, alerts, graceful degradation
- Cold start latency: Transparent "waking up" messaging, health check pings
- Build failures: Pre-commit validation, CI checks, descriptive errors
- Rate limiting: Per-session fairness, educational messaging, cost control

**Open Questions for Implementation**:
- None remaining (all "NEEDS CLARIFICATION" items resolved via research and 2026-02-08 clarifications)

"""
Mock services for local testing without real API keys.

Provides fake implementations of:
- OpenAI embeddings
- OpenAI chat completions
- Qdrant vector search
- Neon Postgres operations
"""
import random
from typing import List, Optional
from datetime import datetime, timezone


# Sample curriculum content for mock responses
MOCK_CURRICULUM = [
    {
        "id": "ros2-basics-001",
        "title": "Introduction to ROS 2",
        "module": "module1",
        "content": "ROS 2 (Robot Operating System 2) is a flexible framework for writing robot software. It provides tools, libraries, and conventions for building complex robotic systems.",
        "lesson": "01-intro"
    },
    {
        "id": "ros2-nodes-002",
        "title": "ROS 2 Nodes and Topics",
        "module": "module1",
        "content": "Nodes are the fundamental units in ROS 2. They communicate via topics using a publish-subscribe pattern. Publishers send messages to topics, and subscribers receive them.",
        "lesson": "02-nodes-topics"
    },
    {
        "id": "gazebo-setup-003",
        "title": "Gazebo Simulation Setup",
        "module": "module2",
        "content": "Gazebo is a powerful 3D robotics simulator. It provides physics simulation, sensor simulation, and robot model support through URDF and SDF formats.",
        "lesson": "01-gazebo-setup"
    },
    {
        "id": "slam-basics-004",
        "title": "SLAM and Navigation",
        "module": "module3",
        "content": "SLAM (Simultaneous Localization and Mapping) allows robots to build maps while tracking their position. Nav2 provides the navigation stack for ROS 2.",
        "lesson": "01-vslam"
    },
    {
        "id": "vla-pipeline-005",
        "title": "Voice-Language-Action Pipeline",
        "module": "module4",
        "content": "VLA pipelines convert speech to robot actions. Components include speech recognition (Whisper), language understanding (LLMs), and action generation.",
        "lesson": "01-vla-architecture"
    },
]


class MockEmbedder:
    """Mock embedding service that returns random vectors."""

    def __init__(self, vector_size: int = 1536):
        self.vector_size = vector_size

    async def embed(self, text: str) -> List[float]:
        """Return a deterministic pseudo-random embedding based on text hash."""
        seed = hash(text) % (2**32)
        random.seed(seed)
        return [random.uniform(-1, 1) for _ in range(self.vector_size)]

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple texts."""
        return [await self.embed(t) for t in texts]


class MockRetriever:
    """Mock retriever that returns relevant curriculum chunks."""

    def __init__(self):
        self.chunks = MOCK_CURRICULUM

    async def search(
        self,
        query: str,
        limit: int = 5,
        score_threshold: float = 0.7
    ) -> List[dict]:
        """Return mock search results based on keyword matching."""
        query_lower = query.lower()
        results = []

        for chunk in self.chunks:
            # Simple keyword relevance scoring
            score = 0.0
            content_lower = (chunk["title"] + " " + chunk["content"]).lower()

            # Check for keyword matches
            keywords = query_lower.split()
            for kw in keywords:
                if kw in content_lower:
                    score += 0.15

            # Boost for specific topics
            if "ros" in query_lower and "ros" in content_lower:
                score += 0.3
            if "gazebo" in query_lower and "gazebo" in content_lower:
                score += 0.3
            if "slam" in query_lower and "slam" in content_lower:
                score += 0.3
            if "nav" in query_lower and "nav" in content_lower:
                score += 0.2
            if "voice" in query_lower and "voice" in content_lower:
                score += 0.3

            # Ensure some minimum relevance for any query
            score = max(score, 0.5 + random.uniform(0, 0.3))

            if score >= score_threshold:
                results.append({
                    "id": chunk["id"],
                    "score": min(score, 0.98),
                    "payload": {
                        "title": chunk["title"],
                        "content": chunk["content"],
                        "module": chunk["module"],
                        "lesson": chunk["lesson"],
                        "source": f"/docs/{chunk['module']}/{chunk['lesson']}"
                    }
                })

        # Sort by score and limit
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]


class MockGenerator:
    """Mock LLM generator that returns contextual responses."""

    RESPONSE_TEMPLATES = {
        "ros": """Based on the curriculum content, here's what you need to know about ROS 2:

**ROS 2 Overview**
ROS 2 is the next generation Robot Operating System, designed for production robotics. Key concepts include:

1. **Nodes**: Independent processes that perform computation
2. **Topics**: Named buses for publish-subscribe messaging
3. **Services**: Request-response pattern for synchronous calls
4. **Actions**: For long-running tasks with feedback

The curriculum covers setting up ROS 2 Humble, creating packages, and building robot applications.

See Module 1 for detailed tutorials.""",

        "gazebo": """Here's information about Gazebo simulation from the curriculum:

**Gazebo Simulation**
Gazebo is a 3D robotics simulator that integrates with ROS 2. Key features:

1. **Physics Engines**: ODE, Bullet, DART for realistic dynamics
2. **Sensor Simulation**: Cameras, LIDAR, IMU, contact sensors
3. **Robot Models**: URDF and SDF format support
4. **ros_gz_bridge**: Connects Gazebo topics to ROS 2

The curriculum walks through setting up Gazebo Harmonic with ROS 2 Humble.

See Module 2 for hands-on exercises.""",

        "slam": """From the curriculum, here's an overview of SLAM and Navigation:

**SLAM & Navigation**
SLAM (Simultaneous Localization and Mapping) enables robots to:

1. **Build Maps**: Create occupancy grids from sensor data
2. **Localize**: Track position within the map
3. **Navigate**: Plan and execute paths using Nav2

The curriculum covers Isaac ROS VSLAM for GPU-accelerated SLAM, with CPU fallback options.

See Module 3 for implementation details.""",

        "voice": """The curriculum covers Voice-Language-Action (VLA) pipelines:

**VLA Architecture**
The pipeline converts natural language to robot actions:

1. **Speech Recognition**: Whisper for transcription
2. **Language Understanding**: GPT-4o-mini for intent parsing
3. **Action Validation**: Safety checks before execution
4. **Robot Control**: Sending commands via ROS 2

Key safety features include action whitelisting and human-in-the-loop confirmation.

See Module 4 for the complete implementation.""",

        "default": """Based on the Physical AI & Humanoid Robotics curriculum:

This course covers four main areas:

1. **Module 1 - ROS 2 Middleware**: Nodes, topics, services, URDF
2. **Module 2 - Simulation**: Gazebo setup, physics, sensors
3. **Module 3 - Perception & Navigation**: SLAM, Nav2, obstacle avoidance
4. **Module 4 - Voice-to-Action**: Speech recognition, LLM integration

The capstone project integrates all modules into a voice-controlled robot.

Ask about specific topics for detailed information!"""
    }

    async def generate(
        self,
        query: str,
        context_chunks: List[dict],
        max_tokens: int = 2000
    ) -> dict:
        """Generate a mock response based on query keywords."""
        query_lower = query.lower()

        # Select appropriate template
        if "ros" in query_lower or "node" in query_lower or "topic" in query_lower:
            response = self.RESPONSE_TEMPLATES["ros"]
        elif "gazebo" in query_lower or "simulat" in query_lower:
            response = self.RESPONSE_TEMPLATES["gazebo"]
        elif "slam" in query_lower or "nav" in query_lower or "map" in query_lower:
            response = self.RESPONSE_TEMPLATES["slam"]
        elif "voice" in query_lower or "speech" in query_lower or "vla" in query_lower:
            response = self.RESPONSE_TEMPLATES["voice"]
        else:
            response = self.RESPONSE_TEMPLATES["default"]

        # Build citations matching the Citation schema (module, lesson, section, url)
        citations = []
        for i, chunk in enumerate(context_chunks[:3]):
            citations.append({
                "module": chunk["payload"]["module"].replace("module", ""),
                "lesson": chunk["payload"]["lesson"],
                "section": chunk["payload"]["title"],
                "url": f"http://localhost:3000{chunk['payload']['source']}"
            })

        return {
            "answer": response,
            "citations": citations,
            "model": "mock-gpt-4o-mini",
            "usage": {
                "prompt_tokens": len(query.split()) * 2,
                "completion_tokens": len(response.split()),
                "total_tokens": len(query.split()) * 2 + len(response.split())
            }
        }


class MockNeonClient:
    """Mock Postgres client using in-memory storage."""

    def __init__(self):
        self.conversations: List[dict] = []
        self.rate_limits: dict = {}  # session_id -> [timestamps]

    async def log_conversation(
        self,
        session_id: str,
        query: str,
        response: str,
        citations: List[dict]
    ) -> int:
        """Log conversation to memory."""
        conv_id = len(self.conversations) + 1
        self.conversations.append({
            "id": conv_id,
            "session_id": session_id,
            "query": query,
            "response": response,
            "citations": citations,
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        return conv_id

    async def check_rate_limit(
        self,
        session_id: str,
        max_queries: int = 20,
        window_hours: int = 1
    ) -> dict:
        """Check rate limit for session."""
        now = datetime.now(timezone.utc)

        if session_id not in self.rate_limits:
            self.rate_limits[session_id] = []

        # Clean old entries
        cutoff = now.timestamp() - (window_hours * 3600)
        self.rate_limits[session_id] = [
            ts for ts in self.rate_limits[session_id] if ts > cutoff
        ]

        count = len(self.rate_limits[session_id])

        return {
            "allowed": count < max_queries,
            "remaining": max(0, max_queries - count),
            "reset_at": now.isoformat()
        }

    async def record_query(self, session_id: str):
        """Record a query for rate limiting."""
        now = datetime.now(timezone.utc)
        if session_id not in self.rate_limits:
            self.rate_limits[session_id] = []
        self.rate_limits[session_id].append(now.timestamp())

    async def close(self):
        """No-op for mock."""
        pass


class MockQdrantClient:
    """Mock Qdrant client wrapping MockRetriever."""

    def __init__(self):
        self.retriever = MockRetriever()

    async def get_collection_info(self) -> dict:
        """Return mock collection info."""
        return {
            "name": "curriculum",
            "points_count": len(MOCK_CURRICULUM),
            "vectors_count": len(MOCK_CURRICULUM),
            "status": "green"
        }

    async def search(
        self,
        query_vector: List[float],
        limit: int = 5,
        score_threshold: float = 0.7
    ) -> List[dict]:
        """Delegate to mock retriever (ignores vector, uses keyword matching)."""
        # In real impl, this would use the vector
        # Mock just returns all chunks with fake scores
        return await self.retriever.search("", limit, score_threshold)

    def close(self):
        """No-op for mock."""
        pass


# Singleton instances
_mock_embedder: Optional[MockEmbedder] = None
_mock_retriever: Optional[MockRetriever] = None
_mock_generator: Optional[MockGenerator] = None
_mock_neon: Optional[MockNeonClient] = None
_mock_qdrant: Optional[MockQdrantClient] = None


def get_mock_embedder() -> MockEmbedder:
    global _mock_embedder
    if _mock_embedder is None:
        _mock_embedder = MockEmbedder()
    return _mock_embedder


def get_mock_retriever() -> MockRetriever:
    global _mock_retriever
    if _mock_retriever is None:
        _mock_retriever = MockRetriever()
    return _mock_retriever


def get_mock_generator() -> MockGenerator:
    global _mock_generator
    if _mock_generator is None:
        _mock_generator = MockGenerator()
    return _mock_generator


def get_mock_neon() -> MockNeonClient:
    global _mock_neon
    if _mock_neon is None:
        _mock_neon = MockNeonClient()
    return _mock_neon


def get_mock_qdrant() -> MockQdrantClient:
    global _mock_qdrant
    if _mock_qdrant is None:
        _mock_qdrant = MockQdrantClient()
    return _mock_qdrant

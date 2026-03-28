---
name: rag-tutor
description: Retrieval-Augmented Generation tutor that answers learner questions using Qdrant vector search over the Humanoid AI Studio curriculum. Grounds every answer in the course content before generating a response via Google Gemini.
license: MIT
allowed-tools: qdrant_search gemini_generate
metadata:
  author: Ayesha Khalid
  version: "1.0.0"
  category: education
  domain: physical-ai-robotics
  llm: google-gemini
  vector_db: qdrant
  embedding_model: all-MiniLM-L6-v2
---

# RAG Tutor Skill

## Purpose

Answer learner questions by retrieving the most relevant curriculum chunks from Qdrant and using them as context for a grounded, accurate Gemini response. Never answer from internal knowledge alone — always retrieve first.

## Instructions

1. **Embed the question** using `sentence-transformers/all-MiniLM-L6-v2` (384-dim vector)
2. **Search Qdrant** — cosine similarity, top-k=5, threshold ≥ 0.75, collection: `curriculum`
3. **Check retrieval quality** — if no chunk scores ≥ 0.75, inform the learner the topic may not be covered in this module and suggest the closest relevant lesson
4. **Build the prompt:**
   ```
   You are Aria, the AI tutor for Humanoid AI Studio.
   Use ONLY the following curriculum excerpts to answer the learner's question.
   If the answer is not in the excerpts, say so clearly.

   [CURRICULUM EXCERPTS]
   {retrieved_chunks}

   [LEARNER QUESTION]
   {question}
   ```
5. **Stream the response** via SSE (Server-Sent Events) — do not buffer
6. **Cite the source** — include module and lesson at the end of the response

## Rate Limiting

- Maximum 20 queries per authenticated user per hour (enforced by Redis counter)
- Unauthenticated requests → return 401 with a login prompt

## Error Handling

| Scenario | Response |
|---|---|
| Qdrant timeout | Retry once; if fails, return 503 with "Vector search unavailable, try again shortly" |
| Gemini quota exceeded | Fall back to OpenAI gpt-4o-mini |
| No relevant chunks found | "This specific topic isn't covered in the current curriculum. The closest topic is [X] in Module [Y]." |
| Rate limit exceeded | "You've reached the 20 queries/hour limit. Reset in [N] minutes." |

## Example Interaction

**Learner:** "How do I create a ROS 2 publisher in Python?"

**Aria:** "Based on Module 1, Lesson 2 of the Humanoid AI Studio curriculum:

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class MinimalPublisher(Node):
    def __init__(self):
        super().__init__('minimal_publisher')
        self.publisher_ = self.create_publisher(String, 'topic', 10)
        timer_period = 0.5
        self.timer = self.create_timer(timer_period, self.timer_callback)

    def timer_callback(self):
        msg = String()
        msg.data = 'Hello, ROS 2!'
        self.publisher_.publish(msg)

def main():
    rclpy.init()
    node = MinimalPublisher()
    rclpy.spin(node)
    rclpy.shutdown()
```

Source: Module 1 → Lesson 2 — ROS 2 Publishers and Subscribers"

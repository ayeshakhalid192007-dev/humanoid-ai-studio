---
name: personalize-chapter
description: Generates a personalized version of any curriculum chapter adapted to the learner's skill level, professional background, and language preference. Uses the learner's profile from Neon Postgres combined with Qdrant-retrieved chapter content.
license: MIT
allowed-tools: neon_postgres_read qdrant_search gemini_generate redis_cache
metadata:
  author: Ayesha Khalid
  version: "1.0.0"
  category: education
  domain: personalization
  requires_auth: "true"
  cache_ttl: "3600"
---

# Personalize Chapter Skill

## Purpose

Rewrite any curriculum chapter to match the learner's background so it feels written specifically for them. A software engineer gets code-heavy analogies; a hardware engineer gets circuit-level comparisons; a student gets first-principles explanations.

## Prerequisites

- Learner must be authenticated (valid RS256 JWT)
- Learner profile must exist in Neon Postgres (`users` table)

## Instructions

1. **Validate JWT** via the JWKS endpoint (`/.well-known/jwks.json`)
2. **Fetch learner profile** from Neon Postgres:
   - `skill_level`: beginner | intermediate | advanced
   - `background`: software_engineer | hardware_engineer | roboticist | student
   - `preferred_language`: en | ur | (other)
3. **Retrieve chapter chunks** from Qdrant (filter by `chapter_id` metadata field, top-k=20)
4. **Check Redis cache** — key: `personalize:{user_id}:{chapter_id}:{profile_hash}` (TTL: 1 hour). Return cached version if hit.
5. **Build the personalization prompt:**
   ```
   You are Aria, personalizing a robotics curriculum chapter.
   The learner is a {background} with {skill_level} level.
   Language: {language}.

   Rewrite the following chapter content so it:
   - Uses analogies from {background} domain
   - Adjusts technical depth for {skill_level}
   - Keeps all code blocks unchanged
   - If language is Urdu: translate prose to Urdu RTL, keep code in English

   [CHAPTER CONTENT]
   {chapter_chunks}
   ```
6. **Stream the personalized chapter** via SSE
7. **Cache the result** in Redis (TTL: 1 hour)

## Supported Personalizations

| Background | Adaptation Strategy |
|---|---|
| `software_engineer` | Emphasize API contracts, async patterns, type systems |
| `hardware_engineer` | Connect to electrical signals, timing, I/O interfaces |
| `roboticist` | Use kinematics/dynamics framing, reference URDF/SDF directly |
| `student` | First-principles explanations, more worked examples, slower pacing |

## Constraints

- Code blocks (`\`\`\``) are NEVER modified or translated
- ROS 2 package names, topic names, and CLI commands stay in English always
- Personalized output must include `skill_level` and `background` in the response metadata

## Error Handling

| Scenario | Response |
|---|---|
| Unauthenticated request | 401 + login modal redirect |
| Profile not found | Use default: beginner + student + English |
| Chapter not in Qdrant | "This chapter has not been indexed yet. Try the standard version." |
| Gemini failure | Fall back to OpenAI; if both fail, return the original chapter with a notice |

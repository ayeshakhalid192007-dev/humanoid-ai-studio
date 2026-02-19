---
id: 8
title: Improve RAG Chunking Strategy
stage: green
date: 2026-02-14
surface: agent
model: claude-opus-4-6
feature: 001-book-publication-rag-chatbot
branch: 001-book-publication-rag-chatbot
user: architect
command: implement
labels: ["rag", "chunking", "embeddings", "metadata", "retrieval"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - backend/scripts/embed_curriculum.py
  - backend/src/services/retriever.py
tests:
  - backend/tests/ (71 tests, all passing)
  - dry-run validation (37 files, 443 chunks, 0 issues)
---

## Prompt

Implement the plan: Improve RAG Chunking Strategy. Upgrade `parse_markdown()` in the ingestion pipeline so the RAG chatbot produces higher-quality, properly-sized, metadata-rich chunks. Fix 6 problems: no max chunk size, no code-awareness, missing metadata for non-module files, no fenced code block protection, no chunk overlap, no content_type metadata.

## Response snapshot

Implemented all 5 plan steps across 2 files:

1. **Helper functions** added: `_is_inside_code_fence()`, `_detect_file_type()`, `_split_large_chunk()`, `_extract_last_sentences()`
2. **parse_markdown() rewritten** with: code-fence aware heading detection, code-prose separation (>10 line blocks), recursive large chunk splitting (400 word max), metadata extraction for capstone/lab-architecture/overview, chunk overlap for prose continuity, enriched metadata (content_type, code_language, heading_level, parent_heading, word_count, file_type)
3. **Qdrant payload updated** with new metadata fields, content_version bumped to 2.0.0
4. **dry_run() enhanced** with word count distribution, content type breakdown, code language stats, stricter validation checks
5. **Retriever updated** with optional `content_type_filter` parameter and enriched result metadata

Dry-run results: 37 files -> 443 chunks (312 prose, 68 code, 63 exercise). Word count: min 6, avg 66, max 321. All validations passed. 71 existing tests pass.

## Outcome

- ✅ Impact: All 6 chunking problems resolved. Chunks are now properly sized, code-aware, metadata-rich, and overlap-connected.
- 🧪 Tests: 71/71 existing tests pass. Dry-run validation: 0 issues across 37 files.
- 📁 Files: 2 files modified (embed_curriculum.py, retriever.py)
- 🔁 Next prompts: Run full embedding pipeline, verify retrieval quality with sample queries
- 🧠 Reflection: Fixed a nested context overlap bug during implementation where `[Context: [Context: ...]]` was compounding. Stripping existing context prefixes before extracting overlap sentences resolved it.

## Evaluation notes (flywheel)

- Failure modes observed: Nested context overlap compounding (fixed by stripping existing prefix before extraction)
- Graders run and results (PASS/FAIL): dry-run PASS, pytest 71/71 PASS
- Prompt variant (if applicable): n/a
- Next experiment (smallest change to try): Tune max_words threshold (currently 400) and overlap sentence count (currently 2) based on retrieval quality metrics

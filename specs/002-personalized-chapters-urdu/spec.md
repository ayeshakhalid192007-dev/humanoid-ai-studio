# Feature Specification: Dynamic Personalized Chapters + Urdu Translation

**Feature Branch**: `002-personalized-chapters-urdu`
**Created**: 2026-02-16
**Status**: Draft
**Input**: User description: "Add two AI-powered features to the Book Project: a Personalized Chapter Button that adapts content based on user background, and an Urdu Translation Button that dynamically translates chapter content."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Authenticated User Generates Personalized Chapter (Priority: P1)

A logged-in user navigates to any chapter page and clicks the "Personalized Version" button. The system fetches their profile (software background, hardware background, robotics knowledge level), sends the chapter content along with the user profile to the AI pipeline, and returns a personalized version that adjusts explanation depth, examples, and focus areas. The user sees a smooth transition from the default content to their personalized version.

**Why this priority**: This is the core differentiating feature. Personalized learning directly improves comprehension and engagement, leveraging existing user profile data that is already collected during signup.

**Independent Test**: Can be fully tested by signing up with a specific profile (e.g., advanced software, beginner hardware, intermediate robotics), navigating to a chapter, clicking "Personalized Version", and verifying the generated content adjusts terminology, examples, and depth appropriately for that profile.

**Acceptance Scenarios**:

1. **Given** a logged-in user with profile data (software: advanced, hardware: beginner, robotics: intermediate), **When** they click "Personalized Version" on Module 1 Lesson 1, **Then** the chapter content is regenerated with advanced software examples, simplified hardware explanations, and moderate robotics detail.
2. **Given** a logged-in user clicks "Personalized Version", **When** content is being generated, **Then** a loading indicator is displayed and the button is disabled.
3. **Given** a personalized version is displayed, **When** the user clicks "Revert to Original", **Then** the default chapter content is restored immediately.
4. **Given** a user has previously generated a personalized version for a chapter, **When** they revisit the same chapter and click "Personalized Version", **Then** the cached version loads instantly without re-generation.

---

### User Story 2 - Unauthenticated User Translates Chapter to Urdu (Priority: P2)

Any visitor (logged in or not) navigates to a chapter page and clicks the "Translate to Urdu" button. The system translates the visible chapter content into Urdu, preserving all formatting, headings, lists, and leaving code blocks untranslated. The user can toggle back to English at any time.

**Why this priority**: Translation expands accessibility to Urdu-speaking learners without requiring any authentication barrier, broadening the platform's reach.

**Independent Test**: Can be fully tested by visiting any chapter as an anonymous user, clicking "Translate to Urdu", and verifying that headings, body text, and lists appear in Urdu while code blocks remain in their original language.

**Acceptance Scenarios**:

1. **Given** any user (authenticated or not) on a chapter page, **When** they click "Translate to Urdu", **Then** all non-code chapter content is displayed in Urdu with proper right-to-left text direction.
2. **Given** a chapter containing code blocks, **When** translated to Urdu, **Then** code blocks remain untranslated and properly formatted.
3. **Given** the Urdu version is displayed, **When** the user clicks "View Original (English)", **Then** the English content is restored instantly.
4. **Given** a chapter has been previously translated, **When** the user or another user requests the same translation, **Then** the cached translation loads without re-generation.

---

### User Story 3 - Unauthenticated User Attempts Personalization (Priority: P3)

A visitor who is not logged in navigates to a chapter and clicks the "Personalized Version" button. A modal dialog appears informing them that login is required to access personalized content, with an option to sign in or sign up.

**Why this priority**: Provides a clear, non-frustrating path for unauthenticated users toward the personalization feature, driving sign-ups while maintaining a good experience.

**Independent Test**: Can be tested by visiting a chapter as an anonymous user, clicking "Personalized Version", and verifying the login modal appears with appropriate messaging and navigation options.

**Acceptance Scenarios**:

1. **Given** an unauthenticated user on a chapter page, **When** they click "Personalized Version", **Then** a modal displays "Login to unlock personalized content" with sign-in and sign-up options.
2. **Given** the login modal is shown, **When** the user successfully signs in, **Then** the modal closes and the personalization process begins automatically.

---

### User Story 4 - Combined Personalization and Translation (Priority: P4)

A logged-in user first generates a personalized version, then translates that personalized version to Urdu (or vice versa). The system supports composing both features so the user can view personalized content in Urdu.

**Why this priority**: Power-user scenario that maximizes accessibility and personalization simultaneously.

**Independent Test**: Can be tested by generating a personalized version first, then clicking "Translate to Urdu" on the personalized content, verifying the Urdu translation reflects the personalized (not original) content.

**Acceptance Scenarios**:

1. **Given** a logged-in user viewing their personalized chapter version, **When** they click "Translate to Urdu", **Then** the personalized content (not the original) is translated to Urdu.
2. **Given** a user viewing personalized+Urdu content, **When** they revert personalization, **Then** the view returns to the original chapter in English.

---

### Edge Cases

- What happens when the AI service is unavailable or times out? The system displays a user-friendly error message ("Unable to generate content. Please try again later.") and retains the current view.
- What happens when a user's profile is incomplete (e.g., missing software background)? The system generates personalization using available profile fields, with sensible defaults for missing data.
- What happens when chapter content is very long? The system processes the full chapter content but may take longer; the loading indicator communicates progress.
- What happens when the user rapidly toggles between versions? Only the most recent request is honored; intermediate requests are canceled.
- What happens when the cached content becomes stale after a chapter update? Cached content includes a version identifier; when the source chapter changes, the cache is invalidated and regeneration is required.
- How does the Urdu translation handle technical terms that have no Urdu equivalent? Technical terms (e.g., "ROS 2", "SLAM", "URDF") are preserved in English within the Urdu text, following standard academic translation practice.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST display a "Personalized Version" button at the top of every chapter page.
- **FR-002**: System MUST display a "Translate to Urdu" button at the top of every chapter page.
- **FR-003**: System MUST require authentication before generating personalized content; unauthenticated users see a login prompt modal.
- **FR-004**: System MUST fetch the user's profile (software background, hardware background, robotics knowledge level) to drive personalization.
- **FR-005**: System MUST use RAG (Retrieval-Augmented Generation) with chapter content indexed in a vector store. Relevant chunks are retrieved and combined with user profile as personalization context when generating personalized versions. The same RAG pipeline is used for Urdu translation.
- **FR-006**: System MUST keep core chapter concepts intact during personalization; only explanation depth, examples, and focus areas change. The original chapter structure (headings, sections, ordering) MUST remain unchanged. Personalization MUST NOT rewrite the entire chapter or inject new sections; it adapts explanations and examples within the existing structure.
- **FR-007**: System MUST preserve all formatting, headings, lists, and code blocks when translating to Urdu.
- **FR-008**: System MUST NOT translate code blocks (including comments within code), command-line examples, or file paths during Urdu translation. Code blocks remain completely untouched.
- **FR-009**: System MUST render Urdu text with proper right-to-left (RTL) direction and appropriate typography.
- **FR-010**: System MUST allow users to toggle between default and personalized versions without page reload. Content is replaced in-place; no tabs or side-by-side views.
- **FR-011**: System MUST allow users to toggle between English and Urdu versions without page reload. Content is replaced in-place; no tabs or side-by-side views.
- **FR-012**: System MUST cache personalized content per user per chapter to avoid repeated generation. Cache has no auto-expiry; invalidation occurs only when the source chapter is updated (FR-019) or the user explicitly clicks a "Regenerate" option.
- **FR-013**: System MUST cache Urdu translations per chapter to serve all users without repeated generation.
- **FR-014**: System MUST display a loading state while AI content is being generated.
- **FR-015**: System MUST allow Urdu translation without authentication.
- **FR-016**: System MUST sanitize all chapter content before sending to AI to prevent prompt injection.
- **FR-017**: System MUST restrict AI context strictly to chapter content and (for personalization) user profile data.
- **FR-018**: System MUST rate-limit AI generation endpoints to prevent abuse.
- **FR-019**: System MUST invalidate cached content when the source chapter is updated.
- **FR-020**: System MUST handle AI service failures gracefully with user-friendly error messages.

### Key Entities

- **ChapterContent**: Represents a chapter's original content, identified by a chapter identifier (derived from the URL path or document slug) and a content version hash.
- **PersonalizedContent**: A user-specific adaptation of a chapter. Linked to a user and a chapter. Contains the AI-generated personalized markdown, the user profile snapshot used for generation, and a generation timestamp.
- **UrduTranslation**: A chapter-level Urdu translation. Linked to a chapter (not user-specific). Contains the AI-generated Urdu markdown and a generation timestamp.
- **UserProfile**: Existing entity containing software background (free text), hardware background (free text), and robotics knowledge level (enum: none/beginner/intermediate/advanced).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can generate a personalized chapter version within 15 seconds of clicking the button.
- **SC-002**: Users can generate an Urdu translation within 15 seconds of clicking the button.
- **SC-003**: Cached personalized content loads in under 2 seconds on subsequent visits.
- **SC-004**: Cached Urdu translations load in under 2 seconds on subsequent visits.
- **SC-005**: Toggling between content versions (original/personalized/Urdu) completes in under 1 second with no page reload.
- **SC-006**: 95% of personalized content retains all core concepts from the original chapter (validated by comparison).
- **SC-007**: 100% of code blocks remain untranslated in Urdu versions.
- **SC-008**: Urdu text renders with correct right-to-left direction on all supported browsers.
- **SC-009**: Unauthenticated users attempting personalization see the login modal within 500 milliseconds.
- **SC-010**: AI generation endpoints handle at least 20 concurrent requests without degradation.

## Assumptions

- The existing AI pipeline (OpenAI gpt-4o-mini) will be extended for personalization and translation; no new AI provider is needed.
- User profile data (software background, hardware background, robotics knowledge) is already populated for most registered users via the existing signup flow.
- Chapter content is served as Markdown via Docusaurus; the personalization and translation features operate on the rendered chapter content accessible from the page or fetched via an identifier.
- The Urdu translation cache is shared across all users (not per-user) since translations are not personalized.
- The existing rate-limiting infrastructure (20 queries/hour/session for chat) provides a baseline pattern; AI generation endpoints will use a similar but separately configured rate limit.
- The existing session cookie (`physical-ai.session_token`) and Better Auth session validation will be reused for authentication on personalization endpoints.

## Dependencies

- OpenAI API for content generation (personalization and translation) and embeddings for RAG.
- Vector store for indexing and retrieving chapter content chunks (e.g., pgvector on Neon Postgres, or a dedicated vector DB).
- Neon Postgres database for storing cached personalized content and Urdu translations.
- Better Auth session validation via the auth-server for the personalization endpoint.
- Existing Docusaurus chapter pages as the content source.

## Clarifications

### Session 2026-02-16

- Q: What should personalization do to the chapter content? → A: Adapt only explanations and examples while keeping structure (headings, sections, ordering) intact. No full rewrites or injected sections.
- Q: Should code block comments be translated to Urdu, or should code blocks remain completely untouched? → A: Code blocks remain completely unchanged, including comments within code.
- Q: Should personalized content cache expire automatically? → A: No auto-expiry. Cache invalidates on source chapter update or manual user regeneration.
- Q: How should toggling between content versions work in the UI? → A: Replace content in-place; buttons toggle between versions. No tabs or side-by-side views.
- Q: Should the AI pipeline use direct prompt or RAG? → A: RAG — index chapter content in a vector store and retrieve relevant chunks for generation.

## Risks

- **AI Quality**: Personalized content may not always accurately reflect the user's level; mitigation is structured prompt templates with explicit constraints and human review of sample outputs.
- **Translation Accuracy**: AI-generated Urdu translations may contain grammatical errors or awkward phrasing for highly technical content; mitigation is preserving technical terms in English and using academic tone instructions.
- **Cost**: Each personalization and translation request incurs OpenAI API costs; mitigation is aggressive caching and rate limiting.

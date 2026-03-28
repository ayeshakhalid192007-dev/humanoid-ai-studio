---
name: translate-urdu
description: Translates Humanoid AI Studio curriculum content to Urdu (RTL) or other supported languages. Code blocks, ROS 2 package names, topic names, and CLI commands are always preserved in English.
license: MIT
allowed-tools: gemini_generate
metadata:
  author: Ayesha Khalid
  version: "1.0.0"
  category: education
  domain: multilingual
  primary_target_language: ur
  rtl_languages: "ur,ar,fa,he"
---

# Translate Urdu Skill

## Purpose

Make the Humanoid AI Studio curriculum accessible to Urdu-speaking learners by translating prose content while keeping all technical identifiers intact and renderable in RTL layout.

## Instructions

1. **Parse the input** — split content into:
   - **Translatable blocks**: regular prose paragraphs, headings, callout text, list items
   - **Preserved blocks**: fenced code blocks (` ``` `), inline code (`` ` ``), ROS 2 package names, topic names (`/cmd_vel`, `/odom`), file paths, CLI commands
2. **Build the translation prompt:**
   ```
   Translate the following educational content to {target_language}.
   Rules:
   - Translate all prose naturally and fluently
   - Do NOT translate anything inside triple backticks (```) or single backticks
   - Do NOT translate ROS 2 package names, topic names, or file extensions
   - Do NOT translate: True, False, None, import, def, class, return
   - For Urdu: output must be right-to-left (RTL). Add metadata flag: dir=rtl

   [CONTENT]
   {content}
   ```
3. **Return structured response:**
   ```json
   {
     "translated_content": "...",
     "target_language": "ur",
     "rtl": true,
     "preserved_blocks": ["code_block_1", "code_block_2"]
   }
   ```

## Supported Languages

| Code | Language | RTL |
|---|---|---|
| `ur` | Urdu | Yes |
| `ar` | Arabic | Yes |
| `fa` | Farsi/Persian | Yes |
| `hi` | Hindi | No |
| `zh` | Chinese (Simplified) | No |
| `fr` | French | No |
| `de` | German | No |

## Composition with Personalization

When a learner requests both personalization AND translation simultaneously:
1. Run `personalize-chapter` first (adapt to learner profile)
2. Run `translate-urdu` on the personalized output
3. Preserve all code blocks through both steps

## Frontend Integration Note

For Urdu and other RTL outputs, the Docusaurus frontend must apply `dir="rtl"` and `lang="ur"` to the content container. The backend response includes `"rtl": true` in metadata to signal this requirement.

## Error Handling

| Scenario | Response |
|---|---|
| Unsupported language | "Translation to {language} is not yet supported. Available: Urdu, Arabic, Hindi, French, German." |
| Gemini translation error | Retry once; if fails, return original content with error notice |
| Malformed code block detection | Log warning, treat block as preserved and skip translation |

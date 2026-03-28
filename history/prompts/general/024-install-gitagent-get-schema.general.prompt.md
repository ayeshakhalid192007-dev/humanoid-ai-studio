---
name: Install gitagent and get schema
description: Install @open-gitagent/gitagent, initialize with standard template, validate, and export all schemas
type: general
stage: general
date: 2026-03-28
surface: agent
model: claude-sonnet-4-6
feature: none
branch: main
user: ayeshakhalid
command: npm i @open-gitagent/gitagent && gitagent init --template standard && gitagent validate && gitagent info && gitagent export --format system-prompt
labels: ["gitagent", "installation", "schema", "agent"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - package.json
  - package-lock.json
  - agent.yaml
  - SOUL.md
  - RULES.md
  - AGENTS.md
  - skills/example-skill/SKILL.md
  - knowledge/index.yaml
  - memory/MEMORY.md
  - memory/context.md
  - memory/key-decisions.md
tests: []
---

## Prompt

Install gitagent in the project:

```
npm i @open-gitagent/gitagent
gitagent init --template standard
gitagent validate
gitagent info
gitagent export --format system-prompt
```

After installation give me its schema.

## Response

Successfully installed `@open-gitagent/gitagent` (60 packages), initialized with standard template, validated (0 warnings), and exported the system prompt. Retrieved all 7 JSON schemas from `node_modules/@open-gitagent/gitagent/spec/schemas/`.

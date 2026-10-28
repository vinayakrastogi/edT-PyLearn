# PyLearn — Agent Development Guide

**Welcome!** If you are an AI agent onboarding onto this project, read this document first. It contains everything you need to understand the architecture, structure, and design decisions of the PyLearn MVP without having to scan the entire codebase.

---

## System Architecture

PyLearn is a decoupled full-stack application designed with modularity as its core priority. It is built to teach Python to kids, but the architecture supports any content.

### Tech Stack
- **Frontend**: React, Vite, TypeScript, TailwindCSS v3, Zustand (state management), React Router v6.
- **Backend**: Python 3.11+, FastAPI, Uvicorn.
- **Database**: PostgreSQL (via Docker Compose), SQLAlchemy 2 (ORM), Alembic (Migrations).
- **Code Editor**: Monaco Editor (`@monaco-editor/react`).
- **Auth**: JWT stored in `httpOnly` cookies (no local storage). Supports local email/password and Google OAuth via Authlib.

### Core Architectural Decisions
1. **Decoupled Content Layer**: The course content (lessons, quizzes, problems) is **not** in the database. It lives in the `content/` directory as Markdown, YAML, and JSON files. The backend serves this via an abstract `ContentRepository`. The database only stores user progress, referenced by string slug IDs (e.g., `module_id="python-basics"`).
2. **Stateless API, Stateful Auth**: The FastAPI backend is mostly stateless. Auth is handled via a secure, `httpOnly` cookie containing a JWT. For Google OAuth, it uses `SessionMiddleware` to maintain the OAuth flow state. Axios on the frontend uses `withCredentials: true` to automatically attach the cookie.
3. **Secure-ish Code Execution**: User Python code is executed server-side using Python's `subprocess` module. A temporary directory is created for each submission, the code is run with a 5-second timeout, and then cleaned up. *Note: This is an MVP, so there is no heavy Docker sandboxing yet.*
4. **Neobrutalist UI**: The frontend adheres strictly to a Neobrutalist design system (bold colors, hard borders, offset solid shadows, dashboard grid layouts).
5. **Continuous Tracking**: The platform actively tracks a user's `last_accessed_path` and `last_accessed_title` in the DB to drive the "Continue Learning" dashboard card.

---

## Directory Structure

```text
edT/
├── content/                    # COURSE CONTENT (No DB changes needed to add content)
│   └── python-basics-demo/     # Example module
│       ├── module.yaml         # Module metadata
│       ├── docs/               # Markdown lessons with YAML frontmatter
│       ├── quiz.json           # Quiz data (answers stripped before sending to client)
│       └── problems/           # Coding problems (hidden tests stripped for client)
│
├── frontend/                   # FRONTEND APPLICATION
│   ├── tailwind.config.ts      # Core design tokens (shadows, colors, fonts)
│   └── src/
│       ├── api/                # Axios wrappers for backend endpoints
│       ├── components/         # Reusable Neobrutalist UI primitives
│       ├── modules/            # Feature-specific components (e.g., Question types)
│       ├── pages/              # Top-level route components
│       └── store/              # Zustand state (e.g., authStore)
│
└── backend/                    # BACKEND APPLICATION
    ├── alembic/                # DB Migrations
    └── app/
        ├── api/                # FastAPI Routers (auth, modules, quiz, problems, progress)
        ├── content_repository/ # Abstraction layer for content (file_repo.py reads /content)
        ├── core/               # Auth, DB engine, Config (pydantic-settings)
        ├── models/             # SQLAlchemy tables (User, Progress, etc.)
        ├── schemas/            # Pydantic models for request/response validation
        └── services/           # Business logic (grading.py, execution.py)
```

---

## Adding New Features

### 1. Adding New Course Content
You **do not** need to change code to add standard content. Just add files to the `content/` directory following the existing schemas (`module.yaml`, `quiz.json`, `problems/*.json`). The `FileSystemContentRepository` will automatically discover and serve them.

### 2. Adding a New Quiz Question Type
1. **Backend**: Update the `grade_quiz` function in `backend/app/services/grading.py` to handle the new question type's grading logic.
2. **Frontend**: Create a new UI component in `frontend/src/modules/QuestionTypes/` and register it in the `QUESTION_COMPONENTS` map inside `frontend/src/pages/QuizPage.tsx`.

### 3. Modifying the Database Schema
If you need to change a database table:
1. Update the SQLAlchemy model in `backend/app/models/`.
2. Run `source backend/venv/bin/activate && alembic revision --autogenerate -m "description"`.
3. Apply the migration: `alembic upgrade head`.

---

## Design System Guidelines (Frontend)

When generating or modifying frontend code, strictly adhere to the Neobrutalist design:
- **Never use Tailwind's default rounded corners or soft shadows.**
- Use `border-2 border-border-dark` for borders.
- Use `shadow-neo` or `shadow-neo-sm` for shadows.
- Primary colors: `brand-yellow`, `brand-blue`, `brand-pink`, `brand-green`, `brand-purple`.
- Use the predefined components (`<Button>`, `<Card>`, `<Badge>`, `<Input>`) instead of building from scratch.
- Maintain micro-animations on interactive elements (`hover:-translate-y-[2px] hover:shadow-neo-lg`).
- **No emoji, anywhere.** Use SVG icons from `lucide-react` (import them directly). Icons whose name comes from the server (badge `icon`, module `icon`) are kebab-case keys rendered with `<AppIcon name=...>` from `frontend/src/lib/icons.tsx`; XP is always `<XpIcon>`; big decorative icons on cards use `<IconTile>`. The logo is the SVG in `frontend/src/components/Logo.tsx`. Decorative icons get `aria-hidden`, icon-only buttons get an `aria-label`. `backend/tests/test_no_emoji.py` enforces this (code may not contain arrow characters either).

---

## Security & Data Flow Notes
- **Quiz Answers & Hidden Tests**: These are defined in the `content/` JSON files but must **never** be leaked to the frontend. The backend `FileSystemContentRepository` actively strips `correct_answer` and `hidden_tests` before serializing responses.
- **Passwords**: Hashed using `bcrypt` directly in `backend/app/core/security.py`. 
- **Progress Tracking**: `LessonProgress`, `QuizAttempt`, and `CodeSubmission` use `postgresql.JSONB` for extensible metadata (like per-question results).

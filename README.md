# PyLearn — Python Learning Platform (MVP)

A full-stack EdTech platform for teaching Python to kids. Built with a modular architecture designed for extensibility — adding new modules, question types, or content sources requires minimal code changes. **Now featuring AI-powered Generative Modules!**

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React + Vite + TypeScript + TailwindCSS v3 |
| Backend | Python 3.11+ · FastAPI · Uvicorn |
| Database | PostgreSQL 16 · SQLAlchemy 2 · Alembic |
| Code Editor | Monaco Editor (`@monaco-editor/react`) |
| Auth | JWT via httpOnly cookie · bcrypt passwords · Google OAuth (Authlib) |
| Dev DB | Docker Compose (Postgres + pgAdmin) |

## Design System — Neobrutalism

- **Bold hard-border cards** with offset shadows (`4px 4px 0px #1A1A1A`, no blur)
- **Base background**: `#FFF9E6` (warm cream — never pure white)
- **Fonts**: Space Grotesk (headings) · Space Mono (code/mono) · Inter (body)
- **Colors**: Yellow `#FFE135`, Blue `#3A86FF`, Pink `#FF4D6D`, Green `#00C875`, Purple `#8338EC`
- Micro-animations: bounce-in, slide-up, shake (error), press effect on buttons
- **Icons, never emoji**: every glyph in the UI is an SVG icon from [lucide-react](https://lucide.dev). Icons named by the server (badge and module icons) are kebab-case keys resolved by `frontend/src/lib/icons.tsx`; `backend/tests/test_no_emoji.py` fails the test suite if an emoji or pictographic symbol appears in code, lessons or docs
- **Logo**: an SVG of Pip's face on a yellow tile, drawn in `frontend/src/components/Logo.tsx` (`<Logo>` / `<LogoMark>`) and reused as the favicon (`frontend/public/favicon.svg`)

---

## Quick Start

For the separate LifeAdmin notes service, including two-device LAN setup, see
[LIFEADMIN_SETUP.md](LIFEADMIN_SETUP.md). Lesson notes use HTTP between independent
projects, with a server-side API key and separate databases.

### Docker startup (recommended)

Install and open Docker Desktop. On a fresh checkout, copy `.env.example` to
`.env` and add your AI / LifeAdmin API keys. Keep an existing `.env` if configured.
Then, from `edT`, run:

```bash
docker compose up -d --build
```

This starts PostgreSQL, the FastAPI backend and the built React frontend together.
Database migrations run automatically. Open `http://localhost:5173`; API docs are
at `http://localhost:8000/docs`. Demo login: `demostudent@example.com` / `demostudent` (student), or `demofaculty@example.com` / `demofaculty` (faculty).

Stop everything with `docker compose stop`. Data is preserved. LifeAdmin remains
a separate, manually started project. See [DOCKER_SETUP.md](DOCKER_SETUP.md) for
configuration, logs, optional pgAdmin and connecting to LifeAdmin on the host.

### Manual development alternative

Use this instead of the full Docker stack when editing the frontend/backend live.
Requires Python 3.11+ and Node.js 24+. Stop the full stack first to free its ports.

### 1. Clone and set up environment

```bash
cd edT
cp .env.example .env
```

### 2. Start only the database for manual development

```bash
docker compose up -d postgres
```

Postgres runs on `localhost:5432`. The optional pgAdmin service is described in the Docker guide.

### 3. Set up the backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

pip install -r requirements.txt

# Run Alembic migrations (creates all tables)
alembic upgrade head

# Start the API server
uvicorn app.main:app --reload --port 8000
```

API docs at `http://localhost:8000/docs`

### 4. Set up the frontend

```bash
cd frontend

# If you get "npm command not found", you may need to load NVM first:
# export PATH="/Users/vinayakrastogi/.nvm/versions/node/v24.12.0/bin:$PATH"

npm install
npm run dev
```

Frontend at `http://localhost:5173`

---

## Project Structure

```
edT/
├── docker-compose.yml          # Frontend + backend + Postgres; optional pgAdmin
├── .env.example                # All env vars documented
├── content/                    # Content files (not in source code!)
│   └── python-basics-demo/
│       ├── module.yaml
│       ├── docs/               # Markdown lessons with YAML frontmatter
│       ├── quiz.json           # Questions with correct answers (server-only)
│       └── problems/           # Problem JSON with hidden test cases (server-only)
├── frontend/
│   ├── tailwind.config.ts      # Full neobrutalist design token system
│   └── src/
│       ├── api/                # Axios functions per resource
│       ├── components/         # Shared UI primitives (Button, Card, Badge, Logo, etc.)
│       ├── lib/                # Helpers, incl. icons.tsx (icon keys -> lucide SVG icons)
│       ├── modules/            # Feature-specific components (QuestionTypes/)
│       ├── pages/              # Page components (all routes)
│       ├── store/              # Zustand stores
│       └── types/              # Shared TypeScript types
└── backend/
    └── app/
        ├── api/                # FastAPI route handlers
        ├── core/               # Config, auth, DB, deps
        ├── models/             # SQLAlchemy ORM models
        ├── schemas/            # Pydantic request/response schemas
        ├── content_repository/ # Abstraction layer (swap file→cloud here)
        └── services/           # Code execution + grading
```

---

## The Curriculum

10 modules, 89 lessons, about 90,000 words, with runnable examples, a module quiz (20+ questions, every answer explained) and 8-12 coding problems each.

| # | Module | Lessons |
|---|--------|:------:|
| 1 | Introduction to Python | 9 |
| 2 | Operators and Decision Making | 9 |
| 3 | Loops and Pattern Programming | 9 |
| 4 | Strings and Built-in Data Structures | 11 |
| 5 | Functions and Modular Programming | 8 |
| 6 | File Handling and Exception Handling | 8 |
| 7 | Object-Oriented Programming | 9 |
| 8 | Python Libraries and Basic Automation | 8 |
| 9 | Introduction to Data Science | 8 |
| 10 | Mini Projects (8 guided projects) | 9 |

Every lesson follows one template (hook, theory, code + output pairs, **Common Mistakes**, **Try It Yourself**, **Recap**). Code blocks in lessons have a **Run** button (executed in the sandbox) and "Try it yourself" blocks are editable. Charts drawn with Matplotlib appear under the output.

**Content is machine-checked.** `cd backend && python -m tools.check_content` runs every lesson example and compares its real output with the output shown in the lesson, checks every quiz, and runs every reference solution against its tests. See [CONTENT_GUIDE.md](CONTENT_GUIDE.md) to add or edit lessons.

### Pip the mascot

`frontend/src/components/Mascot.tsx` draws **Pip**, a placeholder python whose mood changes with the situation: celebrating on great quiz scores, sad on poor ones, confused/thinking on specific Python errors (`lib/pipReactions.ts`). The artwork is deliberately simple SVG: only the `MOODS` table and the drawing need to change to give Pip a proper design.

## Adding New Content

### Add a new module

1. Create `content/{module-id}/module.yaml`
2. Add docs in `content/{module-id}/docs/`
3. Add `quiz.json` and/or problems in `content/{module-id}/problems/`

No backend code changes required — the `FileSystemContentRepository` discovers modules by scanning the directory.

### Add a new question type

**Backend:** Add handling in `app/services/grading.py`'s `grade_quiz()` function.

**Frontend:** Create `src/modules/QuestionTypes/YourType.tsx` and add it to the component map in `QuizPage.tsx`:

```typescript
const QUESTION_COMPONENTS = {
  mcq: MCQQuestion,
  true_false: TrueFalseQuestion,
  fill_blank: FillBlankQuestion,  // ← add here only
}
```

### Swap content source (e.g. to Azure Blob)

1. Implement `ContentRepository` ABC in `backend/app/content_repository/`
2. Update `loader.py` to return your new implementation
3. Zero API or service changes required

---

## AI Generative Modules

The platform now supports fully automated, AI-driven curriculum generation using the **Groq API** and the **Llama-3.3-70b-versatile** model. 

1. **PDF Uploads**: Users can upload PDF study materials via the `Module 0 - Generative Content` tool on the dashboard.
2. **Instant Generation**: The AI analyzes the PDF text and strictly outputs a deeply detailed JSON schema containing markdown lessons, multiple-choice quizzes (with correct answers safely structured), and code practice problems (with starter code and hidden/visible test cases).
3. **Safe Storage & Management**: The backend safely converts the JSON into properly formatted `module.yaml` and `.md` files in the `/content` directory, instantly appearing on the user's dashboard prefixed with `generated-`.
4. **Clean Deletion**: AI-generated modules can be safely uninstalled and deleted directly from the Dashboard UI without affecting standard core modules.

---

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | /api/auth/signup | No | Create account, set cookie |
| POST | /api/auth/login | No | Login, set cookie |
| POST | /api/auth/logout | No | Clear cookie |
| GET | /api/auth/me | Cookie | Current user |
| GET | /api/auth/google/login | No | Redirect to Google OAuth |
| GET | /api/auth/google/callback | No | Google OAuth callback & JWT generation |
| GET | /api/modules | No | List all modules |
| GET | /api/modules/{id} | No | Module detail + lesson list |
| DELETE | /api/modules/{id} | Faculty | Delete an AI-generated module |
| GET | /api/modules/{id}/docs/{doc} | No | Rendered doc page |
| GET | /api/quiz/{module} | Cookie | Quiz questions (no answers) |
| POST | /api/quiz/{module}/submit | Cookie | Submit + grade quiz |
| GET | /api/quiz/{module}/attempts | Cookie | Attempt history |
| GET | /api/problems/{module}/{id} | Cookie | Problem (no hidden tests) |
| POST | /api/problems/{module}/{id}/submit | Cookie | Run code, grade, store |
| GET | /api/problems/{module}/{id}/submissions | Cookie | Submission history |
| POST | /api/progress/lesson-view | Cookie | Mark lesson as read |
| POST | /api/progress/track-access | Cookie | Track last visited location |
| GET | /api/progress/dashboard | Cookie | All-module progress |
| GET | /api/progress/{module} | Cookie | Per-module progress |
| POST | /api/run | Cookie | Run a snippet in the sandbox (rate limited, not graded) |
| POST | /api/generate/from-pdf | Faculty | Upload PDF, return AI-generated module JSON |
| POST | /api/generate/from-topic, /from-text, /from-url | Faculty | JSON body `{topic}` / `{text}` / `{url}` |
| POST | /api/generate/save-local | Faculty | Save AI JSON to disk as `module.yaml` & `.md` |

---

## Data Model

```text
users               → id, email, hashed_password, full_name, google_id, avatar_url, last_accessed_path, last_accessed_title, created_at
lesson_progress     → user_id, module_id, lesson_id, viewed_at, is_complete
quiz_attempts       → user_id, module_id, quiz_id, answers (JSONB), score, per_question_results (JSONB)
code_submissions    → user_id, module_id, problem_id, code, status, test_results (JSONB), stdout, stderr
```

Content IDs (module_id, lesson_id, etc.) are **string slugs** referencing content files — not DB foreign keys to rows. This keeps content and progress data fully decoupled.

---

## Development Notes

- **Code execution**: development uses a temporary directory, timeout and scrubbed environment. Production rejects local mode and uses an authenticated isolated runner or per-submission Docker containers with no network or application mounts; execution can also be disabled. See [DEPLOYMENT.md](DEPLOYMENT.md).
- **Problem kinds**: `function` (call the learner's function), `program` (feed stdin, compare stdout) and `driver` (append a script that exercises classes/files). Expected outputs are generated by running the reference solution (`tools/problem_builder.py`), so an answer key cannot be wrong.
- **Security**: content-generation and module-deletion routes are faculty-only; IDs are validated against path traversal; the URL generator blocks private addresses (SSRF); lessons are rendered client-side from Markdown, so raw HTML in generated content is never executed.
- **Tests**: `cd backend && python -m pytest tests` (grading, sandbox, security, API, and validation of all course content).
- **Hidden tests**: Never sent to client. Stored in `problems/*.json`, loaded server-side only.
- **JWT**: httpOnly cookie, 7-day expiry. Axios sends `withCredentials: true` on every request.
- **Content**: Correct quiz answers and hidden test cases are stripped in `FileSystemContentRepository` before the API responds.

---

## Running Alembic Migrations

```bash
cd backend
source venv/bin/activate

# Apply all migrations
alembic upgrade head

# Generate a new migration after model changes
alembic revision --autogenerate -m "your message"
```
# Web deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for shared cloud databases, HTTPS login settings,
same-origin hosting and isolated Python execution. Uploaded/generated files remain temporary.

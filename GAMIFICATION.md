# Gamification: XP, Levels, Streaks, Badges

PyLearn rewards *learning*, not clicking. Everything below is **server-authoritative** (the browser never says how much XP it earned) and **idempotent** (retrying a request, double-clicking or replaying a response can never double-award).

## Principles

1. **Reward first-time achievements, not repetition.** Re-reading a lesson or re-solving a problem earns nothing; improving a quiz score earns only the improvement.
2. **Best effort.** A bug in gamification must never break lessons, quizzes or grading. Endpoints wrap reward code in try/except and return `rewards: null` on failure.
3. **Kind by default.** Missing a day never wipes a long streak (freezes), leaderboards are opt-in and anonymised, and Pip's messages are encouraging.
4. **Core curriculum only.** Modules whose id starts with `generated-` (AI/faculty-made) earn no XP (they still extend the streak), so they cannot be used to farm XP.

## XP rules (constants live in `backend/app/services/gamification_rules.py`)

| Source | `kind` | XP | Ledger `ref_key` | Notes |
|--------|--------|----|------------------|-------|
| Lesson read | `lesson` | 10 | `{module_id}/{lesson_id}` | once per lesson |
| Module quiz | `quiz` | `round(50 * best_pct / 100)` as a **delta** | `{module_id}:{attempt_id}` | each attempt awards `target - already_awarded_for_module` if positive, where `target` uses the best percentage over all attempts of that module |
| Perfect quiz | `quiz_perfect` | 25 | `{module_id}` | once per module, when an attempt scores 100% |
| Problem solved | `problem` | easy 20 / medium 35 / hard 60 | `{module_id}/{problem_id}` | first `PASS` only |
| First-try solve | `problem_first_try` | 10 | `{module_id}/{problem_id}` | only if that PASS was the learner's very first submission for the problem |
| Module mastered | `module_complete` | 150 | `{module_id}` | all lessons read **and** all problems solved **and** quiz best >= 70% (parts a module lacks are ignored) |
| Daily goal | `daily_goal` | 10 | `{local_date}` | once per local day, the first time the day's XP (excluding this bonus) reaches the goal |
| Streak milestone | `streak_milestone` | 3d:15, 7d:50, 14d:100, 30d:250, 60d:500, 100d:1000 | `{days}` | once per milestone number, ever |

`generated-*` modules award none of the above except they still count as streak activity (the prefix is matched case-insensitively).

### Anti-farming guards (all server-side)

- **Quiz retries.** The answer key is shown after every submit, so an attempt only *counts* (quiz XP, perfect bonus, mastery, quiz badges) when it is the learner's first attempt at the module, or at least `QUIZ_RETRY_COOLDOWN` (12 h) after their previous attempt on it (counted from any previous attempt, so hammering the endpoint keeps the learner on cooldown). Attempts that do not count are still graded, saved and count as streak activity; they just pay nothing. Residual risk, accepted: a script can still wait out the cooldown after reading the key (at most about 75 XP per module, once).
- **Lesson pace.** A lesson pays XP only if `LESSON_MIN_GAP` (20 s) has passed since the learner's previous paid lesson. A view that is not paid is still saved and still counts as "read" everywhere (badges, module mastery, the UI), so what the learner sees always agrees with what counts; only the XP is withheld. Reading the lesson again later pays it.
- **Rate limits.** Quiz submits (10 per minute) and code submits (20 per minute) per learner, in memory per process (`QUIZ_SUBMIT_RATE_LIMIT_PER_MINUTE`, `CODE_SUBMIT_RATE_LIMIT_PER_MINUTE`); `answers` in a quiz submit are capped (at most 200 scalar values, text up to 500 characters).
- **Ids are validated before anything is saved.** Quiz and code submits 404 unless the module id (and problem id) are spelled exactly as the content spells them, so a case-insensitive filesystem cannot be used to store progress under extra spellings. Badge statistics additionally fold ids to lower case.

The ledger table `xp_events` has a **unique constraint on `(user_id, kind, ref_key)`**; awarding means "insert the event; if the unique constraint rejects it, it was already awarded". The cached `xp_total` on the profile is updated with an atomic SQL expression (`xp_total = xp_total + :amount`) in the same transaction as the insert.

## Levels

`xp_for_level(L) = 50 * L * (L - 1)` (cumulative XP at which level L starts): L1 = 0, L2 = 100, L3 = 300, L4 = 600, L5 = 1000, L10 = 4500, L20 = 19000. Level is capped at 99.

`xp_into_level = xp - xp_for_level(L)`, `xp_for_next_level = xp_for_level(L+1) - xp_for_level(L)` (so the progress bar is `xp_into_level / xp_for_next_level`), `next_level_xp = xp_for_level(L+1)`.

Titles by level (highest threshold <= level): 1 Hatchling, 2 Sprout, 3 Apprentice, 4 Bug Hunter, 5 Loop Rider, 6 Function Fan, 7 Class Act, 8 Data Explorer, 9 Automator, 10 Python Pro, 12 Code Wizard, 15 Grand Master, 20 Legend.

## Streaks

A **qualifying activity** is: reading a lesson, submitting a quiz, or submitting code (graded; pass or fail). Page views and the free "Run" button do not count. `POST /api/progress/track-access` no longer touches the streak.

Dates are the learner's **local** date: the browser sends `X-TZ-Offset: <minutes>` (JavaScript's `new Date().getTimezoneOffset()`, i.e. UTC minus local; IST = `-330`). The backend clamps it to `[-840, 840]` and falls back to `0` (UTC) when absent or invalid. `local_date = (utc_now - offset_minutes).date()`.

The header is chosen by the client, so it is not trusted blindly: the first offset a learner sends is stored on the profile (`tz_offset`, `tz_changed_at`) and a *different* offset is only believed `TZ_CHANGE_COOLDOWN` (6 h) after the previous change; until then the stored offset is used. The local date also never moves backwards (it is never earlier than the profile's `last_active_date` or `daily_xp_date`), so flying west does not wipe today's XP and flipping the header cannot mint extra days, streak milestones or daily-goal bonuses.

State (on the profile): `streak_count` mirrors `users.streak_count`, `longest_streak`, `streak_freezes` (0-2), `last_active_date`.

`compute_streak(last_active_date, today, count, freezes, longest)` is a pure function:

| Situation | Result |
|-----------|--------|
| `last_active_date is None` | count = 1 |
| `today == last_active_date` | unchanged (`extended = False`) |
| `today - last = 1 day` | count + 1 (`extended = True`) |
| `today - last = 2 days` and freezes > 0 | freeze spent (`used_freeze = True`), count + 1 |
| otherwise (gap too long, or `today < last` clock skew: treat as same day) | `broken_from = old count` (if old count > 1), count = 1 |

After a gap of **7+ days** an activity also records a one-off `comeback` marker (used by a badge; no XP). When the streak count reaches a multiple of 7 as a result of `extended`, the learner earns one freeze (max 2 banked). `longest_streak = max(longest, count)`. A milestone bonus (see XP table) fires when `count` first equals one of the milestone days.

A streak carried over from before gamification (the old page-view streak, kept if still alive) keeps its count and is shown straight away (reads agree with the first write), but its days were not earned by learning: they pay no streak-milestone XP (zero-XP ledger rows mark the milestones it already passed as paid) and do not raise `longest_streak`, which the streak badges read, until the learner really extends the streak.

`at_risk` (summary only): the learner was active yesterday, has a streak >= 1, and has not been active yet today.

## Daily goal

`daily_goal` (default 30; allowed 20, 30, 50, 80) and `daily_xp` / `daily_xp_date` (local date) on the profile. When the date changes `daily_xp` resets. `daily_xp` counts all XP earned that local day, *excluding* the daily-goal bonus itself. `just_met` is true on the response that crossed the goal. Lowering the goal below what was already earned today pays the (one-off) bonus immediately, from `PATCH /api/gamification/settings`; raising it again never pays a second one.

## Badges (catalogue in `backend/app/services/gamification_rules.py`)

Stored in `user_badges(user_id, badge_id, earned_at)` with a unique `(user_id, badge_id)`. Evaluated after every activity from a stats snapshot. `progress` = `{current, target}` (current is capped at target in the response).

**Icons.** A badge's `icon` is a kebab-case icon *key*, never an emoji. The frontend maps it to an SVG icon from [lucide-react](https://lucide.dev) through the `ICONS` table in `frontend/src/lib/icons.tsx` and renders it with `<AppIcon name={badge.icon}>` (an unknown key falls back to `book-open`, never to raw text). To give a badge a new icon, add the lucide component to `ICONS` first, then use its key in the catalogue. `backend/tests/test_no_emoji.py` fails if an emoji slips back in.

| id | name | icon key | category | rarity | condition |
|----|------|----------|----------|--------|-----------|
| first-lesson | First Steps | `book-open` | learning | common | lessons_read >= 1 |
| lessons-10 | Bookworm | `library` | learning | common | lessons_read >= 10 |
| lessons-30 | Scholar | `graduation-cap` | learning | rare | lessons_read >= 30 |
| lessons-all | Cover to Cover | `landmark` | learning | epic | lessons_read >= 80 |
| first-quiz | Quiz Rookie | `brain` | quizzes | common | quizzes_taken >= 1 |
| quiz-80 | Sharp Mind | `target` | quizzes | common | quizzes_80 >= 1 |
| perfect-quiz | Flawless | `gem` | quizzes | rare | perfect_quizzes >= 1 |
| quiz-champion | Quiz Champion | `trophy` | quizzes | rare | quizzes_80 >= 5 |
| first-solve | First Fix | `wrench` | coding | common | problems_solved >= 1 |
| solve-10 | Problem Solver | `puzzle` | coding | common | problems_solved >= 10 |
| solve-30 | Code Warrior | `swords` | coding | rare | problems_solved >= 30 |
| solve-75 | Bug Crusher | `bug` | coding | epic | problems_solved >= 75 |
| first-try-5 | Sharpshooter | `crosshair` | coding | rare | first_try_solves >= 5 |
| hard-solve | Tough Cookie | `cookie` | coding | rare | hard_solved >= 1 |
| hard-5 | Hard Mode | `mountain` | coding | epic | hard_solved >= 5 |
| streak-3 | On a Roll | `flame` | streaks | common | longest_streak >= 3 |
| streak-7 | Week Warrior | `zap` | streaks | rare | longest_streak >= 7 |
| streak-30 | Unstoppable | `rocket` | streaks | epic | longest_streak >= 30 |
| comeback | Comeback Kid | `sunrise` | streaks | common | comebacks >= 1 |
| goal-getter | Goal Getter | `calendar-check` | streaks | rare | daily_goals_met >= 7 |
| module-1 ... module-10 | Pythonista, Decision Maker, Loop Legend, Data Wrangler, Function Fan, File Detective, Object Architect, Automator, Data Scientist, Project Builder | `terminal` `git-branch` `repeat` `package` `square-function` `folder-search` `blocks` `bot` `chart-column` `hammer` | modules | rare | the module's `module_complete` event exists (module ids: `module-1-introduction-to-python`, `module-2-operators-decision-making`, `module-3-loops-pattern-programming`, `module-4-strings-data-structures`, `module-5-functions-modular`, `module-6-file-exception-handling`, `module-7-oop`, `module-8-libraries-automation`, `module-9-data-science`, `module-10-mini-projects`); badge ids `module-1` ... `module-10` |
| halfway-hero | Halfway Hero | `medal` | modules | epic | modules_completed >= 5 |
| python-graduate | Python Graduate | `crown` | modules | legendary | modules_completed >= 10 |
| level-5 | High Five | `hand` | levels | common | level >= 5 |
| level-10 | Double Digits | `award` | levels | epic | level >= 10 |
| xp-1000 | XP Collector | `sparkles` | levels | rare | xp_total >= 1000 |

Stats definitions (ids are compared case-insensitively): `lessons_read` = distinct lessons read in core modules (see "Lesson pace" above for which views count); `quizzes_taken` = distinct core modules with >= 1 quiz attempt; `quizzes_80` = distinct core modules whose best quiz % >= 80; `perfect_quizzes` = count of `quiz_perfect` events; `problems_solved` = distinct core problems with a PASS; `hard_solved` = of those, difficulty hard (difficulty is read from the ledger event's `meta`); `first_try_solves` = count of `problem_first_try` events; `modules_completed` = count of `module_complete` events; `daily_goals_met` = count of `daily_goal` events; `comebacks` = count of `comeback` events.

## Leaderboard

Weekly (rolling 7 days) XP among **opted-in** users (`show_on_leaderboard`, default **false**). Names are anonymised to first name + last initial (`"Asha K."`; a single plain name stays as is, cut to 15 characters). Only letter-only words (plus apostrophes and hyphens) are ever shown: an e-mail address, phone number or username is replaced by `"Learner"` and never echoed. Signup names are trimmed and limited to 100 characters. Top 10 plus the caller's own rank (`rank = null` when not opted in). Ties share the better rank and are ordered by name.

## API

All endpoints require login (cookie). JSON shapes: `backend/app/schemas/gamification.py` (and the TypeScript mirror `frontend/src/types/gamification.ts`).

| Method | Path | Returns |
|--------|------|---------|
| GET | `/api/gamification/me` | `GamificationSummary` |
| GET | `/api/gamification/badges` | `BadgeListResponse` (the whole catalogue with earned flags and progress) |
| GET | `/api/gamification/leaderboard` | `LeaderboardResponse` |
| PATCH | `/api/gamification/settings` | body `SettingsUpdate` -> `GamificationSummary` (strict: unknown keys and coerced values such as `"50"` or `"yes"` are a 422; `{}` is a no-op) |

Existing endpoints gain an optional `rewards: RewardSummary | null` field: `POST /api/progress/lesson-view` (`LessonProgressRecord`), `POST /api/quiz/{module}/submit` (`QuizSubmitResponse`), `POST /api/problems/{module}/{problem}/submit` (`CodeSubmitResponse`).

### Backend service interface (`backend/app/services/gamification.py`)

```python
def local_today(tz_offset_minutes: int | None, now: datetime | None = None) -> date
def record_lesson_read(db, user, module_id, lesson_id, *, tz_offset=None) -> RewardSummary
def record_quiz_attempt(db, user, module_id, attempt_id, percentage, *, detail, tz_offset=None) -> RewardSummary
def record_problem_submission(db, user, module_id, problem_id, *, difficulty, passed, prior_submissions, detail, tz_offset=None) -> RewardSummary
def get_summary(db, user, *, tz_offset=None) -> GamificationSummary
def list_badges(db, user) -> list[BadgeInfo]
def get_leaderboard(db, user, *, tz_offset=None) -> LeaderboardResponse
def update_settings(db, user, update: SettingsUpdate, *, tz_offset=None) -> GamificationSummary
def is_module_complete(db, user_id, module_id, detail) -> bool   # detail: ModuleDetail (docs, problems, quiz_id)
```

`record_*` functions commit their own transaction, always count as streak activity, and **always return a `RewardSummary`** (possibly with `xp_gained == 0`) so callers can attach it. They are idempotent: calling one twice with the same arguments awards XP once. `detail` is the already-loaded `ModuleDetail` (the endpoint does `await repo.get_module(...)`).

The tz offset comes from `get_tz_offset(request)` in `backend/app/core/deps.py` (reads `X-TZ-Offset`).

### Database

Migration `e8a2b3c4d5f6` (down revision `d7f1a2b3c4e5`) adds `gamification_profiles.tz_offset` / `tz_changed_at` and the index `ix_xp_events_created` on `xp_events(created_at)` that serves the weekly leaderboard (which aggregates in SQL and only loads the learners that can make the top 10). Migration `d7f1a2b3c4e5` (down revision `c5d8e9f12a34`) creates `gamification_profiles` (PK `user_id` -> users.id ON DELETE CASCADE; `xp_total`, `longest_streak`, `streak_freezes`, `last_active_date`, `daily_goal` default 30, `daily_xp`, `daily_xp_date`, `show_on_leaderboard` default false, `created_at`), `xp_events` (`id`, `user_id`, `kind`, `ref_key`, `amount`, `local_date`, `meta` JSON, `created_at`, **unique** `(user_id, kind, ref_key)`, index on `(user_id, created_at)`), and `user_badges`. It must work on PostgreSQL (the production target) and the models must also work on SQLite for tests (`JSONB` is only used elsewhere; use `sqlalchemy.JSON` for `meta`).

## Frontend

- **Icons**: everything is drawn with SVG icons, no emoji. XP is always shown with `<XpIcon>` (a filled yellow star), streaks with lucide's `Flame`, badges with `<AppIcon name={badge.icon}>` (from `frontend/src/lib/icons.tsx`); other glyphs are imported straight from `lucide-react`.
- **Navbar chip** (`components/gamification/XPChip.tsx`): level, level progress bar, XP and streak flame; links to `/achievements`. Hidden when signed out.
- **RewardHost** (mounted once in `App.tsx`): toast stack for XP (`+10 XP · Lesson read`, itemised for quizzes), and queued celebration modals: level-up (Pip celebrating + confetti), new badge(s) (Pip proud), streak milestone / freeze used / comeback (Pip happy/thinking). Accessible (`role="dialog"`, focus trap, Esc closes, `aria-live` toasts), respects reduced motion.
- **Dashboard "Your Journey"** card: level + XP bar, daily-goal ring, streak with freezes, 7-day XP chart, Pip nudge ("Do one lesson to keep your 5-day streak!"), recent badges, leaderboard card with the opt-in toggle.
- **`/achievements` page**: summary header, tabs (All / Earned / Locked) and category filter, badge grid (locked ones show progress bars), recent XP history.
- **Settings**: daily goal chips and leaderboard opt-in.
- Quiz result, lesson footer and problem result show the XP just earned.

## Testing

`cd backend && ./venv/bin/python -m pytest tests -q` (pure rule tests, SQLite-backed service/API tests). `cd frontend && npx tsc -b && npx oxlint && npx vite build`.

## Known limits

- **Local sandbox is not a security boundary.** With `SANDBOX_MODE=local`, learner code runs as the server user and could read `content/*/quiz.json` (the answer key) and hidden tests from disk. The quiz cooldown limits what that is worth, but the real fix is `SANDBOX_MODE=docker` (no host files, no network) in production.
- `PATCH /api/gamification/settings` may pay the one-off daily-goal bonus when a goal is lowered; its response is a summary (not a reward), so a level-up or badge from that bonus appears in the summary but without a celebration.
- The first `X-TZ-Offset` a learner sends is trusted; later changes are believed only after 6 hours.

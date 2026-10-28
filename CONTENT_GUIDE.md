# Content Authoring Guide

Everything a learner sees (lessons, quizzes, coding problems) lives in `content/<module-id>/`. This guide explains the format and the tools that keep the content correct.

```
content/module-1-introduction-to-python/
├── module.yaml            id, title, description, order, icon
├── docs/01-getting-started-with-python.md   lessons (Markdown + frontmatter)
├── quiz.json              20+ questions, each with an explanation
└── problems/01-rectangle-area.json          coding problems (generated, see below)
```

All commands below run from `backend/` with the project's virtual environment (`./venv/bin/python`).

## No emoji

PyLearn draws every symbol as an SVG icon, so **lessons, quizzes, problems, `module.yaml` and docs must not contain emoji** or pictographic symbols (check marks, crosses, stars, warning signs, hourglasses, play triangles...). Write the meaning in words instead:

- "Good:" / "Avoid:" (or "Right" / "Wrong") instead of a tick and a cross,
- "**Warning:**" or "**Tip:**" callouts instead of a warning sign or light bulb,
- `print("Blast off!")` instead of printing a rocket. If example code prints a symbol, the shown output has to change with it.

Plain typographic arrows in prose (`Input → Process → Output`) are fine. `python tests/test_no_emoji.py` lists every offending character with its file and line, and the same check runs as part of `python -m pytest tests`.

## module.yaml

```yaml
id: module-3-loops-pattern-programming   # must equal the folder name
title: "Module 3 - Loops and Pattern Programming"
description: "Master loops, iteration, and create beautiful patterns with code."
order: 3
icon: "repeat"                            # an icon key, not an emoji
```

`icon` is a kebab-case key that the frontend turns into an SVG icon (from [lucide-react](https://lucide.dev)). It must be one of the keys of `ICONS` in `frontend/src/lib/icons.tsx`:

`award` `blocks` `book-open` `bot` `brain` `bug` `calendar-check` `chart-column` `cookie` `crosshair` `crown` `flame` `folder-open` `folder-search` `gem` `git-branch` `graduation-cap` `hammer` `hand` `landmark` `library` `medal` `mountain` `package` `puzzle` `repeat` `rocket` `sparkles` `square-function` `sunrise` `swords` `target` `terminal` `trophy` `wrench` `zap`

Leave it out to get the default, `book-open` (an unknown key also falls back to it). To use a different icon, add the lucide component to `ICONS` first. The core modules use: module 1 `terminal`, 2 `git-branch`, 3 `repeat`, 4 `package`, 5 `square-function`, 6 `folder-open`, 7 `blocks`, 8 `bot`, 9 `chart-column`, 10 `rocket`, and the generative module `sparkles`.

## Lessons

### Frontmatter

```yaml
---
id: 06-type-conversion          # unique in the module; also used in URLs
title: "Type Conversion"
order: 6                        # 1..N with no gaps
concepts: ["type-conversion", "casting"]   # quiz questions link back to lessons through these
---
```

### Required structure

Every lesson needs at least 450 words, three runnable Python examples, and these headings (the validator checks them):

`## Common Mistakes` · `## Try It Yourself` · `## Recap`

A good lesson also opens with a real-world hook and ends with "Next up".

### Code blocks

| Fence | Meaning |
|-------|---------|
| ` ```python ` | runnable example (Run button). If followed by an ` ```output ` block, the real stdout **must match it** |
| ` ```output ` | the expected output, shown in a green panel under the code |
| ` ```python-try ` | editable "Try it yourself" block (must run without error) |
| ` ```text `, ` ```bash ` | static (copyable) blocks |

Flags go on the fence line:

| Flag | Effect |
|------|--------|
| `no-run` | never executed (network, GUI, platform-specific output) |
| `stdin="Asha\|7"` | supplies `input()` answers (`\|` separates lines); pre-fills the input box |
| `expect-error` | the block must fail; the last traceback line must equal the last line of the following ` ```output ` block |

Rules of thumb:

- **Each block is self-contained.** Blocks run in fresh empty folders, so create any file you read.
- Print `input()` prompts with `print()` and call a plain `input()`, so the output panel reads naturally.
- Do not show output that changes between runs (dates, random values, memory addresses): print *properties* (`len`, `True/False`) or use `random.seed`.
- Callouts are blockquotes that start with a bold label: `> **Pip says:** ...`, `**Tip:**`, `**Warning:**`, `**Important:**`, `**Fun fact:**`.

### Tools

```bash
python -m tools.lint_lessons module-1-introduction-to-python   # run every example, compare outputs
python -m tools.fill_outputs ../content/module-1-.../docs/03-x.md   # fill ```output blocks that contain just "?"
```

`fill_outputs` is a time saver for long outputs (patterns, tables): write `?` as the output, run the tool, then **read the result** to make sure it shows what the lesson claims.

## Quizzes

```python
# backend/tools/quizzes/m01.py
from tools.quiz_builder import mcq, tf, write_quiz

Q = [
    mcq("What is `7 // 2`?", ["3.5", "3", "4", "2"], 1,
        "Floor division drops the decimals.", ["arithmetic"]),
    tf("`=` compares two values.", False, "`=` assigns; `==` compares.", ["assignment"]),
]
write_quiz("module-1-introduction-to-python", "m1", "Module 1 Mastery Quiz", Q)
```

- 20+ questions, each with an **explanation**.
- `concepts` must be taught by some lesson in the same module. The results page uses them to say "review Lesson 4".
- `\`code\`` in question text, options and explanations is rendered as inline code.

## Coding problems

Problems are written in Python; expected outputs are **computed by running the reference solution**, so an answer key can never be wrong.

```python
# backend/tools/problems/m01.py
from tools.problem_builder import build

build("module-1-introduction-to-python", [
    dict(id="rectangle-area", title="Rectangle Area", kind="function", concepts=["operators"],
         description="Write `area(width, height)` returning the area.",
         starter="def area(width, height):\n    pass\n",
         solution="def area(width, height):\n    return width * height\n",
         visible=[[3, 4]], hidden=[[10, 2], [0, 7]],
         hints=["Multiply the two numbers."]),
])
```

| `kind` | Tests are | Compared |
|--------|-----------|----------|
| `function` | argument lists (a bare value is one argument) | the printed return value |
| `program` | stdin strings | the whole program's stdout |
| `driver` | scripts appended after the learner's code (classes, files, exceptions) | the script's stdout |

Optional keys: `difficulty` (`easy`/`medium`/`hard`), `hints` (revealed one at a time).

## Validate everything

```bash
python -m tools.check_content                       # all modules
python -m tools.check_content module-6-file-exception-handling
python -m pytest tests                              # the same checks plus the platform tests
```

The validator enforces: 7+ lessons per module, the lesson template, lesson code producing the printed output, quizzes with explanations and valid concepts, and every reference solution passing all of its own tests.

## Adding a module

1. Create `content/<module-id>/module.yaml` (the folder name must equal the `id`).
2. Write the lessons, quiz builder script and problems builder script as above.
3. Run `python -m tools.check_content <module-id>`.

Folders without a `module.yaml` are ignored by the platform.

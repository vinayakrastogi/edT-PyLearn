---
id: 05-project-quiz-app
title: "Project 4: Quiz Application"
order: 5
concepts: ["project-quiz", "classes-in-projects", "project-practice"]
---

# Project 4: Quiz Application

**Goal:** a quiz game that asks multiple-choice questions, scores the player, gives feedback and keeps a high-score table.

**Skills used:** classes, lists of objects, `random`, loops, input validation, JSON.

## Requirements

- Store questions with several options and one correct answer.
- Ask the questions in a random order, with the options shuffled.
- Accept only valid answers (a letter A-D).
- Give instant feedback and a final score with a message.
- Keep the top scores in a file.

## Design

Two small classes model the problem:

| Class | Data | Behaviour |
|-------|------|-----------|
| `Question` | text, options, index of the correct option | `is_correct(choice)`, `shuffled()` |
| `Quiz` | list of questions, score | `run(...)`, `percentage()` |

Keep the **logic** (checking answers, scoring) apart from the **input/output** (`input`, `print`) so that we can test it.

## Step 1: the `Question` class

```python
import random

class Question:
    def __init__(self, text, options, answer):
        if not 0 <= answer < len(options):
            raise ValueError("answer must be a valid option index")
        self.text = text
        self.options = list(options)
        self.answer = answer

    def is_correct(self, choice):
        return choice == self.answer

    def shuffled(self, rng=random):
        """Return a copy with the options in random order (and the answer index updated)."""
        correct_text = self.options[self.answer]
        options = self.options[:]
        rng.shuffle(options)
        return Question(self.text, options, options.index(correct_text))

    def __str__(self):
        letters = "ABCD"
        lines = [self.text] + [f"  {letters[i]}) {opt}" for i, opt in enumerate(self.options)]
        return "\n".join(lines)

q = Question("Which keyword defines a function?", ["func", "def", "define", "lambda"], 1)
print(q)
print(q.is_correct(1), q.is_correct(0))

s = q.shuffled(random.Random(3))
print(s.options[s.answer])
print(sorted(s.options) == sorted(q.options))
```

```output
Which keyword defines a function?
  A) func
  B) def
  C) define
  D) lambda
True False
def
True
```

`shuffled` must update the index of the correct answer, or the shuffled question would mark the wrong option correct. The last two lines check exactly that.

## Step 2: scoring and messages

```python
def score_message(percentage):
    if percentage == 100:
        return "Perfect score!"
    if percentage >= 80:
        return "Excellent work!"
    if percentage >= 50:
        return "Good effort. Keep practising!"
    return "Do not give up: review the lessons and try again."

for p in (100, 85, 60, 20):
    print(p, score_message(p))
```

```output
100 Perfect score!
85 Excellent work!
60 Good effort. Keep practising!
20 Do not give up: review the lessons and try again.
```

## Step 3: the `Quiz` class

```python
import random

class Question:
    def __init__(self, text, options, answer):
        self.text, self.options, self.answer = text, list(options), answer

    def shuffled(self, rng):
        correct = self.options[self.answer]
        options = self.options[:]
        rng.shuffle(options)
        return Question(self.text, options, options.index(correct))

class Quiz:
    def __init__(self, questions, seed=None):
        self.rng = random.Random(seed)
        self.questions = [q.shuffled(self.rng) for q in questions]
        self.rng.shuffle(self.questions)
        self.score = 0

    def answer(self, index, choice):
        """Record an answer to question number `index`; return True if correct."""
        correct = choice == self.questions[index].answer
        if correct:
            self.score += 1
        return correct

    def percentage(self):
        return round(100 * self.score / len(self.questions))

bank = [
    Question("2 + 2 = ?", ["3", "4", "5", "22"], 1),
    Question("Capital of India?", ["Mumbai", "Delhi", "Chennai", "Pune"], 1),
    Question("Python creator?", ["Guido", "Linus", "Ada", "Alan"], 0),
]
quiz = Quiz(bank, seed=1)
for i, q in enumerate(quiz.questions):
    quiz.answer(i, q.answer)          # answer everything correctly
print(quiz.score, quiz.percentage())

quiz = Quiz(bank, seed=1)
quiz.answer(0, (quiz.questions[0].answer + 1) % 4)
print(quiz.score, quiz.percentage())
```

```output
3 100
0 0
```

## Step 4: high scores

```python
import json

def load_scores(path):
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def record_score(path, name, percentage, keep=3):
    scores = load_scores(path)
    scores.append({"name": name, "score": percentage})
    scores.sort(key=lambda s: -s["score"])
    scores = scores[:keep]
    with open(path, "w") as f:
        json.dump(scores, f)
    return scores

for name, score in [("Asha", 80), ("Ravi", 60), ("Pip", 100), ("Zoya", 40), ("Kabir", 90)]:
    top = record_score("scores.json", name, score)
print([f"{s['name']}:{s['score']}" for s in top])
```

```output
['Pip:100', 'Kabir:90', 'Asha:80']
```

## Step 5: the complete game

The full program uses scripted answers here. The seed makes the shuffling repeatable so this example always behaves the same; a real game would pass no seed.

```python stdin="Asha|A|A|D|D"
import json
import random

QUESTIONS = [
    ("Which keyword defines a function?", ["func", "def", "define", "lambda"], 1),
    ("Which symbol starts a comment?", ["#", "//", "--", "/*"], 0),
    ("What does len('abc') return?", ["2", "3", "4", "abc"], 1),
    ("Which type is 3.14?", ["int", "str", "float", "bool"], 2),
]

def ask(question, number):
    text, options, answer = question
    order = list(range(len(options)))
    RNG.shuffle(order)
    print(f"Q{number}. {text}")
    for letter, i in zip("ABCD", order):
        print(f"  {letter}) {options[i]}")
    while True:
        reply = input().strip().upper()
        if reply in ("A", "B", "C", "D")[:len(options)]:
            break
        print("Please answer A, B, C or D")
    chosen = order["ABCD".index(reply)]
    if chosen == answer:
        print("Correct!")
        return True
    print("Wrong. The answer was:", options[answer])
    return False

RNG = random.Random(11)

def main():
    name = input().strip() or "Player"
    order = QUESTIONS[:]
    RNG.shuffle(order)
    score = 0
    for number, question in enumerate(order, start=1):
        if ask(question, number):
            score += 1
    percent = round(100 * score / len(order))
    print(f"{name}, you scored {score}/{len(order)} ({percent}%)")

main()
```

```output
Q1. Which keyword defines a function?
  A) def
  B) func
  C) define
  D) lambda
Correct!
Q2. Which symbol starts a comment?
  A) #
  B) /*
  C) --
  D) //
Correct!
Q3. What does len('abc') return?
  A) 4
  B) abc
  C) 2
  D) 3
Correct!
Q4. Which type is 3.14?
  A) str
  B) bool
  C) int
  D) float
Correct!
Asha, you scored 4/4 (100%)
```

## Testing

```python
class Question:
    def __init__(self, text, options, answer):
        self.text, self.options, self.answer = text, list(options), answer

import random
rng = random.Random(0)

def shuffled(q):
    correct = q.options[q.answer]
    opts = q.options[:]
    rng.shuffle(opts)
    return Question(q.text, opts, opts.index(correct))

q = Question("t", ["a", "b", "c", "d"], 2)
for _ in range(100):
    s = shuffled(q)
    assert s.options[s.answer] == "c", "the correct text must follow the shuffle"
print("quiz tests passed")
```

```output
quiz tests passed
```

## Ideas to extend it

1. **Load questions from a JSON file** so teachers can add their own.
2. **Categories and difficulty**, with the player choosing a category.
3. A **timer** per question using `time`.
4. **True/false and fill-in-the-blank** question types (inheritance: `Question` -> `TrueFalse`).
5. A **lifeline**: remove two wrong options ("50/50").
6. Show **review at the end**: which questions were wrong and the right answers.

## Common Mistakes

**1. Shuffling options but not updating the answer index.** The wrong option becomes "correct".

**2. Trusting the input.** Anything other than A-D must be rejected, not crash.

**3. Mutating the question bank** when shuffling. Copy first.

**4. Mixing scoring with printing.** Keep `answer` (logic) apart from `ask` (display).

```python
options = ["a", "b", "c"]
shuffled = options
shuffled.reverse()
print(options)
copy = options[:]
copy.reverse()
print(options, copy)
```

```output
['c', 'b', 'a']
['c', 'b', 'a'] ['a', 'b', 'c']
```

The first `reverse` also changed `options` because both names pointed to the same list.

## Try It Yourself

Add a `hint(question)` function that returns two options: the correct one and one wrong one (chosen at random, but always shown in alphabetical order), to implement a 50/50 lifeline.

```python-try
import random

def fifty_fifty(options, answer, rng=random):
    wrong = [i for i in range(len(options)) if i != answer]
    keep = rng.choice(wrong)
    return sorted([options[answer], options[keep]])

result = fifty_fifty(["3", "4", "5", "22"], 1, random.Random(2))
assert "4" in result and len(result) == 2
print(result)
```

**Challenge:** Give the player three lives; the game ends after the third wrong answer.

## Recap

- Model data with small classes (`Question`, `Quiz`) and keep logic separate from input/output.
- Shuffling options requires re-finding the index of the correct answer.
- Validate input in a loop until it is acceptable; use a seeded `random.Random` for repeatable tests.
- Store high scores in JSON, sort them and keep only the best few.
- Test tricky behaviour (like shuffling) with many repetitions.

**Next up:** Project 5, a **library management system**.

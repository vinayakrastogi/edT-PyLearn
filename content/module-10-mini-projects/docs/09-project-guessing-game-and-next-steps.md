---
id: 09-project-guessing-game-and-next-steps
title: "Project 8: Number-Guessing Game and Your Next Steps"
order: 9
concepts: ["project-guessing-game", "next-steps", "project-practice"]
---

# Project 8: Number-Guessing Game and Your Next Steps

You have reached the last lesson of the course. We finish with a classic that uses almost every idea you have learned (loops, functions, files, exceptions, random numbers and a bit of maths), and then look at where to go next.

**Goal:** the computer picks a secret number; the player guesses with "higher/lower" hints, a limited number of tries, difficulty levels and a saved best score.

## Requirements

- Three difficulty levels: easy (1-50, 10 tries), medium (1-100, 7 tries), hard (1-500, 9 tries).
- Give hints and count tries.
- Ignore invalid input without wasting a try.
- Remember the best (lowest) number of tries per level.
- Show a smart "optimal strategy" hint at the end.

## Design

| Function | Job |
|----------|-----|
| `judge(guess, secret)` | returns `"low"`, `"high"` or `"correct"` |
| `parse_guess(text, low, high)` | converts text to an in-range integer or raises `ValueError` |
| `play(secret, guesses, tries)` | runs one game on a list of guesses (testable!) |
| `load_best(path)` / `save_best(path, level, tries)` | persistence |
| `max_optimal_tries(low, high)` | how many guesses binary search needs |

## Step 1: the pure logic

```python
def judge(guess, secret):
    if guess < secret:
        return "low"
    if guess > secret:
        return "high"
    return "correct"

def parse_guess(text, low, high):
    try:
        number = int(text)
    except ValueError:
        raise ValueError(f"'{text.strip()}' is not a whole number")
    if not low <= number <= high:
        raise ValueError(f"guess must be between {low} and {high}")
    return number

print(judge(10, 42), judge(80, 42), judge(42, 42))
for text in ["50", " 7 ", "abc", "500", "0"]:
    try:
        print(parse_guess(text, 1, 100))
    except ValueError as e:
        print("Invalid:", e)
```

```output
low high correct
50
7
Invalid: 'abc' is not a whole number
Invalid: guess must be between 1 and 100
Invalid: guess must be between 1 and 100
```

## Step 2: playing a whole game (as a function)

Instead of reading input directly, `play` takes the guesses as an argument, which makes it easy to test. The real program feeds it `input()` values.

```python
def judge(guess, secret):
    return "low" if guess < secret else "high" if guess > secret else "correct"

def play(secret, guesses, max_tries):
    tries = 0
    for guess in guesses:
        tries += 1
        result = judge(guess, secret)
        if result == "correct":
            return True, tries
        print(f"  {guess} is too {result}. {max_tries - tries} tries left")
        if tries == max_tries:
            break
    return False, tries

won, tries = play(42, [50, 25, 37, 43, 42], 7)
print("won" if won else "lost", "in", tries)
won, tries = play(42, [1, 2, 3], 3)
print("won" if won else "lost", "in", tries)
```

```output
  50 is too high. 6 tries left
  25 is too low. 5 tries left
  37 is too low. 4 tries left
  43 is too high. 3 tries left
won in 5
  1 is too low. 2 tries left
  2 is too low. 1 tries left
  3 is too low. 0 tries left
lost in 3
```

## Step 3: best scores

```python
import json

def load_best(path):
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_best(path, level, tries):
    """Save only if it beats the old record. Return True for a new record."""
    best = load_best(path)
    if level not in best or tries < best[level]:
        best[level] = tries
        with open(path, "w") as f:
            json.dump(best, f)
        return True
    return False

print(load_best("best.json"))
print(save_best("best.json", "easy", 8))
print(save_best("best.json", "easy", 5))
print(save_best("best.json", "easy", 6))
print(save_best("best.json", "hard", 9))
print(load_best("best.json"))
```

```output
{}
True
True
False
True
{'easy': 5, 'hard': 9}
```

## Step 4: the maths of the best strategy

If you always guess the middle of the remaining range, every guess halves the possibilities (**binary search**). For a range of `n` numbers you need at most `ceil(log2(n + 1))` guesses.

```python
import math

def max_optimal_tries(low, high):
    return math.ceil(math.log2(high - low + 2))

def bot_guesses(secret, low, high):
    """Return the list of guesses a perfect player would make."""
    guesses = []
    while low <= high:
        mid = (low + high) // 2
        guesses.append(mid)
        if mid == secret:
            break
        if mid < secret:
            low = mid + 1
        else:
            high = mid - 1
    return guesses

print(bot_guesses(42, 1, 100))
print(max_optimal_tries(1, 50), max_optimal_tries(1, 100), max_optimal_tries(1, 500))
print(max(len(bot_guesses(n, 1, 100)) for n in range(1, 101)))
```

```output
[50, 25, 37, 43, 40, 41, 42]
6 7 9
7
```

That explains the levels: 7 tries is *just* enough on 1-100 for a perfect player, 9 tries is just enough on 1-500, and 10 tries on 1-50 gives a comfortable margin.

## Step 5: the complete game

With scripted input so it behaves the same each time (a real game picks `random.randint`).

```python stdin="medium|abc|500|50|25|37|43|42"
import json
import math
import random

LEVELS = {"easy": (1, 50, 10), "medium": (1, 100, 7), "hard": (1, 500, 9)}

def judge(guess, secret):
    return "low" if guess < secret else "high" if guess > secret else "correct"

def parse_guess(text, low, high):
    number = int(text)
    if not low <= number <= high:
        raise ValueError(f"between {low} and {high} please")
    return number

def main():
    print("Choose a level: easy, medium or hard")
    level = input().strip().lower()
    low, high, max_tries = LEVELS.get(level, LEVELS["medium"])
    secret = 42                       # random.randint(low, high) in the real game
    print(f"I am thinking of a number from {low} to {high}. You have {max_tries} tries.")
    tries = 0
    while tries < max_tries:
        try:
            guess = parse_guess(input(), low, high)
        except ValueError as e:
            print("Invalid guess:", e)
            continue
        tries += 1
        result = judge(guess, secret)
        if result == "correct":
            perfect = math.ceil(math.log2(high - low + 2))
            print(f"Correct! You needed {tries} tries (a perfect player needs at most {perfect}).")
            return
        print(f"Too {result}. {max_tries - tries} tries left.")
    print(f"Out of tries. The number was {secret}.")

main()
```

```output
Choose a level: easy, medium or hard
I am thinking of a number from 1 to 100. You have 7 tries.
Invalid guess: invalid literal for int() with base 10: 'abc'
Invalid guess: between 1 and 100 please
Too high. 6 tries left.
Too low. 5 tries left.
Too low. 4 tries left.
Too high. 3 tries left.
Correct! You needed 5 tries (a perfect player needs at most 7).
```

Notice that the two invalid guesses (`abc` and `500`) did **not** use up any tries: `continue` skips the counter.

## Testing

```python
def judge(guess, secret):
    return "low" if guess < secret else "high" if guess > secret else "correct"

def bot_guesses(secret, low, high):
    guesses = []
    while low <= high:
        mid = (low + high) // 2
        guesses.append(mid)
        if mid == secret:
            break
        low, high = (mid + 1, high) if mid < secret else (low, mid - 1)
    return guesses

assert judge(1, 2) == "low" and judge(3, 2) == "high" and judge(2, 2) == "correct"
for secret in range(1, 101):
    assert bot_guesses(secret, 1, 100)[-1] == secret
    assert len(bot_guesses(secret, 1, 100)) <= 7
print("game tests passed")
```

```output
game tests passed
```

Testing every possible secret (all 100!) with the bot is cheap and gives a strong guarantee.

## What you have learned

Look at the journey:

| Module | You learned | Used in these projects |
|--------|-------------|------------------------|
| 1 | variables, types, input/output | every program |
| 2 | decisions | validation, menus |
| 3 | loops | command loops, searches |
| 4 | strings, lists, tuples, sets, dictionaries | tasks, contacts, totals |
| 5 | functions and modules | all the helpers |
| 6 | files and exceptions | saving and error handling |
| 7 | object-oriented programming | library, bank, students |
| 8 | libraries and automation | dates, random, JSON |
| 9 | data science | charts and analysis |
| 10 | design and testing | everything above |

## Where to go next

**Deepen your Python**
- Generators, iterators, decorators, context managers.
- Type hints and `dataclasses`; virtual environments (`venv`) and `pip`.
- Testing with `pytest`; formatting with `black`; linting with `ruff`.
- Read other people's code on GitHub.

**Choose a direction**

| Interest | Learn next |
|----------|-----------|
| Websites | Flask or FastAPI, HTML/CSS/JavaScript, SQL databases |
| Data science / AI | pandas in depth, scikit-learn, then PyTorch or TensorFlow |
| Games | `pygame` |
| Automation | `selenium`, `openpyxl` (Excel), scheduling, APIs |
| Robotics / electronics | MicroPython, Raspberry Pi, Arduino |
| Computer science | algorithms and data structures, Big-O, recursion problems |

**Practise regularly**
- Solve problems on sites such as Codeforces, HackerRank, LeetCode and Advent of Code.
- Build something you personally want: a tool for a hobby, your school, your family.
- Put projects on **GitHub** and write a README for each.
- Explain what you learn to a friend; teaching cements understanding.

## Common Mistakes (of learners at this stage)

**1. Tutorial paralysis.** Watching and reading without building. Build things, even messy ones.

**2. Never reading error messages.** The last line of a traceback usually tells you what is wrong.

**3. Perfectionism.** Working code first; make it beautiful afterwards.

**4. Not asking for help.** Search the error message, read the documentation, ask a friend or a forum, and share a **small example** of the problem.

```python
def halve_until_one(n):
    steps = 0
    while n > 1:
        n //= 2
        steps += 1
    return steps

print(halve_until_one(100), halve_until_one(500))
```

```output
6 8
```

Halving 100 takes 6 steps, which is why binary search stays fast even on huge lists.

## Try It Yourself

Design your own project. Write three requirements, list the functions you would need, and then implement just the *first* function with an `assert` test. Here is an example for a "temperature guessing game" helper:

```python-try
def hint(guess, secret):
    difference = abs(guess - secret)
    if difference == 0:
        return "correct"
    if difference <= 5:
        return "hot"
    if difference <= 15:
        return "warm"
    return "cold"

assert hint(42, 42) == "correct"
assert hint(45, 42) == "hot"
assert hint(50, 42) == "warm"
assert hint(90, 42) == "cold"
print("hint tests passed")
```

**Final challenges:**
1. Let two players compete: whoever guesses in fewer tries wins.
2. Reverse the game: *you* think of a number and the computer guesses with binary search.
3. Build a tkinter window for the guessing game.
4. Combine two earlier projects (for example, the expense tracker with a chart dashboard).

## Recap

- The guessing game combined functions, loops, exceptions, files, `random` and maths.
- Keep pure logic (`judge`, `parse_guess`) separate from input/output so you can test it exhaustively.
- Binary search needs at most `ceil(log2(n + 1))` guesses.
- Keep learning by building real projects and reading other people's code.

**Congratulations! You have completed the PyLearn course.** Take the final quiz, celebrate with Pip, and start your next project. Every expert was once a beginner who kept going.

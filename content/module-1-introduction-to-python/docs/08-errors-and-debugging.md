---
id: 08-errors-and-debugging
title: "Errors and Debugging"
order: 8
concepts: ["errors", "debugging", "syntax-error"]
---

# Errors and Debugging

Here is a secret every programmer knows: **everyone gets errors, all the time**. Professionals see them dozens of times a day. The difference between a beginner and an expert is not that the expert avoids errors. It is that the expert *knows how to read them*. This lesson turns error messages from scary red text into helpful clues.

> **Pip says:** An error message is Python trying to help you. It is not telling you off!

## The three kinds of bugs

A mistake in a program is called a **bug**, and finding and fixing it is **debugging**. (The word comes from an actual moth found inside an early computer in 1947!) Bugs come in three flavours:

| Kind | When it appears | Example |
|------|-----------------|---------|
| **Syntax error** | Before the program starts. Python cannot understand the code. | a missing bracket |
| **Runtime error (exception)** | While running. Python understood, but the operation is impossible. | dividing by zero |
| **Logic error** | Never reported! The program runs but gives the wrong answer. | using `+` instead of `*` |

## Syntax errors

Python checks the grammar of your whole file first. If something is malformed, nothing runs at all.

```python expect-error
print("Hello"
```

```output
SyntaxError: '(' was never closed
```

Typical causes: a missing closing bracket or quote, a missing colon after `if`, or unbalanced indentation.

## Runtime errors (exceptions)

Here Python understood every line but hit something impossible while running. The most common ones:

| Error | Meaning | Trigger |
|-------|---------|---------|
| `NameError` | using a name that does not exist | a typo in a variable name |
| `TypeError` | wrong type for an operation | `"5" + 3` |
| `ValueError` | right type, unsuitable value | `int("abc")` |
| `ZeroDivisionError` | dividing by zero | `10 / 0` |
| `IndexError` | position does not exist | `"cat"[10]` |
| `IndentationError` | inconsistent spaces | mixed indentation |

```python expect-error
total = 10
print(totl)
```

```output
NameError: name 'totl' is not defined
```

## How to read a traceback

When an error occurs, Python prints a **traceback**. Here is a full one:

```text
Traceback (most recent call last):
  File "solution.py", line 3, in <module>
    result = 10 / count
ZeroDivisionError: division by zero
```

Read it from the **bottom up**:

1. **Last line:** the *type* of error and a short reason (`ZeroDivisionError: division by zero`).
2. **The line above it:** the exact code that failed.
3. **`line 3`:** where to look in your file.

That is nearly always enough to find the problem.

## Logic errors: the sneaky ones

The program runs without complaint but the answer is wrong. Python cannot detect this because it does not know what you *meant*.

```python
# Goal: average of two marks
mark1 = 80
mark2 = 90
average = mark1 + mark2 / 2
print(average)
```

```output
125.0
```

The average of 80 and 90 should be 85. The bug: division happens before addition. The fix is brackets: `(mark1 + mark2) / 2`.

## Debugging toolkit

**1. Print your variables.** The simplest and most powerful technique: show what is really inside.

```python
mark1 = 80
mark2 = 90
print("DEBUG mark2 / 2 =", mark2 / 2)
print("DEBUG sum =", mark1 + mark2)
average = (mark1 + mark2) / 2
print(average)
```

```output
DEBUG mark2 / 2 = 45.0
DEBUG sum = 170
85.0
```

**2. Test with tiny inputs** whose answers you already know.

**3. Read the error slowly**, starting with the last line.

**4. Rubber-duck debugging.** Explain your code, line by line, out loud to a rubber duck (or a patient friend). You will often spot the bug mid-sentence.

**5. Change one thing at a time**, then run again.

**6. Take a break.** A fresh mind sees mistakes a tired one misses.

## Common Mistakes

**1. Panicking and changing lots of code at once.** Fix one error, run, repeat.

**2. Ignoring the line number.** The bug is on that line, or on the line just before it (a forgotten bracket often shows up on the *next* line).

**3. Leaving debug prints in the final program.** Remove them when the bug is fixed.

**4. Assuming the computer is wrong.** It does exactly what you wrote. Ask what you actually wrote versus what you meant.

## Try It Yourself

This program is supposed to print the area of a rectangle, but it has a bug. Find it and fix it, then run again.

```python-try
length = 8
width = 5
area = length + width
print("Area is", area)
```

**Challenge:** Deliberately trigger each of `NameError`, `TypeError`, `ValueError` and `ZeroDivisionError` in separate programs and read each message.

## Recap

- Bugs are normal. Reading error messages is a skill you can learn.
- **Syntax errors** stop the program before it starts; **runtime errors** stop it midway; **logic errors** give wrong answers silently.
- Read a traceback from the bottom: the last line names the error, the line above shows the culprit code.
- Debug by printing values, testing small inputs, changing one thing at a time, and explaining the code aloud.

**Next up:** a lab where you combine everything from this module into three real programs.

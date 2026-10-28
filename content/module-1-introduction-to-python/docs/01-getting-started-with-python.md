---
id: 01-getting-started-with-python
title: "Getting Started with Python"
order: 1
concepts: ["python-basics", "running-python", "syntax", "comments"]
---

# Getting Started with Python

Imagine you want to teach a robot to make tea. You cannot just say "make tea" — you have to give it **clear, step-by-step instructions** in a language it understands. That is exactly what programming is: writing instructions for a computer. **Python** is one of the friendliest languages for doing it.

> **Pip says:** Every expert programmer once typed their very first `print("Hello")`. Today is your turn!

## What is Python?

Python is a **high-level, interpreted** programming language created by Guido van Rossum and first released in 1991. Let's unpack those two phrases:

- **High-level** means the code reads a lot like English, so you can focus on your idea instead of on how the computer's hardware works.
- **Interpreted** means Python reads your program one line at a time and runs it immediately. There is no separate "build" step.

### Where is Python used?

| Area | Example |
|------|---------|
| Web development | Instagram, Pinterest and Spotify use Python on their servers |
| Data science & AI | Analysing data, training machine-learning models |
| Automation | Renaming 1,000 files or sending reports automatically |
| Games & apps | Small games, desktop tools, robots |

## Your very first program

The classic first program prints a message on the screen. The tool that does this is the `print()` **function**.

```python
print("Hello, World!")
```

```output
Hello, World!
```

Here `print` is the function's name, the round brackets `( )` hold what we give to it, and `"Hello, World!"` is the text (called a **string**) we want to show. Quotes tell Python "this is text, not a command".

You can call `print()` as many times as you like. Python runs the lines **from top to bottom**.

```python
print("Welcome to Python!")
print("I am learning to code.")
print("This is fun.")
```

```output
Welcome to Python!
I am learning to code.
This is fun.
```

## Python can be your calculator

Numbers do not need quotes. Python does the maths and prints the answer.

```python
print(10 + 5)
print(10 - 3)
print(10 * 2)
print(10 / 4)
```

```output
15
7
20
2.5
```

## Installing Python and an editor

You can already run every example on this page with the **Run** button, but to build real projects you will want Python on your own computer.

1. **Windows:** download the installer from [python.org](https://www.python.org/downloads/). On the first screen tick **"Add Python to PATH"**, then click Install.
2. **macOS:** Python 3 is often present. You can also install it from python.org or with `brew install python`.
3. **Linux:** run `sudo apt install python3` (Ubuntu/Debian) or `sudo dnf install python3` (Fedora).

Check that it worked by opening a terminal and typing:

```bash
python --version
```

You should see something like `Python 3.12.4`. (On macOS/Linux you may need to type `python3`.)

For writing code, install a free editor such as **VS Code** and add its *Python* extension. It highlights your code in colour and points out mistakes.

## Two ways to run Python

**1. Interactive mode (the REPL).** Type `python` in the terminal and you get a `>>>` prompt where each line runs instantly. It is perfect for quick experiments.

```bash
>>> 2 + 3
5
>>> print("hi")
hi
>>> exit()
```

**2. Script mode.** Save your code in a file that ends in `.py` (for example `hello.py`) and run it with `python hello.py`. This is how real programs are run.

## Python syntax: the rules of the language

**Syntax** is the set of grammar rules Python expects. Three rules matter on day one:

1. **Python is case-sensitive.** `print` works, `Print` does not.
2. **Indentation matters.** Python uses spaces at the start of a line to group code together. Always use **4 spaces**.
3. **One statement per line** (normally).

```python
if 5 > 3:
    print("Five is bigger")
    print("This line is inside the if")
print("This line is outside")
```

```output
Five is bigger
This line is inside the if
This line is outside
```

We will study `if` properly in Module 2. For now, just notice how the two indented lines belong together.

## Comments: notes for humans

A **comment** starts with `#`. Python ignores everything after it. Use comments to explain *why* your code does something.

```python
# This whole line is a comment
print("Comments are ignored")  # a comment can also follow code
# print("This line will NOT run")
```

```output
Comments are ignored
```

> **Tip:** Commenting out a line (putting `#` in front) is a quick way to disable code without deleting it.

For longer notes, programmers often use a triple-quoted string as a **docstring**, which you will meet again in the Functions module.

## Common Mistakes

**1. Forgetting the quotes around text.** Python thinks `Hello` is a name it should already know.

```python expect-error
print(Hello)
```

```output
NameError: name 'Hello' is not defined
```

**2. Wrong capital letters.** `Print("hi")` fails because the function is called `print`.

```python expect-error
Print("hi")
```

```output
NameError: name 'Print' is not defined
```

**3. Bad indentation.** Mixing up spaces gives an `IndentationError`. Keep each block aligned to 4 spaces.

> **Reading errors:** the *last line* of an error message tells you what went wrong. The lines above it tell you *where*.

## Try It Yourself

Change the message, add another `print()` line, or try some maths, then press **Run**.

```python-try
# Introduce yourself!
print("Hi, my name is Pip")
print("2 + 2 =", 2 + 2)
```

**Challenge:** write a program that prints your name on the first line and your favourite food on the second line.

## Recap

- Python is a readable, beginner-friendly language used almost everywhere.
- `print()` shows text or numbers on the screen; text goes inside quotes.
- Python runs your code from top to bottom, one line at a time.
- Python is case-sensitive and uses indentation (4 spaces) to group code.
- `#` starts a comment, which Python ignores.

**Next up:** storing information in **variables**.

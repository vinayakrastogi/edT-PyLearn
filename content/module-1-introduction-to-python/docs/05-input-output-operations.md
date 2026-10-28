---
id: 05-input-output-operations
title: "Input and Output"
order: 5
concepts: ["input", "print", "f-strings", "output-formatting"]
---

# Input and Output

So far our programs have talked, but they have not *listened*. Real programs ask questions: "What is your name?", "How much money do you want to withdraw?". In this lesson you will learn to **read** from the user with `input()` and to **display** results beautifully with `print()`.

## Output with `print()`

You have used `print()` already. Here are the tricks that make it more powerful.

### Printing several things at once

Separate items with commas. Python puts a **space** between them.

```python
name = "Asha"
age = 12
print("Name:", name, "Age:", age)
```

```output
Name: Asha Age: 12
```

### The `sep` and `end` options

`sep` changes what goes *between* items. `end` changes what goes at the *end* (normally a new line).

```python
print("2025", "01", "15", sep="-")
print("Loading", end="...")
print("done!")
print("A", "B", "C", sep="")
```

```output
2025-01-15
Loading...done!
ABC
```

### Special characters (escape sequences)

A backslash `\` inside a string starts an **escape sequence**:

| Sequence | Meaning |
|:--------:|---------|
| `\n` | new line |
| `\t` | tab (a wide space) |
| `\\` | a backslash |
| `\"` | a double quote |

```python
print("Line one\nLine two")
print("Name\tScore")
print("Asha\t95")
print("She said \"hi\"")
```

```output
Line one
Line two
Name	Score
Asha	95
She said "hi"
```

## Formatting with f-strings

Joining text and numbers with `+` is clumsy. **f-strings** (formatted string literals) are the modern, readable way. Put an `f` before the opening quote and write variables inside `{ }`.

```python
name = "Asha"
marks = 92
print(f"{name} scored {marks} marks")
print(f"Next year {name} will be {marks + 5} marks better")
```

```output
Asha scored 92 marks
Next year Asha will be 97 marks better
```

You can even put small calculations inside the braces. Formatting details go after a colon:

```python
price = 49.5
pi = 3.14159265
big = 1234567
print(f"Price: {price:.2f}")
print(f"Pi is about {pi:.3f}")
print(f"Population: {big:,}")
print(f"Score: {7/9:.1%}")
```

```output
Price: 49.50
Pi is about 3.142
Population: 1,234,567
Score: 77.8%
```

- `:.2f` means "a float with **2** decimal places".
- `:,` adds thousands separators.
- `:.1%` shows a fraction as a percentage.

Alignment helps when printing tables:

```python
print(f"{'Item':<10}{'Qty':>5}")
print(f"{'Pen':<10}{3:>5}")
print(f"{'Notebook':<10}{12:>5}")
```

```output
Item        Qty
Pen           3
Notebook     12
```

`<` left-aligns and `>` right-aligns inside a field of the given width.

## Input with `input()`

`input()` pauses the program, waits for the user to type something and press Enter, then **returns what they typed**. You can pass it a *prompt* to display first:

```python no-run
name = input("What is your name? ")
print("Nice to meet you,", name)
```

In a real terminal, a run looks like this (the user typed `Asha`):

```text
What is your name? Asha
Nice to meet you, Asha
```

The Run button on this site has an **input box** where you type the answers *before* pressing Run. Because the answers are supplied up front, they are not echoed back in the output panel. That is why the examples below print their questions with `print()` and call a plain `input()`, so the output stays easy to read.

```python stdin="Asha"
print("What is your name?")
name = input()
print("Nice to meet you,", name)
```

```output
What is your name?
Nice to meet you, Asha
```

### Important: `input()` always returns a string

Even if the user types `25`, you receive the text `"25"`, not a number. Trying to do maths on it fails, as you will see in the next lesson on type conversion. The quick fix is to wrap `input()` in `int()` or `float()`.

```python stdin="25"
print("How old are you?")
age = int(input())
print(f"Next year you will be {age + 1}")
```

```output
How old are you?
Next year you will be 26
```

## A complete interactive program

```python stdin="Ravi|7|3"
print("Name?")
name = input()
print("First number?")
a = int(input())
print("Second number?")
b = int(input())
print(f"Hello {name}! {a} + {b} = {a + b}")
```

```output
Name?
First number?
Second number?
Hello Ravi! 7 + 3 = 10
```

## Common Mistakes

**1. Doing maths on the text that `input()` returned.**

```python stdin="5" expect-error
n = input()
print(n + 1)
```

```output
TypeError: can only concatenate str (not "int") to str
```

**2. Forgetting the `f` in front of an f-string.** Without it the braces are printed literally.

```python
score = 90
print("Score is {score}")
print(f"Score is {score}")
```

```output
Score is {score}
Score is 90
```

**3. Mismatched quotes** inside an f-string: `f"{d["a"]}"` can be a problem in older Python versions. Use different quote types inside and outside.

## Try It Yourself

Write a program that asks for a name and a favourite number, then prints a sentence using an f-string. Use the input box below the editor to provide your answers.

```python-try stdin="Pip|9"
print("Your name and favourite number?")
name = input()
number = int(input())
print(f"{name}'s number squared is {number ** 2}")
```

**Challenge:** Ask for the price of an item and the quantity; print the total with exactly 2 decimal places.

## Recap

- `print()` accepts many items, and `sep` / `end` control spacing and line endings.
- `\n` and `\t` are escape sequences for a new line and a tab.
- f-strings (`f"{value}"`) are the cleanest way to mix text and values; `:.2f` formats decimals.
- `input(prompt)` returns whatever the user types, **always as a string**.
- Use `int()` or `float()` around `input()` when you need a number.

**Next up:** converting between types.

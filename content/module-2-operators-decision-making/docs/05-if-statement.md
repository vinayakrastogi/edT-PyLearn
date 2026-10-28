---
id: 05-if-statement
title: "The if Statement"
order: 5
concepts: ["if-statement", "indentation", "conditions"]
---

# The if Statement

Until now your programs ran every line, top to bottom, no matter what. With the **`if` statement**, your program can *choose*: "**if** it is raining, take an umbrella." If the condition is not true, that step is skipped.

## Syntax

```text
if condition:
    statement(s) that run only when the condition is True
```

Three things to notice:

1. The **condition** is anything that evaluates to `True` or `False`.
2. The line ends with a **colon `:`**.
3. The code that belongs to the `if` is **indented** by 4 spaces. This block is called the **body**.

```python
temperature = 34
if temperature > 30:
    print("It is hot today!")
    print("Drink plenty of water.")
print("Have a nice day.")
```

```output
It is hot today!
Drink plenty of water.
Have a nice day.
```

The last line is not indented, so it belongs to the main program and always runs. Now with a cooler day:

```python
temperature = 22
if temperature > 30:
    print("It is hot today!")
    print("Drink plenty of water.")
print("Have a nice day.")
```

```output
Have a nice day.
```

The condition was `False`, so Python skipped the whole indented block.

## The flow of an if

```text
        +-------------+
   ---> | condition ? |--- False ---+
        +-------------+             |
              | True                |
              v                     |
        [ run the body ]            |
              |                     |
              v                     v
        [ continue with the rest of the program ]
```

## Conditions can be anything boolean

You can use every operator you have learned:

```python
password = "python123"
if password == "python123":
    print("Access granted")

name = "Asha"
if name in ["Asha", "Ravi"]:
    print("Welcome back,", name)

score = 85
if score >= 80 and score <= 100:
    print("Distinction")
```

```output
Access granted
Welcome back, Asha
Distinction
```

## Truthiness: shortcut conditions

Any value can act as a condition. Empty and zero values count as `False`, everything else as `True`.

```python
basket = []
if basket:
    print("Basket has items")
if not basket:
    print("Basket is empty")

name = "Pip"
if name:
    print("Hello,", name)
```

```output
Basket is empty
Hello, Pip
```

Writing `if basket:` is more idiomatic than `if len(basket) > 0:`.

## Multiple if statements

Independent `if` statements are all checked, one after the other:

```python
number = 12
if number > 10:
    print("Greater than 10")
if number % 2 == 0:
    print("Even")
if number % 3 == 0:
    print("Divisible by 3")
```

```output
Greater than 10
Even
Divisible by 3
```

## Indentation is meaning

In many languages braces `{ }` group code. In Python, **indentation is the grouping**. All lines in the same block must be indented by the same amount.

```python
x = 7
if x > 5:
    print("A")
    print("B")
print("C")
```

```output
A
B
C
```

Move `print("B")` one level out and it no longer belongs to the `if`. (It would then always run.)

## The `pass` placeholder

A block cannot be empty. When you want to write the structure now and fill it in later, use `pass`, which does nothing.

```python
age = 20
if age >= 18:
    pass  # TODO: add the adult-only code later
print("Done")
```

```output
Done
```

## Reading input in a condition

Combining `input()` with `if` gives your first interactive decision maker:

```python stdin="17"
print("How old are you?")
age = int(input())
if age >= 18:
    print("You can vote!")
print("Thanks for answering.")
```

```output
How old are you?
Thanks for answering.
```

Change the stdin to `20` in the Try It box below to see the other path.

## Common Mistakes

**1. Missing colon.**

```python expect-error
if 5 > 3
    print("yes")
```

```output
SyntaxError: expected ':'
```

**2. Forgetting to indent the body.**

```python expect-error
if 5 > 3:
print("yes")
```

```output
IndentationError: expected an indented block after 'if' statement on line 1
```

**3. Using `=` instead of `==` in a condition.** `if x = 5:` is a syntax error. Write `if x == 5:`.

**4. Inconsistent indentation.** Mixing 2 and 4 spaces (or tabs and spaces) breaks the block. Let your editor insert 4 spaces for the Tab key.

## Try It Yourself

Read a number and tell the user if it is positive, and if it is even. Try several inputs.

```python-try stdin="8"
print("Enter a whole number:")
n = int(input())
if n > 0:
    print("Positive")
if n % 2 == 0:
    print("Even")
print("Done")
```

**Challenge:** Ask for the temperature; if it is below 15, print "Wear a jacket".

## Recap

- `if condition:` followed by an indented body runs the body only when the condition is `True`.
- The colon and the 4-space indentation are mandatory.
- Any value can be a condition: `0`, `""`, `[]` and `None` are falsy.
- Independent `if` statements are each checked.
- Use `pass` as a placeholder for an empty block.

**Next up:** choosing between *two* paths with **if-else**.

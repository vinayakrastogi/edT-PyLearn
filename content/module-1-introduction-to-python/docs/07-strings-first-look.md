---
id: 07-strings-first-look
title: "Strings: A First Look"
order: 7
concepts: ["strings-basics", "indexing", "string-methods"]
---

# Strings: A First Look

Names, messages, passwords, tweets... most of the data people care about is **text**. In Python, text lives in a **string** (`str`). You have already created strings and joined them. In this lesson you will learn to *pick them apart* and *clean them up*. (Module 4 goes much deeper; this is your starter kit.)

## A string is a row of characters

Every character in a string has a position number called an **index**, and Python starts counting from **0**, not 1.

```text
 P   y   t   h   o   n
 0   1   2   3   4   5      (forward)
-6  -5  -4  -3  -2  -1      (backward)
```

Use square brackets to grab one character:

```python
word = "Python"
print(word[0])
print(word[3])
print(word[-1])
print(word[-2])
```

```output
P
h
n
o
```

Negative indexes count from the **end**, so `-1` is always the last character. This is handy when you do not know how long the string is.

## Length

```python
word = "Python"
print(len(word))
print(len("hello world"))
print(len(""))
```

```output
6
11
0
```

Spaces count as characters, too. The last valid index is always `len(word) - 1`.

## Slicing: cutting out a piece

`text[start:stop]` returns the characters from `start` up to, **but not including**, `stop`.

```python
word = "Programming"
print(word[0:3])
print(word[3:7])
print(word[:4])
print(word[7:])
print(word[::2])
print(word[::-1])
```

```output
Pro
gram
Prog
ming
Pormig
gnimmargorP
```

- Leave out `start` to begin at the beginning; leave out `stop` to go to the end.
- A third number is the **step**: `[::2]` takes every second character.
- `[::-1]` reads the string **backwards**. It is the classic trick for reversing text.

## Strings are immutable

You can read a character, but you cannot change one in place.

```python expect-error
word = "cat"
word[0] = "b"
```

```output
TypeError: 'str' object does not support item assignment
```

To "change" a string, build a new one:

```python
word = "cat"
new_word = "b" + word[1:]
print(new_word)
```

```output
bat
```

## Handy string methods

A **method** is a function that belongs to a value and is called with a dot: `text.method()`. Methods never change the original string (remember, strings are immutable). They **return a new one**.

```python
text = "  Hello, Python World  "
print(text.upper())
print(text.lower())
print(text.strip())
print(text.title())
print(text.replace("Python", "Java"))
```

```output
  HELLO, PYTHON WORLD  
  hello, python world  
Hello, Python World
  Hello, Python World  
  Hello, Java World  
```

| Method | What it does |
|--------|--------------|
| `.upper()` / `.lower()` | change letter case |
| `.title()` | Capitalise Each Word |
| `.strip()` | remove spaces from both ends |
| `.replace(old, new)` | swap text |
| `.find(sub)` | index of first match, or `-1` |
| `.count(sub)` | how many times `sub` appears |
| `.startswith(x)` / `.endswith(x)` | True/False checks |
| `.split()` | break into a list of words |

```python
sentence = "the quick brown fox jumps over the lazy dog"
print(sentence.count("the"))
print(sentence.find("fox"))
print(sentence.find("cat"))
print(sentence.startswith("the"))
print(sentence.split())
```

```output
2
16
-1
True
['the', 'quick', 'brown', 'fox', 'jumps', 'over', 'the', 'lazy', 'dog']
```

## Testing for text with `in`

The keyword `in` asks whether one string appears inside another:

```python
message = "Learning Python is fun"
print("Python" in message)
print("Java" in message)
print("python" in message)
```

```output
True
False
False
```

Uppercase and lowercase are different, so the last line is `False`. A common fix is to lowercase both sides: `"python" in message.lower()`.

## Joining and repeating

```python
words = ["Python", "is", "awesome"]
print(" ".join(words))
print("-".join(words))
print("=" * 15)
```

```output
Python is awesome
Python-is-awesome
===============
```

## Common Mistakes

**1. Off-by-one indexing.** The first character is `[0]`, and `word[len(word)]` is one step too far.

```python expect-error
word = "cat"
print(word[3])
```

```output
IndexError: string index out of range
```

**2. Expecting methods to change the original.** `text.upper()` does not modify `text`; you must save the result.

```python
name = "asha"
name.upper()
print(name)
name = name.upper()
print(name)
```

```output
asha
ASHA
```

**3. Forgetting the brackets on a method.** `text.upper` (no `()`) does not call it.

## Try It Yourself

Take a name and print it in capital letters, its length, its first and last letter, and reversed.

```python-try
name = "Priyanka"
print(name.upper())
print("Length:", len(name))
print("First:", name[0], "Last:", name[-1])
print("Reversed:", name[::-1])
```

**Challenge:** Given `email = "  Asha@Example.com "`, print a cleaned-up lowercase version with no surrounding spaces.

## Recap

- Strings are indexed from `0`; negative indexes count from the end.
- `len()` gives the length; slicing `[start:stop:step]` extracts pieces.
- Strings are immutable: methods return **new** strings.
- Useful methods: `upper`, `lower`, `strip`, `replace`, `find`, `count`, `split`, `join`.
- `in` checks whether text appears inside another string.

**Next up:** what to do when things go wrong: **errors and debugging**.

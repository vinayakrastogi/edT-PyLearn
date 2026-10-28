---
id: 04-membership-identity-operators
title: "Membership and Identity Operators"
order: 4
concepts: ["membership-operators", "identity-operators"]
---

# Membership and Identity Operators

Two more families of operators finish our toolkit for asking questions:

- **Membership operators** (`in`, `not in`) ask *"is this thing inside that collection?"*
- **Identity operators** (`is`, `is not`) ask *"are these two names pointing to the very same object?"*

## `in` and `not in`

`in` checks whether a value appears inside a string, list, tuple, set or dictionary. It returns a boolean.

```python
print("a" in "banana")
print("nan" in "banana")
print("z" in "banana")
print("z" not in "banana")
```

```output
True
True
False
True
```

With a string, `in` searches for a **substring**, meaning any run of characters, not just single letters.

### Membership in lists and tuples

```python
fruits = ["apple", "banana", "cherry"]
print("banana" in fruits)
print("grape" in fruits)
print("Banana" in fruits)
print(3 in (1, 2, 3))
```

```output
True
False
False
True
```

Matching is exact: `"Banana"` is not `"banana"`.

### Membership in dictionaries

For dictionaries, `in` checks the **keys**, not the values.

```python
ages = {"Asha": 12, "Ravi": 14}
print("Asha" in ages)
print(12 in ages)
print(12 in ages.values())
```

```output
True
False
True
```

### A tidy replacement for long `or` chains

These two conditions do the same thing, but the second is much shorter:

```python
letter = "e"
print(letter == "a" or letter == "e" or letter == "i" or letter == "o" or letter == "u")
print(letter in "aeiou")
```

```output
True
True
```

### Checking for vowels

```python
word = "education"
vowel_count = 0
for ch in word:
    if ch in "aeiou":
        vowel_count += 1
print(vowel_count)
```

```output
5
```

(The `for` and `if` lines are coming in Modules 2 and 3; the idea is "check each letter for membership".)

## `is` and `is not`

Every value lives in your computer's memory at some **address**. `is` asks whether two names refer to the *same object*, whereas `==` asks whether two objects have *equal contents*.

Think of two identical twins: they look the same (`==`) but they are two different people (`is not`).

```python
a = [1, 2, 3]
b = [1, 2, 3]
c = a
print(a == b)
print(a is b)
print(a is c)
print(id(a) == id(c))
```

```output
True
False
True
True
```

- `a == b` is `True`: same contents.
- `a is b` is `False`: two separate lists that happen to look alike.
- `c = a` does **not** copy; it makes `c` another name for the same list, so `a is c`.

This matters: change the list through one name and the other name sees it.

```python
a = [1, 2, 3]
c = a
c.append(4)
print(a)
```

```output
[1, 2, 3, 4]
```

### The one place you should use `is`: `None`

`None` is a single, unique object, so the correct way to test for it is `is None`.

```python
result = None
print(result is None)
print(result is not None)
value = 0
print(value is None)
print(value == None)
```

```output
True
False
False
False
```

Use `is None` / `is not None` (never `== None`). This is the style that Python programmers expect.

### Beware: `is` with numbers and strings

Python sometimes reuses small numbers and short strings, which can make `is` look like it works. Do not rely on it.

```python
x = 1000
y = 1000
print(x == y)
```

```output
True
```

Always use `==` to compare values. Reserve `is` for `None`, `True` and `False`.

## Summary table

| Operator | Question | Typical use |
|:--------:|----------|-------------|
| `in` | is it inside? | `"a" in text`, `x in my_list` |
| `not in` | is it missing? | `name not in used_names` |
| `is` | same object? | `x is None` |
| `is not` | different object? | `x is not None` |

## Common Mistakes

**1. Using `is` to compare values.** `if age is 18` may appear to work, then fail on other numbers. Use `==`.

**2. Expecting `in` on a dictionary to search values.** It searches keys; use `.values()` for values.

**3. Forgetting that `in` is case-sensitive.** `"py" in "Python"` is `False`.

```python
print("py" in "Python")
print("py" in "Python".lower())
```

```output
False
True
```

**4. Using `in` with a number on the right.**

```python no-run
print(3 in 123)
```

```text
TypeError: argument of type 'int' is not iterable
```

(The wording of this message varies slightly between Python versions.) The right-hand side of `in` must be a string, list, tuple, set or dictionary.

## Try It Yourself

Check whether a username is already taken, and whether a message contains a banned word. Then test a variable for `None`.

```python-try
taken = ["asha", "ravi", "pip"]
username = "pip"
print("Available:", username not in taken)

message = "this is spam"
print("Blocked:", "spam" in message)

nickname = None
print("No nickname yet:", nickname is None)
```

**Challenge:** Store a word in a variable and print whether it contains the letter `"q"`, and whether its first letter is a vowel (hint: `word[0] in "aeiou"`).

## Recap

- `in` / `not in` test membership in strings, lists, tuples, sets and dictionary keys.
- `is` / `is not` test whether two names refer to the same object; `==` tests equal values.
- Use `is None` / `is not None` for `None` and `==` for everything else.
- Assigning a list to another name does not copy it.

**Next up:** finally making the program *act* on these answers with the **`if` statement**.

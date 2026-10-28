---
id: 02-comparison-operators
title: "Comparison Operators"
order: 2
concepts: ["comparison-operators", "booleans"]
---

# Comparison Operators

A program that cannot make decisions is just a calculator. To decide anything, whether "is the password correct?" or "did the player win?", a program first needs to **compare** things. Comparison operators ask a yes/no question and answer with a boolean: `True` or `False`.

## The six comparison operators

| Operator | Question it asks | Example | Result |
|:--------:|------------------|---------|:------:|
| `==` | Are they equal? | `5 == 5` | `True` |
| `!=` | Are they different? | `5 != 5` | `False` |
| `>` | Is left greater? | `7 > 3` | `True` |
| `<` | Is left smaller? | `7 < 3` | `False` |
| `>=` | Greater or equal? | `7 >= 7` | `True` |
| `<=` | Smaller or equal? | `4 <= 3` | `False` |

```python
age = 15
print(age == 15)
print(age != 15)
print(age > 18)
print(age < 18)
print(age >= 15)
print(age <= 14)
```

```output
True
False
False
True
True
False
```

> **Important:** `=` **assigns**; `==` **compares**. Writing `age = 15` stores 15, while `age == 15` asks a question.

## Comparing different types

Numbers of different types compare by value:

```python
print(5 == 5.0)
print(3 < 3.5)
print(True == 1)
```

```output
True
True
True
```

Text is never equal to a number, even when it looks like it:

```python
print("5" == 5)
print("5" == str(5))
print(int("5") == 5)
```

```output
False
True
True
```

## Comparing strings

Strings are compared **letter by letter** using their character codes (dictionary order, with a twist: all capitals come before all lowercase letters).

```python
print("apple" == "apple")
print("apple" == "Apple")
print("apple" < "banana")
print("Zebra" < "apple")
print("cat" < "catalog")
```

```output
True
False
True
True
True
```

Why is `"Zebra" < "apple"` true? Capital `Z` has code 90 while lowercase `a` has code 97. To compare text without caring about case, convert both to the same case:

```python
print("Apple".lower() == "apple".lower())
```

```output
True
```

## Chained comparisons

Python lets you write maths-style ranges in a single expression:

```python
x = 15
print(10 < x < 20)
print(0 <= x <= 10)
print(1 == 1 < 2)
```

```output
True
False
True
```

`10 < x < 20` reads exactly as it does in maths: "x is between 10 and 20". In many languages you would need two comparisons joined together.

## Comparisons return booleans you can store

```python
marks = 72
passed = marks >= 40
distinction = marks >= 75
print(passed, distinction)
print(type(passed))
```

```output
True False
<class 'bool'>
```

Booleans are ordinary values. You can put them in variables, print them, and later use them to control your program.

## Comparing lists (a preview)

The same operators work on lists and tuples, comparing element by element:

```python
print([1, 2, 3] == [1, 2, 3])
print([1, 2, 3] < [1, 2, 4])
print((1, 5) > (1, 4))
```

```output
True
True
True
```

## Common Mistakes

**1. Using `=` instead of `==`.** In an `if` this is a syntax error; elsewhere it silently overwrites your variable.

```python
x = 5
x = 6   # meant to ask "is x equal to 6?" but this overwrites x
print(x)
```

```output
6
```

**2. Comparing text with numbers.** `"10" > 9` raises a `TypeError`. Convert first.

```python expect-error
print("10" > 9)
```

```output
TypeError: '>' not supported between instances of 'str' and 'int'
```

**3. Forgetting that comparing strings is case-sensitive.** `"Yes" == "yes"` is `False`.

**4. Float equality.** `0.1 + 0.2 == 0.3` is `False`. Use a tolerance.

## Try It Yourself

Check each statement about a shopper: do they have enough money for the item, is the item on sale price, is their age in the child ticket range (5 to 12)?

```python-try
money = 500
price = 450
age = 9
print("Can afford:", money >= price)
print("Exactly enough:", money == price)
print("Child ticket:", 5 <= age <= 12)
```

**Challenge:** Ask the user for a password with `input()` and print whether it equals `"python123"`.

## Recap

- `== != > < >= <=` compare values and return `True` or `False`.
- `=` assigns, `==` compares.
- Strings compare letter by letter and case matters; convert to one case to ignore it.
- Chained comparisons like `10 < x < 20` work as in maths.
- Convert types before comparing text to numbers.

**Next up:** combining questions with **logical operators**.

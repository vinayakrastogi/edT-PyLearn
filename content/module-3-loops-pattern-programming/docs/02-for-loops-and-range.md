---
id: 02-for-loops-and-range
title: "The for Loop and range()"
order: 2
concepts: ["for-loop", "range", "iteration"]
---

# The for Loop and range()

A `while` loop is like saying "keep stirring **until** it thickens". A `for` loop is like saying "stir **10 times**" or "**for each** ingredient in the list, add it to the pot". Use `for` when you know how many times to repeat or when you want to visit every item in a collection.

## Syntax

```text
for variable in sequence:
    body (runs once for each item)
```

Python takes the items of the sequence one at a time, puts each into `variable`, and runs the body.

```python
for fruit in ["apple", "banana", "cherry"]:
    print("I like", fruit)
```

```output
I like apple
I like banana
I like cherry
```

## Looping over a string

A string is a sequence of characters, so you can loop over it:

```python
for letter in "Pip":
    print(letter)
```

```output
P
i
p
```

## `range()`: a sequence of numbers

`range()` generates numbers for you. It has three forms:

| Form | Meaning | Example | Numbers |
|------|---------|---------|---------|
| `range(stop)` | 0 up to stop-1 | `range(5)` | 0 1 2 3 4 |
| `range(start, stop)` | start up to stop-1 | `range(2, 6)` | 2 3 4 5 |
| `range(start, stop, step)` | jump by step | `range(0, 10, 3)` | 0 3 6 9 |

The **stop** value is never included.

```python
for i in range(5):
    print(i, end=" ")
print()
for i in range(2, 6):
    print(i, end=" ")
print()
for i in range(0, 10, 3):
    print(i, end=" ")
print()
```

```output
0 1 2 3 4 
2 3 4 5 
0 3 6 9 
```

### Counting down

A negative step counts backwards. The start must be larger than the stop.

```python
for i in range(5, 0, -1):
    print(i, end=" ")
print("Go!")
```

```output
5 4 3 2 1 Go!
```

### Turning a range into a list

`list(range(...))` shows you exactly what a range contains:

```python
print(list(range(4)))
print(list(range(1, 11, 2)))
print(list(range(10, 0, -3)))
print(list(range(5, 5)))
```

```output
[0, 1, 2, 3]
[1, 3, 5, 7, 9]
[10, 7, 4, 1]
[]
```

## Repeating something N times

When you do not need the counter value itself, the convention is to call the variable `_`:

```python
for _ in range(3):
    print("Hip hip hooray!")
```

```output
Hip hip hooray!
Hip hip hooray!
Hip hip hooray!
```

## Accumulating with a for loop

```python
total = 0
for n in range(1, 101):
    total += n
print("Sum of 1 to 100:", total)
```

```output
Sum of 1 to 100: 5050
```

Young Carl Friedrich Gauss famously found this answer in seconds. Your computer does it in microseconds.

## Multiplication table

```python
number = 7
for i in range(1, 6):
    print(f"{number} x {i} = {number * i}")
```

```output
7 x 1 = 7
7 x 2 = 14
7 x 3 = 21
7 x 4 = 28
7 x 5 = 35
```

## `enumerate()`: index and value together

If you need the position of each item as well:

```python
names = ["Asha", "Ravi", "Pip"]
for index, name in enumerate(names):
    print(index, name)
for index, name in enumerate(names, start=1):
    print(f"{index}. {name}")
```

```output
0 Asha
1 Ravi
2 Pip
1. Asha
2. Ravi
3. Pip
```

## Looping with the length: `range(len(...))`

```python
word = "code"
for i in range(len(word)):
    print(i, word[i])
```

```output
0 c
1 o
2 d
3 e
```

Prefer `for letter in word` when you only need the letters, and `enumerate` when you need both.

## for versus while

| Use `for` when... | Use `while` when... |
|-------------------|---------------------|
| you know how many times to repeat | you repeat until something happens |
| you go through every item of a sequence | you wait for user input or a condition |
| counting from A to B | the number of repetitions is unknown |

## Common Mistakes

**1. Forgetting that the stop value is excluded.** `range(5)` gives 0 to 4. For 1 to 5 write `range(1, 6)`.

**2. Wrong direction.** `range(5, 0)` is empty because the default step is +1.

```python
print(list(range(5, 0)))
print(list(range(5, 0, -1)))
```

```output
[]
[5, 4, 3, 2, 1]
```

**3. Using a float in `range()`.**

```python expect-error
for i in range(2.5):
    print(i)
```

```output
TypeError: 'float' object cannot be interpreted as an integer
```

**4. Changing the list you are looping over** (adding or removing items). Loop over a copy instead.

## Try It Yourself

Print the squares of 1 to 10 and the even numbers from 2 to 20.

```python-try
for n in range(1, 11):
    print(n, "squared is", n ** 2)

for even in range(2, 21, 2):
    print(even, end=" ")
print()
```

**Challenge:** Print a countdown from 10 to 1 and then "Happy New Year!".

## Recap

- `for item in sequence:` visits each item in turn.
- `range(stop)`, `range(start, stop)`, `range(start, stop, step)` generate numbers; the stop is excluded.
- A negative step counts down.
- Use `_` when you do not need the loop variable; use `enumerate()` for index + value.
- Choose `for` when the repetition count is known; `while` when it is not.

**Next up:** steering a loop with **break**, **continue** and **pass**.

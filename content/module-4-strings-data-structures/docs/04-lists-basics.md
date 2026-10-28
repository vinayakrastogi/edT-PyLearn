---
id: 04-lists-basics
title: "Lists: Creating and Accessing"
order: 4
concepts: ["lists", "list-indexing", "list-slicing", "list-mutability"]
---

# Lists: Creating and Accessing

Up to now each variable held **one** value. But a shopping list, a class roll or a set of exam marks is a **collection**. Python's most-used collection is the **list**: an ordered, changeable sequence of items, written in square brackets.

## Creating lists

```python
fruits = ["apple", "banana", "cherry"]
marks = [78, 92, 85, 64]
mixed = [1, "two", 3.0, True]
empty = []
print(fruits)
print(marks)
print(mixed)
print(empty)
print(type(fruits))
```

```output
['apple', 'banana', 'cherry']
[78, 92, 85, 64]
[1, 'two', 3.0, True]
[]
<class 'list'>
```

Lists can hold any mix of types (though usually the items are related), and they can be empty. You can also make one from something else:

```python
print(list("abc"))
print(list(range(5)))
print([0] * 4)
print(["hi"] * 3)
```

```output
['a', 'b', 'c']
[0, 1, 2, 3, 4]
[0, 0, 0, 0]
['hi', 'hi', 'hi']
```

## Accessing items by index

Just like strings, list positions start at **0**; negative positions count from the end.

```python
colours = ["red", "green", "blue", "yellow"]
print(colours[0])
print(colours[2])
print(colours[-1])
print(colours[-2])
print(len(colours))
```

```output
red
blue
yellow
blue
4
```

## Slicing

`list[start:stop:step]` returns a **new list**.

```python
n = [10, 20, 30, 40, 50, 60]
print(n[1:4])
print(n[:3])
print(n[3:])
print(n[::2])
print(n[::-1])
print(n[-3:])
```

```output
[20, 30, 40]
[10, 20, 30]
[40, 50, 60]
[10, 30, 50]
[60, 50, 40, 30, 20, 10]
[40, 50, 60]
```

## Lists are mutable

Unlike strings, you **can change** a list in place.

```python
scores = [70, 80, 90]
scores[1] = 85
print(scores)
scores[0] += 5
print(scores)
scores[-1] = 100
print(scores)
```

```output
[70, 85, 90]
[75, 85, 90]
[75, 85, 100]
```

You can even replace a whole slice:

```python
n = [1, 2, 3, 4, 5]
n[1:3] = [20, 30, 99]
print(n)
```

```output
[1, 20, 30, 99, 4, 5]
```

## Looping through a list

```python
pets = ["cat", "dog", "parrot"]
for pet in pets:
    print("I have a", pet)
for i, pet in enumerate(pets, start=1):
    print(f"{i}. {pet}")
```

```output
I have a cat
I have a dog
I have a parrot
1. cat
2. dog
3. parrot
```

## Membership and built-in functions

```python
marks = [78, 92, 85, 64]
print(92 in marks)
print(50 not in marks)
print(len(marks))
print(sum(marks))
print(min(marks), max(marks))
print(sum(marks) / len(marks))
print(sorted(marks))
print(marks)
```

```output
True
True
4
319
64 92
79.75
[64, 78, 85, 92]
[78, 92, 85, 64]
```

`sorted()` gives you a **new** sorted list and leaves the original untouched.

## Joining and repeating lists

```python
a = [1, 2]
b = [3, 4]
print(a + b)
print(a * 3)
print(a)
```

```output
[1, 2, 3, 4]
[1, 2, 1, 2, 1, 2]
[1, 2]
```

## Unpacking

You can spread a list into separate variables:

```python
point = [3, 7]
x, y = point
print(x, y)
first, *rest = [10, 20, 30, 40]
print(first, rest)
*init, last = [10, 20, 30, 40]
print(init, last)
```

```output
3 7
10 [20, 30, 40]
[10, 20, 30] 40
```

## Nested lists (lists of lists)

Items can themselves be lists, which is perfect for grids and tables.

```python
grid = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9],
]
print(grid[0])
print(grid[1][2])
print(len(grid), len(grid[0]))
for row in grid:
    print(row)
```

```output
[1, 2, 3]
6
3 3
[1, 2, 3]
[4, 5, 6]
[7, 8, 9]
```

`grid[1][2]` means "row 1, then item 2 inside it".

## Common Mistakes

**1. Index out of range.**

```python expect-error
items = ["a", "b", "c"]
print(items[3])
```

```output
IndexError: list index out of range
```

The last valid index is `len(items) - 1`, which is why `items[-1]` is safer.

**2. Thinking `b = a` copies a list.** It creates a second *name* for the same list.

```python
a = [1, 2, 3]
b = a
b.append(4)
print(a)
c = a.copy()
c.append(5)
print(a, c)
```

```output
[1, 2, 3, 4]
[1, 2, 3, 4] [1, 2, 3, 4, 5]
```

**3. Building a grid with `[[0] * 3] * 3`.** All rows are the *same* list.

```python
bad = [[0] * 3] * 3
bad[0][0] = 9
print(bad)
good = [[0] * 3 for _ in range(3)]
good[0][0] = 9
print(good)
```

```output
[[9, 0, 0], [9, 0, 0], [9, 0, 0]]
[[9, 0, 0], [0, 0, 0], [0, 0, 0]]
```

**4. Confusing `sorted(x)` with `x.sort()`.** The first returns a new list; the second sorts in place and returns `None` (next lesson).

## Try It Yourself

Store five test marks, then print the highest, lowest, average, and the marks in descending order.

```python-try
marks = [72, 88, 95, 61, 79]
print("Highest:", max(marks))
print("Lowest:", min(marks))
print("Average:", sum(marks) / len(marks))
print("Sorted (high to low):", sorted(marks, reverse=True))
```

**Challenge:** Given `[3, 8, 1, 9]`, print the list reversed using slicing, and the first and last items using unpacking.

## Recap

- A list is an ordered, **mutable** collection written `[a, b, c]`.
- Index from 0 (or from the end with negatives); slice with `[start:stop:step]`.
- `len`, `sum`, `min`, `max`, `sorted`, `in` work on lists.
- `b = a` shares the same list; use `a.copy()` (or `a[:]`) for a copy.
- Lists can be nested to make grids: `grid[row][col]`.

**Next up:** **list methods** that add, remove and reorder items.

---
id: 07-tuples
title: "Tuples"
order: 7
concepts: ["tuples", "tuple-unpacking"]
---

# Tuples

A **tuple** is like a list that has been *locked*: an ordered collection whose contents cannot be changed after it is created. Think of the coordinates of a point on a map, `(12.97, 77.59)`, or the RGB values of a colour `(255, 128, 0)`. These belong together and should never be edited by accident. That is what tuples are for.

## Creating tuples

Tuples are written with round brackets (although it is the commas that really make a tuple).

```python
point = (3, 4)
colour = (255, 128, 0)
mixed = ("Asha", 12, True)
empty = ()
print(point)
print(colour)
print(mixed)
print(empty)
print(type(point))
```

```output
(3, 4)
(255, 128, 0)
('Asha', 12, True)
()
<class 'tuple'>
```

### The one-item tuple trap

A single value in brackets is *not* a tuple. You need a trailing comma.

```python
not_a_tuple = (5)
a_tuple = (5,)
print(type(not_a_tuple))
print(type(a_tuple))
print(len(a_tuple))
```

```output
<class 'int'>
<class 'tuple'>
1
```

### Brackets are optional

```python
t = 1, 2, 3
print(t)
print(tuple([7, 8, 9]))
print(tuple("hi"))
```

```output
(1, 2, 3)
(7, 8, 9)
('h', 'i')
```

## Accessing items

Indexing and slicing work exactly as for lists.

```python
days = ("Mon", "Tue", "Wed", "Thu", "Fri")
print(days[0])
print(days[-1])
print(days[1:4])
print(len(days))
print("Wed" in days)
```

```output
Mon
Fri
('Tue', 'Wed', 'Thu')
5
True
```

## Immutability

You cannot change, add or remove items.

```python expect-error
point = (3, 4)
point[0] = 10
```

```output
TypeError: 'tuple' object does not support item assignment
```

To "modify" a tuple, build a new one:

```python
point = (3, 4)
point = (10,) + point[1:]
print(point)
```

```output
(10, 4)
```

A tuple can contain a mutable item (like a list), and *that* item can still change:

```python
t = (1, [2, 3])
t[1].append(4)
print(t)
```

```output
(1, [2, 3, 4])
```

## Tuple methods

Only two, because tuples cannot change:

```python
t = (1, 2, 2, 3, 2)
print(t.count(2))
print(t.index(3))
```

```output
3
3
```

## Tuple unpacking

This is where tuples shine. Assign each item to its own variable in one line:

```python
point = (3, 4)
x, y = point
print(x, y)

name, age, city = ("Asha", 12, "Delhi")
print(f"{name} is {age} and lives in {city}")

a, b = 1, 2
a, b = b, a
print(a, b)
```

```output
3 4
Asha is 12 and lives in Delhi
2 1
```

The swap `a, b = b, a` is tuple packing and unpacking in action.

Use `*` to grab the rest:

```python
first, *middle, last = (1, 2, 3, 4, 5)
print(first, middle, last)
```

```output
1 [2, 3, 4] 5
```

## Returning several values from a function

Functions (Module 5) commonly return tuples so they can hand back more than one answer.

```python
def min_max(numbers):
    return min(numbers), max(numbers)

low, high = min_max([4, 9, 1, 7])
print(low, high)
print(min_max([4, 9, 1, 7]))
```

```output
1 9
(1, 9)
```

## Looping over a list of tuples

```python
students = [("Asha", 92), ("Ravi", 85), ("Pip", 78)]
for name, mark in students:
    print(f"{name}: {mark}")
print(sorted(students, key=lambda s: s[1]))
```

```output
Asha: 92
Ravi: 85
Pip: 78
[('Pip', 78), ('Ravi', 85), ('Asha', 92)]
```

## Tuples versus lists

| Feature | List `[ ]` | Tuple `( )` |
|---------|:---------:|:-----------:|
| Ordered | Yes | Yes |
| Changeable | Yes | **No** |
| Methods | many | `count`, `index` |
| Can be a dictionary key | No | **Yes** (if items are hashable) |
| Typical use | a collection that grows/changes | a fixed record, coordinates, multiple return values |
| Speed / memory | slightly heavier | slightly lighter |

```python
locations = {(0, 0): "start", (3, 4): "treasure"}
print(locations[(3, 4)])
```

```output
treasure
```

## Common Mistakes

**1. Forgetting the comma in a one-item tuple.** `(5)` is just `5`.

**2. Trying to modify a tuple.** Convert to a list, change it, and convert back if you really must.

```python
t = (1, 2, 3)
items = list(t)
items.append(4)
t = tuple(items)
print(t)
```

```output
(1, 2, 3, 4)
```

**3. Mismatched unpacking counts.**

```python expect-error
a, b = (1, 2, 3)
```

```output
ValueError: too many values to unpack (expected 2)
```

**4. Assuming a tuple is *deeply* frozen.** It only protects the items it directly holds.

## Try It Yourself

Store a person as a tuple, unpack it, and write a function that returns both the area and perimeter of a rectangle as a tuple.

```python-try
person = ("Pip", 9, "Chennai")
name, age, city = person
print(f"{name}, {age}, {city}")

def rectangle(w, h):
    return w * h, 2 * (w + h)

area, perimeter = rectangle(4, 6)
print("Area:", area, "Perimeter:", perimeter)
```

**Challenge:** Given `data = (10, 20, 30, 40, 50)`, print the first, the last, and the middle items using unpacking.

## Recap

- A tuple is an ordered, **immutable** collection: `(a, b, c)`.
- A one-item tuple needs a trailing comma: `(5,)`.
- Indexing, slicing, `len`, `in`, `count`, `index` all work.
- Unpacking (`x, y = point`) assigns each item to a variable; `*rest` collects extras.
- Use tuples for fixed records, multiple return values and dictionary keys.

**Next up:** **sets**, collections of unique items.

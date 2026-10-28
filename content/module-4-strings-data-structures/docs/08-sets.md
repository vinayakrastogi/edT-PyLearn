---
id: 08-sets
title: "Sets"
order: 8
concepts: ["sets", "set-operations"]
---

# Sets

Imagine a guest list where nobody can be listed twice and the order does not matter. Python's **set** is exactly that: an **unordered collection of unique items**. Sets are brilliant for removing duplicates, checking membership super-quickly and doing maths on groups (unions, intersections and so on).

## Creating sets

Sets use curly braces.

```python
fruits = {"apple", "banana", "cherry"}
print(len(fruits))
print("apple" in fruits)
print(type(fruits))
numbers = {1, 2, 2, 3, 3, 3}
print(numbers)
```

```output
3
True
<class 'set'>
{1, 2, 3}
```

Duplicates disappear automatically. Sets have **no order** and no indexes, so the printed order of strings can differ between runs. Do not rely on it.

### The empty set

`{}` makes an empty **dictionary**, not a set. Use `set()`.

```python
empty_dict = {}
empty_set = set()
print(type(empty_dict))
print(type(empty_set))
```

```output
<class 'dict'>
<class 'set'>
```

### From other collections: deduplication

The most common use of a set is removing duplicates:

```python
marks = [80, 90, 80, 70, 90, 100]
unique = set(marks)
print(len(marks), len(unique))
print(sorted(unique))
print(len(set("mississippi")))
```

```output
6 4
[70, 80, 90, 100]
4
```

## Adding and removing

| Method | Effect |
|--------|--------|
| `add(x)` | add one item (ignored if already present) |
| `update(iterable)` | add many items |
| `remove(x)` | remove; **error** if missing |
| `discard(x)` | remove; **no error** if missing |
| `pop()` | remove and return an arbitrary item |
| `clear()` | empty the set |

```python
s = {1, 2, 3}
s.add(4)
s.add(2)
print(sorted(s))
s.update([10, 20])
print(sorted(s))
s.remove(1)
s.discard(99)
print(sorted(s))
```

```output
[1, 2, 3, 4]
[1, 2, 3, 4, 10, 20]
[2, 3, 4, 10, 20]
```

Items must be **hashable** (immutable): numbers, strings and tuples are fine; lists and other sets are not.

```python expect-error
s = {1, [2, 3]}
```

```output
TypeError: cannot use 'list' as a set element (unhashable type: 'list')
```

## Set operations

Sets model the Venn diagrams from maths. Take two groups:

```python
python_club = {"Asha", "Ravi", "Meera", "Pip"}
chess_club = {"Ravi", "Pip", "Zoya"}
```

| Operation | Operator | Method | Meaning |
|-----------|:--------:|--------|---------|
| Union | `a \| b` | `a.union(b)` | in either |
| Intersection | `a & b` | `a.intersection(b)` | in both |
| Difference | `a - b` | `a.difference(b)` | in a but not b |
| Symmetric difference | `a ^ b` | `a.symmetric_difference(b)` | in exactly one |

```python
python_club = {"Asha", "Ravi", "Meera", "Pip"}
chess_club = {"Ravi", "Pip", "Zoya"}
print(sorted(python_club | chess_club))
print(sorted(python_club & chess_club))
print(sorted(python_club - chess_club))
print(sorted(chess_club - python_club))
print(sorted(python_club ^ chess_club))
```

```output
['Asha', 'Meera', 'Pip', 'Ravi', 'Zoya']
['Pip', 'Ravi']
['Asha', 'Meera']
['Zoya']
['Asha', 'Meera', 'Zoya']
```

(We used `sorted()` only to make the printed order predictable.)

### Comparing sets

```python
a = {1, 2}
b = {1, 2, 3}
print(a <= b)
print(a < b)
print(b >= a)
print({1, 2}.isdisjoint({3, 4}))
```

```output
True
True
True
True
```

- `a <= b`: `a` is a **subset** of `b`.
- `a < b`: proper subset (a subset and not equal).
- `isdisjoint`: they share nothing.

## Speed: membership tests

Checking `x in some_set` takes about the same time however big the set is, while `x in some_list` gets slower as the list grows. For large collections where you mostly test membership, a set is the right tool.

```python
big_list = list(range(100000))
big_set = set(big_list)
print(99999 in big_list)
print(99999 in big_set)
```

```output
True
True
```

Both answers agree, but the set answers instantly.

## Set comprehension

```python
words = ["apple", "Avocado", "banana", "Blueberry", "cherry"]
initials = {w[0].lower() for w in words}
print(sorted(initials))
print(sorted({n % 5 for n in range(20)}))
```

```output
['a', 'b', 'c']
[0, 1, 2, 3, 4]
```

## Practical examples

**Find common interests:**

```python
me = {"python", "chess", "music"}
friend = {"music", "football", "python"}
print("Shared:", sorted(me & friend))
print("Only me:", sorted(me - friend))
```

```output
Shared: ['music', 'python']
Only me: ['chess']
```

**Detect a duplicate:**

```python
def has_duplicates(items):
    return len(items) != len(set(items))

print(has_duplicates([1, 2, 3, 4]))
print(has_duplicates([1, 2, 3, 2]))
```

```output
False
True
```

## Frozen sets

A `frozenset` is an immutable set. It can be used as a dictionary key or a set element.

```python
fs = frozenset([1, 2, 3])
print(fs)
print(2 in fs)
```

```output
frozenset({1, 2, 3})
True
```

## Common Mistakes

**1. Writing `{}` for an empty set.** It is a dict; use `set()`.

**2. Expecting order or indexing.**

```python expect-error
s = {10, 20, 30}
print(s[0])
```

```output
TypeError: 'set' object is not subscriptable
```

**3. Using `remove()` on an item that may be absent.** Use `discard()`.

**4. Putting lists inside sets.** Convert them to tuples first.

## Try It Yourself

Two friends list the films they have watched. Find the films both have seen, the films only Asha has seen, and the total number of different films.

```python-try
asha = {"Frozen", "Up", "Coco", "Moana"}
ravi = {"Up", "Cars", "Coco"}
print("Both:", sorted(asha & ravi))
print("Only Asha:", sorted(asha - ravi))
print("All different films:", len(asha | ravi))
```

**Challenge:** Given a sentence, print how many *different* words it has, ignoring capitals.

## Recap

- A set holds **unique**, **unordered** items: `{1, 2, 3}`; use `set()` for an empty one.
- `add`, `update`, `remove` / `discard`, `pop` change a set; there is no indexing.
- Union `|`, intersection `&`, difference `-`, symmetric difference `^`.
- `set(list)` removes duplicates; membership tests on sets are very fast.
- Set items must be hashable (immutable).

**Next up:** **dictionaries**, key-value stores.

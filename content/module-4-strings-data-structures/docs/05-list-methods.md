---
id: 05-list-methods
title: "List Methods"
order: 5
concepts: ["list-methods", "sorting", "list-copying"]
---

# List Methods

Because lists are mutable, they come with many **methods** to grow, shrink and rearrange them. The key thing to remember: most list methods change the list **in place** and return `None`. That is the opposite of string methods, which return new strings.

## Adding items

| Method | What it does |
|--------|--------------|
| `append(x)` | add `x` at the end |
| `insert(i, x)` | put `x` at position `i` |
| `extend(iterable)` | add every item of another collection |

```python
nums = [1, 2, 3]
nums.append(4)
print(nums)
nums.insert(0, 0)
print(nums)
nums.extend([5, 6])
print(nums)
nums.append([7, 8])
print(nums)
```

```output
[1, 2, 3, 4]
[0, 1, 2, 3, 4]
[0, 1, 2, 3, 4, 5, 6]
[0, 1, 2, 3, 4, 5, 6, [7, 8]]
```

Notice the difference: `extend` adds the *items*, `append` adds the argument as *one* item (here, a nested list).

## Removing items

| Method | What it does |
|--------|--------------|
| `remove(x)` | delete the first item equal to `x` |
| `pop()` | remove and **return** the last item |
| `pop(i)` | remove and return the item at index `i` |
| `del list[i]` | delete by index (a statement, not a method) |
| `clear()` | empty the list |

```python
letters = ["a", "b", "c", "d", "e"]
letters.remove("b")
print(letters)
last = letters.pop()
print(last, letters)
first = letters.pop(0)
print(first, letters)
del letters[0]
print(letters)
letters.clear()
print(letters)
```

```output
['a', 'c', 'd', 'e']
e ['a', 'c', 'd']
a ['c', 'd']
['d']
[]
```

## Searching

```python
data = [5, 3, 8, 3, 9]
print(data.index(8))
print(data.count(3))
print(3 in data)
print(data.index(3))
```

```output
2
2
True
1
```

`index(x)` returns the **first** position of `x`.

## Sorting and reversing

```python
n = [5, 2, 9, 1, 7]
n.sort()
print(n)
n.sort(reverse=True)
print(n)
n.reverse()
print(n)
```

```output
[1, 2, 5, 7, 9]
[9, 7, 5, 2, 1]
[1, 2, 5, 7, 9]
```

### `sort()` versus `sorted()`

```python
original = [3, 1, 2]
new_list = sorted(original)
print(original, new_list)
result = original.sort()
print(original, result)
```

```output
[3, 1, 2] [1, 2, 3]
[1, 2, 3] None
```

`sorted()` returns a new list; `.sort()` changes the list itself and returns `None`. A classic bug is writing `nums = nums.sort()` and ending up with `None`.

### Custom sorting with `key`

```python
words = ["banana", "kiwi", "apple", "fig"]
words.sort()
print(words)
words.sort(key=len)
print(words)
names = ["bob", "Alice", "carol", "Dave"]
print(sorted(names))
print(sorted(names, key=str.lower))
```

```output
['apple', 'banana', 'fig', 'kiwi']
['fig', 'kiwi', 'apple', 'banana']
['Alice', 'Dave', 'bob', 'carol']
['Alice', 'bob', 'carol', 'Dave']
```

`key` is a function applied to each item to decide the sort order: here the length. Python's sort is *stable*, so items with equal keys keep their original relative order.

## Copying lists

```python
a = [1, 2, 3]
b = a.copy()
c = a[:]
d = list(a)
b.append(99)
print(a, b, c, d)
```

```output
[1, 2, 3] [1, 2, 3, 99] [1, 2, 3] [1, 2, 3]
```

These make **shallow** copies: the outer list is new, but nested lists inside are still shared.

```python
import copy
matrix = [[1, 2], [3, 4]]
shallow = matrix.copy()
deep = copy.deepcopy(matrix)
matrix[0][0] = 99
print(shallow)
print(deep)
```

```output
[[99, 2], [3, 4]]
[[1, 2], [3, 4]]
```

## Method cheat sheet

| Task | Code |
|------|------|
| add at end | `lst.append(x)` |
| add several | `lst.extend(other)` |
| insert at position | `lst.insert(i, x)` |
| remove by value | `lst.remove(x)` |
| remove by position / take out | `lst.pop(i)` |
| sort in place / new list | `lst.sort()` / `sorted(lst)` |
| reverse in place | `lst.reverse()` |
| count / find | `lst.count(x)` / `lst.index(x)` |

## Removing while looping: a trap

```python
nums = [1, 2, 3, 4, 5, 6]
for n in nums:
    if n % 2 == 0:
        nums.remove(n)
print(nums)
```

```output
[1, 3, 5]
```

That happened to work here, but not in general: deleting while iterating skips items. Try it with `[2, 4, 6, 8]`:

```python
nums = [2, 4, 6, 8]
for n in nums:
    if n % 2 == 0:
        nums.remove(n)
print(nums)
```

```output
[4, 8]
```

Every even number should have been removed! The safe approach is to build a **new** list:

```python
nums = [2, 4, 6, 8, 9]
odds = [n for n in nums if n % 2 != 0]
print(odds)
```

```output
[9]
```

## Common Mistakes

**1. `nums = nums.sort()`** assigns `None`.

```python
nums = [3, 1, 2]
nums = nums.sort()
print(nums)
```

```output
None
```

**2. `remove()` on a missing value** raises `ValueError`. Check `if x in lst` first.

```python expect-error
[1, 2, 3].remove(9)
```

```output
ValueError: list.remove(x): x not in list
```

**3. Using `append` where you meant `extend`.**

**4. `pop()` on an empty list** raises `IndexError`.

## Try It Yourself

Manage a to-do list: add three tasks, remove one, sort them alphabetically and print the result.

```python-try
tasks = []
tasks.append("write report")
tasks.append("buy milk")
tasks.append("call Ravi")
tasks.remove("buy milk")
tasks.sort()
print(tasks)
print("Tasks left:", len(tasks))
```

**Challenge:** Given `[5, 3, 5, 1, 5]`, remove *every* 5 (hint: build a new list, or use a `while 5 in lst` loop).

## Recap

- Add with `append`, `insert`, `extend`; remove with `remove`, `pop`, `del`, `clear`.
- List methods change the list in place and return `None`.
- `sort()` is in place; `sorted()` gives a new list; `key=` customises the order.
- `copy()` / `[:]` make shallow copies; use `copy.deepcopy` for nested lists.
- Do not remove items from a list while looping over it; build a new list instead.

**Next up:** **list comprehensions** and working with 2-D lists.

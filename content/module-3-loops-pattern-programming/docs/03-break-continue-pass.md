---
id: 03-break-continue-pass
title: "break, continue and pass"
order: 3
concepts: ["break", "continue", "pass", "loop-else"]
---

# break, continue and pass

Normally a loop runs from start to finish. But sometimes you need to **stop early** ("I found what I was looking for"), **skip** one round ("that item does not count"), or **leave a placeholder** while you are still designing. Python gives you three small keywords for exactly this.

## `break`: leave the loop immediately

When Python meets `break`, it exits the **innermost** loop right away and continues with the code after the loop.

```python
for n in range(1, 10):
    if n == 4:
        print("Found 4, stopping")
        break
    print(n)
print("After the loop")
```

```output
1
2
3
Found 4, stopping
After the loop
```

### Searching for something

`break` is perfect for searches: once you have the answer, there is no need to keep looking.

```python
names = ["Asha", "Ravi", "Meera", "Pip", "Zoya"]
target = "Pip"
for position, name in enumerate(names):
    if name == target:
        print(f"Found {target} at position {position}")
        break
```

```output
Found Pip at position 3
```

### Breaking out of an "infinite" loop

`while True:` loops forever *unless* something inside calls `break`. It is a common way to write "keep going until the user says stop".

```python stdin="3|8|quit"
total = 0
while True:
    text = input()
    if text == "quit":
        break
    total += int(text)
print("Total:", total)
```

```output
Total: 11
```

## `continue`: skip to the next round

`continue` abandons the **rest of the current iteration** and jumps straight to the next one.

```python
for n in range(1, 8):
    if n % 2 == 0:
        continue
    print(n, end=" ")
print()
```

```output
1 3 5 7 
```

Even numbers triggered `continue`, so the `print` after it was skipped for them.

```python
total = 0
for score in [90, -1, 75, -1, 60]:
    if score < 0:
        continue      # ignore invalid scores
    total += score
print(total)
```

```output
225
```

### break versus continue

| | `break` | `continue` |
|---|---------|------------|
| What it does | ends the loop completely | skips only the current round |
| Loop continues? | No | Yes, with the next item |
| Typical use | search, stop on a command | filter out unwanted items |

```python
for n in range(1, 6):
    if n == 3:
        continue
    print("continue version:", n)

for n in range(1, 6):
    if n == 3:
        break
    print("break version:", n)
```

```output
continue version: 1
continue version: 2
continue version: 4
continue version: 5
break version: 1
break version: 2
```

## `pass`: do nothing (on purpose)

`pass` is a statement that does nothing. Python needs *something* in every block, so `pass` is a placeholder for "I will fill this in later".

```python
for n in range(3):
    pass          # TODO: write the loop body later
print("Structure ready")
```

```output
Structure ready
```

`pass` is different from `continue`: `pass` does nothing and the rest of the body still runs, while `continue` skips the rest of the body.

```python
for n in range(3):
    if n == 1:
        pass
    print(n)
```

```output
0
1
2
```

## The loop `else` clause

A loop can have an `else` block. It runs **only if the loop finished without hitting `break`**. This is neat for searches: "if I never found it, do this".

```python
numbers = [3, 5, 7, 9]
for n in numbers:
    if n % 2 == 0:
        print("Found an even number:", n)
        break
else:
    print("No even numbers")
```

```output
No even numbers
```

## Break only leaves one loop

If loops are nested, `break` leaves only the loop it is in. You will see this in the nested loops lesson.

## Common Mistakes

**1. Using `break` or `continue` outside a loop.**

```python expect-error
if True:
    break
```

```output
SyntaxError: 'break' outside loop
```

**2. `continue` in a `while` loop before the update.** This causes an infinite loop because the counter is never incremented.

```python no-run
n = 0
while n < 5:
    if n == 2:
        continue      # n never changes again: infinite loop!
    n += 1
```

Fix: update `n` *before* `continue`.

**3. Confusing `pass` with `continue`.**

**4. Expecting `else` to run when the loop `break`s.** It does not.

## Try It Yourself

Print numbers from 1 to 20, skipping multiples of 3, and stop completely when you reach 15.

```python-try
for n in range(1, 21):
    if n == 15:
        break
    if n % 3 == 0:
        continue
    print(n, end=" ")
print()
```

**Challenge:** Ask the user for numbers until they type `done`; ignore anything negative; print the total.

## Recap

- `break` exits the innermost loop immediately.
- `continue` skips the rest of this round and moves on to the next.
- `pass` is a do-nothing placeholder.
- `for ... else` / `while ... else`: the `else` runs only when the loop was *not* ended by `break`.
- `while True:` plus `break` is the standard "repeat until told to stop" pattern.

**Next up:** loops inside loops: **nested loops**.

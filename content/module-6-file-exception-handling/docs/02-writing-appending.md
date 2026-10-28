---
id: 02-writing-appending
title: "Writing and Appending Files"
order: 2
concepts: ["writing-files", "appending-files", "file-modes"]
---

# Writing and Appending Files

Reading is only half of the story. To save a high score, log an event or export a report, your program has to **write**. There are two writing modes: `"w"` (start fresh) and `"a"` (add to the end). Choosing the wrong one is a classic way to lose data, so pay close attention.

## Writing with `"w"`

```python
with open("greeting.txt", "w") as f:
    f.write("Hello, file!\n")
    f.write("This is line two.\n")

with open("greeting.txt") as f:
    print(f.read())
```

```output
Hello, file!
This is line two.

```

Key facts about `write()`:

- It writes **exactly** the string you give it. It does **not** add a newline, so include `\n` yourself.
- It accepts **strings only**. Convert numbers with `str()` or an f-string.
- It returns the number of characters written.

```python
with open("numbers.txt", "w") as f:
    for i in range(1, 4):
        f.write(f"Number {i}\n")
    count = f.write("done")
print(count)
with open("numbers.txt") as f:
    print(f.read())
```

```output
4
Number 1
Number 2
Number 3
done
```

## Mode `"w"` erases the file

Opening an existing file in `"w"` mode **empties it immediately**, even before you write anything.

```python
with open("log.txt", "w") as f:
    f.write("first run\n")
with open("log.txt", "w") as f:
    f.write("second run\n")
with open("log.txt") as f:
    print(f.read())
```

```output
second run

```

The first line is gone! If you meant to keep it, you needed append mode.

## Appending with `"a"`

Append mode adds to the end and never erases what is there. If the file does not exist it is created.

```python
with open("log.txt", "w") as f:
    f.write("first run\n")
with open("log.txt", "a") as f:
    f.write("second run\n")
    f.write("third run\n")
with open("log.txt") as f:
    print(f.read())
```

```output
first run
second run
third run

```

## Writing many lines: `writelines()`

`writelines()` takes a list of strings. Like `write()`, it does **not** add newlines.

```python
lines = ["red\n", "green\n", "blue\n"]
with open("colours.txt", "w") as f:
    f.writelines(lines)

names = ["Asha", "Ravi", "Pip"]
with open("names.txt", "w") as f:
    f.writelines(name + "\n" for name in names)
with open("names.txt") as f:
    print(f.read().split())
```

```output
['Asha', 'Ravi', 'Pip']
```

## `print()` can write to files too

The `file=` option redirects `print` into a file and adds the newline for you:

```python
with open("report.txt", "w") as f:
    print("Report", file=f)
    print("=" * 6, file=f)
    print("Total:", 42, file=f)
with open("report.txt") as f:
    print(f.read())
```

```output
Report
======
Total: 42

```

## Read-modify-write

You cannot edit the middle of a text file in place. The standard technique is: read everything, change it in memory, write it back.

```python
with open("scores.txt", "w") as f:
    f.write("Asha 80\nRavi 65\nPip 70\n")

with open("scores.txt") as f:
    lines = f.read().splitlines()

updated = []
for line in lines:
    name, score = line.split()
    updated.append(f"{name} {int(score) + 5}")

with open("scores.txt", "w") as f:
    f.write("\n".join(updated) + "\n")

with open("scores.txt") as f:
    print(f.read())
```

```output
Asha 85
Ravi 70
Pip 75

```

We gave everyone 5 bonus marks. Important: we finished *reading* before we opened the file for writing, because `"w"` would have erased it.

## Exclusive creation: `"x"`

Mode `"x"` creates a file but **fails** if it already exists, which is perfect for "never overwrite" situations.

```python
with open("once.txt", "x") as f:
    f.write("created")
try:
    open("once.txt", "x")
except FileExistsError:
    print("Already exists, not overwritten")
```

```output
Already exists, not overwritten
```

## Building a simple log file

```python
from datetime import date

def log(message):
    with open("app.log", "a") as f:
        f.write(f"[LOG] {message}\n")

log("Program started")
log("User logged in")
log("Program finished")

with open("app.log") as f:
    for line in f:
        print(line.rstrip())
```

```output
[LOG] Program started
[LOG] User logged in
[LOG] Program finished
```

Real logs usually add a timestamp; the `datetime` module (Module 8) gives you that.

## Flushing and closing

Python buffers writes and saves them in chunks. Leaving the `with` block (or calling `f.close()`) flushes everything to disk. If your program crashes *inside* the block, most data written so far is still saved because `with` closes the file.

## Common Mistakes

**1. Using `"w"` when you meant `"a"`.** You silently delete the previous content.

**2. Forgetting `\n`.** All the text runs together on one line.

```python
with open("bad.txt", "w") as f:
    f.write("one")
    f.write("two")
    f.write("three")
with open("bad.txt") as f:
    print(f.read())
```

```output
onetwothree
```

**3. Writing numbers directly.**

```python expect-error
with open("n.txt", "w") as f:
    f.write(42)
```

```output
TypeError: write() argument must be str, not int
```

**4. Reading from a file opened in `"w"` mode.**

```python expect-error
with open("w.txt", "w") as f:
    f.read()
```

```output
io.UnsupportedOperation: not readable
```

## Try It Yourself

Write a program that saves three to-do items to a file, appends a fourth, then prints all the items numbered.

```python-try
with open("todo.txt", "w") as f:
    f.write("Buy milk\nFinish homework\nCall Ravi\n")

with open("todo.txt", "a") as f:
    f.write("Practice Python\n")

with open("todo.txt") as f:
    for n, line in enumerate(f, start=1):
        print(f"{n}. {line.rstrip()}")
```

**Challenge:** Write a function `add_score(name, score)` that appends a line to `scores.txt`, and another that prints the highest score in the file.

## Recap

- `"w"` creates/erases then writes; `"a"` appends; `"x"` creates only if absent.
- `write()` takes a string and adds no newline; `writelines()` takes a list of strings.
- `print(..., file=f)` writes lines to a file conveniently.
- To change a file, read it, modify the data in memory, then write it back.
- Always double-check `"w"` versus `"a"` before running.

**Next up:** **text processing patterns** and working with paths.

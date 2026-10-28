---
id: 01-reading-files
title: "Reading Files"
order: 1
concepts: ["reading-files", "open-function", "with-statement"]
---

# Reading Files

Variables vanish when your program ends. To keep information (scores, notes, settings) you need to save it in a **file** on disk, and to use it later you need to **read** it back. In this lesson you will learn how a program opens and reads text files.

> **Sandbox note:** The examples on this page create their own small files first, because the practice editor runs each program in a fresh empty folder. On your own computer you would simply open an existing file.

## The big idea: open, use, close

Working with a file always follows three steps:

1. **Open** it (Python gives you a *file object*).
2. **Use** it (read or write).
3. **Close** it (so the data is saved and resources are released).

The safest way to do this is the `with` statement, which closes the file automatically, even if an error happens.

```python
with open("story.txt", "w") as f:
    f.write("Once upon a time,\nthere was a snake named Pip.\nHe loved to code.\n")

with open("story.txt", "r") as f:
    content = f.read()

print(content)
print(len(content))
```

```output
Once upon a time,
there was a snake named Pip.
He loved to code.

65
```

`open(filename, mode)` returns the file object. The mode `"w"` means *write* (creating or overwriting the file) and `"r"` means *read*. Reading is the default, so `open("story.txt")` also works.

## File modes

| Mode | Meaning | If file exists | If file is missing |
|:----:|---------|----------------|--------------------|
| `"r"` | read (default) | reads it | **error** |
| `"w"` | write | **erases** it first | creates it |
| `"a"` | append | adds to the end | creates it |
| `"x"` | create only | error | creates it |
| `"r+"` | read and write | keeps content | error |

Add `"b"` for binary files (images, PDFs), e.g. `"rb"`.

## Reading the whole file: `read()`

```python
with open("data.txt", "w") as f:
    f.write("alpha\nbeta\ngamma\n")

with open("data.txt") as f:
    text = f.read()
print(repr(text))
print(text.splitlines())
```

```output
'alpha\nbeta\ngamma\n'
['alpha', 'beta', 'gamma']
```

`repr()` shows the hidden `\n` (newline) characters. Every line in a file ends with one.

You can also read a fixed number of characters:

```python
# Create the sample file first
with open("data.txt", "w") as f:
    f.write("alpha\nbeta\ngamma\n")

with open("data.txt") as f:
    print(f.read(5))
    print(f.read(3))
```

```output
alpha

be
```

The first `read(5)` gets `alpha`; the file object *remembers where it is*, so the next `read(3)` continues from there and returns a newline, `b` and `e`. (That is why a blank line appears before `be`.)

## Reading line by line

`readline()` reads one line at a time; `readlines()` returns them all as a list.

```python
# Create the sample file first
with open("data.txt", "w") as f:
    f.write("alpha\nbeta\ngamma\n")

with open("data.txt") as f:
    first = f.readline()
    second = f.readline()
print(repr(first))
print(repr(second))

with open("data.txt") as f:
    lines = f.readlines()
print(lines)
```

```output
'alpha\n'
'beta\n'
['alpha\n', 'beta\n', 'gamma\n']
```

## Best practice: loop over the file

A file object is **iterable**: a `for` loop hands you one line at a time, without loading the whole file into memory. This is the preferred way for large files.

```python
# Create the sample file first
with open("data.txt", "w") as f:
    f.write("alpha\nbeta\ngamma\n")

with open("data.txt") as f:
    for line in f:
        print(line.strip().upper())
```

```output
ALPHA
BETA
GAMMA
```

`line.strip()` removes the trailing newline (otherwise `print` would add a second blank line).

### Numbering the lines

```python
# Create the sample file first
with open("data.txt", "w") as f:
    f.write("alpha\nbeta\ngamma\n")

with open("data.txt") as f:
    for number, line in enumerate(f, start=1):
        print(f"{number}: {line.rstrip()}")
```

```output
1: alpha
2: beta
3: gamma
```

## Processing numbers from a file

Everything read from a file is text, so convert numbers explicitly.

```python
with open("marks.txt", "w") as f:
    f.write("85\n92\n78\n64\n")

total = 0
count = 0
with open("marks.txt") as f:
    for line in f:
        total += int(line)
        count += 1
print("Count:", count)
print("Average:", total / count)
```

```output
Count: 4
Average: 79.75
```

`int(line)` works even with the trailing newline because `int()` ignores surrounding whitespace.

## Handy file-object facts

```python
# Create the sample file first
with open("data.txt", "w") as f:
    f.write("alpha\nbeta\ngamma\n")

with open("data.txt") as f:
    print(f.name)
    print(f.mode)
    print(f.closed)
print(f.closed)
```

```output
data.txt
r
False
True
```

After the `with` block, the file is closed (`f.closed` is `True`) and you can no longer read from it.

## Why not just `open()` and `close()`?

The manual way works, but if an error occurs before `close()`, the file stays open:

```python
# Create the sample file first
with open("data.txt", "w") as f:
    f.write("alpha\nbeta\ngamma\n")

f = open("data.txt")
text = f.read()
f.close()
print(len(text))
```

```output
17
```

With `with`, closing is guaranteed. Always prefer `with`.

## Encoding

Text files are stored as bytes using an **encoding**. The modern standard is UTF-8, which handles every language and emoji. State it explicitly for portable code:

```python
with open("hello.txt", "w", encoding="utf-8") as f:
    f.write("Namaste, नमस्ते, こんにちは\n")

with open("hello.txt", encoding="utf-8") as f:
    print(f.read().strip())
```

```output
Namaste, नमस्ते, こんにちは
```

## Common Mistakes

**1. Reading a file that does not exist.**

```python expect-error
with open("no_such_file.txt") as f:
    data = f.read()
```

```output
FileNotFoundError: [Errno 2] No such file or directory: 'no_such_file.txt'
```

(The next lessons show how to handle this gracefully.)

**2. Forgetting that lines end with `\n`.** Use `strip()` or `rstrip()`.

**3. Reading twice.** After `f.read()` the file position is at the end; a second `f.read()` returns `""`.

```python
# Create the sample file first
with open("data.txt", "w") as f:
    f.write("alpha\nbeta\ngamma\n")

with open("data.txt") as f:
    first = f.read()
    second = f.read()
print(len(first), repr(second))
```

```output
17 ''
```

**4. Using a file after the `with` block.**

```python expect-error
# Create the sample file first
with open("data.txt", "w") as f:
    f.write("alpha\nbeta\ngamma\n")

with open("data.txt") as f:
    pass
f.read()
```

```output
ValueError: I/O operation on closed file.
```

## Try It Yourself

Create a file with five city names (one per line), then read it back and print each name with its length.

```python-try
with open("cities.txt", "w") as f:
    f.write("Delhi\nMumbai\nChennai\nKolkata\nPune\n")

with open("cities.txt") as f:
    for line in f:
        city = line.strip()
        print(f"{city} has {len(city)} letters")
```

**Challenge:** Count how many lines in a file start with the letter `"M"`.

## Recap

- Files persist data beyond your program's run.
- Use `with open(name, mode) as f:` so files close automatically.
- Modes: `"r"` read, `"w"` write (erases), `"a"` append, `"x"` create-only, add `"b"` for binary.
- `read()` gets everything, `readline()` one line, `readlines()` a list; **looping over the file** is best.
- File contents are text; use `strip()` for newlines and `int()`/`float()` for numbers.

**Next up:** **writing and appending** files.

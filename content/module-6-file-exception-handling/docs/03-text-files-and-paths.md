---
id: 03-text-files-and-paths
title: "Working with Text Files and Paths"
order: 3
concepts: ["text-processing", "file-paths", "pathlib"]
---

# Working with Text Files and Paths

Now that you can read and write, let us use files to *do things*: count words, search for text, transform data, and find files on disk. We will also learn how Python describes a file's **location**.

## Where is the file? Paths

A **path** is the address of a file. There are two kinds:

- **Relative path**: starts from the *current working directory*, e.g. `data/scores.txt`.
- **Absolute path**: starts from the root of the disk, e.g. `/Users/asha/data/scores.txt` or `C:\Users\asha\data\scores.txt`.

`open("notes.txt")` looks in the current working directory. You can see where that is with the `os` module:

```python
import os

print(os.path.basename(os.getcwd()) != "")
print(os.path.exists("nothing_here.txt"))
with open("here.txt", "w") as f:
    f.write("hi")
print(os.path.exists("here.txt"))
print(os.path.getsize("here.txt"))
```

```output
True
False
True
2
```

## The modern way: `pathlib`

`pathlib.Path` treats paths as objects, works the same on Windows, macOS and Linux, and has friendly methods.

```python
from pathlib import Path

p = Path("notes") / "week1" / "summary.txt"
print(p)
print(p.name)
print(p.stem)
print(p.suffix)
print(p.parent)
```

```output
notes/week1/summary.txt
summary.txt
summary
.txt
notes/week1
```

The `/` operator joins path pieces. (On Windows the separators print as backslashes.)

```python
from pathlib import Path

folder = Path("reports")
folder.mkdir(exist_ok=True)
file = folder / "jan.txt"
file.write_text("Sales: 100\n")
print(file.exists())
print(file.read_text())
print([p.name for p in folder.iterdir()])
```

```output
True
Sales: 100

['jan.txt']
```

`write_text()` and `read_text()` are one-line shortcuts for small files. `mkdir(exist_ok=True)` creates a folder without complaining if it exists.

## Finding files

```python
from pathlib import Path

Path("a.txt").write_text("1")
Path("b.txt").write_text("2")
Path("c.csv").write_text("3")
print(sorted(p.name for p in Path(".").glob("*.txt")))
print(sorted(p.name for p in Path(".").glob("*.csv")))
```

```output
['a.txt', 'b.txt']
['c.csv']
```

`glob("*.txt")` matches file names with wildcards.

## Pattern: counting words, lines and characters

```python
text = """Python is fun.
Python is powerful.
Files make programs useful."""
with open("essay.txt", "w") as f:
    f.write(text)

lines = words = chars = 0
with open("essay.txt") as f:
    for line in f:
        lines += 1
        words += len(line.split())
        chars += len(line)
print("Lines:", lines)
print("Words:", words)
print("Characters:", chars)
```

```output
Lines: 3
Words: 10
Characters: 62
```

## Pattern: searching a file

```python
with open("log.txt", "w") as f:
    f.write("INFO start\nERROR disk full\nINFO retry\nERROR timeout\n")

errors = []
with open("log.txt") as f:
    for number, line in enumerate(f, start=1):
        if "ERROR" in line:
            errors.append((number, line.strip()))
for number, line in errors:
    print(f"line {number}: {line}")
print("Total errors:", len(errors))
```

```output
line 2: ERROR disk full
line 4: ERROR timeout
Total errors: 2
```

## Pattern: word frequency

```python
with open("poem.txt", "w") as f:
    f.write("the rain in spain\nfalls mainly on the plain\n")

counts = {}
with open("poem.txt") as f:
    for line in f:
        for word in line.split():
            counts[word] = counts.get(word, 0) + 1
common = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:3]
print(common)
```

```output
[('the', 2), ('falls', 1), ('in', 1)]
```

## Pattern: transform and save (copy with changes)

```python
with open("input.txt", "w") as f:
    f.write("apple\nbanana\ncherry\n")

with open("input.txt") as source, open("output.txt", "w") as target:
    for line in source:
        target.write(line.strip().upper() + "\n")

with open("output.txt") as f:
    print(f.read().split())
```

```output
['APPLE', 'BANANA', 'CHERRY']
```

One `with` can open several files at once, separated by a comma.

## Pattern: numbers in a file

```python
with open("temps.txt", "w") as f:
    f.write("21.5\n19.0\n24.5\n\n22.0\n")

temps = []
with open("temps.txt") as f:
    for line in f:
        line = line.strip()
        if line:
            temps.append(float(line))
print(temps)
print(f"Max {max(temps)}, min {min(temps)}, mean {sum(temps) / len(temps):.2f}")
```

```output
[21.5, 19.0, 24.5, 22.0]
Max 24.5, min 19.0, mean 21.75
```

Skipping blank lines with `if line:` prevents `float("")` from crashing.

## Deleting and renaming

```python
import os
from pathlib import Path

Path("temp.txt").write_text("x")
os.rename("temp.txt", "final.txt")
print(os.path.exists("temp.txt"), os.path.exists("final.txt"))
os.remove("final.txt")
print(os.path.exists("final.txt"))
```

```output
False True
False
```

> **Warning:** `os.remove` deletes permanently; there is no recycle bin. Double-check the file name.

## Common Mistakes

**1. Relying on the working directory.** A script that works from one folder may not find its file when started from another. Build paths explicitly, e.g. relative to the script with `Path(__file__).parent`.

**2. Hard-coding path separators.** `"data\\file.txt"` fails on macOS/Linux. Use `Path("data") / "file.txt"`.

**3. Forgetting to skip blank lines** before converting to numbers.

**4. Loading a huge file with `read()`.** Loop over the file instead.

```python expect-error
from pathlib import Path
Path("missing_folder/file.txt").write_text("hi")
```

```output
FileNotFoundError: [Errno 2] No such file or directory: 'missing_folder/file.txt'
```

Create the folder first with `mkdir`.

## Try It Yourself

Create a file of student names and marks (`Asha 80`), read it back, and print the name with the highest mark.

```python-try
with open("marks.txt", "w") as f:
    f.write("Asha 80\nRavi 92\nPip 75\n")

best_name, best_mark = None, -1
with open("marks.txt") as f:
    for line in f:
        name, mark = line.split()
        if int(mark) > best_mark:
            best_name, best_mark = name, int(mark)
print(best_name, best_mark)
```

**Challenge:** Write a program that reads a text file and prints the longest line and its length.

## Recap

- Relative paths start from the working directory; absolute paths start at the disk root.
- `pathlib.Path` builds paths with `/`, and offers `read_text`, `write_text`, `exists`, `mkdir`, `glob`, `iterdir`.
- Common patterns: count lines/words, search for text, tally frequencies, transform and save, parse numbers.
- Skip blank lines before converting; process large files line by line.
- `os.rename` and `os.remove` change files on disk; be careful.

**Next up:** **CSV files** for tables of data.

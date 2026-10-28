---
id: 01-os-and-files
title: "The os Module: Talking to Your Computer"
order: 1
concepts: ["os-module", "shutil-module", "environment"]
---

# The os Module: Talking to Your Computer

Python can do what you do in a file manager: list folders, create directories, rename, move and delete files. The **`os`** and **`shutil`** modules provide these powers, and they are the foundation of **automation**: getting the computer to do boring work for you.

> **Sandbox note:** the practice editor runs in a private temporary folder, so it is safe to create and delete files here. Try the same code in a scratch folder on your own computer.

## Where am I?

```python
import os

cwd = os.getcwd()
print(type(cwd).__name__)
print(os.path.isabs(cwd))
print(os.name in ("posix", "nt"))
print(os.sep in ("/", "\\"))
```

```output
str
True
True
True
```

- `os.getcwd()` returns the current working directory.
- `os.name` is `"posix"` (macOS/Linux) or `"nt"` (Windows).
- `os.sep` is the path separator for the platform.

## Creating and listing folders

```python
import os

os.mkdir("project")
os.makedirs("project/data/raw", exist_ok=True)
with open("project/readme.txt", "w") as f:
    f.write("hello")
with open("project/data/one.csv", "w") as f:
    f.write("a,b")

print(sorted(os.listdir("project")))
print(sorted(os.listdir("project/data")))
print(os.path.isdir("project/data"), os.path.isfile("project/readme.txt"))
```

```output
['data', 'readme.txt']
['one.csv', 'raw']
True True
```

- `os.mkdir(path)` makes one folder; `os.makedirs(path)` makes the whole chain (with `exist_ok=True` it does not complain if it already exists).
- `os.listdir(path)` returns the names inside a folder (in arbitrary order, so we sorted them).

## Working with paths: `os.path`

```python
import os

path = os.path.join("project", "data", "report.final.csv")
print(path)
print(os.path.basename(path))
print(os.path.dirname(path))
print(os.path.splitext(path))
print(os.path.exists(path))
```

```output
project/data/report.final.csv
report.final.csv
project/data
('project/data/report.final', '.csv')
False
```

`os.path.join` builds paths correctly for the current platform. Never glue paths with `+ "/" +`.

| Function | What it does |
|----------|--------------|
| `os.path.join(a, b)` | join with the right separator |
| `os.path.exists(p)` | does it exist? |
| `os.path.isfile(p)` / `isdir(p)` | file or folder? |
| `os.path.getsize(p)` | size in bytes |
| `os.path.splitext(p)` | split off the extension |
| `os.path.basename(p)` / `dirname(p)` | last part / everything before it |
| `os.path.abspath(p)` | absolute version of a path |

## Walking a whole tree: `os.walk`

`os.walk` visits every folder below a starting point. For each one it gives the folder name, its sub-folders and its files.

```python
import os

os.makedirs("photos/2024/summer")
os.makedirs("photos/2025")
for path in ["photos/a.jpg", "photos/2024/b.jpg", "photos/2024/summer/c.png", "photos/2025/d.jpg"]:
    open(path, "w").write("x")

for folder, subfolders, files in sorted(os.walk("photos")):
    print(folder, sorted(files))
```

```output
photos ['a.jpg']
photos/2024 ['b.jpg']
photos/2024/summer ['c.png']
photos/2025 ['d.jpg']
```

### Counting files by type

```python
import os

os.makedirs("docs")
for name in ["a.txt", "b.txt", "c.csv", "d.txt", "e.py"]:
    open(os.path.join("docs", name), "w").write("")

counts = {}
for name in os.listdir("docs"):
    ext = os.path.splitext(name)[1]
    counts[ext] = counts.get(ext, 0) + 1
print(dict(sorted(counts.items())))
```

```output
{'.csv': 1, '.py': 1, '.txt': 3}
```

## Renaming, moving and deleting

```python
import os

open("old.txt", "w").write("data")
os.rename("old.txt", "new.txt")
print(os.path.exists("old.txt"), os.path.exists("new.txt"))

os.mkdir("archive")
os.rename("new.txt", os.path.join("archive", "new.txt"))
print(os.listdir("archive"))

os.remove("archive/new.txt")
os.rmdir("archive")
print(os.path.exists("archive"))
```

```output
False True
['new.txt']
False
```

- `os.rename(old, new)` renames **or moves**.
- `os.remove(file)` deletes a file; `os.rmdir(folder)` deletes an **empty** folder.

> **Warning:** deletion is permanent. When automating, first *print* what you would delete, and only delete when you are sure.

## `shutil`: higher-level file operations

`shutil` copies and moves whole files and trees, and can delete non-empty folders.

```python
import os
import shutil

os.makedirs("src/sub")
open("src/a.txt", "w").write("A")
open("src/sub/b.txt", "w").write("B")

shutil.copy("src/a.txt", "copy_of_a.txt")
shutil.copytree("src", "src_backup")
print(sorted(os.listdir("src_backup")))
print(open("copy_of_a.txt").read())

shutil.move("copy_of_a.txt", "moved.txt")
print(os.path.exists("copy_of_a.txt"), os.path.exists("moved.txt"))

shutil.rmtree("src_backup")
print(os.path.exists("src_backup"))
```

```output
['a.txt', 'sub']
A
False True
False
```

## Environment variables

Programs read configuration (and secrets such as API keys) from **environment variables**, so they need not be hard-coded in your source.

```python
import os

print(os.environ.get("MY_SECRET_KEY"))
print(os.environ.get("MY_SECRET_KEY", "not set"))
os.environ["APP_MODE"] = "debug"
print(os.environ["APP_MODE"])
```

```output
None
not set
debug
```

Use `.get()` with a default so a missing variable does not crash the program. Never commit real keys to source control.

## Running other programs (a peek)

`subprocess` lets Python launch other programs; for automation scripts it is enormously useful.

```python
import subprocess
import sys

result = subprocess.run([sys.executable, "-c", "print('hello from a child')"],
                        capture_output=True, text=True)
print(result.stdout.strip())
print(result.returncode)
```

```output
hello from a child
0
```

## Common Mistakes

**1. Building paths by hand.** `"folder" + "\\" + "file"` breaks on other systems; use `os.path.join`.

**2. Deleting without checking.** Print first, delete later.

**3. `os.rmdir` on a folder with files.** It fails; use `shutil.rmtree` (carefully).

```python no-run
import os
os.makedirs("full/inside")
os.rmdir("full")
```

```text
OSError: [Errno 39] Directory not empty: 'full'
```

(The error number differs between operating systems.)

**4. Forgetting that `os.listdir` order is arbitrary.** Sort the result if order matters.

## Try It Yourself

Create a folder with a few files, list them with their sizes, and print the total number of bytes.

```python-try
import os

os.mkdir("notes")
for name, text in [("a.txt", "hello"), ("b.txt", "python rocks"), ("c.txt", "")]:
    with open(os.path.join("notes", name), "w") as f:
        f.write(text)

total = 0
for name in sorted(os.listdir("notes")):
    size = os.path.getsize(os.path.join("notes", name))
    print(f"{name:<8}{size:>4} bytes")
    total += size
print("Total:", total)
```

**Challenge:** Write a function that returns the names of all `.txt` files anywhere below a folder (use `os.walk`).

## Recap

- `os.getcwd`, `os.listdir`, `os.mkdir` / `makedirs`, `os.rename`, `os.remove`, `os.rmdir` manage files and folders.
- `os.path.join`, `exists`, `isfile`, `isdir`, `splitext`, `getsize` work with paths.
- `os.walk` visits every folder in a tree; `shutil` copies, moves and removes whole trees.
- Read configuration from `os.environ` with `.get()`.
- Print what you *would* delete before deleting anything.

**Next up:** **dates and times** with `datetime`.

---
id: 07-automation-projects
title: "Automation Projects: Organise, Rename, Repeat"
order: 7
concepts: ["automation-scripts", "file-organizer", "dry-run"]
---

# Automation Projects: Organise, Rename, Repeat

**Automation** means getting the computer to do repetitive work for you: sorting a messy Downloads folder, renaming 500 photos, generating reports every morning. The key ideas are: work out the rule, apply it in a loop, and **test safely before doing anything you cannot undo**.

## The safe-automation recipe

1. **Describe the rule** in plain words first ("move every `.jpg` into a `Images` folder").
2. **Dry run**: print what *would* happen, but change nothing.
3. **Run for real** only after you have read the dry-run output.
4. **Log** what you did so you can undo it.

## Project 1: a file organiser

The rule: sort files into folders by their extension.

```python
import os
import shutil

CATEGORIES = {
    "Images": {".jpg", ".jpeg", ".png", ".gif"},
    "Documents": {".pdf", ".txt", ".docx"},
    "Code": {".py", ".js", ".html"},
}

def category_for(filename):
    ext = os.path.splitext(filename)[1].lower()
    for category, extensions in CATEGORIES.items():
        if ext in extensions:
            return category
    return "Other"

def organise(folder, dry_run=True):
    moves = []
    for name in sorted(os.listdir(folder)):
        path = os.path.join(folder, name)
        if not os.path.isfile(path):
            continue
        target_dir = os.path.join(folder, category_for(name))
        moves.append((name, category_for(name)))
        if not dry_run:
            os.makedirs(target_dir, exist_ok=True)
            shutil.move(path, os.path.join(target_dir, name))
    return moves

# --- build a messy folder to practise on ---
os.mkdir("downloads")
for name in ["holiday.JPG", "notes.txt", "script.py", "song.mp3", "report.pdf", "logo.png"]:
    open(os.path.join("downloads", name), "w").write("x")

print("DRY RUN")
for name, category in organise("downloads", dry_run=True):
    print(f"  {name} -> {category}/")
print(sorted(os.listdir("downloads")))

organise("downloads", dry_run=False)
print("AFTER")
print(sorted(os.listdir("downloads")))
print(sorted(os.listdir("downloads/Images")))
```

```output
DRY RUN
  holiday.JPG -> Images/
  logo.png -> Images/
  notes.txt -> Documents/
  report.pdf -> Documents/
  script.py -> Code/
  song.mp3 -> Other/
['holiday.JPG', 'logo.png', 'notes.txt', 'report.pdf', 'script.py', 'song.mp3']
AFTER
['Code', 'Documents', 'Images', 'Other']
['holiday.JPG', 'logo.png']
```

**What to notice**
- The rule lives in **data** (`CATEGORIES`), so you can extend it without touching the logic.
- `.lower()` makes `.JPG` and `.jpg` behave the same.
- The `dry_run` flag lets you preview safely.

## Project 2: batch renaming

The rule: rename photos to `trip_001.jpg`, `trip_002.jpg`, ... in order.

```python
import os

def rename_batch(folder, prefix, extension, dry_run=True):
    names = sorted(n for n in os.listdir(folder) if n.lower().endswith(extension))
    plan = []
    for number, old in enumerate(names, start=1):
        new = f"{prefix}_{number:03d}{extension}"
        plan.append((old, new))
        if not dry_run:
            os.rename(os.path.join(folder, old), os.path.join(folder, new))
    return plan

os.mkdir("photos")
for name in ["IMG_8841.jpg", "IMG_8802.jpg", "IMG_9015.jpg", "notes.txt"]:
    open(os.path.join("photos", name), "w").write("x")

for old, new in rename_batch("photos", "trip", ".jpg", dry_run=True):
    print(old, "->", new)
rename_batch("photos", "trip", ".jpg", dry_run=False)
print(sorted(os.listdir("photos")))
```

```output
IMG_8802.jpg -> trip_001.jpg
IMG_8841.jpg -> trip_002.jpg
IMG_9015.jpg -> trip_003.jpg
['notes.txt', 'trip_001.jpg', 'trip_002.jpg', 'trip_003.jpg']
```

`{number:03d}` pads with zeros (`001`) so the files sort correctly.

## Project 3: finding duplicates and big files

```python
import os
from collections import defaultdict

os.makedirs("stuff/sub")
files = {"stuff/a.txt": "hello", "stuff/b.txt": "hello", "stuff/sub/c.txt": "different", "stuff/big.bin": "x" * 5000}
for path, text in files.items():
    open(path, "w").write(text)

by_content = defaultdict(list)
big = []
for folder, _, names in os.walk("stuff"):
    for name in names:
        path = os.path.join(folder, name)
        with open(path) as f:
            by_content[f.read()].append(path)
        if os.path.getsize(path) > 1000:
            big.append(path)

for paths in by_content.values():
    if len(paths) > 1:
        print("Duplicates:", sorted(paths))
print("Big files:", big)
```

```output
Duplicates: ['stuff/a.txt', 'stuff/b.txt']
Big files: ['stuff/big.bin']
```

(Real duplicate finders compare file *hashes* with `hashlib` so they can handle huge binary files without reading them fully into memory.)

## Project 4: a daily report generator

```python
from datetime import date

def make_report(day, sales):
    total = sum(sales.values())
    best = max(sales, key=sales.get)
    lines = [f"Sales report for {day.strftime('%d %B %Y')}", "-" * 32]
    for item, amount in sorted(sales.items()):
        lines.append(f"{item:<15}{amount:>10,.2f}")
    lines += ["-" * 32, f"{'TOTAL':<15}{total:>10,.2f}", f"Best seller: {best}"]
    return "\n".join(lines)

report = make_report(date(2025, 3, 14), {"Notebook": 1250.5, "Pen": 480, "Bag": 3999})
print(report)
with open("report.txt", "w") as f:
    f.write(report)
print(len(open("report.txt").read().splitlines()))
```

```output
Sales report for 14 March 2025
--------------------------------
Bag              3,999.00
Notebook         1,250.50
Pen                480.00
--------------------------------
TOTAL            5,729.50
Best seller: Bag
8
```

## Repeating tasks: loops and `time.sleep`

For a task that runs repeatedly, wrap it in a loop with a pause:

```python
import time

def run_every(seconds, times, task):
    for i in range(times):
        task(i)
        if i < times - 1:
            time.sleep(seconds)

run_every(0.1, 3, lambda i: print("check", i + 1))
```

```output
check 1
check 2
check 3
```

On a real computer, the operating system can run scripts on a schedule for you, with no loop needed:

| System | Tool |
|--------|------|
| macOS / Linux | `cron` (`crontab -e`), e.g. `0 8 * * * python3 /path/report.py` |
| Windows | Task Scheduler |
| Python-only | the third-party `schedule` package |

## Text automation: cleaning data

```python
import re

raw = ["  Asha Kumar , 98100-12345 ", "ravi   singh,+91 98222 33444", "  PIP ,9812345678"]
clean = []
for line in raw:
    name, phone = [part.strip() for part in line.split(",")]
    name = " ".join(word.capitalize() for word in name.split())
    digits = re.sub(r"\D", "", phone)[-10:]
    clean.append((name, digits))
for name, phone in clean:
    print(f"{name:<12} {phone}")
```

```output
Asha Kumar   9810012345
Ravi Singh   9822233444
Pip          9812345678
```

`re.sub(r"\D", "", phone)` removes every non-digit character. Regular expressions (`re`) are a powerful tool for pattern-matching in text.

## Automation safety checklist

- **Dry run first** and print the plan.
- **Never delete** in your first version; move to a `trash` folder instead.
- Work on a **copy** of the data while testing.
- Handle **name collisions** (two files ending up with the same name).
- Catch exceptions per file so one bad file does not stop the batch.
- **Log** every action.

## Common Mistakes

**1. Renaming into an existing name.** `os.rename` silently overwrites on macOS and Linux. Check `os.path.exists(new)` first.

**2. Modifying a folder while listing it.** Take a `sorted(os.listdir(...))` snapshot first.

**3. Forgetting subfolders.** `os.listdir` is one level; use `os.walk` for trees.

**4. No dry run.** The first time your rule is wrong, you will wish you had one.

```python
import os
os.mkdir("box")
open("box/a.txt", "w").write("A")
open("box/b.txt", "w").write("B")
try:
    os.rename("box/a.txt", "box/b.txt")
except OSError as e:
    print("error", type(e).__name__)
print(open("box/b.txt").read())
```

```output
A
```

On macOS and Linux the rename silently replaced `b.txt`, and the original `B` is gone (Windows raises an error instead). Always check for collisions yourself.

## Try It Yourself

Write `plan_cleanup(names)` that takes a list of filenames and returns a dictionary mapping each *extension* to the list of names having it (sorted). Then print a summary line for each extension.

```python-try
import os

def plan_cleanup(names):
    plan = {}
    for name in names:
        ext = os.path.splitext(name)[1].lower() or "(none)"
        plan.setdefault(ext, []).append(name)
    return {ext: sorted(v) for ext, v in plan.items()}

names = ["a.TXT", "b.txt", "c.py", "README", "d.py", "e.PNG"]
for ext, group in sorted(plan_cleanup(names).items()):
    print(f"{ext:<8}{len(group)} {group}")
```

**Challenge:** Extend `organise` so it never overwrites: if the target name exists, add `_1`, `_2`... before the extension.

## Recap

- Automate by describing a rule, applying it in a loop and previewing with a **dry run**.
- Keep rules in data (dictionaries) and logic in functions.
- `os`, `shutil` and `pathlib` move and rename; `datetime` names things by date; `re` cleans text.
- `time.sleep` (or `cron` / Task Scheduler) repeats tasks on a schedule.
- Guard against collisions, log actions, and never delete in your first version.

**Next up:** the lab: digital clock, password generator and weather report.

---
id: 06-command-line-scripts
title: "Command-Line Scripts: sys.argv and argparse"
order: 6
concepts: ["command-line-args", "argparse-module", "automation-scripts"]
---

# Command-Line Scripts: sys.argv and argparse

Many of the best automation tools are small programs you run from a terminal with **options**: `python backup.py photos --dry-run`. Instead of asking questions with `input()`, they read **command-line arguments**. That makes them scriptable: other programs (or schedulers) can run them without a human typing.

## `sys.argv`: the raw list

`sys.argv` is a list of strings: the script name followed by everything typed after it.

```python no-run
# greet.py
import sys

print(sys.argv)
name = sys.argv[1] if len(sys.argv) > 1 else "stranger"
print(f"Hello, {name}!")
```

Running it in a terminal:

```bash
python greet.py Asha
```

```text
['greet.py', 'Asha']
Hello, Asha!
```

`sys.argv[0]` is the script name; the user's arguments start at `[1]`. Everything is a **string**, so convert numbers yourself.

You can see the same list inside the practice editor (it has no extra arguments):

```python
import sys

print(len(sys.argv))
print(sys.argv[1:])
```

```output
1
[]
```

## Exit codes

A script tells the caller whether it succeeded through its **exit code**: `0` means success, anything else means failure.

```python
import subprocess
import sys

ok = subprocess.run([sys.executable, "-c", "print('fine')"])
bad = subprocess.run([sys.executable, "-c", "import sys; sys.exit(3)"])
print(ok.returncode, bad.returncode)
```

```output
fine
0 3
```

Use `sys.exit(1)` (or another non-zero number) when your script fails, so shell scripts can react.

## `argparse`: the professional way

Parsing `sys.argv` by hand gets messy fast (options, defaults, `--help`, error messages). The **`argparse`** module does it all.

```python
import argparse

parser = argparse.ArgumentParser(description="Repeat a greeting.")
parser.add_argument("name", help="who to greet")
parser.add_argument("-n", "--times", type=int, default=1, help="how many times")
parser.add_argument("--shout", action="store_true", help="use capitals")

args = parser.parse_args(["Asha", "-n", "2", "--shout"])
message = f"Hello, {args.name}!"
if args.shout:
    message = message.upper()
for _ in range(args.times):
    print(message)
```

```output
HELLO, ASHA!
HELLO, ASHA!
```

Here we pass a list to `parse_args` so the example runs inside the editor. In a real script you call `parser.parse_args()` with no argument and it reads `sys.argv` for you.

### What argparse gives you for free

- **Positional arguments:** `add_argument("name")` are required.
- **Options:** `-n` / `--times` with `type=`, `default=` and `choices=`.
- **Flags:** `action="store_true"` is `False` unless the flag is present.
- **Automatic `--help`** and **error messages**.

```python
import argparse

parser = argparse.ArgumentParser(prog="calc")
parser.add_argument("a", type=float)
parser.add_argument("b", type=float)
parser.add_argument("--op", choices=["add", "sub", "mul", "div"], default="add")

for argv in (["6", "3"], ["6", "3", "--op", "div"], ["2.5", "4", "--op", "mul"]):
    args = parser.parse_args(argv)
    ops = {"add": args.a + args.b, "sub": args.a - args.b,
           "mul": args.a * args.b, "div": args.a / args.b}
    print(args.op, ops[args.op])
```

```output
add 9.0
div 2.0
mul 10.0
```

### Errors are handled for you

```python
import argparse
import io
import contextlib

parser = argparse.ArgumentParser(prog="calc")
parser.add_argument("count", type=int)

err = io.StringIO()
try:
    with contextlib.redirect_stderr(err):
        parser.parse_args(["not-a-number"])
except SystemExit as e:
    print("exit code", e.code)
print(err.getvalue().strip().splitlines()[-1])
```

```output
exit code 2
calc: error: argument count: invalid int value: 'not-a-number'
```

In a real terminal the user sees that message and the usage text, and the script stops with exit code 2.

### Sub-commands

Tools like `git commit` and `pip install` use sub-commands. `argparse` supports them:

```python
import argparse

parser = argparse.ArgumentParser(prog="todo")
sub = parser.add_subparsers(dest="command", required=True)

add = sub.add_parser("add", help="add a task")
add.add_argument("text")

done = sub.add_parser("done", help="finish a task")
done.add_argument("number", type=int)

for argv in (["add", "buy milk"], ["done", "2"]):
    args = parser.parse_args(argv)
    if args.command == "add":
        print("Adding:", args.text)
    else:
        print("Completing task", args.number)
```

```output
Adding: buy milk
Completing task 2
```

## The standard script layout

```python no-run
import argparse

def process(folder, dry_run):
    ...   # the real work lives in ordinary functions

def main():
    parser = argparse.ArgumentParser(description="Tidy a folder.")
    parser.add_argument("folder")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    process(args.folder, args.dry_run)

if __name__ == "__main__":
    main()
```

Keeping the logic in functions and the argument handling in `main()` makes the code easy to test and to reuse as a module (remember `if __name__ == "__main__":` from Module 5).

## Reading from standard input

Scripts can also be **pipelines**: text flows in from another program.

```python stdin="apple|banana|cherry"
import sys

lines = [line.strip() for line in sys.stdin]
print(len(lines))
print(lines[::-1])
```

```output
3
['cherry', 'banana', 'apple']
```

`sys.stdin` is a file-like object, so you can loop over it just like an open file.

## Logging instead of `print`

For longer-running scripts, the `logging` module adds levels and timestamps:

```python
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(levelname)s: %(message)s")
logging.debug("hidden: level too low")
logging.info("starting")
logging.warning("disk almost full")
logging.error("could not open file")
```

```output
INFO: starting
WARNING: disk almost full
ERROR: could not open file
```

## Common Mistakes

**1. Forgetting that `sys.argv` items are strings.** Convert with `int()` or use `type=int` in `argparse`.

**2. Assuming an argument exists.** `sys.argv[1]` raises `IndexError` if the user typed nothing; check the length or use `argparse`.

```python expect-error
import sys
print(sys.argv[1])
```

```output
IndexError: list index out of range
```

**3. Writing an option without `--`** in `add_argument`. `add_argument("times")` is *positional* (required); `add_argument("--times")` is optional.

**4. Ignoring exit codes.** Return non-zero on failure so other tools can tell.

## Try It Yourself

Build a parser for a "word counter" that has a required `text` argument and an optional `--upper` flag, then simulate two runs.

```python-try
import argparse

parser = argparse.ArgumentParser(prog="wc")
parser.add_argument("text")
parser.add_argument("--upper", action="store_true")

for argv in (["hello brave new world"], ["hello brave new world", "--upper"]):
    args = parser.parse_args(argv)
    text = args.text.upper() if args.upper else args.text
    print(len(text.split()), text)
```

**Challenge:** Add a `--min-length` option (an integer, default 0) that only counts words at least that long.

## Recap

- `sys.argv` is the list of command-line strings; index 0 is the script name.
- Exit codes: `0` = success, non-zero = failure (`sys.exit(code)`).
- `argparse` provides positional arguments, options, flags, choices, sub-commands, `--help` and error messages.
- Keep logic in functions and parsing in `main()`; guard with `if __name__ == "__main__":`.
- `sys.stdin` reads piped input; `logging` beats `print` for long-running scripts.

**Next up:** **automation projects**: organising files and repeating tasks.

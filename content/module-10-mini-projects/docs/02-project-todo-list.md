---
id: 02-project-todo-list
title: "Project 1: To-Do List Manager"
order: 2
concepts: ["project-todo", "json-persistence", "project-practice"]
---

# Project 1: To-Do List Manager

**Goal:** a command-line to-do list that remembers your tasks between runs.

**Skills used:** lists, dictionaries, functions, JSON files, exceptions.

## Requirements

- Add a task (with an automatically assigned number).
- List tasks, showing which are done.
- Mark a task as done.
- Delete a task.
- Show a summary ("3 of 5 done").
- Save to a file so tasks survive between runs.

## Design

**Data:** each task is a dictionary; the whole list is a Python list.

```python
task = {"id": 1, "text": "Buy milk", "done": False}
print(task["text"], task["done"])
```

```output
Buy milk False
```

**Functions** (none of them print or read input, so they are easy to test):

| Function | Job |
|----------|-----|
| `load_tasks(path)` | read the JSON file (empty list if missing) |
| `save_tasks(tasks, path)` | write the JSON file |
| `add_task(tasks, text)` | add and return the new task |
| `complete_task(tasks, task_id)` | mark done |
| `delete_task(tasks, task_id)` | remove |
| `summary(tasks)` | text like `2 of 3 done` |

## Step 1: storage

```python
import json

def load_tasks(path):
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

def save_tasks(tasks, path):
    with open(path, "w") as f:
        json.dump(tasks, f, indent=2)

print(load_tasks("tasks.json"))
save_tasks([{"id": 1, "text": "Test", "done": False}], "tasks.json")
print(load_tasks("tasks.json"))
```

```output
[]
[{'id': 1, 'text': 'Test', 'done': False}]
```

A missing (first run) or damaged file gives an empty list rather than a crash.

## Step 2: the operations

```python
def next_id(tasks):
    return max((t["id"] for t in tasks), default=0) + 1

def add_task(tasks, text):
    text = text.strip()
    if not text:
        raise ValueError("task text cannot be empty")
    task = {"id": next_id(tasks), "text": text, "done": False}
    tasks.append(task)
    return task

def find_task(tasks, task_id):
    for task in tasks:
        if task["id"] == task_id:
            return task
    raise KeyError(f"no task with id {task_id}")

def complete_task(tasks, task_id):
    find_task(tasks, task_id)["done"] = True

def delete_task(tasks, task_id):
    tasks.remove(find_task(tasks, task_id))

def summary(tasks):
    done = sum(1 for t in tasks if t["done"])
    return f"{done} of {len(tasks)} done"

tasks = []
add_task(tasks, "Buy milk")
add_task(tasks, "Finish homework")
add_task(tasks, "Call Ravi")
complete_task(tasks, 2)
print(summary(tasks))
delete_task(tasks, 1)
print([t["id"] for t in tasks])
print(add_task(tasks, "Water plants")["id"])
```

```output
1 of 3 done
[2, 3]
4
```

Notice that after deleting task 1, the next id is 4, not 1: ids are never reused, so they stay unique.

## Step 3: display

Formatting is a separate function so that you can change how tasks look without touching the logic.

```python
def format_tasks(tasks):
    if not tasks:
        return "(no tasks yet)"
    lines = []
    for t in tasks:
        box = "[x]" if t["done"] else "[ ]"
        lines.append(f"{t['id']:>2}. {box} {t['text']}")
    return "\n".join(lines)

demo = [
    {"id": 1, "text": "Buy milk", "done": False},
    {"id": 2, "text": "Finish homework", "done": True},
]
print(format_tasks(demo))
print(format_tasks([]))
```

```output
 1. [ ] Buy milk
 2. [x] Finish homework
(no tasks yet)
```

## Step 4: the user interface (a command loop)

Here is the complete program with a text menu. We supply a scripted list of commands so you can see it run.

```python stdin="add Buy milk|add Finish homework|list|done 2|list|del 1|list|summary|quit"
import json

FILENAME = "todo_project.json"

def load_tasks(path=FILENAME):
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_tasks(tasks, path=FILENAME):
    with open(path, "w") as f:
        json.dump(tasks, f, indent=2)

def next_id(tasks):
    return max((t["id"] for t in tasks), default=0) + 1

def find_task(tasks, task_id):
    for t in tasks:
        if t["id"] == task_id:
            return t
    raise KeyError(task_id)

def format_tasks(tasks):
    if not tasks:
        return "(no tasks yet)"
    return "\n".join(f"{t['id']:>2}. {'[x]' if t['done'] else '[ ]'} {t['text']}" for t in tasks)

def main():
    tasks = load_tasks()
    while True:
        command = input().strip()
        verb, _, rest = command.partition(" ")
        try:
            if verb == "add":
                tasks.append({"id": next_id(tasks), "text": rest, "done": False})
                print("Added:", rest)
            elif verb == "list":
                print(format_tasks(tasks))
            elif verb == "done":
                find_task(tasks, int(rest))["done"] = True
                print("Marked done:", rest)
            elif verb == "del":
                tasks.remove(find_task(tasks, int(rest)))
                print("Deleted:", rest)
            elif verb == "summary":
                done = sum(t["done"] for t in tasks)
                print(f"{done} of {len(tasks)} done")
            elif verb == "quit":
                save_tasks(tasks)
                print("Saved. Goodbye!")
                break
            else:
                print("Unknown command")
        except (KeyError, ValueError):
            print("Please give a valid task number")

if __name__ == "__main__":
    main()
```

```output
Added: Buy milk
Added: Finish homework
 1. [ ] Buy milk
 2. [ ] Finish homework
Marked done: 2
 1. [ ] Buy milk
 2. [x] Finish homework
Deleted: 1
 2. [x] Finish homework
1 of 1 done
Saved. Goodbye!
```

## Step 5: test it

```python
def next_id(tasks):
    return max((t["id"] for t in tasks), default=0) + 1

assert next_id([]) == 1
assert next_id([{"id": 1}, {"id": 5}]) == 6

def summary(tasks):
    done = sum(1 for t in tasks if t["done"])
    return f"{done} of {len(tasks)} done"

assert summary([]) == "0 of 0 done"
assert summary([{"done": True}, {"done": False}]) == "1 of 2 done"
print("todo tests passed")
```

```output
todo tests passed
```

## Ideas to extend it

1. **Due dates** using `datetime`, with a command that lists overdue tasks.
2. **Priorities** (high, medium, low) and sorting by priority.
3. **Search** for tasks containing a word.
4. **Undo** the last delete (keep a stack of removed tasks).
5. **Categories/tags** using a set per task.
6. Turn the menu into a **tkinter** window.

## Common Mistakes

**1. Reusing ids** by using `len(tasks) + 1`. After a deletion two tasks can get the same id; use `max id + 1`.

**2. Not saving on exit.** Save after every change, or at least on `quit`.

**3. Crashing on bad input.** Wrap conversions like `int(rest)` in `try/except`.

**4. Printing inside the logic functions.** Return values and let `main` print.

```python
tasks = [{"id": 1}, {"id": 2}, {"id": 3}]
tasks.pop(0)
print(len(tasks) + 1, max(t["id"] for t in tasks) + 1)
```

```output
3 4
```

The first method would create a duplicate id `3`; the second stays unique.

## Try It Yourself

Add a `search_tasks(tasks, word)` function that returns the tasks whose text contains the word (ignoring capitals), and test it.

```python-try
def search_tasks(tasks, word):
    word = word.lower()
    return [t for t in tasks if word in t["text"].lower()]

tasks = [
    {"id": 1, "text": "Buy Milk", "done": False},
    {"id": 2, "text": "Call Ravi", "done": True},
    {"id": 3, "text": "milk the cow", "done": False},
]
found = search_tasks(tasks, "MILK")
assert [t["id"] for t in found] == [1, 3]
assert search_tasks(tasks, "zzz") == []
print([t["text"] for t in found])
```

**Challenge:** Add an `edit` command that changes a task's text.

## Recap

- Represent each task as a dictionary and keep them in a list; save the list as JSON.
- Keep logic functions free of `print`/`input` so they can be tested.
- Assign ids with `max id + 1`; handle a missing or damaged file gracefully.
- A command loop (`add`, `list`, `done`, `del`, `quit`) gives the program a simple interface.
- Test the small functions with `assert` before trusting the whole program.

**Next up:** Project 2, a **contact book**.

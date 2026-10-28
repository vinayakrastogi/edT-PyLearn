---
id: 05-tkinter-intro
title: "Building Windows with tkinter"
order: 5
concepts: ["tkinter-intro", "gui-events"]
---

# Building Windows with tkinter

So far your programs talk through a black-and-white terminal. Real apps have **windows, buttons and text boxes**, which is called a **GUI** (Graphical User Interface). Python includes a GUI toolkit called **tkinter** in its standard library (on most systems there is nothing to install).

> **Not runnable here:** a GUI needs a real screen, and the practice editor has none. All examples in this lesson are for you to **copy into a file and run on your own computer** (`python app.py`). We show what you will see in words and small diagrams.

## The recipe for every tkinter app

1. Create the **main window** (`tk.Tk()`).
2. Create **widgets** (labels, buttons, entries) and place them in the window.
3. Call `mainloop()`, which keeps the window open and waits for the user.

## Hello, window

```python no-run
import tkinter as tk

root = tk.Tk()
root.title("My First App")
root.geometry("300x150")

label = tk.Label(root, text="Hello, tkinter!", font=("Arial", 16))
label.pack(pady=30)

root.mainloop()
```

```text
+---------------------------------+
| My First App                    |
+---------------------------------+
|                                 |
|        Hello, tkinter!          |
|                                 |
+---------------------------------+
```

- `Tk()` is the window; `title()` and `geometry("WIDTHxHEIGHT")` set its caption and size.
- `Label` shows text; `pack()` places it.
- `mainloop()` is an *event loop*: it runs until the window is closed. Nothing after it runs until then.

## Common widgets

| Widget | Purpose |
|--------|---------|
| `Label` | show text or an image |
| `Button` | a clickable button |
| `Entry` | one-line text input |
| `Text` | multi-line text box |
| `Checkbutton` | tick box |
| `Radiobutton` | pick one of several |
| `Listbox` | a list of choices |
| `Frame` | a container to group widgets |
| `Canvas` | free drawing |

## Buttons and events: doing something on click

A GUI program is **event-driven**: you say *"when this happens, run that function"*.

```python no-run
import tkinter as tk

count = 0

def on_click():
    global count
    count += 1
    label.config(text=f"Clicked {count} times")

root = tk.Tk()
root.title("Counter")

label = tk.Label(root, text="Clicked 0 times", font=("Arial", 14))
label.pack(pady=10)

button = tk.Button(root, text="Click me!", command=on_click)
button.pack(pady=10)

root.mainloop()
```

Pass the function **without brackets** (`command=on_click`, not `on_click()`), otherwise it runs immediately once instead of on each click.

## Reading user input with `Entry`

```python no-run
import tkinter as tk

def greet():
    name = entry.get()
    result.config(text=f"Hello, {name}!" if name else "Please type a name")

root = tk.Tk()
root.title("Greeter")

tk.Label(root, text="Your name:").pack(pady=(10, 0))
entry = tk.Entry(root, width=25)
entry.pack(pady=5)
tk.Button(root, text="Greet", command=greet).pack(pady=5)
result = tk.Label(root, text="", font=("Arial", 14))
result.pack(pady=10)

root.mainloop()
```

`entry.get()` returns the text (always a string), just like `input()`.

## Laying widgets out

tkinter has three layout managers (use only **one** per container):

| Manager | Idea |
|---------|------|
| `pack()` | stack widgets top to bottom (or side by side) |
| `grid(row=, column=)` | a table of rows and columns |
| `place(x=, y=)` | exact pixel positions (rarely a good idea) |

```python no-run
import tkinter as tk

root = tk.Tk()
root.title("Grid Layout")

tk.Label(root, text="Width:").grid(row=0, column=0, padx=5, pady=5)
width = tk.Entry(root)
width.grid(row=0, column=1, padx=5)

tk.Label(root, text="Height:").grid(row=1, column=0, padx=5, pady=5)
height = tk.Entry(root)
height.grid(row=1, column=1, padx=5)

def calculate():
    try:
        area = float(width.get()) * float(height.get())
        answer.config(text=f"Area = {area}")
    except ValueError:
        answer.config(text="Enter two numbers")

tk.Button(root, text="Area", command=calculate).grid(row=2, column=0, columnspan=2, pady=8)
answer = tk.Label(root, text="")
answer.grid(row=3, column=0, columnspan=2)

root.mainloop()
```

```text
+-------------------------------+
| Grid Layout                   |
+-------------------------------+
|  Width:   [_______________]   |
|  Height:  [_______________]   |
|            [   Area   ]       |
|            Area = 200.0       |
+-------------------------------+
```

This calculator uses `try/except` from Module 6 to cope with bad input.

## A digital clock: repeating with `after`

Because `mainloop()` owns the program, **never** use `time.sleep()` or a `while True` loop inside a GUI: the window would freeze. Instead ask tkinter to call your function again later with `after(milliseconds, function)`.

```python no-run
import tkinter as tk
from datetime import datetime

def tick():
    clock.config(text=datetime.now().strftime("%H:%M:%S"))
    root.after(1000, tick)      # run again in 1000 ms

root = tk.Tk()
root.title("Digital Clock")
clock = tk.Label(root, font=("Courier", 40), fg="green", bg="black", padx=20, pady=10)
clock.pack()

tick()
root.mainloop()
```

```text
+-----------------------+
| Digital Clock         |
+-----------------------+
|       14:32:07        |
+-----------------------+
```

This is the core of the lab project in the last lesson.

## Message boxes

```python no-run
import tkinter as tk
from tkinter import messagebox

def ask():
    if messagebox.askyesno("Quit", "Do you really want to quit?"):
        root.destroy()
    else:
        messagebox.showinfo("Phew", "Glad you stayed!")

root = tk.Tk()
tk.Button(root, text="Quit?", command=ask).pack(padx=40, pady=30)
root.mainloop()
```

## Structuring a GUI as a class

Larger apps use a class to hold the widgets and their behaviour together (Module 7 in action):

```python no-run
import tkinter as tk

class CounterApp:
    def __init__(self, root):
        self.count = 0
        self.label = tk.Label(root, text="0", font=("Arial", 30))
        self.label.pack(pady=10)
        tk.Button(root, text="+1", command=self.add).pack(side="left", padx=10, pady=10)
        tk.Button(root, text="Reset", command=self.reset).pack(side="left", padx=10)

    def add(self):
        self.count += 1
        self.label.config(text=str(self.count))

    def reset(self):
        self.count = 0
        self.label.config(text="0")

root = tk.Tk()
root.title("Counter")
CounterApp(root)
root.mainloop()
```

## Checking that tkinter is available

You can test for tkinter without opening a window:

```python
import tkinter
print(tkinter.TkVersion >= 8.5)
```

```output
True
```

If `import tkinter` fails on Linux, install it with `sudo apt install python3-tk`.

## Common Mistakes

**1. Calling the function in `command=`.** Use `command=on_click`, not `command=on_click()`.

**2. Mixing `pack` and `grid` in the same container.** It leads to a frozen or crashing layout.

**3. Blocking the event loop** with `time.sleep()` or long loops. Use `after()`.

**4. Forgetting `mainloop()`.** The window flashes and disappears immediately.

```python no-run
import tkinter as tk
root = tk.Tk()
tk.Label(root, text="I vanish instantly").pack()
# missing root.mainloop()
```

## Try It Yourself

Write (and run on your own computer) a small **tip calculator** window with an entry for the bill, an entry for the tip percentage and a button that shows the total. Use `try/except` to handle bad numbers. Start from the grid area calculator above.

```python-try
# The calculation logic can be tested without any window:
def tip_total(bill, percent):
    return round(bill * (1 + percent / 100), 2)

print(tip_total(500, 10))
print(tip_total(1250, 15))
```

**Challenge:** Turn the greeter into a class-based app and add a button that clears the entry.

## Recap

- tkinter builds GUIs: create `Tk()`, add widgets, call `mainloop()`.
- Widgets: `Label`, `Button`, `Entry`, `Text`, `Frame`...; place them with `pack`, `grid` or `place` (one manager per container).
- GUIs are event-driven: `command=function` runs your code on click.
- Use `widget.config(...)` to change widgets and `entry.get()` to read input.
- Never block the loop; use `root.after(ms, func)` to repeat actions.

**Next up:** **command-line tools** with `sys.argv` and `argparse`.

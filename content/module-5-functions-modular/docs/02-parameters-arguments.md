---
id: 02-parameters-arguments
title: "Parameters, Arguments and Default Values"
order: 2
concepts: ["parameters", "keyword-arguments", "default-arguments"]
---

# Parameters, Arguments and Default Values

When you order a coffee you specify a few details: size, milk, sugar. The barista's "recipe" has *slots* for those details. In a function, those slots are **parameters**; the details you pass in are the **arguments**. Python is unusually flexible about how you fill them.

> **Vocabulary:** `def greet(name):` here `name` is a **parameter**. `greet("Asha")` here `"Asha"` is an **argument**.

## Positional arguments

By default, arguments are matched to parameters **by position**: first with first, second with second.

```python
def describe_pet(animal, name):
    print(f"I have a {animal} named {name}.")

describe_pet("dog", "Rex")
describe_pet("Rex", "dog")
```

```output
I have a dog named Rex.
I have a Rex named dog.
```

Swap the order and you swap the meaning, so the order matters.

## Keyword arguments

Name the parameter in the call and the order no longer matters. This also makes calls easier to read.

```python
def describe_pet(animal, name):
    print(f"I have a {animal} named {name}.")

describe_pet(name="Rex", animal="dog")
describe_pet("cat", name="Tom")
```

```output
I have a dog named Rex.
I have a cat named Tom.
```

Positional arguments must come **before** keyword arguments in a call.

## Default parameter values

Give a parameter a default with `=`. If the caller omits it, the default is used.

```python
def power(base, exponent=2):
    return base ** exponent

print(power(5))
print(power(5, 3))
print(power(exponent=4, base=2))
```

```output
25
125
16
```

Parameters with defaults must come **after** those without.

```python
def greet(name, greeting="Hello", punctuation="!"):
    return f"{greeting}, {name}{punctuation}"

print(greet("Asha"))
print(greet("Asha", "Namaste"))
print(greet("Asha", punctuation="?"))
print(greet("Asha", greeting="Hi", punctuation="."))
```

```output
Hello, Asha!
Namaste, Asha!
Hello, Asha?
Hi, Asha.
```

## The mutable default trap

**Never use a list or dictionary as a default value.** The default is created *once*, when the function is defined, and then shared between all calls.

```python
def add_item(item, basket=[]):
    basket.append(item)
    return basket

print(add_item("apple"))
print(add_item("banana"))
```

```output
['apple']
['apple', 'banana']
```

The second call remembers the first! The correct pattern uses `None` as the default:

```python
def add_item(item, basket=None):
    if basket is None:
        basket = []
    basket.append(item)
    return basket

print(add_item("apple"))
print(add_item("banana"))
```

```output
['apple']
['banana']
```

## Any number of arguments: `*args`

Put `*` before a parameter name and it collects **all extra positional arguments into a tuple**.

```python
def total(*numbers):
    print(numbers)
    return sum(numbers)

print(total(1, 2, 3))
print(total(10, 20))
print(total())
```

```output
(1, 2, 3)
6
(10, 20)
30
()
0
```

## Any number of keyword arguments: `**kwargs`

Two stars collect extra keyword arguments into a **dictionary**.

```python
def show_profile(**details):
    for key, value in details.items():
        print(f"{key}: {value}")

show_profile(name="Asha", age=12, city="Delhi")
```

```output
name: Asha
age: 12
city: Delhi
```

You can combine everything, in this order: normal parameters, `*args`, keyword defaults, `**kwargs`.

```python
def report(title, *scores, curve=0, **extra):
    adjusted = [s + curve for s in scores]
    print(title, adjusted, extra)

report("Maths", 70, 80, curve=5, teacher="Ms Rao")
```

```output
Maths [75, 85] {'teacher': 'Ms Rao'}
```

## Unpacking arguments when you call

The `*` and `**` operators also work in calls: they unpack a list or dictionary into arguments.

```python
def add(a, b, c):
    return a + b + c

values = [1, 2, 3]
print(add(*values))
opts = {"a": 10, "b": 20, "c": 30}
print(add(**opts))
```

```output
6
60
```

## Positional-only and keyword-only parameters

A bare `*` forces the parameters after it to be **keyword-only**, which prevents mixing up long argument lists.

```python
def connect(host, *, port=80, secure=False):
    return f"{host}:{port} secure={secure}"

print(connect("example.com", port=443, secure=True))
```

```output
example.com:443 secure=True
```

## Arguments are passed by reference

The function receives a *reference* to your object. If the object is mutable (like a list), changes made inside the function are visible outside.

```python
def add_bonus(marks):
    marks.append(10)

scores = [50, 60]
add_bonus(scores)
print(scores)

def rebind(x):
    x = 99

n = 5
rebind(n)
print(n)
```

```output
[50, 60, 10]
5
```

Changing the list *inside* is visible; reassigning the parameter name (`x = 99`) only affects the local name.

## Common Mistakes

**1. Wrong number of arguments.**

```python expect-error
def add(a, b):
    return a + b

print(add(1, 2, 3))
```

```output
TypeError: add() takes 2 positional arguments but 3 were given
```

**2. Positional argument after a keyword argument.** `f(a=1, 2)` is a syntax error.

**3. A mutable default** such as `def f(items=[])`.

**4. Unknown keyword.**

```python expect-error
def f(a):
    return a

f(b=1)
```

```output
TypeError: f() got an unexpected keyword argument 'b'
```

## Try It Yourself

Write `make_sandwich(bread, *fillings, toasted=False)` that returns a description like `"toasted wheat sandwich with cheese, tomato"`.

```python-try
def make_sandwich(bread, *fillings, toasted=False):
    prefix = "toasted " if toasted else ""
    return f"{prefix}{bread} sandwich with " + ", ".join(fillings)

print(make_sandwich("wheat", "cheese", "tomato", toasted=True))
print(make_sandwich("white", "jam"))
```

**Challenge:** Write `average(*numbers)` that returns 0 when called with no numbers.

## Recap

- Parameters are the names in `def`; arguments are the values passed in the call.
- Match by position or by keyword; defaults make parameters optional.
- Never use a mutable default like `[]`; use `None` and create the list inside.
- `*args` collects extra positional arguments (a tuple); `**kwargs` collects keyword ones (a dict).
- Mutable arguments can be changed inside a function; rebinding a name cannot.

**Next up:** **return values** in depth.

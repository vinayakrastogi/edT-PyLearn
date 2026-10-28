---
id: 08-lab-function-programs
title: "Lab: Calculator and Number Guessing Game"
order: 8
concepts: ["lab-practice", "function-programs"]
---

# Lab: Programs Built from Functions

In this lab you will see how good programs are structured: many **small functions**, each with a single job, tied together by a short **main flow**. We build a calculator and a guessing game, then a menu-driven program.

## Program 1: calculator using functions

**Design:**
- One function per operation: `add`, `subtract`, `multiply`, `divide`.
- One function that chooses the operation from a symbol.
- A main section that reads input and prints the answer.

```python stdin="12|4|/"
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        return "Error: cannot divide by zero"
    return a / b

def calculate(a, b, operator):
    operations = {"+": add, "-": subtract, "*": multiply, "/": divide}
    if operator not in operations:
        return "Error: unknown operator"
    return operations[operator](a, b)

print("First number?")
x = float(input())
print("Second number?")
y = float(input())
print("Operator (+ - * /)?")
op = input()
print("Result:", calculate(x, y, op))
```

```output
First number?
Second number?
Operator (+ - * /)?
Result: 3.0
```

**Why is this good design?** Each function can be tested alone. Adding a new operation (say `power`) means writing one function and one dictionary entry; nothing else changes. The dictionary replaces a long `if/elif` chain.

### Testing the functions

```python
def add(a, b):
    return a + b

def divide(a, b):
    if b == 0:
        return "Error: cannot divide by zero"
    return a / b

print(add(2, 3) == 5)
print(divide(9, 3) == 3)
print(divide(1, 0))
```

```output
True
True
Error: cannot divide by zero
```

Simple `==` checks like these are a first step toward **automated testing**.

## Program 2: number guessing game

**Design:**
- The computer picks a secret number.
- The player guesses; the program answers "too high" or "too low".
- Count the attempts and celebrate.

To make our example repeatable we pass in the secret number and the list of guesses.

```python
def check_guess(guess, secret):
    if guess < secret:
        return "too low"
    elif guess > secret:
        return "too high"
    return "correct"

def play(secret, guesses):
    attempts = 0
    for guess in guesses:
        attempts += 1
        result = check_guess(guess, secret)
        print(f"Guess {attempts}: {guess} is {result}")
        if result == "correct":
            print(f"You won in {attempts} attempts!")
            return attempts
    print(f"Out of guesses. The number was {secret}.")
    return None

play(42, [50, 25, 37, 43, 42])
```

```output
Guess 1: 50 is too high
Guess 2: 25 is too low
Guess 3: 37 is too low
Guess 4: 43 is too high
Guess 5: 42 is correct
You won in 5 attempts!
```

The interactive version chooses the secret with `random.randint` and reads guesses with `input()`:

```python no-run
import random

def play_interactive():
    secret = random.randint(1, 100)
    attempts = 0
    while True:
        guess = int(input("Your guess (1-100): "))
        attempts += 1
        result = check_guess(guess, secret)
        print(result)
        if result == "correct":
            print(f"You won in {attempts} attempts!")
            break
```

### Smart strategy: binary search

If you always guess the middle of the remaining range, you need at most 7 guesses for numbers from 1 to 100. Let us have a function play the game for us:

```python
def binary_guess(secret, low=1, high=100):
    attempts = 0
    while low <= high:
        guess = (low + high) // 2
        attempts += 1
        result = check_guess(guess, secret)
        if result == "correct":
            return attempts
        elif result == "too low":
            low = guess + 1
        else:
            high = guess - 1

def check_guess(guess, secret):
    if guess < secret:
        return "too low"
    elif guess > secret:
        return "too high"
    return "correct"

print(binary_guess(42))
print(max(binary_guess(n) for n in range(1, 101)))
```

```output
7
7
```

Each guess halves the search space, so no number takes more than 7 tries.

## Program 3: a menu-driven unit converter

```python stdin="2|100|3|3|q"
def km_to_miles(km):
    return km * 0.621371

def celsius_to_fahrenheit(c):
    return c * 9 / 5 + 32

def kg_to_pounds(kg):
    return kg * 2.20462

def show_menu():
    print("1) km to miles")
    print("2) Celsius to Fahrenheit")
    print("3) kg to pounds")
    print("q) quit")

conversions = {"1": km_to_miles, "2": celsius_to_fahrenheit, "3": kg_to_pounds}

while True:
    show_menu()
    choice = input()
    if choice == "q":
        print("Goodbye!")
        break
    if choice in conversions:
        value = float(input())
        print(f"Result: {conversions[choice](value):.2f}")
    else:
        print("Invalid choice")
```

```output
1) km to miles
2) Celsius to Fahrenheit
3) kg to pounds
q) quit
Result: 212.00
1) km to miles
2) Celsius to Fahrenheit
3) kg to pounds
q) quit
Result: 6.61
1) km to miles
2) Celsius to Fahrenheit
3) kg to pounds
q) quit
Goodbye!
```

Here the input `2 / 100` converted 100 degrees Celsius, then `3 / 3` converted 3 kg, and `q` quit.

## Program structure checklist

1. **Small functions** with clear names and one job each.
2. **Pure where possible**: take parameters, return results, avoid globals.
3. **A short main section** that connects the pieces.
4. **Guard** demo code with `if __name__ == "__main__":`.
5. **Test** each function with a few inputs, including edge cases.

## Common Mistakes

**1. One giant function.** Split it into helpers.

**2. Functions that do input, calculation *and* printing.** Separate the calculation so you can reuse and test it.

**3. Forgetting edge cases** such as division by zero or invalid menu choices.

**4. Comparing `input()` text with numbers.** `choice == 1` is never true when `choice` is `"1"`.

## Try It Yourself

Add a `power` operation and a `modulus` operation to the calculator, then test them.

```python-try
def power(a, b):
    return a ** b

def modulus(a, b):
    if b == 0:
        return "Error: cannot divide by zero"
    return a % b

print(power(2, 8))
print(modulus(17, 5))
print(modulus(1, 0))
```

**More challenges:**
1. Write `is_prime(n)` and use it to print all primes below 50.
2. Build a "temperature report" that calls three helper functions and prints a formatted summary.
3. Improve the guessing game so the player has a maximum of 7 attempts.

## Recap

- Build programs from small, well-named functions and a short main flow.
- A dictionary of functions can replace a long if/elif chain.
- Keep calculation separate from input/output so functions are easy to test.
- Binary search halves the possibilities every guess.
- Test each function with normal and edge-case inputs.

**Congratulations!** Your code is now organised and reusable. Module 6 teaches how programs work with **files** and survive **errors**.

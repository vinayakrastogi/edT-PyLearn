---
id: 01-while-loops
title: "While Loops - Repetition Control"
order: 1
concepts: ["while-loop", "iteration", "loop-control"]
---

# While Loops - Repetition Control

## What is a Loop?

A **loop** is a programming structure that repeats a block of code multiple times. Instead of writing the same code again and again, we use loops for efficiency.

### Why Use Loops?

**Without Loop (Inefficient):**
```python
print("Welcome!")
print("Welcome!")
print("Welcome!")
print("Welcome!")
print("Welcome!")
```

**With Loop (Efficient):**
```python
count = 0
while count < 5:
    print("Welcome!")
    count += 1
```

## The while Loop Syntax

```python
while condition:
    # Code to repeat
    # This runs as long as condition is True
```

### How It Works

1. Check if condition is `True`
2. If `True`: Execute the code block, then go back to step 1
3. If `False`: Exit the loop and continue with rest of program

```python
# Example: Count to 5
count = 1
while count <= 5:
    print(count)
    count += 1

print("Done!")
```

Output:
```
1
2
3
4
5
Done!
```

## Basic While Loop Examples

### Example 1: Countdown Timer
```python
countdown = 10
while countdown > 0:
    print(f"{countdown}...")
    countdown -= 1
print("Blast off!")
```

Output:
```
10...
9...
8...
...
1...
Blast off!
```

### Example 2: Sum of Numbers
```python
total = 0
number = 1

while number <= 10:
    total += number  # Add number to total
    number += 1

print(f"Sum of 1 to 10: {total}")  # 55
```

### Example 3: User Input Validation
```python
password = ""
while password != "python123":
    password = input("Enter password: ")
    if password != "python123":
        print("Wrong password! Try again.")

print("Access granted!")
```

### Example 4: Multiplication Table
```python
number = int(input("Enter a number: "))
multiplier = 1

print(f"\nMultiplication Table of {number}:")
while multiplier <= 10:
    result = number * multiplier
    print(f"{number} × {multiplier} = {result}")
    multiplier += 1
```

## Loop Control: Increment and Decrement

### Increment (Increase)
```python
# count = count + 1 is same as count += 1
count = 0
while count < 5:
    print(count)
    count += 1  # Increment by 1

# Increment by other values
count = 0
while count < 20:
    print(count)
    count += 5  # Increment by 5 (0, 5, 10, 15)
```

### Decrement (Decrease)
```python
count = 10
while count > 0:
    print(count)
    count -= 1  # Decrement by 1

# Decrement by other values
count = 100
while count > 0:
    print(count)
    count -= 10  # Decrement by 10 (100, 90, 80...)
```

## Infinite Loops (Careful!)

An **infinite loop** runs forever because the condition never becomes `False`.

### Common Causes

**1. Forgetting to Update Counter:**
```python
# INFINITE LOOP - Don't run this!
count = 1
while count <= 5:
    print("Hello")
    # Forgot: count += 1
```

**2. Wrong Condition:**
```python
# INFINITE LOOP
count = 1
while count > 0:  # Always true!
    print(count)
    count += 1  # Makes it even larger
```

### Intentional Infinite Loops

Sometimes we want loops to run forever (until broken):
```python
while True:
    command = input("Enter command (or 'quit'): ")
    if command == "quit":
        break
    print(f"You entered: {command}")
```

## Loop Patterns

### Pattern 1: Counter-Based Loop
```python
# Execute exactly N times
counter = 0
while counter < 10:
    print(f"Iteration {counter + 1}")
    counter += 1
```

### Pattern 2: Sentinel-Based Loop
```python
# Loop until special value entered
total = 0
number = int(input("Enter number (0 to stop): "))

while number != 0:
    total += number
    number = int(input("Enter number (0 to stop): "))

print(f"Total: {total}")
```

### Pattern 3: Flag-Based Loop
```python
found = False
count = 0

while not found and count < 100:
    count += 1
    if count % 7 == 0 and count % 3 == 0:
        print(f"Found: {count}")
        found = True
```

## Complex While Loop Examples

### Example 1: Factorial Calculator
```python
number = int(input("Enter a number: "))
factorial = 1
counter = 1

while counter <= number:
    factorial *= counter
    counter += 1

print(f"Factorial of {number} is {factorial}")
```

**Example:**
- Input: 5
- Calculation: 1 × 2 × 3 × 4 × 5 = 120

### Example 2: Fibonacci Series
```python
n = int(input("How many Fibonacci numbers? "))
a, b = 0, 1
count = 0

print("Fibonacci Series:")
while count < n:
    print(a, end=" ")
    a, b = b, a + b  # Simultaneous assignment
    count += 1

print()
```

**Example Output (n=10):**
```
0 1 1 2 3 5 8 13 21 34
```

### Example 3: Number Guessing Game
```python
import random

secret = random.randint(1, 100)
attempts = 0
guess = 0

print("I'm thinking of a number between 1 and 100...")

while guess != secret:
    guess = int(input("Your guess: "))
    attempts += 1
    
    if guess < secret:
        print("Too low! Try again.")
    elif guess > secret:
        print("Too high! Try again.")

print(f"Correct! You got it in {attempts} attempts!")
```

### Example 4: Prime Number Checker
```python
number = int(input("Enter a number: "))
divisor = 2
is_prime = True

if number < 2:
    is_prime = False
else:
    while divisor <= number // 2:
        if number % divisor == 0:
            is_prime = False
            break
        divisor += 1

if is_prime:
    print(f"{number} is a prime number")
else:
    print(f"{number} is not a prime number")
```

## Nested While Loops

A loop inside another loop:

### Example 1: Multiplication Table (1-5)
```python
outer = 1
while outer <= 5:
    inner = 1
    while inner <= 5:
        print(f"{outer} × {inner} = {outer * inner:2}", end="  ")
        inner += 1
    print()  # New line after each row
    outer += 1
```

Output:
```
1 × 1 =  1  1 × 2 =  2  1 × 3 =  3  1 × 4 =  4  1 × 5 =  5  
2 × 1 =  2  2 × 2 =  4  2 × 3 =  6  2 × 4 =  8  2 × 5 = 10  
...
```

### Example 2: Number Pattern
```python
row = 1
while row <= 5:
    col = 1
    while col <= row:
        print(col, end=" ")
        col += 1
    print()
    row += 1
```

Output:
```
1
1 2
1 2 3
1 2 3 4
1 2 3 4 5
```

## Common While Loop Patterns

### 1. Sum Accumulator
```python
total = 0
count = 1
while count <= 100:
    total += count
    count += 1
print(f"Sum: {total}")  # 5050
```

### 2. Max/Min Finder
```python
maximum = float('-inf')
count = 0

while count < 5:
    num = int(input(f"Enter number {count + 1}: "))
    if num > maximum:
        maximum = num
    count += 1

print(f"Maximum: {maximum}")
```

### 3. Validation Loop
```python
age = -1
while age < 0 or age > 120:
    age = int(input("Enter age (0-120): "))
    if age < 0 or age > 120:
        print("Invalid age! Try again.")

print(f"Valid age: {age}")
```

## Loop Debugging Tips

### Tip 1: Print Counter Values
```python
count = 1
while count <= 5:
    print(f"Counter: {count}")  # Debug output
    # Your code here
    count += 1
```

### Tip 2: Set Maximum Iterations (Safety)
```python
count = 0
max_iterations = 1000

while condition and count < max_iterations:
    # Your code
    count += 1

if count >= max_iterations:
    print("Warning: Loop limit reached!")
```

### Tip 3: Use Meaningful Variable Names
```python
# Bad
i = 0
while i < 10:
    # What is i?
    i += 1

# Good
attempt_count = 0
while attempt_count < 10:
    # Clear purpose
    attempt_count += 1
```

## Summary

### Key Concepts
- **while loop**: Repeats code while condition is `True`
- **Increment/Decrement**: `count += 1` or `count -= 1`
- **Infinite loops**: Avoid by ensuring condition eventually becomes `False`
- **Loop patterns**: Counter-based, sentinel-based, flag-based
- **Nested loops**: Loop inside a loop for complex patterns

### When to Use While Loops
- Unknown number of iterations
- Need to loop until specific condition
- User input validation
- Menu-driven programs
- Game loops

### Common Mistakes
1. Forgetting to update loop variable
2. Wrong comparison operators
3. Not initializing variables before loop
4. Off-by-one errors (< vs <=)

### Practice Problems

1. **Sum Input Numbers**: Keep asking for numbers until user enters 0, then show sum
2. **Reverse Number**: Input 12345, output 54321 using while loop
3. **Digit Counter**: Count how many digits in a number
4. **Power Calculator**: Calculate x^y using repeated multiplication
5. **Menu System**: Create a calculator menu that loops until user chooses "Exit"

**Next Up**: Learn about for loops and the range() function!

---
id: 02-for-loops-and-range
title: "For Loops and Range Function"
order: 2
concepts: ["for-loop", "range", "iteration", "sequences"]
---

# For Loops and Range Function

## What is a For Loop?

A **for loop** iterates over a sequence (like a list, string, or range) and executes code for each item. It's cleaner than while loops when you know exactly how many times to iterate.

### Basic Syntax

```python
for variable in sequence:
    # Code to execute for each item
```

## The range() Function

The `range()` function generates a sequence of numbers. It's the most common way to create for loops with numbers.

### range() Variations

**1. range(stop)** - From 0 to stop-1:
```python
for i in range(5):
    print(i)
# Output: 0, 1, 2, 3, 4
```

**2. range(start, stop)** - From start to stop-1:
```python
for i in range(2, 7):
    print(i)
# Output: 2, 3, 4, 5, 6
```

**3. range(start, stop, step)** - With custom increment:
```python
# Count by 2
for i in range(0, 11, 2):
    print(i)
# Output: 0, 2, 4, 6, 8, 10

# Count backwards
for i in range(10, 0, -1):
    print(i)
# Output: 10, 9, 8, 7, 6, 5, 4, 3, 2, 1
```

### Understanding range()

```python
# range() creates a sequence, but doesn't store it in memory
print(range(5))        # range(0, 5)
print(list(range(5)))  # [0, 1, 2, 3, 4]

# Memory efficient - generates numbers on demand
for i in range(1000000):
    pass  # Uses minimal memory
```

## Basic For Loop Examples

### Example 1: Print Numbers
```python
print("Numbers 1 to 10:")
for num in range(1, 11):
    print(num, end=" ")
print()  # Newline

# Output: 1 2 3 4 5 6 7 8 9 10
```

### Example 2: Multiplication Table
```python
number = int(input("Enter a number: "))

print(f"\nMultiplication Table of {number}:")
for i in range(1, 11):
    result = number * i
    print(f"{number} × {i} = {result}")
```

Output (for 7):
```
Multiplication Table of 7:
7 × 1 = 7
7 × 2 = 14
...
7 × 10 = 70
```

### Example 3: Sum of Numbers
```python
total = 0
for num in range(1, 101):
    total += num

print(f"Sum of 1 to 100: {total}")  # 5050
```

### Example 4: Even Numbers
```python
print("Even numbers from 1 to 20:")
for num in range(2, 21, 2):  # Start at 2, step by 2
    print(num, end=" ")
print()

# Alternative approach
print("\nEven numbers (alternative):")
for num in range(1, 21):
    if num % 2 == 0:
        print(num, end=" ")
print()
```

## Iterating Over Strings

You can iterate over each character in a string:

```python
word = "Python"
for char in word:
    print(char)

# Output:
# P
# y
# t
# h
# o
# n
```

### String Examples

**Count Vowels:**
```python
text = "Hello World"
vowels = "aeiouAEIOU"
count = 0

for char in text:
    if char in vowels:
        count += 1

print(f"Vowels: {count}")  # 3
```

**Reverse a String:**
```python
text = "Python"
reversed_text = ""

for char in text:
    reversed_text = char + reversed_text

print(reversed_text)  # nohtyP
```

## Iterating Over Lists

```python
fruits = ["apple", "banana", "cherry", "date"]

# Method 1: Direct iteration
for fruit in fruits:
    print(f"I like {fruit}")

# Method 2: Using index
for i in range(len(fruits)):
    print(f"{i + 1}. {fruits[i]}")

# Method 3: Using enumerate (best for index + value)
for index, fruit in enumerate(fruits):
    print(f"{index}: {fruit}")
```

Output:
```
I like apple
I like banana
I like cherry
I like date

1. apple
2. banana
3. cherry
4. date

0: apple
1: banana
2: cherry
3: date
```

## Nested For Loops

A for loop inside another for loop - useful for patterns and 2D structures.

### Example 1: Simple Pattern
```python
for row in range(3):
    for col in range(5):
        print("*", end=" ")
    print()  # New line after each row

# Output:
# * * * * *
# * * * * *
# * * * * *
```

### Example 2: Number Grid
```python
for row in range(1, 4):
    for col in range(1, 6):
        print(row * col, end="\t")
    print()

# Output:
# 1	2	3	4	5
# 2	4	6	8	10
# 3	6	9	12	15
```

### Example 3: Multiplication Table (1-5)
```python
print("Multiplication Table (1-5):\n")
for i in range(1, 6):
    for j in range(1, 6):
        print(f"{i*j:3}", end=" ")
    print()

# Output:
#   1   2   3   4   5 
#   2   4   6   8  10 
#   3   6   9  12  15 
#   4   8  12  16  20 
#   5  10  15  20  25
```

## Loop Control Statements

### 1. break - Exit Loop Early

```python
# Find first number divisible by 7
for num in range(1, 100):
    if num % 7 == 0:
        print(f"First number divisible by 7: {num}")
        break  # Exit loop

# Search in a list
students = ["Alice", "Bob", "Charlie", "David"]
search = "Charlie"

for student in students:
    if student == search:
        print(f"Found {search}!")
        break
else:
    print(f"{search} not found")
```

### 2. continue - Skip Current Iteration

```python
# Print odd numbers only
for num in range(1, 11):
    if num % 2 == 0:
        continue  # Skip even numbers
    print(num, end=" ")

# Output: 1 3 5 7 9

# Skip negative numbers
numbers = [5, -2, 8, -1, 3, -7, 9]
for num in numbers:
    if num < 0:
        continue
    print(num, end=" ")

# Output: 5 8 3 9
```

### 3. pass - Do Nothing (Placeholder)

```python
# Placeholder for future code
for i in range(5):
    if i == 3:
        pass  # TODO: Implement special case later
    else:
        print(i)

# Useful in development
for item in shopping_list:
    pass  # Will implement later
```

### 4. else with For Loop

The `else` block runs if loop completes normally (not broken):

```python
# Check if number is prime
number = 17
for divisor in range(2, number):
    if number % divisor == 0:
        print(f"{number} is not prime")
        break
else:
    print(f"{number} is prime")

# Search example
numbers = [10, 20, 30, 40]
search_for = 25

for num in numbers:
    if num == search_for:
        print(f"Found {search_for}")
        break
else:
    print(f"{search_for} not found")  # This runs
```

## Advanced For Loop Patterns

### Pattern 1: Factorial
```python
n = int(input("Enter a number: "))
factorial = 1

for i in range(1, n + 1):
    factorial *= i

print(f"Factorial of {n} = {factorial}")
```

### Pattern 2: Fibonacci Series
```python
n = int(input("How many terms? "))
a, b = 0, 1

print("Fibonacci Series:")
for _ in range(n):
    print(a, end=" ")
    a, b = b, a + b
print()
```

### Pattern 3: Prime Numbers in Range
```python
start = int(input("Start: "))
end = int(input("End: "))

print(f"Prime numbers between {start} and {end}:")
for num in range(start, end + 1):
    if num < 2:
        continue
    
    is_prime = True
    for divisor in range(2, int(num ** 0.5) + 1):
        if num % divisor == 0:
            is_prime = False
            break
    
    if is_prime:
        print(num, end=" ")
print()
```

### Pattern 4: Reverse Number
```python
number = int(input("Enter a number: "))
reversed_num = 0

temp = number
for _ in range(len(str(number))):
    digit = temp % 10
    reversed_num = reversed_num * 10 + digit
    temp //= 10

print(f"Original: {number}")
print(f"Reversed: {reversed_num}")
```

## For vs While Loops

### Use For Loop When:
- Iterating over a sequence (list, string, range)
- You know the number of iterations
- Working with indices

```python
# Perfect for for loop
for i in range(10):
    print(f"Iteration {i}")

for fruit in fruits:
    print(fruit)
```

### Use While Loop When:
- Unknown number of iterations
- Condition-based looping
- User input validation

```python
# Better with while loop
password = ""
while password != "secret":
    password = input("Enter password: ")
```

## Common For Loop Patterns

### 1. Accumulator Pattern
```python
# Sum
total = 0
for num in range(1, 11):
    total += num

# Product
product = 1
for num in range(1, 6):
    product *= num
```

### 2. Counter Pattern
```python
text = "Hello World"
space_count = 0

for char in text:
    if char == " ":
        space_count += 1
```

### 3. Filter Pattern
```python
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
evens = []

for num in numbers:
    if num % 2 == 0:
        evens.append(num)
```

### 4. Transform Pattern
```python
names = ["alice", "bob", "charlie"]
capitalized = []

for name in names:
    capitalized.append(name.title())
```

## Practical Examples

### Example 1: Grade Calculator
```python
print("=== Grade Calculator ===")
num_students = int(input("Number of students: "))
total = 0

for i in range(1, num_students + 1):
    score = float(input(f"Score for student {i}: "))
    total += score

average = total / num_students
print(f"\nClass Average: {average:.2f}")

if average >= 90:
    print("Grade: A")
elif average >= 80:
    print("Grade: B")
elif average >= 70:
    print("Grade: C")
else:
    print("Grade: F")
```

### Example 2: Shopping Cart
```python
total = 0
print("=== Shopping Cart ===")

for i in range(1, 4):
    print(f"\nItem {i}:")
    price = float(input("  Price: $"))
    quantity = int(input("  Quantity: "))
    total += price * quantity

tax = total * 0.08
final_total = total + tax

print(f"\nSubtotal: ${total:.2f}")
print(f"Tax (8%): ${tax:.2f}")
print(f"Total: ${final_total:.2f}")
```

### Example 3: Password Strength Checker
```python
password = input("Enter password: ")

has_upper = False
has_lower = False
has_digit = False
has_special = False

for char in password:
    if char.isupper():
        has_upper = True
    elif char.islower():
        has_lower = True
    elif char.isdigit():
        has_digit = True
    elif char in "!@#$%^&*":
        has_special = True

strength = sum([has_upper, has_lower, has_digit, has_special])

print(f"\nPassword Strength: {strength}/4")
if strength == 4 and len(password) >= 8:
    print("Strong password!")
elif strength >= 3:
    print("Medium password")
else:
    print("Weak password")
```

## Summary

### Key Concepts
- **for loop**: Iterate over sequences
- **range()**: Generate number sequences
- **break**: Exit loop early
- **continue**: Skip current iteration
- **else**: Runs if loop completes normally
- **Nested loops**: Loop inside a loop

### range() Quick Reference
```python
range(5)           # 0, 1, 2, 3, 4
range(2, 7)        # 2, 3, 4, 5, 6
range(0, 10, 2)    # 0, 2, 4, 6, 8
range(10, 0, -1)   # 10, 9, 8, ..., 1
```

### Best Practices
1. Use for loops for known iterations
2. Use meaningful variable names
3. Avoid modifying loop variable inside loop
4. Use enumerate() for index + value
5. Use break/continue wisely

### Practice Problems

1. **Sum of Squares**: Calculate 1² + 2² + 3² + ... + 10²
2. **Prime Checker**: Check if a number is prime
3. **Palindrome Detector**: Check if a string reads same forwards and backwards
4. **Digit Sum**: Find sum of digits in a number
5. **Pattern Printer**: Create a right-angled triangle pattern with numbers

**Next Up**: Learn about pattern programming and nested loops!

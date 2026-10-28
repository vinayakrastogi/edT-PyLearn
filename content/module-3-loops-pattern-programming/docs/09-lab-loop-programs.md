---
id: 09-lab-loop-programs
title: "Lab: Tables, Primes, Fibonacci and Factorial"
order: 9
concepts: ["lab-practice", "loop-programs"]
---

# Lab: Classic Loop Programs

These four programs appear in every programming course and interview. Each one uses a loop recipe you already know. Read the idea, study the code, predict the output, then run it.

## Program 1: multiplication table

**Idea:** multiply the chosen number by 1, 2, 3, ... 10.

```python stdin="7"
print("Which table?")
n = int(input())
for i in range(1, 11):
    print(f"{n} x {i:2} = {n * i:3}")
```

```output
Which table?
7 x  1 =   7
7 x  2 =  14
7 x  3 =  21
7 x  4 =  28
7 x  5 =  35
7 x  6 =  42
7 x  7 =  49
7 x  8 =  56
7 x  9 =  63
7 x 10 =  70
```

`:2` and `:3` reserve widths so the numbers line up in neat columns.

## Program 2: factorial

**Idea:** `n!` is the product `1 x 2 x 3 x ... x n`. It counts the ways to arrange `n` objects. Use the *product accumulator* starting at 1. By definition `0! = 1`.

```python stdin="5"
print("Factorial of?")
n = int(input())
result = 1
for i in range(2, n + 1):
    result *= i
print(f"{n}! = {result}")
```

```output
Factorial of?
5! = 120
```

Try `0` (the loop does not run, so the answer stays 1) and `20` (a huge number, but Python integers never overflow).

## Program 3: prime number check

**Idea:** a **prime** is a number greater than 1 that has no divisors other than 1 and itself. To test `n`, try every possible divisor from 2 up to `n - 1`. If any divides evenly, it is not prime. We can stop early at the square root, because divisors come in pairs.

```python stdin="29"
print("Enter a number:")
n = int(input())
is_prime = n > 1
i = 2
while i * i <= n:
    if n % i == 0:
        is_prime = False
        break
    i += 1
print(n, "is prime" if is_prime else "is not prime")
```

```output
Enter a number:
29 is prime
```

`i * i <= n` is the same as `i <= sqrt(n)`. Checking 1,000,003 needs about 1,000 tests instead of a million.

### All primes up to N

```python
limit = 30
primes = []
for n in range(2, limit + 1):
    is_prime = True
    for d in range(2, int(n ** 0.5) + 1):
        if n % d == 0:
            is_prime = False
            break
    if is_prime:
        primes.append(n)
print(primes)
```

```output
[2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
```

## Program 4: Fibonacci series

**Idea:** each number is the sum of the previous two: 0, 1, 1, 2, 3, 5, 8, 13, ... Keep two variables and update them together.

```python stdin="10"
print("How many terms?")
count = int(input())
a, b = 0, 1
for _ in range(count):
    print(a, end=" ")
    a, b = b, a + b
print()
```

```output
How many terms?
0 1 1 2 3 5 8 13 21 34
```

The line `a, b = b, a + b` is the whole trick: the right side is calculated first using the **old** values, then both variables are updated at once.

## Program 5: sum of digits and reversing a number

```python
n = 12345
digit_sum = 0
reversed_n = 0
while n > 0:
    digit = n % 10
    digit_sum += digit
    reversed_n = reversed_n * 10 + digit
    n //= 10
print("Digit sum:", digit_sum)
print("Reversed:", reversed_n)
```

```output
Digit sum: 15
Reversed: 54321
```

## Program 6: number guessing hint (loop with `break`)

```python stdin="50|75|63|68|65"
secret = 65
attempts = 0
while True:
    guess = int(input())
    attempts += 1
    if guess == secret:
        print(f"Correct in {attempts} tries!")
        break
    elif guess < secret:
        print(guess, "is too low")
    else:
        print(guess, "is too high")
```

```output
50 is too low
75 is too high
63 is too low
68 is too high
Correct in 5 tries!
```

## Choosing the right loop

| Program | Loop used | Reason |
|---------|-----------|--------|
| Multiplication table | `for` with `range(1, 11)` | fixed count |
| Factorial | `for` with `range(2, n+1)` | known count |
| Prime check | `while` with `break` | stop early |
| Fibonacci | `for` with `range(count)` | known count |
| Guessing | `while True` + `break` | unknown count |

## Common Mistakes

**1. Factorial with `range(1, n)`.** That stops at `n - 1`. Use `range(2, n + 1)`.

**2. Treating 1 as prime.** Primes must be greater than 1. The `n > 1` guard handles it.

**3. Updating Fibonacci variables one at a time.**

```python
a, b = 0, 1
a = b
b = a + b
print(a, b)
```

```output
1 2
```

This loses the old `a`. The correct first step from `(0, 1)` is `(1, 1)`, which needs the simultaneous update `a, b = b, a + b`.

**4. Forgetting that `input()` returns text.**

## Try It Yourself

Print the first 10 terms of the Fibonacci series, then the factorial of 6, then the sum of all multiples of 3 or 5 below 100.

```python-try
a, b = 0, 1
for _ in range(10):
    print(a, end=" ")
    a, b = b, a + b
print()

fact = 1
for i in range(2, 7):
    fact *= i
print("6! =", fact)

total = 0
for n in range(1, 100):
    if n % 3 == 0 or n % 5 == 0:
        total += n
print("Sum:", total)
```

**More challenges:**
1. Print all perfect numbers under 1000 (a number equal to the sum of its proper divisors, like 6 = 1 + 2 + 3).
2. Check whether a number is a palindrome using the reverse trick.
3. Print the Collatz sequence of a number (if even divide by 2, otherwise 3n + 1) until it reaches 1.

## Recap

- Multiplication tables and factorials are `for` loops with accumulators.
- A prime test loops over possible divisors and `break`s early; stopping at the square root makes it fast.
- Fibonacci uses simultaneous assignment: `a, b = b, a + b`.
- `while True` with `break` fits "repeat until the user is right" problems.
- Choose `for` for known counts and `while` for the unknown.

**Congratulations!** You can now automate repetition. Module 4 gives your programs real memory with **strings, lists, tuples, sets and dictionaries**.

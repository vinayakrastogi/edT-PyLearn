---
id: 01-while-loops
title: "The while Loop"
order: 1
concepts: ["while-loop", "loop-counter", "infinite-loop"]
---

# The while Loop

Imagine you have to write "I will not talk in class" 100 times as a punishment. You *could* write 100 `print()` lines... or you could tell the computer: "keep doing this **while** the count is below 100". That idea, **repeating code**, is called a **loop**, and it is the biggest time-saver in programming.

## Syntax

```text
while condition:
    body (repeated as long as the condition is True)
```

Python checks the condition. If it is `True`, it runs the body and then checks the condition **again**. When the condition becomes `False`, the loop ends and the program continues after it.

```python
count = 1
while count <= 5:
    print("Count is", count)
    count += 1
print("Done!")
```

```output
Count is 1
Count is 2
Count is 3
Count is 4
Count is 5
Done!
```

## The three parts of a good while loop

Almost every `while` loop has three ingredients:

1. **Initialise** the loop variable before the loop (`count = 1`).
2. **Test** it in the condition (`count <= 5`).
3. **Update** it inside the body (`count += 1`).

If you forget the update, the condition never changes and the loop **never ends**. That is called an **infinite loop**.

## Tracing a loop

Follow the variables step by step as though you were the computer:

```python
total = 0
n = 1
while n <= 4:
    total += n
    print(f"n={n}, total={total}")
    n += 1
print("Final total:", total)
```

```output
n=1, total=1
n=2, total=3
n=3, total=6
n=4, total=10
Final total: 10
```

We have just added 1 + 2 + 3 + 4. Tracing with print statements (or a table on paper) is the best way to understand loops.

## Counting down

```python
n = 5
while n > 0:
    print(n)
    n -= 1
print("Liftoff!")
```

```output
5
4
3
2
1
Liftoff!
```

## Counting by steps

The update does not have to be `+ 1`:

```python
n = 0
while n <= 20:
    print(n, end=" ")
    n += 5
print()
```

```output
0 5 10 15 20 
```

## Loops that depend on the user

A `while` loop is perfect when you do not know in advance how many times to repeat: for example, keep asking until the user gives a valid answer.

```python stdin="abc|-4|7"
print("Enter a number from 1 to 10:")
answer = input()
while not (answer.isdigit() and 1 <= int(answer) <= 10):
    print("Invalid, try again:")
    answer = input()
print("You chose", answer)
```

```output
Enter a number from 1 to 10:
Invalid, try again:
Invalid, try again:
You chose 7
```

The loop kept asking until it got a valid answer. This pattern (ask once, then repeat while invalid) is called **input validation**.

## The sentinel pattern

A **sentinel** is a special value that means "stop". Here `0` ends the list:

```python stdin="10|20|5|0"
total = 0
print("Enter numbers (0 to stop):")
number = int(input())
while number != 0:
    total += number
    number = int(input())
print("Sum:", total)
```

```output
Enter numbers (0 to stop):
Sum: 35
```

## while with else

A `while` loop may have an `else` block that runs when the loop ends **normally** (not through `break`, which you will meet soon).

```python
n = 1
while n <= 3:
    print(n)
    n += 1
else:
    print("Loop finished normally")
```

```output
1
2
3
Loop finished normally
```

## Infinite loops (and how to escape)

Sometimes an infinite loop is on purpose (a game's main loop, a server waiting for requests). Otherwise it is a bug. If your program seems stuck, press **Ctrl + C** in the terminal to stop it. On this site, code that runs longer than 5 seconds is stopped automatically.

```python no-run
count = 1
while count <= 5:
    print(count)
    # Oops! Forgot count += 1, so this prints 1 forever
```

## Common Mistakes

**1. Forgetting to update the loop variable** (infinite loop, as shown above).

**2. Off-by-one errors.** `while n < 5` stops at 4 while `while n <= 5` includes 5.

```python
n = 1
while n < 5:
    print(n, end=" ")
    n += 1
print()
```

```output
1 2 3 4 
```

**3. Updating in the wrong direction.** Counting down needs `n -= 1`, not `n += 1`.

**4. Modifying the wrong variable.** Make sure the variable in the condition is the same one you update.

## Try It Yourself

Print the first 10 multiples of 3, then compute the sum of the digits of 4729 using a loop and `%` / `//`.

```python-try
n = 1
while n <= 10:
    print(3 * n, end=" ")
    n += 1
print()

number = 4729
digit_sum = 0
while number > 0:
    digit_sum += number % 10
    number //= 10
print("Digit sum:", digit_sum)
```

**Challenge:** Keep asking the user for a password until they type `python`.

## Recap

- A `while` loop repeats its body as long as the condition is `True`.
- Initialise, test, update: forget the update and you get an infinite loop.
- Trace loops with a table or `print()` to see what is happening.
- `while` is ideal when you do not know how many repetitions you need (validation, sentinels).
- Off-by-one errors come from choosing `<` versus `<=`.

**Next up:** the `for` loop and `range()`, for when you *do* know how many times.

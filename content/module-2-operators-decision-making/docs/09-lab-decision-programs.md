---
id: 09-lab-decision-programs
title: "Lab: Grade Calculator, Largest Number and ATM"
order: 9
concepts: ["lab-practice", "decision-programs"]
---

# Lab: Decision-Making Programs

Now you will combine everything from this module (operators, `if`, `elif`, `else`, nesting) to build three complete programs. For each one: read the *problem*, study the *plan*, then look at the *solution*. Try to write your own version first!

## Program 1: Grade calculator

**Problem:** read marks for three subjects, compute the average and print the grade.

**Plan:**
1. Read three marks (as numbers).
2. Average = total / 3.
3. Use an `elif` chain from the highest grade down.

```python stdin="88|92|79"
print("Enter three marks:")
m1 = float(input())
m2 = float(input())
m3 = float(input())

average = (m1 + m2 + m3) / 3

if average >= 90:
    grade = "A"
elif average >= 80:
    grade = "B"
elif average >= 70:
    grade = "C"
elif average >= 60:
    grade = "D"
else:
    grade = "F"

print(f"Average: {average:.2f}")
print(f"Grade: {grade}")
```

```output
Enter three marks:
Average: 86.33
Grade: B
```

**Edge cases to test:** exactly 90, exactly 60, all zeros, all 100.

## Program 2: Largest of three numbers

**Problem:** read three numbers and print the largest.

```python stdin="14|42|27"
print("Enter three numbers:")
a = int(input())
b = int(input())
c = int(input())

if a >= b and a >= c:
    largest = a
elif b >= a and b >= c:
    largest = b
else:
    largest = c

print("Largest:", largest)
```

```output
Enter three numbers:
Largest: 42
```

**Why does this work?** If `a` is not the largest and `b` is not the largest, `c` must be. Also try it with equal numbers such as `5, 5, 3`.

## Program 3: ATM eligibility and withdrawal

**Problem:** the ATM asks for the PIN and the amount. The withdrawal is allowed only when:
- the PIN is correct (`1234`),
- the amount is a multiple of 100,
- the amount does not exceed the balance,
- the amount is at most 10,000 per transaction.

```python stdin="1234|2500"
balance = 5000
print("Enter PIN:")
pin = input()
print("Enter amount:")
amount = int(input())

if pin != "1234":
    print("Wrong PIN")
elif amount % 100 != 0:
    print("Amount must be a multiple of 100")
elif amount > 10000:
    print("Limit is 10000 per transaction")
elif amount > balance:
    print("Insufficient funds")
else:
    balance -= amount
    print(f"Collect your cash: {amount}")
    print(f"Remaining balance: {balance}")
```

```output
Enter PIN:
Enter amount:
Collect your cash: 2500
Remaining balance: 2500
```

Notice the style: a flat `elif` chain of "reasons to refuse", with `else` being the success case. Each rule is easy to add or remove. This is far more readable than five levels of nested `if`s.

## Bonus: leap year checker

```python stdin="2100"
print("Enter a year:")
year = int(input())
if (year % 4 == 0 and year % 100 != 0) or year % 400 == 0:
    print(year, "is a leap year")
else:
    print(year, "is not a leap year")
```

```output
Enter a year:
2100 is not a leap year
```

## Common Mistakes

**1. Reading the marks as text.** `"88" + "92"` joins text; always convert.

**2. Testing conditions in the wrong order.** In the grade program, testing `average >= 60` first would give everyone a D.

**3. Not testing boundary values.** Bugs hide at the edges (`>=` versus `>`). Test 90, 89.99, 60, 59.

```python
average = 89.99
if average >= 90:
    print("A")
elif average >= 80:
    print("B")
```

```output
B
```

**4. Forgetting the final `else`.** Decide what should happen when no condition matches.

## Try It Yourself

Write a **Triangle classifier**: given three side lengths, print whether the triangle is *equilateral* (all equal), *isosceles* (two equal) or *scalene* (all different).

```python-try stdin="5|5|8"
print("Three sides?")
a = int(input())
b = int(input())
c = int(input())
if a == b == c:
    print("Equilateral")
elif a == b or b == c or a == c:
    print("Isosceles")
else:
    print("Scalene")
```

**More challenges:**
1. Extend the classifier so it first checks that the sides can form a triangle at all (each side is less than the sum of the other two).
2. Write a "shipping cost" program where cost depends on weight ranges.
3. Write a simple calculator that reads two numbers and an operator (`+ - * /`) and prints the result, refusing to divide by zero.

## Recap

- Plan first: inputs, rules, outputs; then code.
- An `elif` chain from the strictest condition down keeps programs flat and readable.
- A list of "reasons to refuse" followed by `else` for success is a great pattern.
- Always test boundary values and unusual inputs.

**Congratulations!** Your programs can now think. In Module 3 you will make them **repeat** with loops.

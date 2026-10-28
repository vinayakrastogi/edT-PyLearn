---
id: 09-lab-first-programs
title: "Lab: Calculator, Temperature Converter and Interest"
order: 9
concepts: ["lab-practice", "input-processing-output"]
---

# Lab: Your First Real Programs

Time to put everything together! Almost every program follows the same three-step recipe, **Input → Process → Output**:

1. **Input:** get data from the user with `input()`.
2. **Process:** convert types and calculate with operators.
3. **Output:** show results with `print()` and f-strings.

In this lab you will build three classic programs. Each one is shown complete, and then you get to modify it.

## Program 1: Calculator

Ask for two numbers and show all the basic results.

```python stdin="17|5"
print("=== Simple Calculator ===")
print("First number?")
a = float(input())
print("Second number?")
b = float(input())

print(f"{a} + {b} = {a + b}")
print(f"{a} - {b} = {a - b}")
print(f"{a} * {b} = {a * b}")
print(f"{a} / {b} = {a / b:.2f}")
print(f"{a} // {b} = {a // b}")
print(f"{a} % {b} = {a % b}")
```

```output
=== Simple Calculator ===
First number?
Second number?
17.0 + 5.0 = 22.0
17.0 - 5.0 = 12.0
17.0 * 5.0 = 85.0
17.0 / 5.0 = 3.40
17.0 // 5.0 = 3.0
17.0 % 5.0 = 2.0
```

**What to notice:** we used `float()` so the calculator accepts decimals like `2.5`. The `:.2f` in the division line rounds the display to two decimals.

## Program 2: Temperature converter

Convert Celsius to Fahrenheit and Kelvin using the formulas

- `F = C × 9/5 + 32`
- `K = C + 273.15`

```python stdin="37"
print("Temperature in Celsius?")
celsius = float(input())

fahrenheit = celsius * 9 / 5 + 32
kelvin = celsius + 273.15

print(f"{celsius}C = {fahrenheit:.1f}F")
print(f"{celsius}C = {kelvin:.2f}K")
```

```output
Temperature in Celsius?
37.0C = 98.6F
37.0C = 310.15K
```

Body temperature: 37 °C is 98.6 °F. The formula works!

## Program 3: Simple interest calculator

If you deposit **P** rupees at **R**% per year for **T** years, the simple interest is

`I = P × R × T / 100`

and the final amount is `P + I`.

```python stdin="10000|5|3"
print("Principal (P)?")
principal = float(input())
print("Rate per year in % (R)?")
rate = float(input())
print("Time in years (T)?")
years = int(input())

interest = principal * rate * years / 100
total = principal + interest

print(f"Interest earned: {interest:,.2f}")
print(f"Total amount:    {total:,.2f}")
```

```output
Principal (P)?
Rate per year in % (R)?
Time in years (T)?
Interest earned: 1,500.00
Total amount:    11,500.00
```

## Bonus: tip splitter

Here is one you might use for real: split a restaurant bill with a tip.

```python stdin="1200|10|4"
print("Bill amount?")
bill = float(input())
print("Tip percentage?")
tip_percent = float(input())
print("Number of people?")
people = int(input())

tip = bill * tip_percent / 100
total = bill + tip
per_person = total / people

print(f"Tip: {tip:.2f}")
print(f"Total: {total:.2f}")
print(f"Each person pays: {per_person:.2f}")
```

```output
Bill amount?
Tip percentage?
Number of people?
Tip: 120.00
Total: 1320.00
Each person pays: 330.00
```

## Common Mistakes

**1. Integer versus float confusion.** `int()` rejects `"2.5"`. If users might type decimals, use `float()`.

**2. Forgetting to convert `input()`.** If a result looks like `"1020"` instead of `30`, you added text.

**3. Wrong formula order.** `celsius * 9 / 5 + 32` is right; `celsius * 9 / (5 + 32)` is not. Test with a known answer such as `100°C = 212°F`.

```python
celsius = 100
print(celsius * 9 / 5 + 32)
print(celsius * 9 / (5 + 32))
```

```output
212.0
24.324324324324323
```

**4. Not testing edge cases.** Try `0`, negative numbers and huge numbers.

## Try It Yourself

Write an **Area and perimeter** program for a rectangle: read the length and width, then print the area (`length × width`) and the perimeter (`2 × (length + width)`).

```python-try stdin="8|5"
print("Length?")
length = float(input())
print("Width?")
width = float(input())
print("Area:", length * width)
print("Perimeter:", 2 * (length + width))
```

**More challenges:**
1. Convert kilometres to miles (`miles = km * 0.621371`).
2. Read a name and a birth year and print the person's age this year.
3. Write a program that asks for hours and minutes and prints the total in minutes.

When you feel ready, head to the **Practice problems** and the **module quiz** to test yourself.

## Recap

- Programs follow **Input → Process → Output**.
- Convert `input()` with `int()` / `float()` before calculating.
- f-strings with `:.2f` and `:,` produce polished output.
- Always test with values whose answer you already know.

**Congratulations!** You now know enough Python to write useful programs. In Module 2 you will teach your programs to **make decisions**.

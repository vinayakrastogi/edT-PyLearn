---
id: 05-loop-recipes
title: "Loop Recipes: Sum, Count, Max and More"
order: 5
concepts: ["loop-recipes", "accumulator", "counters"]
---

# Loop Recipes: Sum, Count, Max and More

Cooks do not invent a new method for every dish. They know a handful of **recipes** and combine them. Programmers do the same. Almost every loop you will write is a variation on one of the patterns below. Learn them well and loops will stop feeling mysterious.

## Recipe 1: the accumulator (sum / product)

Start with a neutral value, then combine each item into it.

- For sums, start at `0` and use `+=`.
- For products, start at `1` and use `*=`.

```python
numbers = [4, 8, 15, 16, 23, 42]

total = 0
for n in numbers:
    total += n
print("Sum:", total)

product = 1
for n in [1, 2, 3, 4, 5]:
    product *= n
print("Product:", product)
```

```output
Sum: 108
Product: 120
```

## Recipe 2: the counter

Count how many items meet a condition.

```python
marks = [45, 82, 67, 91, 38, 75, 59]
passed = 0
for m in marks:
    if m >= 50:
        passed += 1
print(f"{passed} out of {len(marks)} passed")
```

```output
5 out of 7 passed
```

## Recipe 3: the average

Combine the accumulator with `len()`:

```python
marks = [45, 82, 67, 91, 38, 75, 59]
total = 0
for m in marks:
    total += m
average = total / len(marks)
print(f"Average: {average:.2f}")
```

```output
Average: 65.29
```

## Recipe 4: find the maximum (or minimum)

Assume the first item is the biggest, then challenge it with every other item.

```python
marks = [45, 82, 67, 91, 38, 75, 59]
highest = marks[0]
for m in marks:
    if m > highest:
        highest = m
print("Highest:", highest)

lowest = marks[0]
for m in marks:
    if m < lowest:
        lowest = m
print("Lowest:", lowest)
```

```output
Highest: 91
Lowest: 38
```

(Python also offers `max()` and `min()`, but knowing the recipe lets you solve variations such as "the *position* of the maximum".)

## Recipe 5: build a new collection

Start with an empty list and `append` items that pass a filter or a transformation.

```python
numbers = [1, 2, 3, 4, 5, 6, 7, 8]
evens = []
squares = []
for n in numbers:
    if n % 2 == 0:
        evens.append(n)
    squares.append(n * n)
print(evens)
print(squares)
```

```output
[2, 4, 6, 8]
[1, 4, 9, 16, 25, 36, 49, 64]
```

## Recipe 6: building a string

```python
word = "python"
reversed_word = ""
for letter in word:
    reversed_word = letter + reversed_word
print(reversed_word)

vowels = 0
for letter in "education":
    if letter in "aeiou":
        vowels += 1
print("Vowels:", vowels)
```

```output
nohtyp
Vowels: 5
```

## Recipe 7: flag (does *any* item match?)

Start with `False`; flip it to `True` if you find a match.

```python
numbers = [3, 7, 12, 19]
has_even = False
for n in numbers:
    if n % 2 == 0:
        has_even = True
        break
print("Contains an even number:", has_even)
```

```output
Contains an even number: True
```

## Recipe 8: the sentinel loop (repeat until "stop")

```python stdin="80|65|90|-1"
total = 0
count = 0
print("Enter marks, -1 to finish:")
mark = int(input())
while mark != -1:
    total += mark
    count += 1
    mark = int(input())
if count > 0:
    print("Average:", total / count)
else:
    print("No marks entered")
```

```output
Enter marks, -1 to finish:
Average: 78.33333333333333
```

Notice the `if count > 0` guard. Without it, an empty list would cause a division by zero.

## Recipe 9: frequency counting

Count how often each thing appears, using a dictionary (preview of Module 4).

```python
text = "banana"
counts = {}
for ch in text:
    if ch in counts:
        counts[ch] += 1
    else:
        counts[ch] = 1
print(counts)
```

```output
{'b': 1, 'a': 3, 'n': 2}
```

## Recipe 10: the running result (Fibonacci)

Keep a few variables and update them together.

```python
a, b = 0, 1
for _ in range(10):
    print(a, end=" ")
    a, b = b, a + b
print()
```

```output
0 1 1 2 3 5 8 13 21 34 
```

## Which recipe do I need?

| The problem says... | Recipe |
|---------------------|--------|
| "total", "sum of..." | accumulator (start 0) |
| "how many...", "count..." | counter |
| "average" | accumulator + `len` |
| "largest", "smallest" | max / min tracker |
| "all the ... that ..." | build a new list |
| "is there any ...?" | flag with `break` |
| "until the user types..." | sentinel loop |

## Common Mistakes

**1. Starting the accumulator in the wrong place.** Put `total = 0` **before** the loop; inside, it resets every time.

```python
for n in [1, 2, 3]:
    total = 0
    total += n
print(total)
```

```output
3
```

The answer should have been 6, but `total` was reset to 0 on every round.

**2. Starting a product at 0.** Anything times 0 is 0; start products at 1.

**3. Dividing by `len()` of an empty list.**

**4. Starting `highest = 0`.** This fails for lists of negative numbers. Start with the first item.

## Try It Yourself

For the list below compute the sum, the count of numbers above 10, and the largest number using loops only.

```python-try
values = [7, 14, 3, 22, 9, 18]
total = 0
above_ten = 0
largest = values[0]
for v in values:
    total += v
    if v > 10:
        above_ten += 1
    if v > largest:
        largest = v
print("Sum:", total)
print("Above 10:", above_ten)
print("Largest:", largest)
```

**Challenge:** Compute how many words in a sentence start with a capital letter (hint: `sentence.split()` and `word[0].isupper()`).

## Recap

- Accumulator: start at 0 (or 1) and combine each item.
- Counter: `count += 1` under an `if`.
- Max/min tracker: start from the first item, compare with the rest.
- Build lists and strings by starting empty and adding.
- Use a flag plus `break` for "does any item match?".
- Initialise *before* the loop, not inside it.

**Next up:** using nested loops to draw **star patterns**.

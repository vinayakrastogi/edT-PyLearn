---
id: 03-random-math-statistics
title: "random, math, statistics and secrets"
order: 3
concepts: ["random-module", "math-module", "statistics-module", "secrets-module"]
---

# random, math, statistics and secrets

The standard library is a giant toolbox. In this lesson we meet four modules you will use constantly: **random** for chance and games, **math** for scientific calculations, **statistics** for analysing data and **secrets** for *secure* random values such as passwords.

## `random`: controlled chaos

Computers cannot truly "roll dice", so they use an algorithm that produces numbers that *look* random (**pseudo-random**). Starting the algorithm from the same **seed** gives the same sequence every time, which is perfect for repeatable tests.

```python
import random

random.seed(7)
first = [random.randint(1, 100) for _ in range(5)]
random.seed(7)
second = [random.randint(1, 100) for _ in range(5)]
print(first == second)
print(all(1 <= n <= 100 for n in first))
```

```output
True
True
```

### The everyday functions

| Function | Returns |
|----------|---------|
| `random.random()` | float from 0.0 up to (not including) 1.0 |
| `random.uniform(a, b)` | float between `a` and `b` |
| `random.randint(a, b)` | integer from `a` to `b`, **both included** |
| `random.randrange(start, stop, step)` | like `range`, chosen at random |
| `random.choice(seq)` | one random item |
| `random.choices(seq, k=n)` | `n` items, **with** repeats |
| `random.sample(seq, n)` | `n` **unique** items |
| `random.shuffle(list)` | shuffles the list **in place** |

```python
import random

random.seed(1)
print(0 <= random.random() < 1)
print(2.5 <= random.uniform(2.5, 3.5) <= 3.5)
print(random.randrange(0, 100, 10) % 10 == 0)
print(random.choice("abc") in "abc")
print(len(random.choices([1, 2, 3], k=10)))
print(len(set(random.sample(range(100), 10))))

deck = list(range(1, 6))
random.shuffle(deck)
print(sorted(deck))
```

```output
True
True
True
True
10
10
[1, 2, 3, 4, 5]
```

### Weighted choices

```python
import random

random.seed(3)
picks = random.choices(["common", "rare"], weights=[90, 10], k=1000)
print(picks.count("common") > picks.count("rare"))
```

```output
True
```

### Simulating dice

```python
import random

random.seed(10)
rolls = [random.randint(1, 6) + random.randint(1, 6) for _ in range(6000)]
counts = {}
for r in rolls:
    counts[r] = counts.get(r, 0) + 1
most_common = max(counts, key=counts.get)
print(most_common)
print(min(rolls), max(rolls))
```

```output
7
2 12
```

Seven is the most common total of two dice, because there are more ways to make it (1+6, 2+5, 3+4...). With a large number of rolls the simulation shows the theory.

## `math`: beyond arithmetic

```python
import math

print(math.sqrt(144), math.isqrt(50))
print(math.ceil(4.1), math.floor(4.9), math.trunc(-4.9))
print(round(math.pi, 4), round(math.e, 4))
print(math.factorial(6), math.comb(5, 2), math.perm(5, 2))
print(math.gcd(48, 18), math.lcm(4, 6))
print(round(math.log(100, 10), 2), round(math.log2(8), 2))
print(round(math.degrees(math.pi), 1), round(math.radians(180), 4))
print(math.isclose(0.1 + 0.2, 0.3))
print(math.inf > 10 ** 100, math.isnan(float("nan")))
```

```output
12.0 7
5 4 -4
3.1416 2.7183
720 10 20
6 12
2.0 3.0
180.0 3.1416
True
True True
```

- `comb(n, k)` = combinations ("n choose k"), `perm(n, k)` = permutations.
- `isclose` compares floats with a tolerance.

### Trigonometry and geometry

```python
import math

angle = math.radians(30)
print(round(math.sin(angle), 3), round(math.cos(angle), 3), round(math.tan(angle), 3))
print(math.hypot(6, 8))
print(round(math.dist((0, 0), (3, 4)), 1))
radius = 5
print(round(math.pi * radius ** 2, 2))
```

```output
0.5 0.866 0.577
10.0
5.0
78.54
```

Trig functions work in **radians**; convert degrees with `math.radians`.

## `statistics`: understanding data

```python
import statistics as st

marks = [72, 85, 90, 65, 85, 78, 92, 85]
print(st.mean(marks))
print(st.median(marks))
print(st.mode(marks))
print(round(st.stdev(marks), 2))
print(round(st.variance(marks), 2))
print(min(marks), max(marks), max(marks) - min(marks))
```

```output
81.5
85.0
85
9.21
84.86
65 92 27
```

| Function | Meaning |
|----------|---------|
| `mean` | the average |
| `median` | the middle value when sorted |
| `mode` | the most frequent value |
| `stdev` | how spread out the data is (sample standard deviation) |
| `variance` | the square of the standard deviation |

Why both mean and median? One extreme value changes the mean a lot but the median barely:

```python
import statistics as st

salaries = [30, 32, 35, 36, 38, 400]
print(round(st.mean(salaries), 1))
print(st.median(salaries))
```

```output
95.2
35.5
```

The median (35.5) describes the "typical" salary far better than the mean (95.2).

## `secrets`: randomness you can trust

`random` is predictable if someone learns its seed, so **never** use it for passwords, tokens or anything security-related. The `secrets` module draws from the operating system's secure source.

```python
import secrets
import string

alphabet = string.ascii_letters + string.digits
password = "".join(secrets.choice(alphabet) for _ in range(12))
print(len(password))
print(all(c in alphabet for c in password))
print(len(secrets.token_hex(8)))
print(len(secrets.token_urlsafe(16)) >= 16)
print(0 <= secrets.randbelow(10) < 10)
```

```output
12
True
16
True
True
```

The `string` module provides handy character sets:

```python
import string

print(string.ascii_lowercase)
print(string.ascii_uppercase[:5])
print(string.digits)
print(string.punctuation[:8])
```

```output
abcdefghijklmnopqrstuvwxyz
ABCDE
0123456789
!"#$%&'(
```

## Putting it together: a lucky-draw program

```python
import random

def draw_winners(entries, count, seed=None):
    rng = random.Random(seed)
    return sorted(rng.sample(entries, count))

names = ["Asha", "Ravi", "Meera", "Pip", "Zoya", "Kabir"]
winners = draw_winners(names, 3, seed=5)
print(len(winners), all(w in names for w in winners))
print(winners == draw_winners(names, 3, seed=5))
```

```output
3 True
True
```

`random.Random(seed)` creates a private generator, so your program's randomness does not interfere with other code.

## Common Mistakes

**1. `random.randint(1, 6)` versus `random.randrange(1, 6)`.** `randint` includes 6; `randrange(1, 6)` stops at 5.

**2. Using `random` for passwords.** Use `secrets`.

**3. Forgetting that `shuffle` works in place and returns `None`.**

```python
import random

cards = [1, 2, 3]
result = random.shuffle(cards)
print(result)
```

```output
None
```

**4. `statistics.mode` on empty data, or `stdev` with one value** raises `StatisticsError`.

```python expect-error
import statistics
statistics.stdev([5])
```

```output
statistics.StatisticsError: stdev requires at least two data points
```

## Try It Yourself

Simulate 1000 coin flips (with a seed), count the heads, and compute the mean and median of a list of test scores.

```python-try
import random
import statistics as st

random.seed(2024)
flips = random.choices(["H", "T"], k=1000)
heads = flips.count("H")
print("Heads between 400 and 600:", 400 <= heads <= 600)

scores = [55, 70, 70, 82, 91, 64]
print("Mean:", round(st.mean(scores), 2))
print("Median:", st.median(scores))
print("Mode:", st.mode(scores))
```

**Challenge:** Write `roll_dice(n)` that returns a list of `n` dice rolls, and compute how often each face appears.

## Recap

- `random` gives pseudo-random values; `seed()` makes them repeatable; `sample` picks unique items and `choices` allows repeats.
- `math` supplies `sqrt`, `ceil`, `floor`, `factorial`, `gcd`, `log`, trigonometry (radians!), `isclose`.
- `statistics` offers `mean`, `median`, `mode`, `stdev`; the median resists outliers.
- Use `secrets` (never `random`) for passwords and tokens.
- Private generators via `random.Random(seed)` keep code independent.

**Next up:** **JSON and web APIs** with `requests`.

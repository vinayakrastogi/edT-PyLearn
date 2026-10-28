---
id: 02-datetime
title: "Dates and Times with datetime"
order: 2
concepts: ["datetime-module", "timedelta", "date-formatting"]
---

# Dates and Times with datetime

Ages, deadlines, timestamps in log files, "how many days until my birthday?": dates are everywhere, and doing arithmetic on them by hand is a nightmare (months have different lengths, leap years, time zones...). Python's **`datetime`** module handles all of that.

## The main classes

| Class | Holds | Example |
|-------|-------|---------|
| `date` | year, month, day | `2025-03-14` |
| `time` | hour, minute, second | `09:30:00` |
| `datetime` | both together | `2025-03-14 09:30:00` |
| `timedelta` | a *duration* | `5 days, 3:00:00` |

## Creating dates

```python
from datetime import date, datetime

d = date(2025, 3, 14)
print(d)
print(d.year, d.month, d.day)
dt = datetime(2025, 3, 14, 9, 30, 15)
print(dt)
print(dt.hour, dt.minute, dt.second)
print(d.weekday())
print(d.strftime("%A"))
```

```output
2025-03-14
2025 3 14
2025-03-14 09:30:15
9 30 15
4
Friday
```

`weekday()` gives Monday as 0 up to Sunday as 6, so 4 is Friday.

## The current date and time

```python
from datetime import date, datetime

today = date.today()
now = datetime.now()
print(type(today).__name__, type(now).__name__)
print(today.year >= 2024)
print(0 <= now.hour <= 23)
```

```output
date datetime
True
True
```

(Exact values depend on when you run it, so we print only checks here. On your own machine, `print(datetime.now())` shows the actual moment.)

## Formatting dates: `strftime`

`strftime` (*string from time*) turns a date into text using **format codes**.

| Code | Meaning | Example |
|:----:|---------|---------|
| `%Y` | 4-digit year | `2025` |
| `%y` | 2-digit year | `25` |
| `%m` | month number | `03` |
| `%B` | month name | `March` |
| `%b` | short month | `Mar` |
| `%d` | day of month | `14` |
| `%A` | weekday name | `Friday` |
| `%a` | short weekday | `Fri` |
| `%H` | hour (24h) | `09` |
| `%I` `%p` | hour (12h) and AM/PM | `09 AM` |
| `%M` | minute | `30` |
| `%S` | second | `15` |

```python
from datetime import datetime

dt = datetime(2025, 3, 14, 15, 5, 9)
print(dt.strftime("%d/%m/%Y"))
print(dt.strftime("%B %d, %Y"))
print(dt.strftime("%A, %d %b %Y"))
print(dt.strftime("%H:%M:%S"))
print(dt.strftime("%I:%M %p"))
print(dt.isoformat())
```

```output
14/03/2025
March 14, 2025
Friday, 14 Mar 2025
15:05:09
03:05 PM
2025-03-14T15:05:09
```

## Parsing text into dates: `strptime`

`strptime` (*string parse time*) does the reverse: it reads text and builds a `datetime`. You describe the layout with the same codes.

```python
from datetime import datetime

d = datetime.strptime("14/03/2025", "%d/%m/%Y")
print(d)
print(d.year, d.strftime("%A"))
d2 = datetime.strptime("March 5, 2024 4:45 PM", "%B %d, %Y %I:%M %p")
print(d2)
```

```output
2025-03-14 00:00:00
2025 Friday
2024-03-05 16:45:00
```

If the text does not match the format, you get a `ValueError`:

```python expect-error
from datetime import datetime
datetime.strptime("2025-13-40", "%Y-%m-%d")
```

```output
ValueError: time data '2025-13-40' does not match format '%Y-%m-%d'
```

## Date arithmetic with `timedelta`

Subtracting two dates gives a `timedelta`; adding a `timedelta` to a date moves it forward or back.

```python
from datetime import date, timedelta

start = date(2025, 1, 1)
end = date(2025, 12, 25)
gap = end - start
print(gap)
print(gap.days)

print(start + timedelta(days=45))
print(start - timedelta(days=1))
print(start + timedelta(weeks=2))
```

```output
358 days, 0:00:00
358
2025-02-15
2024-12-31
2025-01-15
```

`timedelta` accepts `days`, `seconds`, `minutes`, `hours` and `weeks`.

```python
from datetime import datetime, timedelta

meeting = datetime(2025, 6, 10, 14, 0)
print(meeting + timedelta(hours=2, minutes=30))
print((datetime(2025, 6, 10, 18, 0) - meeting).seconds // 3600)
print(timedelta(days=1, hours=12).total_seconds())
```

```output
2025-06-10 16:30:00
4
129600.0
```

## Comparing dates

Dates compare with the usual operators.

```python
from datetime import date

a = date(2025, 5, 1)
b = date(2025, 8, 15)
print(a < b)
print(max(a, b))
print(a == date(2025, 5, 1))
deadlines = [date(2025, 9, 1), date(2025, 7, 4), date(2025, 8, 20)]
print(sorted(deadlines)[0])
```

```output
True
2025-08-15
True
2025-07-04
```

## Calculating age

```python
from datetime import date

def age(born, today):
    years = today.year - born.year
    if (today.month, today.day) < (born.month, born.day):
        years -= 1
    return years

print(age(date(2010, 6, 15), date(2025, 6, 14)))
print(age(date(2010, 6, 15), date(2025, 6, 15)))
```

```output
14
15
```

The trick: subtract one if this year's birthday has not happened yet. Comparing the `(month, day)` tuples does that neatly.

## Days until a date

```python
from datetime import date

def days_until(target, today):
    return (target - today).days

today = date(2025, 3, 10)
print(days_until(date(2025, 12, 25), today))
print(days_until(date(2025, 3, 1), today))
```

```output
290
-9
```

A negative answer means the date has already passed.

## Time zones (a brief look)

Basic `datetime` objects are *naive*: they have no time zone. For real applications with users in different places, attach a zone:

```python
from datetime import datetime, timezone, timedelta

utc = datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc)
ist = timezone(timedelta(hours=5, minutes=30))
print(utc)
print(utc.astimezone(ist))
```

```output
2025-01-01 12:00:00+00:00
2025-01-01 17:30:00+05:30
```

## Measuring time with `time`

The `time` module is handy for pauses and stopwatches:

```python
import time

start = time.time()
time.sleep(0.2)
elapsed = time.time() - start
print(0.15 < elapsed < 1.0)
```

```output
True
```

`time.sleep(seconds)` pauses the program; it is the heart of clocks, reminders and polling loops.

## Common Mistakes

**1. Mixing `date` and `datetime`.**

```python expect-error
from datetime import date, datetime
print(datetime(2025, 1, 1) - date(2025, 1, 1))
```

```output
TypeError: unsupported operand type(s) for -: 'datetime.datetime' and 'datetime.date'
```

**2. Wrong format codes in `strptime`.** `%m` is month, `%M` is minute!

**3. Forgetting that `.days` ignores the seconds part** of a `timedelta`. Use `.total_seconds()` for exact durations.

**4. Ignoring time zones** in programs used across regions.

## Try It Yourself

Compute how many days remain until a fixed target date, and print the weekday it falls on.

```python-try
from datetime import date, timedelta

today = date(2025, 4, 20)
exam = date(2025, 5, 12)
print("Days left:", (exam - today).days)
print("Exam day:", exam.strftime("%A, %d %B %Y"))
print("Two weeks before:", exam - timedelta(weeks=2))
```

**Challenge:** Write a function that returns the weekday name for any date given as `"DD/MM/YYYY"`.

## Recap

- `date`, `time`, `datetime` hold points in time; `timedelta` holds durations.
- `strftime` formats a date as text; `strptime` parses text into a date.
- Subtract dates to get a `timedelta`; add a `timedelta` to shift a date.
- Compare dates with `<`, `>`, `==`; `weekday()` gives Monday = 0.
- Use time zones for global apps and `time.sleep` for pauses.

**Next up:** **random, math and statistics** for simulations and analysis.

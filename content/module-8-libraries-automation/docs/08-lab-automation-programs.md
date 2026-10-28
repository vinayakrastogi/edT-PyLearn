---
id: 08-lab-automation-programs
title: "Lab: Digital Clock, Password Generator and Weather Report"
order: 8
concepts: ["lab-practice", "library-programs"]
---

# Lab: Libraries at Work

Three small programs, each built by combining a library from this module with the Python you already know. As always: read the requirements, sketch your own solution, then compare.

## Program 1: digital clock

**Requirements:** show the current time updating every second, in 12-hour format with AM/PM, plus the date.

### Step 1: the formatting function (testable!)

Separate *what to show* from *how to show it*. The function below takes a `datetime`, so we can test it with fixed values:

```python
from datetime import datetime

def clock_text(moment):
    return moment.strftime("%I:%M:%S %p"), moment.strftime("%A, %d %B %Y")

time_part, date_part = clock_text(datetime(2025, 3, 14, 16, 5, 9))
print(time_part)
print(date_part)
time_part, date_part = clock_text(datetime(2025, 12, 31, 0, 0, 0))
print(time_part, "|", date_part)
```

```output
04:05:09 PM
Friday, 14 March 2025
12:00:00 AM | Wednesday, 31 December 2025
```

### Step 2: a console clock

Pass the "display" action in as a function, so the same clock can print, log or (later) update a window:

```python
import time
from datetime import datetime

def clock_text(moment):
    return moment.strftime("%I:%M:%S %p"), moment.strftime("%A, %d %B %Y")

def run_clock(seconds, show):
    for _ in range(seconds):
        t, d = clock_text(datetime.now())
        show(f"{d} - {t}")
        time.sleep(1)

lines = []
start = time.time()
run_clock(2, lines.append)
print(len(lines), "ticks")
print(all(":" in line for line in lines))
print("ran for about", round(time.time() - start), "seconds")
```

```output
2 ticks
True
ran for about 2 seconds
```

On your own computer, use `run_clock(10, print)` to watch it tick.

### Step 3: the GUI clock (run on your computer)

```python no-run
import tkinter as tk
from datetime import datetime

def clock_text(moment):
    return moment.strftime("%I:%M:%S %p"), moment.strftime("%A, %d %B %Y")

def tick():
    t, d = clock_text(datetime.now())
    time_label.config(text=t)
    date_label.config(text=d)
    root.after(1000, tick)

root = tk.Tk()
root.title("Digital Clock")
root.configure(bg="black")
time_label = tk.Label(root, font=("Courier", 48, "bold"), fg="lime", bg="black")
time_label.pack(padx=30, pady=(20, 0))
date_label = tk.Label(root, font=("Arial", 16), fg="white", bg="black")
date_label.pack(pady=(0, 20))
tick()
root.mainloop()
```

The same `clock_text` function is used by both the console and GUI versions. That is the benefit of separating logic from display.

## Program 2: random password generator

**Requirements**
- Choose a length (at least 8).
- Guarantee at least one lower-case letter, upper-case letter, digit and symbol.
- Use a *secure* random source.

```python
import secrets
import string

def generate_password(length=12):
    if length < 8:
        raise ValueError("password must be at least 8 characters")
    groups = [string.ascii_lowercase, string.ascii_uppercase, string.digits, "!@#$%&*?"]
    chars = [secrets.choice(g) for g in groups]           # one from each group
    everything = "".join(groups)
    chars += [secrets.choice(everything) for _ in range(length - len(chars))]
    secrets.SystemRandom().shuffle(chars)
    return "".join(chars)

def strength(password):
    score = sum([
        len(password) >= 12,
        any(c.islower() for c in password),
        any(c.isupper() for c in password),
        any(c.isdigit() for c in password),
        any(c in "!@#$%&*?" for c in password),
    ])
    return ["very weak", "weak", "fair", "good", "strong", "excellent"][score]

pw = generate_password(14)
print(len(pw))
print(any(c.islower() for c in pw), any(c.isupper() for c in pw))
print(any(c.isdigit() for c in pw), any(c in "!@#$%&*?" for c in pw))
print(strength(pw))
print(strength("abc"))
print(generate_password() != generate_password())
try:
    generate_password(4)
except ValueError as e:
    print("Error:", e)
```

```output
14
True True
True True
excellent
weak
True
Error: password must be at least 8 characters
```

We print *properties* of the password rather than the password itself, because it is different each run.

**Why this design?**
- Guaranteeing one character from each group avoids the (unlikely) case of a password with no digit.
- `secrets` instead of `random` makes the password unpredictable.
- Shuffling afterwards stops the first four characters always being lower, upper, digit, symbol.

## Program 3: weather information using an API

**Requirements:** ask a weather API for a city and print a friendly summary; handle errors.

The network part is small; the *parsing and formatting* is where the logic lives, so we write and test that first with sample data.

```python
import json

SAMPLE_RESPONSE = json.dumps({
    "name": "Bengaluru",
    "sys": {"country": "IN"},
    "main": {"temp": 297.65, "feels_like": 298.1, "humidity": 71},
    "weather": [{"main": "Clouds", "description": "scattered clouds"}],
    "wind": {"speed": 3.6},
})

def kelvin_to_celsius(k):
    return round(k - 273.15, 1)

def describe(payload):
    data = json.loads(payload)
    if "main" not in data:
        return f"No weather data ({data.get('message', 'unknown error')})"
    temp = kelvin_to_celsius(data["main"]["temp"])
    feels = kelvin_to_celsius(data["main"]["feels_like"])
    desc = data["weather"][0]["description"].capitalize()
    wind_kmh = round(data["wind"]["speed"] * 3.6, 1)
    advice = "Carry a jacket." if temp < 18 else "Stay hydrated." if temp > 30 else "Enjoy the day!"
    return (f"{data['name']}, {data['sys']['country']}: {desc}\n"
            f"Temperature: {temp} C (feels like {feels} C)\n"
            f"Humidity: {data['main']['humidity']}%   Wind: {wind_kmh} km/h\n"
            f"{advice}")

print(describe(SAMPLE_RESPONSE))
print(describe('{"cod": "404", "message": "city not found"}'))
```

```output
Bengaluru, IN: Scattered clouds
Temperature: 24.5 C (feels like 25.0 C)
Humidity: 71%   Wind: 13.0 km/h
Enjoy the day!
No weather data (city not found)
```

Now the small networking wrapper (run it on your own computer with an API key from a service such as OpenWeatherMap):

```python no-run
import os
import requests

def fetch_weather(city):
    key = os.environ["WEATHER_API_KEY"]
    url = "https://api.openweathermap.org/data/2.5/weather"
    try:
        response = requests.get(url, params={"q": city, "appid": key}, timeout=10)
    except requests.exceptions.RequestException as e:
        return json.dumps({"message": f"network problem: {type(e).__name__}"})
    return response.text

city = input("City: ")
print(describe(fetch_weather(city)))
```

Because `describe` was tested on sample data first, any bug now is in the networking, not the parsing.

## Reflection: what patterns did we use?

| Pattern | Seen in |
|---------|---------|
| Separate logic from display | clock, weather |
| Test with fixed inputs before real ones | clock, weather |
| Use the right library | `datetime`, `secrets`, `json` + `requests` |
| Validate input | password length |
| Handle failure gracefully | weather errors |

## Common Mistakes

**1. Blocking a GUI with `time.sleep`.** Use `after()`.

**2. Using `random` for passwords.** Use `secrets`.

**3. Forgetting unit conversions** (Kelvin, metres per second).

**4. Trusting an API response blindly.** Check for error fields before indexing.

```python expect-error
import json
data = json.loads('{"cod": "404", "message": "city not found"}')
print(data["main"]["temp"])
```

```output
KeyError: 'main'
```

## Try It Yourself

Write a `format_duration(seconds)` helper that returns text like `1h 02m 05s`, useful for a stopwatch or a countdown clock.

```python-try
def format_duration(seconds):
    hours, rest = divmod(seconds, 3600)
    minutes, secs = divmod(rest, 60)
    if hours:
        return f"{hours}h {minutes:02d}m {secs:02d}s"
    return f"{minutes}m {secs:02d}s"

print(format_duration(3725))
print(format_duration(59))
print(format_duration(600))
```

**More challenges:**
1. Add a countdown mode to the console clock that counts from 10 to 0.
2. Make the password generator accept a "no ambiguous characters" option that excludes `0`, `O`, `l` and `1`.
3. Extend `describe` to show the wind direction from degrees.

## Recap

- Split programs into **logic** (pure, testable functions) and **plumbing** (GUI, network, files).
- Use `datetime.strftime` for clocks, `secrets` for security-sensitive randomness, `json` + `requests` for APIs.
- Validate input and handle API errors before indexing into the response.
- Print properties (not random values) when testing randomised code.

**Congratulations!** You can now automate tasks and talk to the outside world. In Module 9 you will analyse and visualise **data** with NumPy, Pandas and Matplotlib.

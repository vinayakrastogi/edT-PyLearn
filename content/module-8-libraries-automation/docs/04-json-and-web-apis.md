---
id: 04-json-and-web-apis
title: "JSON and Web APIs with requests"
order: 4
concepts: ["json-basics", "requests-library", "api-errors"]
---

# JSON and Web APIs with requests

When you open a weather app, it does not measure the temperature itself. It **asks a server on the internet**, which replies with data. That conversation happens through a **web API** (Application Programming Interface), and the data almost always arrives in **JSON** format. In this lesson you will learn to read that data in Python and to talk to APIs with the `requests` library.

> **Sandbox note:** the practice editor cannot reach the internet, so the live `requests` examples below are marked "not runnable here". Copy them into a file on your own computer (after `pip install requests`) to see them work. Everything about *parsing* JSON runs right here.

## JSON in five minutes

JSON is text that looks just like Python dictionaries and lists.

```python
import json

text = '{"city": "Delhi", "temp": 31.5, "humid": true, "tags": ["hot", "dry"], "rain": null}'
data = json.loads(text)
print(type(data).__name__)
print(data["city"], data["temp"])
print(data["humid"], data["rain"])
print(data["tags"][0])
print(len(data))
```

```output
dict
Delhi 31.5
True None
hot
5
```

The JSON `true`/`null` became Python `True`/`None`. The reverse trip:

```python
import json

report = {"city": "Mumbai", "temp": 29, "forecast": ["sunny", "cloudy"]}
text = json.dumps(report, indent=2)
print(text)
print(json.loads(text) == report)
```

```output
{
  "city": "Mumbai",
  "temp": 29,
  "forecast": [
    "sunny",
    "cloudy"
  ]
}
True
```

## Digging into nested JSON

Real API responses are nested. Walk through them one key at a time.

```python
import json

response = """
{
  "location": {"name": "Chennai", "country": "India"},
  "current": {"temp_c": 33.2, "condition": {"text": "Partly cloudy", "code": 1003}},
  "forecast": [
    {"day": "Mon", "max": 35, "min": 27},
    {"day": "Tue", "max": 34, "min": 26},
    {"day": "Wed", "max": 31, "min": 25}
  ]
}
"""
data = json.loads(response)
print(data["location"]["name"])
print(data["current"]["condition"]["text"])
for day in data["forecast"]:
    print(f"{day['day']}: {day['min']} to {day['max']}")
hottest = max(data["forecast"], key=lambda d: d["max"])
print("Hottest:", hottest["day"])
print(sum(d["max"] for d in data["forecast"]) / len(data["forecast"]))
```

```output
Chennai
Partly cloudy
Mon: 27 to 35
Tue: 26 to 34
Wed: 25 to 31
Hottest: Mon
33.333333333333336
```

### Missing keys: `get` and defaults

APIs sometimes leave fields out. Use `.get()` so your program does not crash.

```python
data = {"name": "Asha", "address": {"city": "Pune"}}
print(data.get("age", "unknown"))
print(data.get("address", {}).get("city"))
print(data.get("phone", {}).get("home", "none"))
```

```output
unknown
Pune
none
```

## What is an API request?

A request has:

- a **URL** (where to ask),
- a **method** (`GET` = fetch data, `POST` = send data),
- optional **parameters** (extra details like `?city=Delhi`),
- optional **headers** (such as an API key).

The server replies with a **status code** and a **body**.

| Status | Meaning |
|:------:|---------|
| `200` | OK: here is your data |
| `201` | Created |
| `400` | Bad request: you sent something wrong |
| `401` / `403` | Not authorised / forbidden (check your API key) |
| `404` | Not found |
| `429` | Too many requests: slow down |
| `500` | The server had a problem |

## `requests`: the friendly HTTP library

Install it once with `pip install requests`, then:

```python no-run
import requests

response = requests.get("https://api.github.com/users/octocat", timeout=10)
print(response.status_code)          # 200
data = response.json()               # parsed JSON -> dict
print(data["login"], data["public_repos"])
```

```text
200
octocat 8
```

Always pass `timeout=` (in seconds); without it a stuck server can freeze your program forever.

### Query parameters

Let `requests` build the `?key=value` part for you (it also handles special characters):

```python no-run
import requests

params = {"q": "python tutorials", "page": 2}
response = requests.get("https://example.com/search", params=params, timeout=10)
print(response.url)   # https://example.com/search?q=python+tutorials&page=2
```

### Headers and API keys

```python no-run
import os
import requests

api_key = os.environ.get("WEATHER_API_KEY")
response = requests.get(
    "https://api.example.com/weather",
    params={"city": "Delhi"},
    headers={"Authorization": f"Bearer {api_key}"},
    timeout=10,
)
```

Read keys from environment variables (from the last lessons), never hard-code them or commit them to source control.

### Sending data: POST

```python no-run
import requests

payload = {"name": "Asha", "score": 92}
response = requests.post("https://example.com/api/scores", json=payload, timeout=10)
print(response.status_code)
print(response.json())
```

## Handling errors properly

Networks fail. Write defensive code:

```python no-run
import requests

def get_json(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()        # raises for 4xx / 5xx
        return response.json()
    except requests.exceptions.Timeout:
        print("The server took too long")
    except requests.exceptions.HTTPError as e:
        print("Server said no:", e)
    except requests.exceptions.ConnectionError:
        print("Could not connect; check your internet")
    except ValueError:
        print("Response was not valid JSON")
    return None
```

`raise_for_status()` turns an error status code into an exception, so you can handle it with `try/except`.

## Testing your parsing without the network

Good practice: put the parsing in its own function and test it with sample JSON. Then you know it works before you ever touch the internet.

```python
import json

SAMPLE = '{"main": {"temp": 301.15, "humidity": 62}, "weather": [{"description": "haze"}], "name": "Delhi"}'

def summarise_weather(payload):
    data = json.loads(payload) if isinstance(payload, str) else payload
    celsius = data["main"]["temp"] - 273.15
    return {
        "city": data["name"],
        "temp_c": round(celsius, 1),
        "humidity": data["main"]["humidity"],
        "description": data["weather"][0]["description"],
    }

print(summarise_weather(SAMPLE))
```

```output
{'city': 'Delhi', 'temp_c': 28.0, 'humidity': 62, 'description': 'haze'}
```

The temperature here arrives in Kelvin, so the function converts it. That is a typical API quirk: always read the documentation for units.

## Rate limits and being polite

- Respect the API's **rate limit**; use `time.sleep()` between requests in loops.
- **Cache** results you have already fetched.
- Send a descriptive `User-Agent` when asked.
- Read the **terms of use**, especially for scraping websites.

## Common Mistakes

**1. No timeout.** Your script may hang forever.

**2. Not checking the status code** and trying to parse an error page as JSON.

**3. Hard-coding API keys** in code you share.

**4. Assuming the JSON structure never changes.** Use `.get()` and validate.

```python expect-error
import json
json.loads("{'single': 'quotes'}")
```

```output
json.decoder.JSONDecodeError: Expecting property name enclosed in double quotes: line 1 column 2 (char 1)
```

JSON requires double quotes; Python-style single quotes are invalid.

## Try It Yourself

Parse this JSON and print each student's name with their average mark, sorted highest first.

```python-try
import json

text = '''
[
  {"name": "Asha", "marks": [90, 85, 95]},
  {"name": "Ravi", "marks": [70, 65, 80]},
  {"name": "Pip", "marks": [88, 92, 79]}
]
'''
students = json.loads(text)
ranked = sorted(students, key=lambda s: sum(s["marks"]) / len(s["marks"]), reverse=True)
for s in ranked:
    print(f"{s['name']:<6} {sum(s['marks']) / len(s['marks']):.1f}")
```

**Challenge:** Write a function that takes the nested weather JSON above and returns the day with the biggest temperature range.

## Recap

- JSON is text that maps to dicts, lists, strings, numbers, booleans and `None`; `json.loads`/`dumps` convert between text and Python.
- Navigate nested data with chained keys and use `.get()` for optional fields.
- `requests.get(url, params=..., headers=..., timeout=...)` fetches data; `.json()` parses it; `raise_for_status()` turns bad statuses into exceptions.
- Handle timeouts, connection errors and invalid JSON; keep secrets in environment variables.
- Write parsing code as separate functions so you can test it with sample data.

**Next up:** building a window with **tkinter**.

---
id: 02-string-methods
title: "String Methods"
order: 2
concepts: ["string-methods-toolkit", "split-join", "searching-text"]
---

# String Methods

A **method** is a function attached to a value. Strings come with about 40 of them, like a Swiss Army knife for text. This lesson groups the most useful into families. Remember: strings are immutable, so every method **returns a new string** and the original stays the same.

## Changing case

```python
text = "hELLo pYtHoN wOrLd"
print(text.upper())
print(text.lower())
print(text.title())
print(text.capitalize())
print(text.swapcase())
```

```output
HELLO PYTHON WORLD
hello python world
Hello Python World
Hello python world
HellO PyThOn WoRlD
```

`.lower()` is the tool for case-insensitive comparisons: `answer.lower() == "yes"`.

## Trimming whitespace

```python
messy = "   hello   "
print(f"[{messy.strip()}]")
print(f"[{messy.lstrip()}]")
print(f"[{messy.rstrip()}]")
print("xxhixx".strip("x"))
```

```output
[hello]
[hello   ]
[   hello]
hi
```

Always `.strip()` user input before comparing it.

## Searching

| Method | Returns |
|--------|---------|
| `.find(sub)` | index of first match, `-1` if missing |
| `.rfind(sub)` | index of last match |
| `.index(sub)` | like `find`, but raises `ValueError` if missing |
| `.count(sub)` | number of non-overlapping matches |
| `.startswith(x)` / `.endswith(x)` | `True`/`False` |

```python
s = "the cat sat on the mat"
print(s.find("cat"))
print(s.find("dog"))
print(s.rfind("the"))
print(s.count("at"))
print(s.startswith("the"), s.endswith("mat"))
```

```output
4
-1
15
3
True True
```

## Replacing

```python
s = "I like cats. Cats are great."
print(s.replace("cats", "dogs"))
print(s.replace("Cats", "Dogs"))
print("banana".replace("a", "o", 2))
```

```output
I like dogs. Cats are great.
I like cats. Dogs are great.
bonona
```

Replacement is case-sensitive; the third argument limits how many replacements are made.

## Splitting and joining

`split()` breaks a string into a **list**; `join()` glues a list back into a string. They are opposites.

```python
sentence = "the quick brown fox"
words = sentence.split()
print(words)
print(len(words))
print("-".join(words))
print("a,b,,c".split(","))
print("2025-01-15".split("-"))
print("one  two   three".split())
```

```output
['the', 'quick', 'brown', 'fox']
4
the-quick-brown-fox
['a', 'b', '', 'c']
['2025', '01', '15']
['one', 'two', 'three']
```

With no argument `split()` splits on any run of whitespace and ignores extras. With a separator, every occurrence counts, which is why `"a,b,,c"` produced an empty string.

```python
print("a=1;b=2".split(";"))
print("line1\nline2\nline3".splitlines())
print("k=v=w".split("=", 1))
```

```output
['a=1', 'b=2']
['line1', 'line2', 'line3']
['k', 'v=w']
```

## Testing what a string contains

These return `True` or `False` and are perfect for validation:

| Method | True when... |
|--------|--------------|
| `.isdigit()` | all characters are digits (and at least one) |
| `.isalpha()` | all letters |
| `.isalnum()` | all letters or digits |
| `.isspace()` | all whitespace |
| `.isupper()` / `.islower()` | all cased letters are upper / lower |

```python
print("12345".isdigit(), "12.5".isdigit(), "".isdigit())
print("Hello".isalpha(), "Hello1".isalpha())
print("abc123".isalnum(), "a b".isalnum())
print("ABC".isupper(), "Abc".isupper())
```

```output
True False False
True False
True False
True False
```

Note that `"12.5".isdigit()` is `False` because of the dot, and `"-5".isdigit()` is `False` because of the minus sign.

## Aligning and padding

```python
print("7".zfill(3))
print("cat".ljust(6) + "|")
print("cat".rjust(6) + "|")
print("cat".center(7, "*"))
```

```output
007
cat   |
   cat|
**cat**
```

## Chaining methods

Since each method returns a string, you can chain them:

```python
raw = "  ALICE Smith  "
print(raw.strip().lower().title())
print("  a-b-c  ".strip().replace("-", "").upper())
```

```output
Alice Smith
ABC
```

## Method summary by task

| I want to... | Use |
|--------------|-----|
| ignore capitals | `.lower()` |
| remove spaces around input | `.strip()` |
| get the words | `.split()` |
| make a sentence from words | `" ".join(words)` |
| does it contain X? | `x in s`, `.find`, `.count` |
| is this input valid? | `.isdigit()`, `.isalpha()` |
| swap text | `.replace(old, new)` |

## A worked example: clean up a name

```python
def clean_name(raw):
    parts = raw.strip().split()
    return " ".join(p.capitalize() for p in parts)

print(clean_name("  aSHA   kumar "))
print(clean_name("PIP"))
```

```output
Asha Kumar
Pip
```

## Common Mistakes

**1. Forgetting to save the result.**

```python
name = "asha"
name.title()
print(name)
name = name.title()
print(name)
```

```output
asha
Asha
```

**2. Using `.index()` when the item may be missing.** It raises `ValueError`; `.find()` returns -1.

```python expect-error
print("hello".index("z"))
```

```output
ValueError: substring not found
```

**3. Believing `isdigit()` accepts negatives or decimals.** It does not.

**4. Expecting `split()` and `split(" ")` to behave the same.** With `" "`, multiple spaces produce empty strings.

```python
print("a  b".split())
print("a  b".split(" "))
```

```output
['a', 'b']
['a', '', 'b']
```

## Try It Yourself

Given a sentence, print the number of words, the longest word, and the sentence with each word capitalised.

```python-try
sentence = "the quick brown fox jumps over the lazy dog"
words = sentence.split()
print(len(words))
longest = words[0]
for w in words:
    if len(w) > len(longest):
        longest = w
print(longest)
print(sentence.title())
```

**Challenge:** Read an email address and print the username part (before `@`) and the domain (after it).

## Recap

- String methods return **new** strings; save the result if you need it.
- Case: `upper`, `lower`, `title`; trimming: `strip`; searching: `find`, `count`, `startswith`.
- `split()` turns text into a list of words; `"sep".join(list)` does the reverse.
- `isdigit`, `isalpha`, `isalnum` validate input.
- Methods can be chained: `s.strip().lower().title()`.

**Next up:** **string formatting** in detail.

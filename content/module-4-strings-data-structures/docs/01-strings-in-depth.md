---
id: 01-strings-in-depth
title: "Strings in Depth"
order: 1
concepts: ["strings", "escape-sequences", "string-immutability", "string-iteration"]
---

# Strings in Depth

You met strings in Module 1. Now we go under the hood, because text is everywhere: names, messages, web pages, file contents, passwords. A **string** is an ordered, **immutable** sequence of characters.

## Creating strings

Single, double and triple quotes all create strings:

```python
a = 'single quotes'
b = "double quotes"
c = """triple quotes
can span several lines"""
print(a)
print(b)
print(c)
```

```output
single quotes
double quotes
triple quotes
can span several lines
```

Use whichever quote type avoids escaping:

```python
print("It's easy")
print('She said "hello"')
print("She said \"hi\" and it's fine")
```

```output
It's easy
She said "hello"
She said "hi" and it's fine
```

## Escape sequences

A backslash starts a special character:

| Code | Meaning |
|:----:|---------|
| `\n` | new line |
| `\t` | tab |
| `\\` | backslash |
| `\'` `\"` | quote characters |
| `\u00e9` | a Unicode character (é) |

```python
print("Line 1\nLine 2")
print("Col1\tCol2\tCol3")
print("C:\\Users\\Asha")
print("caf\u00e9")
```

```output
Line 1
Line 2
Col1	Col2	Col3
C:\Users\Asha
café
```

### Raw strings

Put an `r` before the quote and backslashes are kept literally. This is handy for file paths and regular expressions.

```python
print(r"C:\new\table")
print(len(r"\n"))
```

```output
C:\new\table
2
```

## Length, indexing, slicing (a recap with more depth)

```python
s = "Hello, World"
print(len(s))
print(s[0], s[-1])
print(s[7:12])
print(s[:5])
print(s[::-1])
print(s[::3])
```

```output
12
H d
World
Hello
dlroW ,olleH
Hl r
```

Slices never raise errors when they run past the end; they just stop:

```python
s = "Python"
print(s[2:100])
print(s[10:20] == "")
```

```output
thon
True
```

## Immutability

Once created, a string cannot be modified in place. Operations build *new* strings.

```python
s = "hello"
t = s.upper()
print(s)
print(t)
s = s + " world"
print(s)
```

```output
hello
HELLO
hello world
```

Building a long string by repeatedly using `+` in a loop creates many temporary strings. For larger jobs, collect the parts in a list and use `"".join(parts)`.

```python
parts = []
for i in range(1, 6):
    parts.append(str(i))
print("-".join(parts))
```

```output
1-2-3-4-5
```

## Iterating over a string

```python
word = "Python"
for ch in word:
    print(ch, end=" ")
print()
for i, ch in enumerate(word):
    if i % 2 == 0:
        print(ch.upper(), end="")
    else:
        print(ch.lower(), end="")
print()
```

```output
P y t h o n 
PyThOn
```

## Comparing and testing strings

```python
print("abc" == "abc")
print("abc" < "abd")
print("Python" in "I love Python")
print("Python".startswith("Py"), "Python".endswith("on"))
```

```output
True
True
True
True True
```

## Character codes

Every character has a numeric **Unicode code point**:

```python
print(ord("A"), ord("a"), ord("0"))
print(chr(72), chr(105))
print("".join(chr(ord(c) + 1) for c in "HAL"))
```

```output
65 97 48
H i
IBM
```

The last line shifts each letter of "HAL" forward by one, giving "IBM". (A famous movie reference!)

## Concatenation and repetition

```python
first = "Py"
last = "thon"
print(first + last)
print("=" * 10)
print("ab" * 3 + "!")
```

```output
Python
==========
ababab!
```

You cannot concatenate a string and a number directly. Convert with `str()` or use an f-string.

## A worked example: is it a palindrome?

A **palindrome** reads the same forwards and backwards (`level`, `madam`).

```python
def is_palindrome(text):
    cleaned = text.lower().replace(" ", "")
    return cleaned == cleaned[::-1]

print(is_palindrome("level"))
print(is_palindrome("Never odd or even"))
print(is_palindrome("Python"))
```

```output
True
True
False
```

## Common Mistakes

**1. Trying to change a character.**

```python expect-error
s = "cat"
s[0] = "b"
```

```output
TypeError: 'str' object does not support item assignment
```

**2. Forgetting that methods return new strings.** `s.upper()` on its own line does nothing useful.

**3. Off-by-one slice bounds.** `s[0:3]` gives 3 characters (indexes 0, 1, 2).

**4. Backslashes in Windows paths.** `"C:\new"` contains a newline! Use a raw string.

```python
print(len("C:\new"))
print(len(r"C:\new"))
```

```output
5
6
```

## Try It Yourself

Write a program that takes a word and prints it with the letters separated by dashes, then reversed, then with alternating capitals.

```python-try
word = "Programming"
print("-".join(word))
print(word[::-1])
result = ""
for i, ch in enumerate(word):
    result += ch.upper() if i % 2 == 0 else ch.lower()
print(result)
```

**Challenge:** Check whether two words are anagrams (hint: compare `sorted(a) == sorted(b)`).

## Recap

- Strings can use single, double or triple quotes; escape sequences insert special characters.
- Raw strings (`r"..."`) keep backslashes.
- Indexing and slicing never modify a string; strings are immutable.
- `"sep".join(list)` is the efficient way to combine many pieces.
- `ord()` and `chr()` convert between characters and codes.

**Next up:** the powerful **string methods**.

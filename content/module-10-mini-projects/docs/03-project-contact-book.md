---
id: 03-project-contact-book
title: "Project 2: Contact Book"
order: 3
concepts: ["project-contacts", "dictionaries-in-projects", "project-practice"]
---

# Project 2: Contact Book

**Goal:** store names with phone numbers and emails, search them (even by part of a name), and keep them between runs.

**Skills used:** dictionaries, sorting, string methods, validation, JSON files.

## Requirements

- Add a contact with a name, phone number and (optional) email.
- Reject duplicates and invalid phone numbers.
- Find by exact name, or search by part of a name.
- Update and delete contacts.
- List everyone alphabetically.
- Save and load from a JSON file.

## Design

**Data:** a dictionary keyed by the *lower-cased* name (so `Asha` and `asha` are the same person), each value a dictionary of details:

```python
book = {
    "asha": {"name": "Asha", "phone": "9810012345", "email": "asha@example.com"},
    "ravi": {"name": "Ravi", "phone": "9822233444", "email": ""},
}
print(book["asha"]["phone"])
print(sorted(c["name"] for c in book.values()))
```

```output
9810012345
['Asha', 'Ravi']
```

The key is normalised, while the display name keeps its original capitals.

## Step 1: validation helpers

```python
def clean_phone(text):
    digits = "".join(ch for ch in text if ch.isdigit())
    if digits.startswith("91") and len(digits) == 12:
        digits = digits[2:]
    if len(digits) != 10:
        raise ValueError(f"phone must have 10 digits, got {len(digits)}")
    return digits

def valid_email(text):
    return text == "" or ("@" in text and "." in text.split("@")[-1])

for raw in ["98100-12345", "+91 98222 33444", "12345"]:
    try:
        print(clean_phone(raw))
    except ValueError as e:
        print("Error:", e)
print(valid_email("a@b.com"), valid_email("nope"), valid_email(""))
```

```output
9810012345
9822233444
Error: phone must have 10 digits, got 5
True False True
```

We keep only the digits, accept an optional `+91` country code, and insist on exactly ten digits. `valid_email` is deliberately simple: an `@` and a dot in the domain part (an empty email is allowed).

## Step 2: the core operations

```python
def clean_phone(text):
    digits = "".join(ch for ch in text if ch.isdigit())
    if digits.startswith("91") and len(digits) == 12:
        digits = digits[2:]
    if len(digits) != 10:
        raise ValueError("phone must have 10 digits")
    return digits

def key_for(name):
    return " ".join(name.lower().split())

def add_contact(book, name, phone, email=""):
    key = key_for(name)
    if not key:
        raise ValueError("name cannot be empty")
    if key in book:
        raise ValueError(f"{name} already exists")
    book[key] = {"name": " ".join(name.split()).title(), "phone": clean_phone(phone), "email": email.strip()}

def find_contact(book, name):
    return book.get(key_for(name))

def search(book, text):
    text = text.lower()
    return sorted(c["name"] for k, c in book.items() if text in k)

def update_phone(book, name, phone):
    contact = find_contact(book, name)
    if contact is None:
        raise KeyError(name)
    contact["phone"] = clean_phone(phone)

def delete_contact(book, name):
    if book.pop(key_for(name), None) is None:
        raise KeyError(name)

book = {}
add_contact(book, "asha  kumar", "98100 12345", "asha@example.com")
add_contact(book, "Ravi Singh", "+91 98222 33444")
add_contact(book, "Meera Kapoor", "9812345678")
print(find_contact(book, "ASHA KUMAR")["phone"])
print(search(book, "ra"))
update_phone(book, "ravi singh", "98999 88777")
print(book["ravi singh"]["phone"])
delete_contact(book, "Meera Kapoor")
print(sorted(c["name"] for c in book.values()))
try:
    add_contact(book, "Asha Kumar", "9000000000")
except ValueError as e:
    print("Error:", e)
```

```output
9810012345
['Meera Kapoor', 'Ravi Singh']
9899988777
['Asha Kumar', 'Ravi Singh']
Error: Asha Kumar already exists
```

`search(book, "ra")` returns every contact whose lower-cased name contains the letters `ra`. Look at which names appear in the output and check the letters yourself: that is how you convince yourself the search works.

## Step 3: saving and loading

```python
import json

def save_book(book, path):
    with open(path, "w") as f:
        json.dump(book, f, indent=2, sort_keys=True)

def load_book(path):
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

book = {"asha": {"name": "Asha", "phone": "9810012345", "email": ""}}
save_book(book, "contacts.json")
print(load_book("contacts.json") == book)
print(load_book("missing.json"))
```

```output
True
{}
```

## Step 4: the interactive program

```python stdin="add|Asha Kumar|98100 12345|asha@example.com|add|Ravi Singh|98222 33444||add|Asha Kumar|9000000000||find|asha kumar|search|ra|list|delete|ravi singh|list|quit"
import json

FILENAME = "contacts_project.json"

def clean_phone(text):
    digits = "".join(ch for ch in text if ch.isdigit())
    if digits.startswith("91") and len(digits) == 12:
        digits = digits[2:]
    if len(digits) != 10:
        raise ValueError("phone must have 10 digits")
    return digits

def key_for(name):
    return " ".join(name.lower().split())

def load_book():
    try:
        with open(FILENAME) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_book(book):
    with open(FILENAME, "w") as f:
        json.dump(book, f, indent=2)

def show(contact):
    email = contact["email"] or "-"
    return f"{contact['name']:<12} {contact['phone']}  {email}"

def main():
    book = load_book()
    while True:
        choice = input().strip().lower()
        if choice == "add":
            name, phone, email = input(), input(), input()
            try:
                key = key_for(name)
                if key in book:
                    raise ValueError("already exists")
                book[key] = {"name": name.title(), "phone": clean_phone(phone), "email": email}
                print("Added", name.title())
            except ValueError as e:
                print("Could not add:", e)
        elif choice == "find":
            contact = book.get(key_for(input()))
            print(show(contact) if contact else "Not found")
        elif choice == "search":
            text = input().lower()
            hits = [c for k, c in sorted(book.items()) if text in k]
            print(f"{len(hits)} match(es)")
            for c in hits:
                print(" ", show(c))
        elif choice == "list":
            for k in sorted(book):
                print(show(book[k]))
        elif choice == "delete":
            name = input()
            print("Deleted" if book.pop(key_for(name), None) else "Not found")
        elif choice == "quit":
            save_book(book)
            print("Saved", len(book), "contacts")
            break

main()
```

```output
Added Asha Kumar
Added Ravi Singh
Could not add: already exists
Asha Kumar   9810012345  asha@example.com
1 match(es)
  Ravi Singh   9822233444  -
Asha Kumar   9810012345  asha@example.com
Ravi Singh   9822233444  -
Deleted
Asha Kumar   9810012345  asha@example.com
Saved 1 contacts
```

## Step 5: test the helpers

```python
def key_for(name):
    return " ".join(name.lower().split())

assert key_for("  Asha   KUMAR ") == "asha kumar"
assert key_for("") == ""

def clean_phone(text):
    digits = "".join(ch for ch in text if ch.isdigit())
    if digits.startswith("91") and len(digits) == 12:
        digits = digits[2:]
    if len(digits) != 10:
        raise ValueError("bad phone")
    return digits

assert clean_phone("98100-12345") == "9810012345"
assert clean_phone("+91 98222 33444") == "9822233444"
for bad in ["", "123", "98100123456789"]:
    try:
        clean_phone(bad)
    except ValueError:
        pass
    else:
        raise AssertionError(f"{bad!r} should have been rejected")
print("contact tests passed")
```

```output
contact tests passed
```

## Ideas to extend it

1. **Multiple phone numbers** per contact (a list).
2. **Groups/tags** (family, work) stored as sets.
3. **Import/export CSV** with the `csv` module.
4. **Birthdays** and a "who has a birthday this month?" report using `datetime`.
5. **Fuzzy search** that tolerates typos (`difflib.get_close_matches`).
6. A **tkinter** address-book window with a search box.

## Common Mistakes

**1. Using the raw name as the key.** `"asha"` and `"Asha"` become two contacts; normalise first.

**2. Storing phone numbers as integers.** You lose leading zeros and cannot store `+91` or dashes. Use strings.

**3. Trusting user input.** Always validate before saving.

**4. Overwriting an existing contact by accident.** Check for the key before assigning.

```python
print(int("0123456789"))
print(str(123456789).zfill(10))
```

```output
123456789
0123456789
```

Storing as an `int` dropped the leading zero.

## Try It Yourself

Write `by_domain(book)` that groups contacts by their email domain (the part after `@`), ignoring contacts without an email.

```python-try
def by_domain(book):
    groups = {}
    for c in book.values():
        if "@" in c["email"]:
            domain = c["email"].split("@")[1]
            groups.setdefault(domain, []).append(c["name"])
    return {d: sorted(names) for d, names in groups.items()}

book = {
    "a": {"name": "Asha", "email": "asha@school.edu"},
    "b": {"name": "Ravi", "email": "ravi@gmail.com"},
    "c": {"name": "Meera", "email": "meera@school.edu"},
    "d": {"name": "Pip", "email": ""},
}
result = by_domain(book)
assert result == {"school.edu": ["Asha", "Meera"], "gmail.com": ["Ravi"]}
print(result)
```

**Challenge:** Add an `edit` command that lets the user change any one field.

## Recap

- Normalise keys (`lower`, collapse spaces) so lookups are forgiving; keep a display name.
- Validate at the boundary: clean phones, check emails, reject duplicates and empty names.
- Use dictionaries for lookup, `sorted` for stable listings, substring search for "find as you type".
- Persist with JSON; handle a missing or damaged file gracefully.
- Test helper functions with `assert`, including bad inputs.

**Next up:** Project 3, an **expense tracker**.

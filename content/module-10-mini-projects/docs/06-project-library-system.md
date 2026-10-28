---
id: 06-project-library-system
title: "Project 5: Library Management System"
order: 6
concepts: ["project-library", "oop-in-projects", "project-practice"]
---

# Project 5: Library Management System

**Goal:** model a small library: books, members, borrowing and returning, due dates and fines.

**Skills used:** classes and objects, composition, exceptions, `datetime`, dictionaries.

## Requirements

- A library holds many books; each book has a title, author and ISBN.
- Members can borrow up to 3 books at a time for 14 days.
- A book can be borrowed by only one member at once.
- Returning late costs a fine of 2 rupees per day.
- Search by title/author and list overdue books.

## Design: nouns become classes

| Class | Data | Behaviour |
|-------|------|-----------|
| `Book` | isbn, title, author, borrower, due date | `is_available()` |
| `Member` | name, list of borrowed books | `can_borrow()` |
| `Library` | dict of books, dict of members | add, borrow, return, search, overdue |
| `LibraryError` | (custom exception) | signals rule violations |

A `Library` **has** books and members (composition), so it holds them as attributes.

## Step 1: the building blocks

```python
from datetime import date, timedelta

class LibraryError(Exception):
    pass

class Book:
    def __init__(self, isbn, title, author):
        self.isbn = isbn
        self.title = title
        self.author = author
        self.borrower = None
        self.due = None

    def is_available(self):
        return self.borrower is None

    def __repr__(self):
        state = "available" if self.is_available() else f"due {self.due}"
        return f"Book({self.title!r}, {state})"

class Member:
    MAX_BOOKS = 3

    def __init__(self, name):
        self.name = name
        self.books = []

    def can_borrow(self):
        return len(self.books) < self.MAX_BOOKS

book = Book("111", "Matilda", "Roald Dahl")
print(book)
print(book.is_available())
member = Member("Asha")
print(member.can_borrow(), Member.MAX_BOOKS)
```

```output
Book('Matilda', available)
True
True 3
```

## Step 2: the `Library` class

```python
from datetime import date, timedelta

class LibraryError(Exception):
    pass

class Book:
    def __init__(self, isbn, title, author):
        self.isbn, self.title, self.author = isbn, title, author
        self.borrower = None
        self.due = None

    def is_available(self):
        return self.borrower is None

class Member:
    MAX_BOOKS = 3
    def __init__(self, name):
        self.name = name
        self.books = []
    def can_borrow(self):
        return len(self.books) < self.MAX_BOOKS

class Library:
    LOAN_DAYS = 14
    FINE_PER_DAY = 2

    def __init__(self):
        self.books = {}
        self.members = {}

    def add_book(self, isbn, title, author):
        if isbn in self.books:
            raise LibraryError(f"ISBN {isbn} already exists")
        self.books[isbn] = Book(isbn, title, author)

    def join(self, name):
        if name in self.members:
            raise LibraryError(f"{name} is already a member")
        self.members[name] = Member(name)

    def borrow(self, name, isbn, today):
        member = self.members.get(name)
        book = self.books.get(isbn)
        if member is None:
            raise LibraryError(f"{name} is not a member")
        if book is None:
            raise LibraryError(f"no book with ISBN {isbn}")
        if not book.is_available():
            raise LibraryError(f"'{book.title}' is already borrowed")
        if not member.can_borrow():
            raise LibraryError(f"{name} has reached the limit of {Member.MAX_BOOKS} books")
        book.borrower = name
        book.due = today + timedelta(days=self.LOAN_DAYS)
        member.books.append(book)
        return book.due

    def give_back(self, isbn, today):
        book = self.books.get(isbn)
        if book is None or book.is_available():
            raise LibraryError("that book is not on loan")
        late_days = max(0, (today - book.due).days)
        fine = late_days * self.FINE_PER_DAY
        self.members[book.borrower].books.remove(book)
        book.borrower = book.due = None
        return fine

    def search(self, text):
        text = text.lower()
        return sorted(b.title for b in self.books.values()
                      if text in b.title.lower() or text in b.author.lower())

    def overdue(self, today):
        return sorted((b.title, b.borrower, (today - b.due).days)
                      for b in self.books.values()
                      if not b.is_available() and today > b.due)

lib = Library()
lib.add_book("1", "Matilda", "Roald Dahl")
lib.add_book("2", "The BFG", "Roald Dahl")
lib.add_book("3", "The Jungle Book", "Rudyard Kipling")
lib.add_book("4", "Charlie and the Chocolate Factory", "Roald Dahl")
lib.join("Asha")
lib.join("Ravi")

start = date(2025, 3, 1)
print(lib.borrow("Asha", "1", start))
print(lib.borrow("Asha", "2", start))
print(lib.borrow("Asha", "3", start))

for name, isbn in [("Asha", "4"), ("Ravi", "1"), ("Zoya", "2"), ("Ravi", "99")]:
    try:
        lib.borrow(name, isbn, start)
    except LibraryError as e:
        print("Refused:", e)

print(lib.search("dahl"))
print(lib.overdue(date(2025, 3, 20)))
print("Fine for Matilda:", lib.give_back("1", date(2025, 3, 20)))
print("Fine for The BFG:", lib.give_back("2", date(2025, 3, 10)))
print([b.title for b in lib.members["Asha"].books])
```

```output
2025-03-15
2025-03-15
2025-03-15
Refused: Asha has reached the limit of 3 books
Refused: 'Matilda' is already borrowed
Refused: Zoya is not a member
Refused: no book with ISBN 99
['Charlie and the Chocolate Factory', 'Matilda', 'The BFG']
[('Matilda', 'Asha', 5), ('The BFG', 'Asha', 5), ('The Jungle Book', 'Asha', 5)]
Fine for Matilda: 10
Fine for The BFG: 0
['The Jungle Book']
```

Read the output line by line against the rules: the 4th book is refused because Asha has 3 already; Ravi cannot take a borrowed book; unknown members and unknown ISBNs are refused. Matilda was due on 15 March, so returning on 20 March is 5 days late and costs 10 rupees.

## Step 3: a friendly report

```python
from datetime import date, timedelta

def status_line(title, borrower, due, today):
    if borrower is None:
        return f"{title:<20} available"
    left = (due - today).days
    when = f"due in {left} days" if left >= 0 else f"OVERDUE by {-left} days"
    return f"{title:<20} {borrower:<6} {when}"

today = date(2025, 3, 20)
print(status_line("Matilda", "Asha", date(2025, 3, 15), today))
print(status_line("The BFG", "Asha", date(2025, 3, 25), today))
print(status_line("The Jungle Book", None, None, today))
```

```output
Matilda              Asha   OVERDUE by 5 days
The BFG              Asha   due in 5 days
The Jungle Book      available
```

## Step 4: an interactive session

```python stdin="join Asha|add 1 Matilda|add 2 The BFG|borrow Asha 1|borrow Asha 1|list|return 1|list|quit"
from datetime import date, timedelta

books = {}
loans = {}
members = set()
today = date(2025, 3, 1)

def handle(line):
    verb, *args = line.split()
    if verb == "join":
        members.add(args[0])
        return f"Welcome, {args[0]}"
    if verb == "add":
        books[args[0]] = " ".join(args[1:])
        return f"Added {books[args[0]]}"
    if verb == "borrow":
        name, isbn = args
        if name not in members:
            return "Not a member"
        if isbn in loans:
            return f"{books[isbn]} is already borrowed"
        loans[isbn] = (name, today + timedelta(days=14))
        return f"{name} borrowed {books[isbn]}, due {loans[isbn][1]}"
    if verb == "return":
        name, due = loans.pop(args[0])
        return f"{books[args[0]]} returned by {name}"
    if verb == "list":
        return "; ".join(f"{t} ({'out' if i in loans else 'in'})" for i, t in sorted(books.items()))
    return "Unknown command"

while True:
    line = input().strip()
    if line == "quit":
        print("Goodbye")
        break
    print(handle(line))
```

```output
Welcome, Asha
Added Matilda
Added The BFG
Asha borrowed Matilda, due 2025-03-15
Matilda is already borrowed
Matilda (out); The BFG (in)
Matilda returned by Asha
Matilda (in); The BFG (in)
Goodbye
```

## Testing the rules

```python
from datetime import date, timedelta

LOAN_DAYS, FINE = 14, 2

def fine_for(due, returned):
    return max(0, (returned - due).days) * FINE

due = date(2025, 3, 15)
assert fine_for(due, date(2025, 3, 15)) == 0       # on the due date
assert fine_for(due, date(2025, 3, 10)) == 0       # early
assert fine_for(due, date(2025, 3, 16)) == 2       # one day late
assert fine_for(due, date(2025, 4, 14)) == 60      # 30 days late
assert date(2025, 3, 1) + timedelta(days=LOAN_DAYS) == due
print("library tests passed")
```

```output
library tests passed
```

## Ideas to extend it

1. **Reservations**: a queue of members waiting for a borrowed book.
2. **Different loan periods** for different book types (inheritance: `Book`, `Magazine`, `Reference`).
3. **Save the library** to JSON and load it back.
4. **Membership types** with different limits (child, adult, staff).
5. A **history** of every loan for statistics: most popular book, busiest month.
6. A **web or tkinter** front end.

## Common Mistakes

**1. Two sources of truth.** If the book stores its borrower and the member stores its books, update both in the same place, or they drift apart.

**2. Comparing the wrong dates.** Fine days are `returned - due`, not `returned - borrowed`.

**3. Letting invalid actions succeed silently.** Raise a clear `LibraryError`.

**4. Storing the current date inside the class** (`date.today()`), which makes testing impossible. Pass `today` in as an argument.

```python
from datetime import date

def is_late(due, returned):
    return returned > due

print(is_late(date(2025, 3, 15), date(2025, 3, 15)))
print(is_late(date(2025, 3, 15), date(2025, 3, 16)))
```

```output
False
True
```

Returning *on* the due date is not late.

## Try It Yourself

Add a method `available_titles(library)` (as a plain function) that returns the sorted titles of books that are currently available.

```python-try
class Book:
    def __init__(self, title, borrower=None):
        self.title = title
        self.borrower = borrower

def available_titles(books):
    return sorted(b.title for b in books if b.borrower is None)

shelf = [Book("Matilda", "Asha"), Book("The BFG"), Book("Holes"), Book("Dune", "Ravi")]
result = available_titles(shelf)
assert result == ["Holes", "The BFG"]
print(result)
```

**Challenge:** Add `renew(name, isbn, today)` that extends the due date by 7 days, but only once per loan.

## Recap

- Nouns become classes; a `Library` **has** `Book`s and `Member`s (composition).
- Enforce business rules in methods and signal violations with a custom exception.
- Pass "today" as a parameter so date logic is testable.
- Keep related data consistent by updating it in one method.
- Test the rules (especially boundaries such as "due today") with `assert`.

**Next up:** Project 6, a **student management system**.

---
id: 07-project-student-management
title: "Project 6: Student Management System"
order: 7
concepts: ["project-students", "data-persistence-projects", "project-practice"]
---

# Project 6: Student Management System

**Goal:** a small school register: enrol students, record marks in several subjects, see report cards and class statistics, and save everything to a file.

**Skills used:** classes with properties, dictionaries of lists, sorting, statistics, JSON persistence, error handling.

## Requirements

- Enrol students with a unique roll number.
- Record marks (0-100) for subjects.
- A student's report card shows each subject, the average and a grade.
- Class reports: the topper, subject averages, students needing help.
- Save and load the whole register.
- Refuse bad data with clear messages.

## Design

| Class | Responsibility |
|-------|----------------|
| `Student` | name, roll number, marks per subject; average and grade |
| `Register` | all students; enrol, record, reports; save/load |

Data shape for saving: a list of plain dictionaries, which JSON handles easily. Each class gets `to_dict` and `from_dict` methods to convert.

## Step 1: the `Student` class

```python
class Student:
    def __init__(self, roll, name):
        if not name.strip():
            raise ValueError("name cannot be empty")
        self.roll = roll
        self.name = name.strip().title()
        self.marks = {}

    def record(self, subject, mark):
        if not 0 <= mark <= 100:
            raise ValueError(f"marks must be between 0 and 100, got {mark}")
        self.marks[subject.strip().lower()] = mark

    @property
    def average(self):
        return sum(self.marks.values()) / len(self.marks) if self.marks else 0.0

    @property
    def grade(self):
        avg = self.average
        for cutoff, letter in [(90, "A"), (75, "B"), (60, "C"), (40, "D")]:
            if avg >= cutoff:
                return letter
        return "F"

    def to_dict(self):
        return {"roll": self.roll, "name": self.name, "marks": self.marks}

    @classmethod
    def from_dict(cls, data):
        student = cls(data["roll"], data["name"])
        student.marks = dict(data["marks"])
        return student

    def report_card(self):
        lines = [f"Report card: {self.name} (roll {self.roll})", "-" * 28]
        for subject, mark in sorted(self.marks.items()):
            lines.append(f"{subject.title():<14}{mark:>6}")
        lines += ["-" * 28, f"{'Average':<14}{self.average:>6.1f}", f"{'Grade':<14}{self.grade:>6}"]
        return "\n".join(lines)

s = Student(7, "asha kumar")
s.record("Maths", 88)
s.record("science", 92)
s.record("English", 79)
print(s.report_card())
try:
    s.record("art", 120)
except ValueError as e:
    print("Error:", e)
print(Student.from_dict(s.to_dict()).average == s.average)
```

```output
Report card: Asha Kumar (roll 7)
----------------------------
English           79
Maths             88
Science           92
----------------------------
Average         86.3
Grade              B
Error: marks must be between 0 and 100, got 120
True
```

`average` and `grade` are properties: they are always calculated from the current marks and can never go out of date.

## Step 2: the `Register`

```python
import json

class Student:
    def __init__(self, roll, name):
        self.roll, self.name, self.marks = roll, name.strip().title(), {}
    def record(self, subject, mark):
        if not 0 <= mark <= 100:
            raise ValueError(f"marks must be between 0 and 100, got {mark}")
        self.marks[subject.lower()] = mark
    @property
    def average(self):
        return sum(self.marks.values()) / len(self.marks) if self.marks else 0.0
    def to_dict(self):
        return {"roll": self.roll, "name": self.name, "marks": self.marks}
    @classmethod
    def from_dict(cls, d):
        s = cls(d["roll"], d["name"])
        s.marks = dict(d["marks"])
        return s

class Register:
    def __init__(self):
        self.students = {}

    def enrol(self, roll, name):
        if roll in self.students:
            raise ValueError(f"roll number {roll} is already taken")
        self.students[roll] = Student(roll, name)

    def get(self, roll):
        try:
            return self.students[roll]
        except KeyError:
            raise KeyError(f"no student with roll number {roll}") from None

    def topper(self):
        return max(self.students.values(), key=lambda s: s.average) if self.students else None

    def subject_averages(self):
        totals, counts = {}, {}
        for s in self.students.values():
            for subject, mark in s.marks.items():
                totals[subject] = totals.get(subject, 0) + mark
                counts[subject] = counts.get(subject, 0) + 1
        return {sub: round(totals[sub] / counts[sub], 1) for sub in sorted(totals)}

    def needs_help(self, cutoff=50):
        return sorted(s.name for s in self.students.values() if s.marks and s.average < cutoff)

    def save(self, path):
        with open(path, "w") as f:
            json.dump([s.to_dict() for s in self.students.values()], f, indent=2)

    @classmethod
    def load(cls, path):
        register = cls()
        try:
            with open(path) as f:
                for d in json.load(f):
                    register.students[d["roll"]] = Student.from_dict(d)
        except FileNotFoundError:
            pass
        return register

reg = Register()
for roll, name in [(1, "Asha"), (2, "Ravi"), (3, "Pip"), (4, "Kabir")]:
    reg.enrol(roll, name)
data = {1: {"maths": 88, "science": 92}, 2: {"maths": 72, "science": 65},
        3: {"maths": 95, "science": 90}, 4: {"maths": 45, "science": 40}}
for roll, marks in data.items():
    for subject, mark in marks.items():
        reg.get(roll).record(subject, mark)

print("Topper:", reg.topper().name)
print("Subject averages:", reg.subject_averages())
print("Needs help:", reg.needs_help())
try:
    reg.enrol(2, "Duplicate")
except ValueError as e:
    print("Error:", e)
try:
    reg.get(99)
except KeyError as e:
    print("Error:", e.args[0])

reg.save("school.json")
copy = Register.load("school.json")
print(len(copy.students), copy.get(3).average)
print(len(Register.load("missing.json").students))
```

```output
Topper: Pip
Subject averages: {'maths': 75.0, 'science': 71.8}
Needs help: ['Kabir']
Error: roll number 2 is already taken
Error: no student with roll number 99
4 92.5
0
```

## Step 3: a rank list

```python
students = [("Asha", 90.0), ("Ravi", 68.5), ("Pip", 92.5), ("Zoya", 68.5), ("Kabir", 42.5)]

ranked = sorted(students, key=lambda s: (-s[1], s[0]))
rank = 0
previous = None
for position, (name, avg) in enumerate(ranked, start=1):
    if avg != previous:
        rank = position
    previous = avg
    print(f"{rank}. {name:<6}{avg:>6.1f}")
```

```output
1. Pip     92.5
2. Asha    90.0
3. Ravi    68.5
3. Zoya    68.5
5. Kabir   42.5
```

Students with equal averages share a rank ("competition ranking"), and the alphabetical tie-break makes the order stable.

## Step 4: an interactive session

```python stdin="enrol 1 Asha|enrol 2 Ravi|mark 1 maths 88|mark 1 science 92|mark 2 maths 72|mark 2 science 61|mark 2 art 150|card 1|top|quit"
students = {}

def average(marks):
    return sum(marks.values()) / len(marks) if marks else 0

while True:
    parts = input().split()
    verb = parts[0]
    try:
        if verb == "enrol":
            roll, name = int(parts[1]), " ".join(parts[2:]).title()
            if roll in students:
                raise ValueError("roll number already used")
            students[roll] = {"name": name, "marks": {}}
            print(f"Enrolled {name} (roll {roll})")
        elif verb == "mark":
            roll, subject, mark = int(parts[1]), parts[2], int(parts[3])
            if not 0 <= mark <= 100:
                raise ValueError("mark must be 0-100")
            students[roll]["marks"][subject] = mark
            print(f"Recorded {subject} {mark} for {students[roll]['name']}")
        elif verb == "card":
            s = students[int(parts[1])]
            print(f"{s['name']}: " + ", ".join(f"{k} {v}" for k, v in sorted(s["marks"].items())))
            print(f"Average {average(s['marks']):.1f}")
        elif verb == "top":
            best = max(students.values(), key=lambda s: average(s["marks"]))
            print(f"Topper: {best['name']} ({average(best['marks']):.1f})")
        elif verb == "quit":
            print("Bye")
            break
        else:
            print("Unknown command")
    except (KeyError, ValueError, IndexError) as e:
        print("Problem:", e)
```

```output
Enrolled Asha (roll 1)
Enrolled Ravi (roll 2)
Recorded maths 88 for Asha
Recorded science 92 for Asha
Recorded maths 72 for Ravi
Recorded science 61 for Ravi
Problem: mark must be 0-100
Asha: maths 88, science 92
Average 90.0
Topper: Asha (90.0)
Bye
```

## Testing

```python
def grade(avg):
    for cutoff, letter in [(90, "A"), (75, "B"), (60, "C"), (40, "D")]:
        if avg >= cutoff:
            return letter
    return "F"

assert grade(100) == "A"
assert grade(90) == "A"      # boundary
assert grade(89.99) == "B"
assert grade(40) == "D"
assert grade(39.9) == "F"
assert grade(0) == "F"
print("student tests passed")
```

```output
student tests passed
```

## Ideas to extend it

1. **Attendance** tracking with percentages and a warning below 75%.
2. **Classes/sections** (a `Section` class holding many students).
3. **Weighted subjects** (exam 70%, project 30%).
4. A **CSV import** of a whole class from a spreadsheet.
5. **Charts**: a histogram of averages, a bar chart of subject averages (Module 9).
6. **Password-protected** teacher and student roles.

## Common Mistakes

**1. Storing the average as an attribute.** It goes stale when a mark changes. Use a property.

**2. Dividing by zero for a student with no marks.** Guard with `if self.marks`.

**3. Forgetting that JSON turns integer keys into strings.** If you store `{1: ...}` and reload it, the key becomes `"1"`. That is why we saved a *list* of records and rebuilt the dictionary.

**4. Letting duplicates in.** Check the roll number before enrolling.

```python
import json
data = {1: "Asha"}
print(json.loads(json.dumps(data)))
```

```output
{'1': 'Asha'}
```

## Try It Yourself

Write `distribution(averages)` that counts how many averages fall in each grade band (A, B, C, D, F), returning a dictionary that always includes all five letters.

```python-try
def band(avg):
    for cutoff, letter in [(90, "A"), (75, "B"), (60, "C"), (40, "D")]:
        if avg >= cutoff:
            return letter
    return "F"

def distribution(averages):
    counts = {letter: 0 for letter in "ABCDF"}
    for a in averages:
        counts[band(a)] += 1
    return counts

result = distribution([95, 88, 76, 60, 59, 12, 91])
assert result == {"A": 2, "B": 2, "C": 1, "D": 1, "F": 1}
print(result)
```

**Challenge:** Add a `remove(roll)` method to `Register` and make sure the JSON file is updated.

## Recap

- Split responsibilities: `Student` handles its own marks and grade; `Register` manages the collection.
- Use properties for values derived from other data (average, grade).
- Convert objects to plain dictionaries (`to_dict` / `from_dict`) to save them as JSON.
- Watch for JSON turning integer keys into strings; validate and guard against division by zero.
- Reports (topper, subject averages, ranks) are small functions over the data.

**Next up:** Project 7, a **banking system**.

---
id: 03-pattern-programming
title: "Pattern Programming - Star and Number Patterns"
order: 3
concepts: ["patterns", "nested-loops", "logic-building"]
---

# Pattern Programming

## What is Pattern Programming?

Pattern programming involves creating shapes and designs using characters (stars, numbers, letters) with nested loops. It's excellent for developing logical thinking and loop mastery.

### Why Learn Patterns?

1. **Logic Building**: Strengthens problem-solving skills
2. **Loop Mastery**: Deep understanding of nested loops
3. **Interview Prep**: Common in coding interviews
4. **Visual Feedback**: See your code create art!

## Understanding Pattern Logic

### The Pattern Formula

Most patterns follow this structure:

```python
for row in range(rows):
    # Print spaces (if needed)
    # Print main pattern (stars/numbers)
    # Move to next line
```

### Key Concepts

1. **Rows**: Outer loop controls number of lines
2. **Columns**: Inner loop controls items per line
3. **Spaces**: Often needed for alignment
4. **Relationship**: Find relation between row and columns

## Star Patterns

### Pattern 1: Right Triangle (Stars)

```
*
**
***
****
*****
```

**Code:**
```python
rows = 5
for i in range(1, rows + 1):
    for j in range(i):
        print("*", end="")
    print()
```

**Logic:**
- Row 1: 1 star
- Row 2: 2 stars
- Row 3: 3 stars
- Pattern: Row number = Number of stars

### Pattern 2: Inverted Right Triangle

```
*****
****
***
**
*
```

**Code:**
```python
rows = 5
for i in range(rows, 0, -1):
    for j in range(i):
        print("*", end="")
    print()

# Alternative approach
for i in range(rows):
    for j in range(rows - i):
        print("*", end="")
    print()
```

### Pattern 3: Left Triangle (Right-Aligned)

```
    *
   **
  ***
 ****
*****
```

**Code:**
```python
rows = 5
for i in range(1, rows + 1):
    # Print spaces
    for j in range(rows - i):
        print(" ", end="")
    # Print stars
    for j in range(i):
        print("*", end="")
    print()
```

**Logic Breakdown:**
```
Row 1: 4 spaces, 1 star
Row 2: 3 spaces, 2 stars
Row 3: 2 spaces, 3 stars
Row 4: 1 space,  4 stars
Row 5: 0 spaces, 5 stars

Spaces = total_rows - current_row
Stars = current_row
```

### Pattern 4: Pyramid (Centered Triangle)

```
    *
   ***
  *****
 *******
*********
```

**Code:**
```python
rows = 5
for i in range(1, rows + 1):
    # Print spaces
    for j in range(rows - i):
        print(" ", end="")
    # Print stars
    for j in range(2 * i - 1):
        print("*", end="")
    print()
```

**Logic:**
```
Row 1: 4 spaces, 1 star  (2×1-1 = 1)
Row 2: 3 spaces, 3 stars (2×2-1 = 3)
Row 3: 2 spaces, 5 stars (2×3-1 = 5)
Row 4: 1 space,  7 stars (2×4-1 = 7)
Row 5: 0 spaces, 9 stars (2×5-1 = 9)

Spaces = rows - i
Stars = 2 × i - 1
```

### Pattern 5: Inverted Pyramid

```
*********
 *******
  *****
   ***
    *
```

**Code:**
```python
rows = 5
for i in range(rows, 0, -1):
    # Print spaces
    for j in range(rows - i):
        print(" ", end="")
    # Print stars
    for j in range(2 * i - 1):
        print("*", end="")
    print()
```

### Pattern 6: Diamond

```
    *
   ***
  *****
 *******
*********
 *******
  *****
   ***
    *
```

**Code:**
```python
rows = 5

# Upper pyramid
for i in range(1, rows + 1):
    print(" " * (rows - i) + "*" * (2 * i - 1))

# Lower inverted pyramid
for i in range(rows - 1, 0, -1):
    print(" " * (rows - i) + "*" * (2 * i - 1))
```

### Pattern 7: Hollow Square

```
*****
*   *
*   *
*   *
*****
```

**Code:**
```python
rows = 5
for i in range(rows):
    for j in range(rows):
        # Print star on borders
        if i == 0 or i == rows - 1 or j == 0 or j == rows - 1:
            print("*", end="")
        else:
            print(" ", end="")
    print()
```

### Pattern 8: Hollow Pyramid

```
    *
   * *
  *   *
 *     *
*********
```

**Code:**
```python
rows = 5
for i in range(1, rows + 1):
    # Print spaces
    for j in range(rows - i):
        print(" ", end="")
    
    # Print stars and hollow spaces
    for j in range(1, 2 * i):
        if j == 1 or j == 2 * i - 1 or i == rows:
            print("*", end="")
        else:
            print(" ", end="")
    print()
```

## Number Patterns

### Pattern 9: Simple Number Triangle

```
1
12
123
1234
12345
```

**Code:**
```python
rows = 5
for i in range(1, rows + 1):
    for j in range(1, i + 1):
        print(j, end="")
    print()
```

### Pattern 10: Repeated Number Pattern

```
1
22
333
4444
55555
```

**Code:**
```python
rows = 5
for i in range(1, rows + 1):
    for j in range(i):
        print(i, end="")
    print()
```

### Pattern 11: Sequential Number Triangle

```
1
2 3
4 5 6
7 8 9 10
11 12 13 14 15
```

**Code:**
```python
rows = 5
num = 1

for i in range(1, rows + 1):
    for j in range(i):
        print(num, end=" ")
        num += 1
    print()
```

### Pattern 12: Number Pyramid (Centered)

```
    1
   121
  12321
 1234321
123454321
```

**Code:**
```python
rows = 5
for i in range(1, rows + 1):
    # Print spaces
    print(" " * (rows - i), end="")
    
    # Print ascending numbers
    for j in range(1, i + 1):
        print(j, end="")
    
    # Print descending numbers
    for j in range(i - 1, 0, -1):
        print(j, end="")
    
    print()
```

### Pattern 13: Floyd's Triangle

```
1
2 3
4 5 6
7 8 9 10
11 12 13 14 15
```

**Code:**
```python
rows = 5
num = 1

for i in range(1, rows + 1):
    for j in range(i):
        print(f"{num:3}", end=" ")
        num += 1
    print()
```

### Pattern 14: Reverse Number Triangle

```
12345
1234
123
12
1
```

**Code:**
```python
rows = 5
for i in range(rows, 0, -1):
    for j in range(1, i + 1):
        print(j, end="")
    print()
```

### Pattern 15: Binary Pattern

```
1
01
101
0101
10101
```

**Code:**
```python
rows = 5
for i in range(1, rows + 1):
    for j in range(1, i + 1):
        # Alternating 0 and 1
        if (i + j) % 2 == 0:
            print("1", end="")
        else:
            print("0", end="")
    print()
```

## Advanced Patterns

### Pattern 16: Pascal's Triangle

```
    1
   1 1
  1 2 1
 1 3 3 1
1 4 6 4 1
```

**Code:**
```python
rows = 5
for i in range(rows):
    # Print spaces
    print(" " * (rows - i), end="")
    
    # Calculate and print values
    num = 1
    for j in range(i + 1):
        print(num, end=" ")
        num = num * (i - j) // (j + 1)
    print()
```

### Pattern 17: Butterfly Pattern

```
*        *
**      **
***    ***
****  ****
**********
**********
****  ****
***    ***
**      **
*        *
```

**Code:**
```python
rows = 5

# Upper part
for i in range(1, rows + 1):
    # Left stars
    print("*" * i, end="")
    # Spaces
    print(" " * (2 * (rows - i)), end="")
    # Right stars
    print("*" * i)

# Lower part
for i in range(rows, 0, -1):
    # Left stars
    print("*" * i, end="")
    # Spaces
    print(" " * (2 * (rows - i)), end="")
    # Right stars
    print("*" * i)
```

### Pattern 18: Hourglass Pattern

```
*********
 *******
  *****
   ***
    *
   ***
  *****
 *******
*********
```

**Code:**
```python
rows = 5

# Upper inverted pyramid
for i in range(rows, 0, -1):
    print(" " * (rows - i) + "*" * (2 * i - 1))

# Lower pyramid
for i in range(2, rows + 1):
    print(" " * (rows - i) + "*" * (2 * i - 1))
```

### Pattern 19: Alphabet Pattern

```
A
AB
ABC
ABCD
ABCDE
```

**Code:**
```python
rows = 5
for i in range(1, rows + 1):
    for j in range(i):
        print(chr(65 + j), end="")  # 65 is ASCII for 'A'
    print()
```

### Pattern 20: Diamond Numbers

```
    1
   232
  34543
 4567654
567898765
```

**Code:**
```python
rows = 5
for i in range(1, rows + 1):
    # Spaces
    print(" " * (rows - i), end="")
    
    # Ascending numbers
    for j in range(i, 2 * i):
        print(j, end="")
    
    # Descending numbers
    for j in range(2 * i - 2, i - 1, -1):
        print(j, end="")
    
    print()
```

## Pattern Problem-Solving Strategy

### Step 1: Analyze the Pattern
- Count rows and columns
- Identify what changes in each row
- Look for relationships

### Step 2: Break It Down
```python
# Template
for row in range(n):
    # Step A: Leading spaces (if any)
    # Step B: Left part of pattern
    # Step C: Middle part (if any)
    # Step D: Right part (if any)
    print()  # New line
```

### Step 3: Find Formulas

**Common Relationships:**
- Stars increasing: `stars = row + 1`
- Stars decreasing: `stars = n - row`
- Pyramid stars: `stars = 2 * row + 1`
- Spaces before: `spaces = n - row - 1`

### Step 4: Test and Debug
- Print intermediate values
- Check boundary cases (first and last rows)
- Verify your formula

## Practice Problems

### Beginner Level
1. Print a square of stars (5×5)
2. Right triangle with increasing numbers
3. Inverted triangle of stars
4. Left-aligned triangle

### Intermediate Level
5. Hollow square
6. Diamond pattern
7. Number pyramid (centered)
8. Floyd's triangle with even numbers only

### Advanced Level
9. Butterfly pattern with numbers
10. Hollow diamond
11. Zigzag pattern
12. Spiral number pattern

## Interactive Pattern Generator

```python
def print_pattern(pattern_type, rows):
    """
    Interactive pattern generator
    """
    if pattern_type == "triangle":
        for i in range(1, rows + 1):
            print("*" * i)
    
    elif pattern_type == "pyramid":
        for i in range(1, rows + 1):
            print(" " * (rows - i) + "*" * (2 * i - 1))
    
    elif pattern_type == "diamond":
        # Upper pyramid
        for i in range(1, rows + 1):
            print(" " * (rows - i) + "*" * (2 * i - 1))
        # Lower inverted
        for i in range(rows - 1, 0, -1):
            print(" " * (rows - i) + "*" * (2 * i - 1))
    
    elif pattern_type == "hollow_square":
        for i in range(rows):
            if i == 0 or i == rows - 1:
                print("*" * rows)
            else:
                print("*" + " " * (rows - 2) + "*")

# Usage
print_pattern("pyramid", 7)
```

## Common Pattern Mistakes

### Mistake 1: Off-by-One Errors
```python
# Wrong
for i in range(5):      # 0 to 4
    print("*" * i)      # Starts with 0 stars!

# Right
for i in range(1, 6):   # 1 to 5
    print("*" * i)
```

### Mistake 2: Forgetting Spaces
```python
# Wrong - Not centered
for i in range(1, 6):
    print("*" * (2 * i - 1))

# Right - Centered pyramid
for i in range(1, 6):
    print(" " * (5 - i) + "*" * (2 * i - 1))
```

### Mistake 3: Wrong Formula
```python
# Debug your formula
rows = 5
for i in range(1, rows + 1):
    spaces = rows - i
    stars = 2 * i - 1
    print(f"Row {i}: {spaces} spaces, {stars} stars")
    print(" " * spaces + "*" * stars)
```

## Summary

### Key Concepts
- **Nested Loops**: Outer for rows, inner for columns
- **Spaces**: Often needed for alignment (formula: `n - row`)
- **Pattern Formula**: Find relationship between row number and output
- **Logic Building**: Break complex patterns into steps

### Pattern Categories
1. **Simple**: Right triangle, inverted triangle
2. **Centered**: Pyramid, diamond
3. **Hollow**: Hollow square, hollow pyramid
4. **Number**: Sequential, palindrome, Floyd's
5. **Advanced**: Butterfly, hourglass, Pascal's

### Tips for Success
1. Start with simple patterns
2. Draw the pattern on paper first
3. Find the formula for spaces and symbols
4. Test with small inputs (3-5 rows)
5. Use proper indentation and spacing
6. Print debug information to verify logic

**Next Up**: Learn about advanced loop techniques and algorithms!

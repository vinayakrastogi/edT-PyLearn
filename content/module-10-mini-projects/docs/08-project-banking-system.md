---
id: 08-project-banking-system
title: "Project 7: Simple Banking System"
order: 8
concepts: ["project-banking", "inheritance-in-projects", "project-practice"]
---

# Project 7: Simple Banking System

**Goal:** a bank with customers, different account types, deposits, withdrawals, transfers, a statement and interest, with **money handled safely**.

**Skills used:** inheritance and overriding, encapsulation, custom exceptions, composition, formatting, tests.

## Requirements

- Open accounts for customers; each account has a unique number.
- Deposit and withdraw; reject invalid amounts.
- **Savings account**: earns interest and cannot go below a minimum balance.
- **Current account**: may overdraw up to a limit.
- Transfer money between accounts (both succeed or neither does).
- A statement lists every transaction with the running balance.

## Money and floating point

Never use `float` for real money. `0.1 + 0.2` is not exactly `0.3`. Two safe approaches:

1. Store **paise** (whole numbers) and convert only for display.
2. Use `decimal.Decimal`.

We will use whole paise, so every calculation is exact.

```python
print(0.1 + 0.2 == 0.3)
print(10 + 20 == 30)

def rupees(paise):
    return f"Rs {paise // 100:,}.{paise % 100:02d}"

print(rupees(123456))
print(rupees(5))
print(rupees(100000000))
```

```output
False
True
Rs 1,234.56
Rs 0.05
Rs 1,000,000.00
```

## Design

| Class | Role |
|-------|------|
| `InsufficientFundsError`, `InvalidAmountError` | custom exceptions (both inherit from `BankError`) |
| `Account` | base class: number, owner, balance, history; deposit, withdraw |
| `SavingsAccount(Account)` | minimum balance; `add_interest` |
| `CurrentAccount(Account)` | overdraft limit |
| `Bank` | opens accounts, finds them, transfers between them |

## Step 1: exceptions and the base class

```python
class BankError(Exception):
    pass

class InvalidAmountError(BankError):
    pass

class InsufficientFundsError(BankError):
    pass

def rupees(paise):
    sign = "-" if paise < 0 else ""
    paise = abs(paise)
    return f"{sign}Rs {paise // 100:,}.{paise % 100:02d}"

class Account:
    def __init__(self, number, owner, opening=0):
        self.number = number
        self.owner = owner
        self._balance = 0
        self._history = []
        if opening:
            self.deposit(opening, "Opening deposit")

    @property
    def balance(self):
        return self._balance

    def _check_amount(self, amount):
        if not isinstance(amount, int) or amount <= 0:
            raise InvalidAmountError("amount must be a positive whole number of paise")

    def _available(self):
        return self._balance          # subclasses may change this

    def deposit(self, amount, note="Deposit"):
        self._check_amount(amount)
        self._balance += amount
        self._history.append((note, amount, self._balance))

    def withdraw(self, amount, note="Withdrawal"):
        self._check_amount(amount)
        if amount > self._available():
            raise InsufficientFundsError(
                f"cannot withdraw {rupees(amount)}; available {rupees(self._available())}")
        self._balance -= amount
        self._history.append((note, -amount, self._balance))

    def statement(self):
        lines = [f"Account {self.number} - {self.owner}", f"{'Description':<18}{'Amount':>14}{'Balance':>14}"]
        for note, amount, balance in self._history:
            lines.append(f"{note:<18}{rupees(amount):>14}{rupees(balance):>14}")
        return "\n".join(lines)

acc = Account("AC001", "Asha", opening=100000)
acc.deposit(25050)
acc.withdraw(40000)
print(acc.statement())
for bad in (0, -5, 12.5):
    try:
        acc.deposit(bad)
    except InvalidAmountError as e:
        print("Rejected:", e)
try:
    acc.withdraw(10_000_000)
except InsufficientFundsError as e:
    print("Refused:", e)
```

```output
Account AC001 - Asha
Description               Amount       Balance
Opening deposit      Rs 1,000.00   Rs 1,000.00
Deposit                Rs 250.50   Rs 1,250.50
Withdrawal            -Rs 400.00     Rs 850.50
Rejected: amount must be a positive whole number of paise
Rejected: amount must be a positive whole number of paise
Rejected: amount must be a positive whole number of paise
Refused: cannot withdraw Rs 100,000.00; available Rs 850.50
```

## Step 2: account types through inheritance

```python
class BankError(Exception):
    pass

class InvalidAmountError(BankError):
    pass

class InsufficientFundsError(BankError):
    pass

class Account:
    def __init__(self, number, owner, opening=0):
        self.number, self.owner = number, owner
        self._balance = 0
        self._history = []
        if opening:
            self.deposit(opening, "Opening deposit")

    @property
    def balance(self):
        return self._balance

    def _available(self):
        return self._balance

    def deposit(self, amount, note="Deposit"):
        if amount <= 0:
            raise InvalidAmountError("amount must be positive")
        self._balance += amount
        self._history.append((note, amount, self._balance))

    def withdraw(self, amount, note="Withdrawal"):
        if amount <= 0:
            raise InvalidAmountError("amount must be positive")
        if amount > self._available():
            raise InsufficientFundsError("insufficient funds")
        self._balance -= amount
        self._history.append((note, -amount, self._balance))

class SavingsAccount(Account):
    MIN_BALANCE = 50000            # Rs 500.00 in paise

    def __init__(self, number, owner, opening=0, annual_rate=4):
        super().__init__(number, owner, opening)
        self.annual_rate = annual_rate      # percent

    def _available(self):
        return max(0, self._balance - self.MIN_BALANCE)

    def add_interest(self):
        interest = self._balance * self.annual_rate // 100 // 12   # one month, whole paise
        if interest:
            self.deposit(interest, "Monthly interest")
        return interest

class CurrentAccount(Account):
    def __init__(self, number, owner, opening=0, overdraft=200000):
        super().__init__(number, owner, opening)
        self.overdraft = overdraft

    def _available(self):
        return self._balance + self.overdraft

sav = SavingsAccount("SB001", "Asha", opening=1200000)
print(sav.add_interest())
print(sav.balance)
sav.withdraw(1000000)
print(sav.balance)
try:
    sav.withdraw(200000)
except InsufficientFundsError as e:
    print("Savings refused:", e)

cur = CurrentAccount("CA001", "Ravi", opening=100000)
cur.withdraw(250000)
print(cur.balance)
try:
    cur.withdraw(100000)
except InsufficientFundsError as e:
    print("Current refused:", e)
```

```output
4000
1204000
204000
Savings refused: insufficient funds
-150000
Current refused: insufficient funds
```

Notice how little each subclass needs: they override just `_available()` (how much may be withdrawn) and add their own extras. The base class `withdraw` does all the checking. That is the payoff of good inheritance.

## Step 3: the `Bank` and safe transfers

A **transfer** is two steps: withdraw from A, deposit to B. If the second step failed after the first, money would vanish. The design rule: do the step most likely to fail *first*, and undo if something goes wrong later.

```python
class BankError(Exception):
    pass

class InvalidAmountError(BankError):
    pass

class InsufficientFundsError(BankError):
    pass

class Account:
    def __init__(self, number, owner, opening=0):
        self.number, self.owner, self._balance = number, owner, opening
        self.log = []
    @property
    def balance(self):
        return self._balance
    def deposit(self, amount, note="Deposit"):
        if amount <= 0:
            raise InvalidAmountError("amount must be positive")
        self._balance += amount
        self.log.append(note)
    def withdraw(self, amount, note="Withdrawal"):
        if amount <= 0:
            raise InvalidAmountError("amount must be positive")
        if amount > self._balance:
            raise InsufficientFundsError(f"{self.number}: insufficient funds")
        self._balance -= amount
        self.log.append(note)

class Bank:
    def __init__(self):
        self.accounts = {}
        self._next = 1

    def open_account(self, owner, opening=0):
        number = f"AC{self._next:03d}"
        self._next += 1
        self.accounts[number] = Account(number, owner, opening)
        return number

    def get(self, number):
        try:
            return self.accounts[number]
        except KeyError:
            raise BankError(f"no account {number}") from None

    def transfer(self, source, target, amount):
        src, dst = self.get(source), self.get(target)
        if src is dst:
            raise BankError("cannot transfer to the same account")
        src.withdraw(amount, f"Transfer to {target}")
        try:
            dst.deposit(amount, f"Transfer from {source}")
        except BankError:
            src.deposit(amount, "Transfer reversed")
            raise

    def total_deposits(self):
        return sum(a.balance for a in self.accounts.values())

bank = Bank()
a = bank.open_account("Asha", 100000)
b = bank.open_account("Ravi", 50000)
print(a, b)
bank.transfer(a, b, 30000)
print(bank.get(a).balance, bank.get(b).balance)
for args in [(a, b, 999999), (a, "AC999", 100), (a, a, 100), (a, b, -5)]:
    try:
        bank.transfer(*args)
    except BankError as e:
        print("Refused:", e)
print(bank.get(a).balance, bank.get(b).balance)
print(bank.total_deposits())
```

```output
AC001 AC002
70000 80000
Refused: AC001: insufficient funds
Refused: no account AC999
Refused: cannot transfer to the same account
Refused: amount must be positive
70000 80000
150000
```

The final total is still exactly what we started with (150000): a transfer never creates or destroys money. That invariant is a great thing to test.

## Step 4: an ATM session

```python stdin="1234|balance|deposit 500|withdraw 200|withdraw 5000|withdraw 30|quit"
balance = 1000
pin = "1234"

print("Enter PIN")
attempt = input().strip()
if attempt != pin:
    print("Wrong PIN")
else:
    print("Welcome")
    while True:
        parts = input().split()
        if not parts:
            continue
        action = parts[0]
        try:
            if action == "balance":
                print(f"Balance: {balance}")
            elif action in ("deposit", "withdraw"):
                amount = int(parts[1])
                if amount <= 0:
                    raise ValueError("amount must be positive")
                if action == "withdraw":
                    if amount % 100 != 0:
                        raise ValueError("ATM dispenses multiples of 100 only")
                    if amount > balance:
                        raise ValueError("insufficient funds")
                    balance -= amount
                else:
                    balance += amount
                print(f"{action.title()} of {amount} done. Balance: {balance}")
            elif action == "quit":
                print("Thank you. Goodbye!")
                break
            else:
                print("Unknown action")
        except (ValueError, IndexError) as e:
            print("Error:", e)
```

```output
Enter PIN
Welcome
Balance: 1000
Deposit of 500 done. Balance: 1500
Withdraw of 200 done. Balance: 1300
Error: insufficient funds
Error: ATM dispenses multiples of 100 only
Thank you. Goodbye!
```

## Testing invariants

The most important banking rule: total money is conserved. Test it with many random transfers.

```python
import random

random.seed(4)
balances = [1000, 2500, 400, 9000]
total_before = sum(balances)

for _ in range(500):
    a, b = random.sample(range(4), 2)
    amount = random.randint(1, 500)
    if balances[a] >= amount:
        balances[a] -= amount
        balances[b] += amount

assert sum(balances) == total_before
assert all(b >= 0 for b in balances)
print("money conserved:", sum(balances) == total_before)
```

```output
money conserved: True
```

## Ideas to extend it

1. **Passwords/PINs** stored as hashes (`hashlib`), with a lock after three wrong attempts.
2. **Fixed deposits** with maturity dates.
3. **Save the bank** to JSON and reload it.
4. **Monthly statements** with `datetime` timestamps.
5. **Fees**: a charge for too many withdrawals per month.
6. Use `decimal.Decimal` instead of paise.

## Common Mistakes

**1. Using floats for money.** Use integers (paise) or `Decimal`.

**2. Non-atomic transfers.** If step two can fail, plan how to undo step one.

**3. Letting subclasses skip the checks.** Override small hooks (like `_available`) instead of copying `withdraw`.

**4. Trusting user input.** Reject zero, negative and non-numeric amounts.

```python
from decimal import Decimal

print(Decimal("0.1") + Decimal("0.2"))
print(Decimal("0.1") + Decimal("0.2") == Decimal("0.3"))
```

```output
0.3
True
```

## Try It Yourself

Write `compound(principal, rate, years)` that returns the balance in whole paise after yearly compounding at `rate` percent, using integer arithmetic (round down each year).

```python-try
def compound(principal, rate, years):
    balance = principal
    for _ in range(years):
        balance += balance * rate // 100
    return balance

assert compound(100000, 10, 0) == 100000
assert compound(100000, 10, 1) == 110000
assert compound(100000, 10, 2) == 121000
assert compound(1000, 5, 3) == 1157
print(compound(100000, 10, 3))
```

**Challenge:** Add an `OverdraftFee` to `CurrentAccount` that charges 500 paise every time the balance goes below zero.

## Recap

- Represent money as whole paise (or `Decimal`), never `float`.
- Put shared rules in a base class and let subclasses override small hooks (`_available`, `add_interest`).
- Use a custom exception hierarchy so callers can catch broadly (`BankError`) or narrowly.
- Multi-step operations (transfers) must not lose money: check first, act, and undo on failure.
- Test invariants ("total money never changes") as well as individual cases.

**Next up:** the final project, a **number-guessing game** and your next steps.

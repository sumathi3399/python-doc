# Part 2: Control Flow - Assignments

## Assignment Guidelines

- **Estimated time:** 8-12 hours total
- **Prerequisites:** Complete [README.md](README.md); Part 1 knowledge assumed
- **Submission:** Python files with instructions to run; optional `sample_data/` for test inputs
- **Rules:** Use only Part 1-2 concepts (no functions required but allowed; no OOP)

---

## Assignment 1: Text-Based Survival Simulation

### Scenario

Build "Last Outpost" — a terminal survival game where the player manages resources over a series of days. Every decision uses control flow: conditionals, loops, and loop control (`break`, `continue`, `pass`).

### Requirements

Implement a game with:

1. **Game state variables:** health (0-100), food, water, day count, inventory list, game_over flag

2. **Main game loop:** Each day presents 3 random events from a pool of at least 8 events. Events modify resources based on player choices

3. **Daily menu** (use `while` until valid input):
   - Explore (risk/reward — may lose health or gain food)
   - Rest (restore health, consume food/water)
   - Craft (requires inventory items; uses nested `if`)
   - Trade at outpost (spend resources)
   - View status
   - Skip day (`continue` to next iteration without processing extra events)

4. **Win/lose conditions:**
   - Lose: health ≤ 0 or food ≤ 0 for 2 consecutive days
   - Win: survive 30 days with health ≥ 50
   - Use `break` to exit main loop on win/lose

5. **Nested structures:**
   - Event handler with `if/elif/else` inside the day loop
   - At least one `for` loop over inventory with `continue` to skip unusable items
   - Loop `else` clause: e.g., search inventory for an item; `else` prints "item not found"

6. **Advanced loop techniques:**
   - Use `enumerate()` when displaying numbered inventory
   - Use `zip()` to display paired resources (e.g., food/water amounts side by side)
   - Use `range()` for countdown timers during risky actions

7. **Input validation loop:** Keep asking until player enters a valid menu choice (1-6)

### Technical Specifications

Must demonstrate:

- `if` / `elif` / `else` with compound conditions (`and`, `or`, `not`)
- `for` and `while` loops
- `break`, `continue`, `pass`
- Nested loops (max 3 levels)
- `enumerate()`, `zip()`, `range()`
- Loop `else` clause
- Ternary expressions where readable
- Chained comparisons (e.g., `0 < health <= 100`)

### Acceptance Criteria

- [ ] Game is playable start-to-finish in the terminal
- [ ] At least 8 distinct random events
- [ ] All five loop control keywords used meaningfully
- [ ] `enumerate` and `zip` used at least once each
- [ ] Loop `else` used at least once
- [ ] Invalid input does not crash the game
- [ ] Win and lose endings display different messages with final stats

### Bonus Challenges

- Add difficulty levels (easy/normal/hard) affecting event probabilities using nested conditionals
- Implement a simple combat sub-loop with `while` and `break` on flee or victory
- Save high score (longest survival) across runs using a variable that persists in the outer `while True` replay loop

### Hints

- Use `import random` for events
- Structure event data as tuples: `(description, choice_a_effect, choice_b_effect)`
- A `pass` can sit in an unfinished "coming soon" branch to show you know the keyword
- Track "consecutive zero food days" with a counter incremented in `else` of a food check

---

## Assignment 2: Academic Analytics Engine

### Scenario

A school administrator needs a terminal tool to analyze student records, compute statistics, and generate reports. This assignment stress-tests loops and conditionals on structured data.

### Requirements

Process a hardcoded dataset of at least 15 students. Each student has: name, roll number, grades in 5 subjects, attendance percentage.

Implement a menu system:

1. **Class statistics:** highest/lowest/average per subject; overall class average
2. **Grade assignment:** Assign letter grades (A/B/C/D/F) using `if/elif` chains based on average score
3. **Honor roll:** List students with average ≥ 85 AND attendance ≥ 90% (compound condition)
4. **At-risk report:** Students with average < 50 OR attendance < 75%
5. **Prime roll numbers:** Print students whose roll number is prime (implement prime check with loop)
6. **Pattern report:** Print a histogram of grade distribution using nested loops:

```
A: **** (4)
B: ****** (6)
C: *** (3)
```

7. **Search:** Find student by roll number using a loop with `break` when found; use `else` to print "not found"
8. **Fibonacci bonus menu:** Print first N Fibonacci numbers where N is user input

### Technical Specifications

- Nested `for` loops for 2D grade processing
- `while` loops for input validation and prime checking
- `continue` to skip students with incomplete data (simulate 1-2 entries with missing grades as `-1`)
- Sorting: implement bubble sort OR selection sort using loops (no `sorted()` for the honors ranking feature — optional use elsewhere)
- Multiplication table generator for any number 1-20

### Acceptance Criteria

- [ ] All 8 menu features work correctly
- [ ] Prime checker correctly identifies primes 1-100
- [ ] Histogram counts match actual grade distribution
- [ ] Search uses for/else pattern correctly
- [ ] Class statistics match hand-calculated values for sample data
- [ ] No off-by-one errors in loops (document edge cases in comments)

### Bonus Challenges

- Matrix operations: store grades as nested lists; compute row averages and column averages
- Password-style validation loop: admin must enter a 4-digit PIN with max 3 attempts before lockout (`break`)
- Palindrome checker for student names (optional fun feature)

### Hints

- Store students as list of dicts if comfortable, or parallel lists from Part 1 style
- Prime algorithm: `for i in range(2, int(n**0.5)+1)` — or simple trial division
- Build histogram with a string multiplied by count: `"*" * count`
- Use `continue` when `grade == -1` to skip incomplete records

---

## Assignment 3: Interactive ATM & Billing System

### Scenario

Combine an ATM simulation with a retail billing subsystem in one application. The user switches between modes from a top-level menu. Tests nested control structures and real-world validation flows.

### Requirements

**ATM Mode:**
- Starting balance: $1000
- Operations: balance, deposit, withdraw, transfer (to a second hardcoded account), mini-statement
- Withdrawal rules: multiples of $20 only; max $500 per transaction; insufficient funds handling
- Transaction history (last 10) stored in a list
- `while` loop until user exits ATM mode

**Billing Mode:**
- Add items from a catalog (at least 10 products with price)
- Apply discount tiers using `if/elif`:
  - Total ≥ $500: 15% off
  - Total ≥ $200: 10% off
  - Total ≥ $100: 5% off
- Tax calculation (8%)
- Print itemized bill with aligned columns
- `for` loop over cart; `continue` to skip out-of-stock items (mark 2 products out of stock)

**Shared:**
- Top-level menu switches between ATM, Billing, and Exit
- All monetary values formatted to 2 decimal places
- At least 3 levels of nesting in one validation block (e.g., withdraw → amount valid → balance sufficient → daily limit)

### Technical Specifications

- `if/elif/else` decision trees
- `while` and `for` loops
- `break`/`continue`/`pass`
- Nested `if` and nested loops
- Input validation loops
- Running totals and counters in loops

### Acceptance Criteria

- [ ] Both modes fully functional independently
- [ ] Withdrawal rejects invalid amounts with specific error messages
- [ ] Billing discounts apply correctly at each tier boundary (test $99.99 vs $100.00)
- [ ] Transaction history shows last 10 entries only (use slicing)
- [ ] Three-level nested validation demonstrated
- [ ] Program never crashes on invalid numeric input

### Bonus Challenges

- ATM PIN entry with 3-attempt lockout and `break`
- Combine modes: "pay bill from ATM balance" with confirmation prompt
- Generate a simple receipt number using day counter and zero-padded format in a loop

### Hints

- Use a flag variable `locked = False` for ATM lockout
- Test boundary values for discounts explicitly
- Mini-statement: `for i, tx in enumerate(history[-10:], 1):`

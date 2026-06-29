# Part 1: Python Fundamentals - Assignments

## Assignment Guidelines

- **Estimated time:** 6-10 hours total
- **Prerequisites:** Complete all sections in [README.md](README.md) before starting
- **Submission:** One Python file or small package per assignment with a `README` explaining how to run it
- **Rules:** Use only concepts from Part 1 (no functions beyond basic `print`/`input`, no classes, no imports except `sys` and `math` if needed)

---

## Assignment 1: Python Runtime Inspector

### Scenario

You are building an internal training tool for new developers. The tool inspects Python values at runtime and explains what is happening under the hood — types, mutability, identity, and memory behavior.

### Requirements

Build a command-line program that:

1. Accepts user input in a loop until the user types `quit`
2. Supports these commands:
   - `inspect <value>` — analyze a literal or expression the user provides (e.g. `42`, `"hello"`, `[1,2,3]`)
   - `compare <a> <b>` — compare two values using `==` and `is`, and explain the difference
   - `mutate <type>` — demonstrate mutability vs immutability for `int`, `str`, `list`, and `tuple`
   - `scope` — demonstrate local vs global scope with a small embedded example
   - `convert <value> <target_type>` — convert between `int`, `float`, `str`, and `bool` with error handling via basic checks (no try/except yet — use `if` checks or note that invalid conversion should be handled in Assignment 2's part if needed; actually Part 1 doesn't have exception handling - use conditional checks)

3. For each `inspect` command, print a structured report:
   - Value
   - Type (`type()`)
   - Memory address (`id()`)
   - Mutable or immutable classification
   - Whether the value is truthy or falsy

4. Include a `demo` command that runs a scripted walkthrough showing:
   - Integer interning (small integers sharing `id`)
   - String immutability (reassignment creates new object)
   - List mutability (in-place modification keeps same `id`)

### Technical Specifications

You must demonstrate understanding of:

- Python execution model (interpreted, line-by-line behavior)
- Variables as references to objects
- Built-in types: `int`, `float`, `str`, `bool`, `None`
- Operators: arithmetic, comparison, logical, assignment
- `is` vs `==`
- Mutable vs immutable types
- `id()` and object identity
- Global vs local scope
- Type conversion rules
- Truthiness of values

### Acceptance Criteria

- [ ] All commands work without crashing on valid input
- [ ] `inspect` correctly classifies at least 8 different value types/examples
- [ ] `compare` explains when `==` is True but `is` is False (and vice versa where applicable)
- [ ] `mutate` clearly shows that lists can change in-place but strings cannot
- [ ] `demo` output includes `id()` values proving interning or identity behavior
- [ ] Code uses meaningful variable names and comments explaining *why*, not just *what*
- [ ] Program handles invalid commands gracefully with a helpful message

### Bonus Challenges

- Add a `philosophy` command that prints 5 Zen of Python principles and maps each to an example in your code
- Add support for inspecting compound expressions entered as strings (e.g. `inspect 3 + 4` using `eval` with a restricted namespace — document security implications)
- Track and display how many objects were "created" during a session by comparing `id()` before/after operations

### Hints

- Use `type(value).__name__` for readable type names
- A dict mapping types to `"mutable"` / `"immutable"` keeps classification logic clean
- For the `demo` command, print before/after `id()` side by side
- Remember: `None` is falsy; empty string `""` is falsy; `0` is falsy

---

## Assignment 2: Personal Finance Console Application

### Scenario

Build a personal finance tracker that runs entirely in the terminal. Users record income and expenses, view summaries, and convert amounts between currencies. This assignment integrates variables, operators, data types, and formatted output.

### Requirements

Build a menu-driven application with:

1. **Main menu** (loops until Exit):
   - Add income entry (amount, category, description)
   - Add expense entry (amount, category, description)
   - View all transactions
   - View summary (total income, total expenses, net balance)
   - Currency converter
   - Unit converter (km↔miles, °C↔°F, kg↔lbs)
   - Exit

2. **Transaction storage:** Use lists to store transactions. Each transaction is represented using a consistent structure (e.g., tuple or parallel lists — no dicts required but allowed)

3. **Summary calculations:**
   - Subtotal by category
   - Percentage of total expenses per category (use `/` and `*` carefully; handle division when total is zero)
   - Running balance after each transaction when viewing history

4. **Currency converter:** Support at least 3 hardcoded exchange rates (e.g., USD, EUR, INR). User selects from → to and enters amount

5. **Formatted receipt-style output** for summaries:

```
=================================
       FINANCE SUMMARY
=================================
Total Income:     $5,250.00
Total Expenses:   $3,180.50
Net Balance:      $2,069.50
---------------------------------
Top Expense Categories:
  Food:           $890.00 (28.0%)
  Transport:      $420.00 (13.2%)
=================================
```

6. **Input validation** using conditionals only:
   - Reject negative amounts for expenses/income
   - Reject non-numeric input with a clear message (check with string methods or manual parsing)

### Technical Specifications

You must use:

- Variables and dynamic typing
- All arithmetic operators (`+`, `-`, `*`, `/`, `//`, `%`, `**`)
- Comparison and logical operators
- String formatting (f-strings preferred)
- Type conversion (`int()`, `float()`, `str()`)
- Lists (and optionally tuples for immutable config like exchange rates)
- Boolean logic for menu validation
- Operator precedence in calculations (document one complex expression in comments)

### Acceptance Criteria

- [ ] Application runs in a continuous loop with a clear menu
- [ ] At least 5 transactions can be added and displayed correctly
- [ ] Summary math is accurate to 2 decimal places
- [ ] Currency and unit converters produce correct results for known test cases
- [ ] Invalid menu choices and invalid numeric input do not crash the program
- [ ] At least one use of tuple unpacking or chained comparison
- [ ] Code demonstrates awareness of float precision (e.g., round money to 2 decimals)

### Bonus Challenges

- Add a "savings goal" feature: user sets a target; show progress bar using string repetition (`"=" * n`)
- Implement transaction editing by index without using functions — use indexing and reassignment
- Add a `profile` section storing user name, currency preference, and birth year (calculate age from current year constant)

### Hints

- Store exchange rates in a nested structure you can index by currency code
- Use `round(value, 2)` for currency display
- When validating numeric input, try converting and check with `isdigit()` or exception-free parsing
- Keep menu logic flat; avoid deeply nested `if` blocks by using `elif` chains

---

## Assignment 3: Type System Deep-Dive Workbook (Written + Code)

### Scenario

You are preparing study notes for a technical interview. Combine short written explanations with runnable code snippets in a single script that serves as an executable workbook.

### Requirements

Create `type_system_workbook.py` that:

1. **Section A — Identity & Equality:** 5 coded examples, each printing explanation + output for:
   - `==` vs `is` with integers
   - `==` vs `is` with strings
   - `==` vs `is` with lists
   - Checking for `None` correctly
   - Aliasing (two variables, one object)

2. **Section B — Mutability:** 3 examples showing:
   - Modifying a list through one variable affects another reference
   - Reassigning a string does not modify the original binding's target for another variable
   - Attempting to modify a tuple (show what happens)

3. **Section C — Type Coercion:** Table-driven tests:
   - `int("42")`, `float("3.14")`, `str(100)`, `bool(0)`, `bool("")`, `bool("hello")`
   - Print each input, output, and output type

4. **Section D — Scope:** One example with nested blocks showing local shadows global (use only Part 1 knowledge)

5. **Section E — Written answers** as multi-line strings printed to console:
   - Why is Python described as "dynamically typed"?
   - What is the difference between compilation and interpretation in Python's model?
   - Name three beginner mistakes from Part 1 and how to avoid them

### Technical Specifications

- Cover all Part 1 topics: philosophy, execution model, memory references, data types, operators, type system, scope
- Each section must run when the script executes (use `print` headers like `"=== Section A ==="`)
- No user input required — fully automated output

### Acceptance Criteria

- [ ] Script runs top-to-bottom without errors
- [ ] At least 15 distinct code demonstrations
- [ ] Written sections answer all three questions with 2+ sentences each
- [ ] Output is readable and labeled
- [ ] Comments connect each example to the concept it demonstrates

### Bonus Challenges

- Add a self-check at the end: script verifies its own expected outputs for 3 key assertions
- Include a "common mistakes" section with wrong code commented out and correct version active

### Hints

- Structure with clear `print("\n" + "="*50)` section dividers
- For list aliasing: `a = [1,2]; b = a; a.append(3); print(b)` tells the story
- For `None`: always use `is None`, never `== None`

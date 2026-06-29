# Part 5: Collections & Data Structures - Assignments

## Assignment Guidelines

- **Estimated time:** 12-16 hours total
- **Prerequisites:** Parts 1-4 complete
- **Submission:** Python modules with benchmark output and sample data files
- **Rules:** Choose appropriate data structures deliberately; document time complexity of key operations

---

## Assignment 1: Log Analytics & Performance Benchmark Suite

### Scenario

You receive web server log files and must parse, analyze, and report on them efficiently. Wrong data structure choices will make the tool slow on large inputs — justify every choice.

### Requirements

**Input:** Provide or generate a sample log file (1000+ lines) with format:
```
2024-01-15 10:23:45 GET /api/users 200 45ms 192.168.1.1
```

**Implement:**

1. **Parser** using string operations → store records in appropriate structures

2. **Analyses (each a function):**
   - Unique IP addresses → **set**
   - Request count per endpoint → **dict** or **Counter**
   - Top 10 endpoints by traffic → **heapq.nlargest**
   - Status code distribution → **Counter**
   - Requests per hour → **defaultdict**
   - Sliding window: requests in last N minutes per IP → **deque** per IP (or single deque for global rate)

3. **Inverted index:** word → set of line numbers where path contains word → **defaultdict(set)**

4. **LRU Cache (manual):** `OrderedDict`-based cache for parsed log lines (max 100 entries); demonstrate hit/miss stats

5. **Benchmark module:**
   - Compare list vs set membership for 10K IPs
   - Compare dict vs linear search for 10K endpoint lookups
   - Print timing table for 1K, 10K, 100K sizes

6. **Report generator:** formatted summary to console and optional output file

### Technical Specifications

- Lists, tuples, sets, dicts — when and why
- `collections.defaultdict`, `Counter`, `namedtuple` or `NamedTuple` for LogRecord
- `deque` for sliding windows and LRU
- `heapq` for top-K queries
- `OrderedDict` for LRU cache
- Time complexity awareness: O(1) vs O(n) lookups documented in comments

### Acceptance Criteria

- [ ] Parses 1000+ line file without error
- [ ] Top 10 endpoints correct on hand-verified sample
- [ ] LRU cache evicts oldest when full
- [ ] Benchmark shows set faster than list for membership at 10K+
- [ ] Inverted index returns correct line numbers for test queries
- [ ] Each analysis function documents Big-O in docstring

### Bonus Challenges

- `frozen set` of blocked IPs; O(1) check during parse
- `chain`/`groupby` from itertools for grouping by status code
- Memory comparison: size of list vs set for same elements (conceptual estimate)

### Hints

- LogRecord: `namedtuple('LogRecord', ['timestamp', 'method', 'path', 'status', 'duration', 'ip'])`
- Counter.most_common(10) is acceptable alongside heapq exercise
- LRU: on access, `move_to_end(key)`; evict `popitem(last=False)`

---

## Assignment 2: Inventory & Supply Chain Manager

### Scenario

A warehouse tracks products, stock levels, suppliers, and purchase orders. Operations must be fast for lookups and safe for concurrent-style updates (logical consistency).

### Requirements

**Data structures:**

1. **Product catalog:** `dict[sku -> Product]` where Product is `namedtuple` or small dataclass
2. **Categories:** `dict[category -> set of skus]` for many-to-many via sets
3. **Stock levels:** `dict[sku -> int]`
4. **Low stock alert queue:** `heapq` min-heap by stock level (tie-break by sku)
5. **Order history per sku:** `defaultdict(deque)` — last 20 stock changes
6. **Supplier index:** `dict[supplier_name -> list of skus]`
7. **Active purchase orders:** `OrderedDict` preserving insertion order

**Operations:**
- `add_product`, `restock`, `sell`, `transfer_between_warehouses`
- `get_low_stock(threshold)` using heap
- `products_by_category(category)` O(1) category lookup
- `find_products(predicate)` filter across catalog
- `merge_inventories(inv1, inv2)` combining two dicts without duplicating skus incorrectly

**Set operations:**
- `discontinued_skus` set ∩ `active_skus` → detect data errors
- `exclusive_to_supplier(supplier)` — skus only from that supplier

**Tuple usage:**
- Immutable `PricePoint(sku, price, effective_date)` stored in sorted list by date
- Return multiple values as tuples from `sell()`: `(success, new_level, message)`

### Technical Specifications

- All core collections + advanced (`defaultdict`, `Counter`, `deque`, `heapq`, `OrderedDict`, `namedtuple`)
- Choosing right structure for each operation
- Set operations: union, intersection, difference
- Nested structures: dict of sets, dict of deques

### Acceptance Criteria

- [ ] 50+ products manageable via CLI menu
- [ ] Low stock heap returns correct ordering
- [ ] Sell fails gracefully when insufficient stock (no negative inventory)
- [ ] Order history deque never exceeds 20 entries
- [ ] Set intersection finds conflicting skus
- [ ] Category browse is efficient (no full scan if using index)

### Bonus Challenges

- Multi-warehouse: `dict[warehouse_id -> dict[sku -> qty]]`
- `bisect` on sorted price history for "price at date" queries
- Export/import inventory as JSON using dict comprehensions

### Hints

- Heap entries: `(stock_level, sku)` for min-heap low stock
- On restock: push new heap entry; lazy deletion acceptable for assignment
- `deque(maxlen=20)` auto-evicts old history

---

## Assignment 3: Text Corpus Analyzer

### Scenario

Build a text analysis engine for a document corpus (3+ text files). Demonstrates nested collections and algorithmic choices.

### Requirements

1. **Load corpus** into `list[str]` (lines or documents)

2. **Word frequency:** `Counter` across corpus; exclude stop words (provide `set` of ~20 stop words)

3. **Bigram/trigram analysis:** `defaultdict(Counter)` or nested dict

4. **Document-term matrix:** `dict[doc_id -> Counter]` for TF analysis

5. **Unique vocabulary:** `set` union across documents; `frozenset` for immutable snapshot

6. **Find documents containing all query words:** set intersection of per-word doc sets

7. **Longest word per document:** `max(words, key=len)` with tie handling via list

8. **Flatten nested table data:** recursive function flattening `list` of `list` of `tuple` rows to flat records

9. **Performance report:** compare scanning all docs vs indexed lookup for keyword search

### Technical Specifications

- Lists, tuples, sets, dicts in combination
- `Counter`, `defaultdict`
- Nested list/dict comprehension
- Time complexity section in README

### Acceptance Criteria

- [ ] Word frequency matches manual count on small sample
- [ ] Intersection search returns only docs with ALL query terms
- [ ] Bigram counter produces expected pairs on test sentence
- [ ] Flatten handles 3+ nesting levels
- [ ] README explains structure choices with Big-O

### Bonus Challenges

- Implement inverted index with `defaultdict(set)` for O(1) word lookup per doc
- Jaccard similarity between two documents using sets
- `heapq` for top 20 words across entire corpus

### Hints

- Tokenize with `str.split()` and `str.lower()`; strip punctuation simply
- Inverted index: for each word, add doc_id to `index[word]`
- Intersection: `set.intersection(*[index[w] for w in query_words])`

# CS 499 Milestone Three Course Planner

This package contains the original `ProjectTwo.cpp` from CS 300 and the enhanced
`ProjectTwo_Enhanced.cpp`. The original uses a binary search tree to list and
find courses. The enhanced program preserves those functions and adds a
prerequisite graph and a valid course order using Kahn's topological sort.

## Build and run

From this folder with a C++17 compiler:

```sh
g++ -std=c++17 -Wall -Wextra -Wpedantic -O2 ProjectTwo_Enhanced.cpp -o course_planner
./course_planner
```

Choose option 1 and enter `CS 300 ABCU_Advising_Program_Input.csv`. Option 2
prints an alphanumeric list; option 3 searches for one course; option 4 prints
a prerequisite-respecting order. This order is not a term-by-term plan: it does
not account for course offerings, credit limits, or concurrent enrollment.

The provided CSV uses plain comma-delimited fields and empty trailing columns.
Quoted commas in titles are outside the format of this course input. Invalid
records, unknown or repeated prerequisites, duplicate course numbers, and
cycles are rejected. A failed reload leaves previously loaded data intact.

## Run the checks

```sh
python3 test_planner.py
```

The checks exercise the supplied eight-course file, prerequisite ordering,
case-insensitive search, validation failures, cycle detection, and safe reload.
The code compiles without warnings using the command above. The graph build
and topological sort use O(V + E) expected time with hash-based lookups, where
V is the number of courses and E is the number of prerequisites. The separate
binary search tree retains the original sorted-list behavior, but can become
unbalanced and take O(V^2) total insertion time for adversarial input order.

## Files

- `ProjectTwo.cpp` — unmodified original CS 300 source.
- `ProjectTwo_Enhanced.cpp` — CS 499 enhancement.
- `CS 300 ABCU_Advising_Program_Input.csv` — supplied sample data.
- `test_planner.py` — integration checks.

AI use acknowledgment: ChatGPT assisted with drafting and reviewing the
enhanced code, tests, documentation, and narrative. I reviewed the design and
test results before submission.

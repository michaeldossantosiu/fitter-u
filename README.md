# Fitter-U Habit Tracker

A Python command-line application for tracking daily and weekly habits with streak analytics.

**Author:** Michael Dos Santos
**Student ID:** 92108332
**Course:** DLBDSOOFPP01 - Object-Oriented and Functional Programming with Python

## Project Overview

This habit tracking application helps users build consistency by providing measurable accountability through habit monitoring. Users can define habits with daily or weekly periodicities, log completions, and analyze their performance through streak calculations.

## Requirements

- Python 3.7+
- pytest (for running tests)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/michaeldossantosiu/fitter-u.git
cd fitter-u
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Quick Start

1. Seed the database with sample data:
```bash
python seed.py
```

2. Run the application:
```bash
python cli.py
```

## Predefined Habits (Fixture Data)

The seed script populates the database with 5 predefined habits and 4 weeks of tracking data:

| Habit | Periodicity | Description |
|-------|-------------|-------------|
| Read 20 minutes | Daily | Reading habit with varied completion pattern |
| Walk 10 minutes | Daily | Exercise habit with perfect 28-day streak |
| Meditate | Daily | Mindfulness habit with gaps |
| Call family | Weekly | Communication habit with 4-week streak |
| Review goals | Weekly | Reflection habit with one missed week |

## How to Use

### Creating a New Habit

1. Run `python cli.py`
2. Select option `1` (Create habit)
3. Enter the habit name
4. Select periodicity: `1` for daily, `2` for weekly
5. Enter target completions per period (default: 1)

### Checking Off a Habit

1. Run `python cli.py`
2. Select option `3` (Check-off habit)
3. Enter the habit ID to mark as completed
4. The completion is logged with the current timestamp

### Viewing Analytics

1. Run `python cli.py`
2. Select option `5` (View analytics)
3. Choose from:
   - List all tracked habits
   - List habits by periodicity (daily/weekly)
   - View longest streak across all habits
   - View longest streak for a specific habit

## CLI Menu Structure

```
Main Menu:
1. Create habit
2. List habits
3. Check-off habit
4. Delete habit
5. View analytics
   ├── 1. List all tracked habits
   ├── 2. List habits by periodicity
   ├── 3. Longest streak (all habits)
   ├── 4. Longest streak (specific habit)
   └── 5. Back to main menu
6. Exit
```

## Running Tests

Run the complete test suite:
```bash
pytest tests/ -v
```

Run individual test modules:
```bash
pytest tests/test_habit.py -v      # Habit class tests
pytest tests/test_storage.py -v    # Database operation tests
pytest tests/test_analytics.py -v  # Analytics and streak tests
```

**Test Coverage: 40 tests across 3 modules**

| Test File | Tests | Coverage Area |
|-----------|-------|---------------|
| `test_habit.py` | 9 | Domain model validation |
| `test_storage.py` | 13 | CRUD operations |
| `test_analytics.py` | 18 | Streak calculations |

**Critical Paths Tested:**
- Consecutive daily/weekly streaks
- Broken streaks with gaps
- Multiple completions per period (deduplication)
- Habits with no completions
- Invalid periodicity rejection
- Cascading delete (habit + completions)

## Architecture

The application follows a four-layer architecture with clear separation of concerns:

```
┌─────────────────────────────────────┐
│            CLI Layer                │  cli.py
│      (User Interaction)             │
├─────────────────────────────────────┤
│          Habit Core                 │  habit.py
│     (Domain Model - OOP)            │
├─────────────────────────────────────┤
│         Storage Layer               │  storage.py
│    (SQLite Persistence)             │
├─────────────────────────────────────┤
│        Analytics Layer              │  analytics.py
│  (Functional Programming)           │
└─────────────────────────────────────┘
```

### Module Responsibilities

| Module | Responsibility | Paradigm |
|--------|---------------|----------|
| `habit.py` | Habit class definition and validation | OOP |
| `storage.py` | All SQLite database operations | Procedural |
| `analytics.py` | Streak calculations and filtering | Functional |
| `cli.py` | User interface and menu handling | Procedural |
| `seed.py` | Fixture data generation | Procedural |

### Architectural Integrity

**Separation of Concerns:**
- No circular dependencies between modules
- CLI layer never touches SQL directly - all queries go through `storage.py`
- Analytics functions are pure - derive results without mutating state
- Database serves as single source of truth

**Import Hierarchy:**
```
habit.py      → imports nothing from project
storage.py    → imports Habit
analytics.py  → imports Habit, storage
cli.py        → imports Habit, storage, analytics
```

## Database Schema

SQLite database with two tables:

**habits**
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key (auto-increment) |
| name | TEXT | Unique habit name |
| periodicity | TEXT | 'daily' or 'weekly' |
| target_per_period | INTEGER | Completions required per period |
| created_at | TEXT | ISO 8601 timestamp |
| active | INTEGER | 1 = active, 0 = inactive |

**completions**
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key (auto-increment) |
| habit_id | INTEGER | Foreign key to habits |
| timestamp | TEXT | ISO 8601 completion timestamp |

## Analytics Functions

The analytics module implements exactly four functions using functional programming principles:

1. **get_all_tracked_habits()** - Returns list of all active habits
2. **get_habits_by_periodicity(periodicity)** - Filters habits by daily/weekly
3. **get_longest_streak_all()** - Returns habit with longest streak overall
4. **get_longest_streak_for_habit(habit_id)** - Returns longest streak for specific habit

**Design Principles:**
- Pure functions with no side effects
- No mutation of stored data
- Results derived dynamically from completion records

## Streak Calculation Logic

- **Daily habits:** Consecutive calendar days with at least one completion
- **Weekly habits:** Consecutive calendar weeks with at least one completion
- **Week definition:** Monday to Sunday (ISO standard)
- **Broken streak:** Missing a period resets the streak counter
- **Multiple completions:** Same period counts as one completion

### Algorithm Walkthrough

The streak calculation in `analytics.py` follows this pipeline:

```
1. Fetch habit → get periodicity (daily/weekly)
2. Fetch completions → list of timestamps
3. Normalize to periods → extract unique period start dates
4. Sort chronologically
5. Count consecutive periods → compare each to expected next
```

**Period Normalization:**
- Daily: Each timestamp normalized to midnight (`datetime(year, month, day)`)
- Weekly: Each timestamp normalized to Monday of that week (`date - timedelta(days=weekday())`)

**Streak Counting:**
```python
period_duration = timedelta(days=1) if daily else timedelta(weeks=1)

for each period after first:
    if period == previous + period_duration:
        current_streak += 1
    else:
        current_streak = 1  # Gap detected, reset
```

### Edge Cases Handled

| Edge Case | Result |
|-----------|--------|
| No completions | 0 |
| Single completion | 1 |
| Multiple same day | 1 period |
| Multiple same week | 1 period |
| Nonexistent habit | 0 |

## Project Structure

```
fitter-u/
├── habit.py           # Habit class (OOP)
├── storage.py         # SQLite operations
├── analytics.py       # Analytics functions (FP)
├── cli.py             # Command-line interface
├── seed.py            # Fixture data seeding
├── requirements.txt   # Dependencies
├── README.md          # Documentation
├── habits.db          # SQLite database (generated)
└── tests/
    ├── __init__.py
    ├── test_habit.py
    ├── test_storage.py
    └── test_analytics.py
```

## License

This project was developed as part of the IU International University of Applied Sciences portfolio course.

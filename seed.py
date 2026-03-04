"""
Fitter-U Habit Tracker - Seed Module

This module populates the database with predefined habits and 4 weeks of
example completion data. It provides realistic fixture data for:
- Demonstrating application functionality
- Testing analytics calculations
- Validating streak logic with known patterns

The fixture data includes varied completion patterns to showcase different
streak scenarios (perfect streaks, broken streaks, gaps).
"""

from datetime import datetime, timedelta

from habit import Habit
import storage


# Predefined habits as specified in requirements
# 3 daily habits + 2 weekly habits = 5 total
PREDEFINED_HABITS = [
    Habit(name="Read 20 minutes", periodicity="daily", target_per_period=1),
    Habit(name="Walk 10 minutes", periodicity="daily", target_per_period=1),
    Habit(name="Meditate", periodicity="daily", target_per_period=1),
    Habit(name="Call family", periodicity="weekly", target_per_period=1),
    Habit(name="Review goals", periodicity="weekly", target_per_period=1),
]


def seed_database(database_name: str = storage.DATABASE_NAME, clear_existing: bool = True):
    """
    Seed the database with predefined habits and 4-week fixture data.

    Creates all predefined habits and populates them with completion
    records spanning 4 weeks with varied patterns.

    Args:
        database_name: Name of the database file to seed.
        clear_existing: If True, clears all existing data before seeding.
    """
    # Initialize database tables
    storage.initialize_database(database_name)

    # Optionally clear existing data for clean seeding
    if clear_existing:
        storage.clear_all_data(database_name)

    # Calculate date range for fixture data
    # Start from 4 weeks ago to have historical data
    today = datetime.now().replace(hour=12, minute=0, second=0, microsecond=0)
    four_weeks_ago = today - timedelta(weeks=4)

    # Dictionary to map habit names to their database IDs after creation
    habit_id_mapping = {}

    # Create each predefined habit with backdated created_at timestamp
    for habit_template in PREDEFINED_HABITS:
        new_habit = Habit(
            name=habit_template.name,
            periodicity=habit_template.periodicity,
            target_per_period=habit_template.target_per_period,
            created_at=four_weeks_ago,  # Backdate to match fixture data range
            active=True
        )
        habit_id = storage.create_habit(new_habit, database_name)
        habit_id_mapping[habit_template.name] = habit_id

    # Generate completion records for all habits
    seed_daily_habit_completions(habit_id_mapping, four_weeks_ago, database_name)
    seed_weekly_habit_completions(habit_id_mapping, four_weeks_ago, database_name)

    print(f"Database seeded with {len(PREDEFINED_HABITS)} habits and 4 weeks of data.")


def seed_daily_habit_completions(
    habit_id_mapping: dict,
    start_date: datetime,
    database_name: str
):
    """
    Seed completion data for daily habits over 4 weeks.

    Creates varied completion patterns to demonstrate different streak scenarios:
    - "Read 20 minutes": Most days, with gaps (longest streak: 10 days)
    - "Walk 10 minutes": Perfect attendance (28-day streak)
    - "Meditate": Irregular pattern with gaps (longest streak: 5 days)

    Args:
        habit_id_mapping: Dictionary mapping habit names to database IDs.
        start_date: The starting date for fixture data (4 weeks ago).
        database_name: Name of the database file.
    """
    # --- Read 20 minutes ---
    # Pattern: Days 0-9 (streak of 10), skip 10-11, days 12-19 (streak of 8), skip 20-21, days 22-27
    # Longest streak: 10 consecutive days
    read_habit_id = habit_id_mapping["Read 20 minutes"]
    read_completion_days = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 12, 13, 14, 15, 16, 17, 18, 19, 22, 23, 24, 25, 26, 27]
    for day_offset in read_completion_days:
        # Add completion at 8:30 PM each day
        completion_timestamp = start_date + timedelta(days=day_offset, hours=20, minutes=30)
        storage.add_completion(read_habit_id, completion_timestamp, database_name)

    # --- Walk 10 minutes ---
    # Pattern: Every single day for 28 days (perfect streak)
    # Longest streak: 28 consecutive days
    walk_habit_id = habit_id_mapping["Walk 10 minutes"]
    for day_offset in range(28):
        # Add completion at 7:00 AM each day (morning walk)
        completion_timestamp = start_date + timedelta(days=day_offset, hours=7, minutes=0)
        storage.add_completion(walk_habit_id, completion_timestamp, database_name)

    # --- Meditate ---
    # Pattern: Irregular with multiple gaps
    # Days 0-4 (streak of 5), skip 5-6, days 7-8, skip 9, day 10, skip 11-13,
    # days 14-17 (streak of 4), skip 18-20, days 21-23 (streak of 3), skip 24, days 25-27
    # Longest streak: 5 consecutive days
    meditate_habit_id = habit_id_mapping["Meditate"]
    meditate_completion_days = [0, 1, 2, 3, 4, 7, 8, 10, 14, 15, 16, 17, 21, 22, 23, 25, 26, 27]
    for day_offset in meditate_completion_days:
        # Add completion at 6:30 AM each day (morning meditation)
        completion_timestamp = start_date + timedelta(days=day_offset, hours=6, minutes=30)
        storage.add_completion(meditate_habit_id, completion_timestamp, database_name)


def seed_weekly_habit_completions(
    habit_id_mapping: dict,
    start_date: datetime,
    database_name: str
):
    """
    Seed completion data for weekly habits over 4 weeks.

    Creates completion patterns for weekly habits:
    - "Call family": Every week for 4 weeks (perfect 4-week streak)
    - "Review goals": Weeks 1, 2, 4 (missed week 3) - longest streak: 2 weeks

    Args:
        habit_id_mapping: Dictionary mapping habit names to database IDs.
        start_date: The starting date for fixture data (4 weeks ago).
        database_name: Name of the database file.
    """
    # --- Call family ---
    # Pattern: Completed every week (perfect attendance)
    # Longest streak: 4 consecutive weeks
    call_family_habit_id = habit_id_mapping["Call family"]
    for week_offset in range(4):
        # Complete on Sunday of each week at 6:00 PM
        # (day 6 = Sunday when start_date is Monday)
        completion_timestamp = start_date + timedelta(weeks=week_offset, days=6, hours=18, minutes=0)
        storage.add_completion(call_family_habit_id, completion_timestamp, database_name)

    # --- Review goals ---
    # Pattern: Weeks 0, 1, and 3 (missed week 2)
    # Longest streak: 2 consecutive weeks (weeks 0-1)
    review_goals_habit_id = habit_id_mapping["Review goals"]
    review_completion_weeks = [0, 1, 3]  # Week indices (0-based), skipping week 2
    for week_offset in review_completion_weeks:
        # Complete on Friday of each week at 5:00 PM
        # (day 4 = Friday when start_date is Monday)
        completion_timestamp = start_date + timedelta(weeks=week_offset, days=4, hours=17, minutes=0)
        storage.add_completion(review_goals_habit_id, completion_timestamp, database_name)


# Allow running this module directly to seed the database
if __name__ == "__main__":
    seed_database()

"""
Fitter-U Habit Tracker - Analytics Module

This module implements analytics functions using the Functional Programming (FP)
paradigm. All functions are pure - they derive results from completion data
without mutating any stored state.

The module provides exactly four analytics functions as specified:
1. get_all_tracked_habits() - List all active habits
2. get_habits_by_periodicity() - Filter habits by daily/weekly
3. get_longest_streak_all() - Find habit with longest streak
4. get_longest_streak_for_habit() - Calculate streak for specific habit
"""

from datetime import datetime, timedelta
from typing import List, Tuple, Optional

from habit import Habit
import storage


def get_all_tracked_habits(database_name: str = storage.DATABASE_NAME) -> List[Habit]:
    """
    Return a list of all currently tracked (active) habits.

    This is a simple wrapper around storage that maintains the analytics
    interface. Returns only habits where active=True.

    Args:
        database_name: Name of the database file.

    Returns:
        List of active Habit objects.
    """
    return storage.get_active_habits(database_name)


def get_habits_by_periodicity(
    periodicity: str,
    database_name: str = storage.DATABASE_NAME
) -> List[Habit]:
    """
    Return a list of all habits with the same periodicity.

    Uses functional filter() to select habits matching the specified
    periodicity. Demonstrates FP approach over imperative loops.

    Args:
        periodicity: 'daily' or 'weekly' to filter by.
        database_name: Name of the database file.

    Returns:
        List of Habit objects matching the specified periodicity.
    """
    all_habits = storage.get_all_habits(database_name)

    # Use filter() with lambda for functional approach
    # This is more declarative than a for loop with conditional append
    return list(filter(lambda habit: habit.periodicity == periodicity, all_habits))


def get_longest_streak_all(database_name: str = storage.DATABASE_NAME) -> Tuple[Optional[Habit], int]:
    """
    Return the longest run streak of all defined habits.

    Iterates through all habits, calculates each one's longest streak,
    and returns the habit with the maximum streak value.

    Args:
        database_name: Name of the database file.

    Returns:
        Tuple of (Habit with longest streak, streak length).
        Returns (None, 0) if no habits exist or no completions recorded.
    """
    all_habits = storage.get_all_habits(database_name)

    # Handle edge case: no habits in database
    if not all_habits:
        return (None, 0)

    # Build list of (habit, streak) tuples using list comprehension
    # This demonstrates functional mapping pattern
    habit_streaks = [
        (habit, get_longest_streak_for_habit(habit.id, database_name))
        for habit in all_habits
    ]

    # Find the habit with maximum streak using max() with key function
    # default=(None, 0) handles empty list edge case
    best_habit_streak = max(habit_streaks, key=lambda pair: pair[1], default=(None, 0))

    return best_habit_streak


def get_longest_streak_for_habit(
    habit_id: int,
    database_name: str = storage.DATABASE_NAME
) -> int:
    """
    Return the longest run streak for a given habit.

    A streak is defined as consecutive periods (days or weeks) with at
    least one completion. Missing a period breaks the streak.

    Algorithm:
    1. Fetch all completions for the habit
    2. Extract unique periods from completion timestamps
    3. Sort periods chronologically
    4. Count consecutive periods without gaps

    Args:
        habit_id: ID of the habit to analyze.
        database_name: Name of the database file.

    Returns:
        The longest streak length (number of consecutive periods).
        Returns 0 if habit not found or has no completions.
    """
    # Fetch the habit to get its periodicity
    habit = storage.get_habit_by_id(habit_id, database_name)
    if not habit:
        return 0

    # Fetch all completion records for this habit
    completions = storage.get_completions(habit_id, database_name)
    if not completions:
        return 0

    # Extract just the timestamps from completion tuples
    # completions is List[Tuple[id, timestamp]] - we need only timestamps
    completion_timestamps = [completion[1] for completion in completions]

    # Convert timestamps to unique period start dates
    # Multiple completions on same day/week count as one period
    completed_periods = extract_completed_periods(completion_timestamps, habit.periodicity)

    if not completed_periods:
        return 0

    # Calculate and return the longest consecutive sequence
    return calculate_longest_streak(completed_periods, habit.periodicity)


def extract_completed_periods(
    timestamps: List[datetime],
    periodicity: str
) -> List[datetime]:
    """
    Extract unique completed periods from timestamps.

    Converts raw completion timestamps into normalized period start dates.
    Multiple completions within the same period are deduplicated.

    For daily habits: each unique calendar day becomes one period
    For weekly habits: each unique calendar week becomes one period

    Args:
        timestamps: List of completion timestamps.
        periodicity: 'daily' or 'weekly' determining period granularity.

    Returns:
        Sorted list of unique period start dates.
    """
    # Use set to automatically deduplicate periods
    # (multiple completions on same day/week count as one)
    unique_periods = set()

    for timestamp in timestamps:
        # Normalize timestamp to period start (midnight of day, or Monday of week)
        period_start = get_period_start_date(timestamp, periodicity)
        unique_periods.add(period_start)

    # Return sorted list for sequential streak calculation
    return sorted(unique_periods)


def get_period_start_date(date_time: datetime, periodicity: str) -> datetime:
    """
    Get the start of the period for a given datetime.

    Normalizes a timestamp to the beginning of its containing period:
    - Daily: midnight (00:00:00) of that day
    - Weekly: midnight of Monday of that week (ISO standard)

    Args:
        date_time: The datetime to normalize.
        periodicity: 'daily' or 'weekly'.

    Returns:
        Datetime representing the start of the period.
    """
    if periodicity == 'daily':
        # Strip time component, keeping only the date at midnight
        return datetime(date_time.year, date_time.month, date_time.day)
    else:
        # Weekly: find the Monday of this week
        # weekday() returns 0 for Monday, 6 for Sunday
        days_since_monday = date_time.weekday()
        week_start = date_time - timedelta(days=days_since_monday)
        # Return Monday at midnight
        return datetime(week_start.year, week_start.month, week_start.day)


def calculate_longest_streak(
    completed_periods: List[datetime],
    periodicity: str
) -> int:
    """
    Calculate the longest streak from sorted period dates.

    Iterates through sorted periods, checking if each period is exactly
    one period-length after the previous. Consecutive periods increment
    the current streak; gaps reset it.

    Args:
        completed_periods: Sorted list of period start dates.
        periodicity: 'daily' or 'weekly' - determines expected gap.

    Returns:
        Length of the longest consecutive streak found.
    """
    if not completed_periods:
        return 0

    # Define the expected time gap between consecutive periods
    # Daily: exactly 1 day apart
    # Weekly: exactly 7 days (1 week) apart
    period_duration = timedelta(days=1) if periodicity == 'daily' else timedelta(weeks=1)

    # Initialize tracking variables
    # A single completion counts as streak of 1
    longest_streak = 1
    current_streak = 1

    # Iterate through periods starting from the second one
    # Compare each period to its predecessor
    for index in range(1, len(completed_periods)):
        # Calculate what the next period should be if streak continues
        expected_next_period = completed_periods[index - 1] + period_duration

        if completed_periods[index] == expected_next_period:
            # Period follows immediately - streak continues
            current_streak += 1
            # Update longest if current exceeds it
            longest_streak = max(longest_streak, current_streak)
        else:
            # Gap detected - streak is broken, reset counter
            current_streak = 1

    return longest_streak

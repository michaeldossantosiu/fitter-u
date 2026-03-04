"""Tests for the analytics module."""

import pytest
import os
from datetime import datetime, timedelta

from habit import Habit
import storage
import analytics


TEST_DATABASE = "test_analytics.db"


@pytest.fixture(autouse=True)
def setup_and_teardown():
    """Setup and teardown for each test."""
    storage.initialize_database(TEST_DATABASE)
    storage.clear_all_data(TEST_DATABASE)
    yield
    if os.path.exists(TEST_DATABASE):
        os.remove(TEST_DATABASE)


class TestGetAllTrackedHabits:
    """Tests for get_all_tracked_habits function."""

    def test_returns_active_habits(self):
        """Test that only active habits are returned."""
        storage.create_habit(Habit(name="Active", periodicity="daily", active=True), TEST_DATABASE)
        storage.create_habit(Habit(name="Inactive", periodicity="daily", active=False), TEST_DATABASE)

        tracked_habits = analytics.get_all_tracked_habits(TEST_DATABASE)

        assert len(tracked_habits) == 1
        assert tracked_habits[0].name == "Active"

    def test_returns_empty_when_no_habits(self):
        """Test returns empty list when no habits exist."""
        tracked_habits = analytics.get_all_tracked_habits(TEST_DATABASE)
        assert len(tracked_habits) == 0


class TestGetHabitsByPeriodicity:
    """Tests for get_habits_by_periodicity function."""

    def test_filter_daily_habits(self):
        """Test filtering daily habits."""
        storage.create_habit(Habit(name="Daily 1", periodicity="daily"), TEST_DATABASE)
        storage.create_habit(Habit(name="Daily 2", periodicity="daily"), TEST_DATABASE)
        storage.create_habit(Habit(name="Weekly 1", periodicity="weekly"), TEST_DATABASE)

        daily_habits = analytics.get_habits_by_periodicity("daily", TEST_DATABASE)

        assert len(daily_habits) == 2
        assert all(habit.periodicity == "daily" for habit in daily_habits)

    def test_filter_weekly_habits(self):
        """Test filtering weekly habits."""
        storage.create_habit(Habit(name="Daily 1", periodicity="daily"), TEST_DATABASE)
        storage.create_habit(Habit(name="Weekly 1", periodicity="weekly"), TEST_DATABASE)

        weekly_habits = analytics.get_habits_by_periodicity("weekly", TEST_DATABASE)

        assert len(weekly_habits) == 1
        assert weekly_habits[0].name == "Weekly 1"


class TestDailyStreakCalculation:
    """Tests for daily habit streak calculations."""

    def test_consecutive_days_streak(self):
        """Test streak calculation for consecutive daily completions."""
        daily_habit = Habit(name="Daily Test", periodicity="daily")
        habit_id = storage.create_habit(daily_habit, TEST_DATABASE)

        base_date = datetime(2025, 1, 1, 10, 0, 0)
        for day_offset in range(5):
            storage.add_completion(habit_id, base_date + timedelta(days=day_offset), TEST_DATABASE)

        longest_streak = analytics.get_longest_streak_for_habit(habit_id, TEST_DATABASE)

        assert longest_streak == 5

    def test_broken_streak(self):
        """Test streak calculation when streak is broken."""
        daily_habit = Habit(name="Daily Test", periodicity="daily")
        habit_id = storage.create_habit(daily_habit, TEST_DATABASE)

        base_date = datetime(2025, 1, 1, 10, 0, 0)
        # Days 0, 1, 2 (streak of 3)
        for day_offset in range(3):
            storage.add_completion(habit_id, base_date + timedelta(days=day_offset), TEST_DATABASE)
        # Skip day 3
        # Days 4, 5 (streak of 2)
        for day_offset in range(4, 6):
            storage.add_completion(habit_id, base_date + timedelta(days=day_offset), TEST_DATABASE)

        longest_streak = analytics.get_longest_streak_for_habit(habit_id, TEST_DATABASE)

        assert longest_streak == 3

    def test_multiple_completions_same_day(self):
        """Test that multiple completions on same day count as one period."""
        daily_habit = Habit(name="Daily Test", periodicity="daily")
        habit_id = storage.create_habit(daily_habit, TEST_DATABASE)

        base_date = datetime(2025, 1, 1, 10, 0, 0)
        # Day 0: two completions
        storage.add_completion(habit_id, base_date, TEST_DATABASE)
        storage.add_completion(habit_id, base_date + timedelta(hours=2), TEST_DATABASE)
        # Day 1: one completion
        storage.add_completion(habit_id, base_date + timedelta(days=1), TEST_DATABASE)

        longest_streak = analytics.get_longest_streak_for_habit(habit_id, TEST_DATABASE)

        assert longest_streak == 2

    def test_single_completion(self):
        """Test streak with only one completion."""
        daily_habit = Habit(name="Daily Test", periodicity="daily")
        habit_id = storage.create_habit(daily_habit, TEST_DATABASE)

        storage.add_completion(habit_id, datetime(2025, 1, 1, 10, 0, 0), TEST_DATABASE)

        longest_streak = analytics.get_longest_streak_for_habit(habit_id, TEST_DATABASE)

        assert longest_streak == 1


class TestWeeklyStreakCalculation:
    """Tests for weekly habit streak calculations."""

    def test_consecutive_weeks_streak(self):
        """Test streak calculation for consecutive weekly completions."""
        weekly_habit = Habit(name="Weekly Test", periodicity="weekly")
        habit_id = storage.create_habit(weekly_habit, TEST_DATABASE)

        # Monday of week 1
        base_date = datetime(2025, 1, 6, 10, 0, 0)
        for week_offset in range(4):
            storage.add_completion(habit_id, base_date + timedelta(weeks=week_offset), TEST_DATABASE)

        longest_streak = analytics.get_longest_streak_for_habit(habit_id, TEST_DATABASE)

        assert longest_streak == 4

    def test_broken_weekly_streak(self):
        """Test weekly streak when a week is missed."""
        weekly_habit = Habit(name="Weekly Test", periodicity="weekly")
        habit_id = storage.create_habit(weekly_habit, TEST_DATABASE)

        base_date = datetime(2025, 1, 6, 10, 0, 0)
        # Weeks 0, 1 (streak of 2)
        storage.add_completion(habit_id, base_date, TEST_DATABASE)
        storage.add_completion(habit_id, base_date + timedelta(weeks=1), TEST_DATABASE)
        # Skip week 2
        # Week 3 (streak of 1)
        storage.add_completion(habit_id, base_date + timedelta(weeks=3), TEST_DATABASE)

        longest_streak = analytics.get_longest_streak_for_habit(habit_id, TEST_DATABASE)

        assert longest_streak == 2

    def test_multiple_completions_same_week(self):
        """Test that multiple completions in same week count as one period."""
        weekly_habit = Habit(name="Weekly Test", periodicity="weekly")
        habit_id = storage.create_habit(weekly_habit, TEST_DATABASE)

        # Monday of week 1
        base_date = datetime(2025, 1, 6, 10, 0, 0)
        # Two completions in week 1
        storage.add_completion(habit_id, base_date, TEST_DATABASE)
        storage.add_completion(habit_id, base_date + timedelta(days=3), TEST_DATABASE)
        # One completion in week 2
        storage.add_completion(habit_id, base_date + timedelta(weeks=1), TEST_DATABASE)

        longest_streak = analytics.get_longest_streak_for_habit(habit_id, TEST_DATABASE)

        assert longest_streak == 2


class TestEdgeCases:
    """Tests for edge cases."""

    def test_habit_with_no_completions(self):
        """Test streak for habit with no completions."""
        empty_habit = Habit(name="Empty Habit", periodicity="daily")
        habit_id = storage.create_habit(empty_habit, TEST_DATABASE)

        longest_streak = analytics.get_longest_streak_for_habit(habit_id, TEST_DATABASE)

        assert longest_streak == 0

    def test_nonexistent_habit(self):
        """Test streak for nonexistent habit."""
        longest_streak = analytics.get_longest_streak_for_habit(9999, TEST_DATABASE)
        assert longest_streak == 0

    def test_longest_streak_all_no_habits(self):
        """Test longest streak all when no habits exist."""
        best_habit, longest_streak = analytics.get_longest_streak_all(TEST_DATABASE)

        assert best_habit is None
        assert longest_streak == 0

    def test_longest_streak_all_no_completions(self):
        """Test longest streak all when habits have no completions."""
        storage.create_habit(Habit(name="Empty 1", periodicity="daily"), TEST_DATABASE)
        storage.create_habit(Habit(name="Empty 2", periodicity="weekly"), TEST_DATABASE)

        best_habit, longest_streak = analytics.get_longest_streak_all(TEST_DATABASE)

        assert longest_streak == 0


class TestLongestStreakAll:
    """Tests for get_longest_streak_all function."""

    def test_finds_habit_with_longest_streak(self):
        """Test finding the habit with the longest streak."""
        short_streak_habit = Habit(name="Short Streak", periodicity="daily")
        long_streak_habit = Habit(name="Long Streak", periodicity="daily")
        short_habit_id = storage.create_habit(short_streak_habit, TEST_DATABASE)
        long_habit_id = storage.create_habit(long_streak_habit, TEST_DATABASE)

        base_date = datetime(2025, 1, 1, 10, 0, 0)
        # Habit 1: 3 day streak
        for day_offset in range(3):
            storage.add_completion(short_habit_id, base_date + timedelta(days=day_offset), TEST_DATABASE)
        # Habit 2: 7 day streak
        for day_offset in range(7):
            storage.add_completion(long_habit_id, base_date + timedelta(days=day_offset), TEST_DATABASE)

        best_habit, longest_streak = analytics.get_longest_streak_all(TEST_DATABASE)

        assert best_habit.name == "Long Streak"
        assert longest_streak == 7

    def test_compares_daily_and_weekly(self):
        """Test comparison between daily and weekly habits."""
        daily_habit = Habit(name="Daily", periodicity="daily")
        weekly_habit = Habit(name="Weekly", periodicity="weekly")
        daily_habit_id = storage.create_habit(daily_habit, TEST_DATABASE)
        weekly_habit_id = storage.create_habit(weekly_habit, TEST_DATABASE)

        base_date = datetime(2025, 1, 6, 10, 0, 0)
        # Daily: 5 day streak
        for day_offset in range(5):
            storage.add_completion(daily_habit_id, base_date + timedelta(days=day_offset), TEST_DATABASE)
        # Weekly: 3 week streak
        for week_offset in range(3):
            storage.add_completion(weekly_habit_id, base_date + timedelta(weeks=week_offset), TEST_DATABASE)

        best_habit, longest_streak = analytics.get_longest_streak_all(TEST_DATABASE)

        assert best_habit.name == "Daily"
        assert longest_streak == 5


class TestFixtureDataStreaks:
    """Tests using fixture-like data patterns."""

    def test_28_day_streak(self):
        """Test a perfect 28-day (4 week) streak."""
        perfect_daily_habit = Habit(name="Perfect Daily", periodicity="daily")
        habit_id = storage.create_habit(perfect_daily_habit, TEST_DATABASE)

        base_date = datetime(2025, 1, 1, 7, 0, 0)
        for day_offset in range(28):
            storage.add_completion(habit_id, base_date + timedelta(days=day_offset), TEST_DATABASE)

        longest_streak = analytics.get_longest_streak_for_habit(habit_id, TEST_DATABASE)

        assert longest_streak == 28

    def test_4_week_weekly_streak(self):
        """Test a perfect 4-week streak."""
        perfect_weekly_habit = Habit(name="Perfect Weekly", periodicity="weekly")
        habit_id = storage.create_habit(perfect_weekly_habit, TEST_DATABASE)

        base_date = datetime(2025, 1, 6, 18, 0, 0)  # Monday
        for week_offset in range(4):
            storage.add_completion(habit_id, base_date + timedelta(weeks=week_offset), TEST_DATABASE)

        longest_streak = analytics.get_longest_streak_for_habit(habit_id, TEST_DATABASE)

        assert longest_streak == 4

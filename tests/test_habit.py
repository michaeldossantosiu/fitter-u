"""Tests for the Habit class."""

import pytest
from datetime import datetime

from habit import Habit


class TestHabitCreation:
    """Tests for Habit instantiation."""

    def test_create_daily_habit(self):
        """Test creating a daily habit with default values."""
        daily_habit = Habit(name="Test habit", periodicity="daily")

        assert daily_habit.name == "Test habit"
        assert daily_habit.periodicity == "daily"
        assert daily_habit.target_per_period == 1
        assert daily_habit.active is True
        assert daily_habit.id is None
        assert isinstance(daily_habit.created_at, datetime)

    def test_create_weekly_habit(self):
        """Test creating a weekly habit."""
        weekly_habit = Habit(name="Weekly test", periodicity="weekly", target_per_period=2)

        assert weekly_habit.name == "Weekly test"
        assert weekly_habit.periodicity == "weekly"
        assert weekly_habit.target_per_period == 2

    def test_create_habit_with_custom_created_at(self):
        """Test creating a habit with custom created_at timestamp."""
        custom_creation_date = datetime(2025, 1, 1, 12, 0, 0)
        custom_habit = Habit(name="Test", periodicity="daily", created_at=custom_creation_date)

        assert custom_habit.created_at == custom_creation_date

    def test_create_habit_invalid_periodicity(self):
        """Test that invalid periodicity raises ValueError."""
        with pytest.raises(ValueError):
            Habit(name="Test", periodicity="monthly")

    def test_create_habit_with_id(self):
        """Test creating a habit with an ID."""
        habit_with_id = Habit(name="Test", periodicity="daily", id=42)

        assert habit_with_id.id == 42


class TestHabitEquality:
    """Tests for Habit equality comparison."""

    def test_habits_equal_by_id(self):
        """Test that habits with same ID are equal."""
        first_habit = Habit(name="Habit 1", periodicity="daily", id=1)
        second_habit = Habit(name="Habit 2", periodicity="weekly", id=1)

        assert first_habit == second_habit

    def test_habits_equal_by_name_when_no_id(self):
        """Test that habits with same name are equal when no ID."""
        first_habit = Habit(name="Same Name", periodicity="daily")
        second_habit = Habit(name="Same Name", periodicity="weekly")

        assert first_habit == second_habit

    def test_habits_not_equal(self):
        """Test that different habits are not equal."""
        first_habit = Habit(name="Habit 1", periodicity="daily", id=1)
        second_habit = Habit(name="Habit 2", periodicity="daily", id=2)

        assert first_habit != second_habit


class TestHabitRepresentation:
    """Tests for Habit string representation."""

    def test_string_representation(self):
        """Test the string representation of a habit."""
        test_habit = Habit(name="Test", periodicity="daily", target_per_period=1, active=True)
        representation_string = repr(test_habit)

        assert "Test" in representation_string
        assert "daily" in representation_string
        assert "1" in representation_string
        assert "True" in representation_string

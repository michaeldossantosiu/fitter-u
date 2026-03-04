"""Tests for the storage module."""

import pytest
import os
from datetime import datetime

from habit import Habit
import storage


TEST_DATABASE = "test_habits.db"


@pytest.fixture(autouse=True)
def setup_and_teardown():
    """Setup and teardown for each test."""
    storage.initialize_database(TEST_DATABASE)
    storage.clear_all_data(TEST_DATABASE)
    yield
    if os.path.exists(TEST_DATABASE):
        os.remove(TEST_DATABASE)


class TestHabitStorage:
    """Tests for habit CRUD operations."""

    def test_create_habit(self):
        """Test creating a habit in the database."""
        new_habit = Habit(name="Test Habit", periodicity="daily")
        habit_id = storage.create_habit(new_habit, TEST_DATABASE)

        assert habit_id is not None
        assert habit_id > 0

    def test_get_habit_by_id(self):
        """Test retrieving a habit by ID."""
        new_habit = Habit(name="Test Habit", periodicity="daily", target_per_period=2)
        habit_id = storage.create_habit(new_habit, TEST_DATABASE)

        retrieved_habit = storage.get_habit_by_id(habit_id, TEST_DATABASE)

        assert retrieved_habit is not None
        assert retrieved_habit.name == "Test Habit"
        assert retrieved_habit.periodicity == "daily"
        assert retrieved_habit.target_per_period == 2

    def test_get_habit_by_name(self):
        """Test retrieving a habit by name."""
        new_habit = Habit(name="Unique Name", periodicity="weekly")
        storage.create_habit(new_habit, TEST_DATABASE)

        retrieved_habit = storage.get_habit_by_name("Unique Name", TEST_DATABASE)

        assert retrieved_habit is not None
        assert retrieved_habit.name == "Unique Name"

    def test_get_nonexistent_habit(self):
        """Test retrieving a habit that doesn't exist."""
        result = storage.get_habit_by_id(9999, TEST_DATABASE)
        assert result is None

    def test_get_all_habits(self):
        """Test retrieving all habits."""
        storage.create_habit(Habit(name="Habit 1", periodicity="daily"), TEST_DATABASE)
        storage.create_habit(Habit(name="Habit 2", periodicity="weekly"), TEST_DATABASE)

        all_habits = storage.get_all_habits(TEST_DATABASE)

        assert len(all_habits) == 2

    def test_get_active_habits(self):
        """Test retrieving only active habits."""
        active_habit = Habit(name="Active", periodicity="daily", active=True)
        inactive_habit = Habit(name="Inactive", periodicity="daily", active=False)
        storage.create_habit(active_habit, TEST_DATABASE)
        storage.create_habit(inactive_habit, TEST_DATABASE)

        active_habits = storage.get_active_habits(TEST_DATABASE)

        assert len(active_habits) == 1
        assert active_habits[0].name == "Active"

    def test_delete_habit(self):
        """Test deleting a habit."""
        habit_to_delete = Habit(name="To Delete", periodicity="daily")
        habit_id = storage.create_habit(habit_to_delete, TEST_DATABASE)

        deletion_result = storage.delete_habit(habit_id, TEST_DATABASE)

        assert deletion_result is True
        assert storage.get_habit_by_id(habit_id, TEST_DATABASE) is None


class TestCompletionStorage:
    """Tests for completion operations."""

    def test_add_completion(self):
        """Test adding a completion."""
        new_habit = Habit(name="Test", periodicity="daily")
        habit_id = storage.create_habit(new_habit, TEST_DATABASE)

        completion_id = storage.add_completion(habit_id, database_name=TEST_DATABASE)

        assert completion_id is not None
        assert completion_id > 0

    def test_add_completion_with_timestamp(self):
        """Test adding a completion with specific timestamp."""
        new_habit = Habit(name="Test", periodicity="daily")
        habit_id = storage.create_habit(new_habit, TEST_DATABASE)
        completion_timestamp = datetime(2025, 6, 15, 10, 30, 0)

        storage.add_completion(habit_id, completion_timestamp, TEST_DATABASE)
        all_completions = storage.get_completions(habit_id, TEST_DATABASE)

        assert len(all_completions) == 1
        assert all_completions[0][1] == completion_timestamp

    def test_get_completions(self):
        """Test retrieving completions for a habit."""
        new_habit = Habit(name="Test", periodicity="daily")
        habit_id = storage.create_habit(new_habit, TEST_DATABASE)

        storage.add_completion(habit_id, database_name=TEST_DATABASE)
        storage.add_completion(habit_id, database_name=TEST_DATABASE)

        all_completions = storage.get_completions(habit_id, TEST_DATABASE)

        assert len(all_completions) == 2

    def test_get_completions_empty(self):
        """Test retrieving completions when none exist."""
        new_habit = Habit(name="Test", periodicity="daily")
        habit_id = storage.create_habit(new_habit, TEST_DATABASE)

        all_completions = storage.get_completions(habit_id, TEST_DATABASE)

        assert len(all_completions) == 0

    def test_delete_habit_removes_completions(self):
        """Test that deleting a habit also removes its completions."""
        new_habit = Habit(name="Test", periodicity="daily")
        habit_id = storage.create_habit(new_habit, TEST_DATABASE)
        storage.add_completion(habit_id, database_name=TEST_DATABASE)

        storage.delete_habit(habit_id, TEST_DATABASE)

        all_completions = storage.get_all_completions(TEST_DATABASE)
        assert len(all_completions) == 0

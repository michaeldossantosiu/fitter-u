"""
Fitter-U Habit Tracker - Storage Module

This module handles all SQLite database operations for the habit tracker.
It provides a clean interface for CRUD operations on habits and completions,
abstracting away the SQL implementation details from other modules.

The database serves as the single source of truth for the application.
"""

import sqlite3
from datetime import datetime
from typing import List, Optional, Tuple

from habit import Habit


# Default database filename - can be overridden for testing
DATABASE_NAME = "habits.db"


def get_database_connection(database_name: str = DATABASE_NAME) -> sqlite3.Connection:
    """
    Get a connection to the SQLite database.

    Args:
        database_name: Name of the database file.

    Returns:
        SQLite connection object with Row factory enabled.
    """
    connection = sqlite3.connect(database_name)

    # Enable Row factory to access columns by name instead of index
    # This makes the code more readable and maintainable
    connection.row_factory = sqlite3.Row

    return connection


def initialize_database(database_name: str = DATABASE_NAME) -> None:
    """
    Initialize the database with required tables.

    Creates the 'habits' and 'completions' tables if they don't exist.
    This function is idempotent - safe to call multiple times.

    Args:
        database_name: Name of the database file.
    """
    connection = get_database_connection(database_name)
    database_cursor = connection.cursor()

    # Create habits table - stores habit metadata
    # Using TEXT for timestamps in ISO 8601 format for portability
    # Active stored as INTEGER (0/1) since SQLite lacks native boolean
    database_cursor.execute("""
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            periodicity TEXT NOT NULL,
            target_per_period INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL,
            active INTEGER NOT NULL DEFAULT 1
        )
    """)

    # Create completions table - stores timestamped check-off events
    # Foreign key links each completion to its parent habit
    # This event-log design enables streak calculation from raw data
    database_cursor.execute("""
        CREATE TABLE IF NOT EXISTS completions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id INTEGER NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (habit_id) REFERENCES habits (id)
        )
    """)

    connection.commit()
    connection.close()


def create_habit(habit: Habit, database_name: str = DATABASE_NAME) -> int:
    """
    Insert a new habit into the database.

    Args:
        habit: Habit object to insert.
        database_name: Name of the database file.

    Returns:
        The auto-generated ID of the inserted habit.
    """
    connection = get_database_connection(database_name)
    database_cursor = connection.cursor()

    # Convert Habit object to database row format
    # Boolean 'active' converted to INTEGER (1 or 0) for SQLite
    # Datetime converted to ISO 8601 string for consistent storage
    database_cursor.execute(
        """
        INSERT INTO habits (name, periodicity, target_per_period, created_at, active)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            habit.name,
            habit.periodicity,
            habit.target_per_period,
            habit.created_at.isoformat(),
            1 if habit.active else 0
        )
    )

    # Capture the auto-generated ID before closing connection
    habit_id = database_cursor.lastrowid
    connection.commit()
    connection.close()

    return habit_id


def get_habit_by_name(name: str, database_name: str = DATABASE_NAME) -> Optional[Habit]:
    """
    Retrieve a habit by its name.

    Useful for checking if a habit already exists before creation.

    Args:
        name: Name of the habit to find.
        database_name: Name of the database file.

    Returns:
        Habit object if found, None otherwise.
    """
    connection = get_database_connection(database_name)
    database_cursor = connection.cursor()

    database_cursor.execute("SELECT * FROM habits WHERE name = ?", (name,))
    row = database_cursor.fetchone()
    connection.close()

    # Convert database row to Habit object if found
    if row:
        return convert_row_to_habit(row)
    return None


def get_habit_by_id(habit_id: int, database_name: str = DATABASE_NAME) -> Optional[Habit]:
    """
    Retrieve a habit by its ID.

    Primary method for fetching a specific habit for operations.

    Args:
        habit_id: Database ID of the habit.
        database_name: Name of the database file.

    Returns:
        Habit object if found, None otherwise.
    """
    connection = get_database_connection(database_name)
    database_cursor = connection.cursor()

    database_cursor.execute("SELECT * FROM habits WHERE id = ?", (habit_id,))
    row = database_cursor.fetchone()
    connection.close()

    if row:
        return convert_row_to_habit(row)
    return None


def get_all_habits(database_name: str = DATABASE_NAME) -> List[Habit]:
    """
    Retrieve all habits from the database.

    Returns both active and inactive habits.

    Args:
        database_name: Name of the database file.

    Returns:
        List of all Habit objects in the database.
    """
    connection = get_database_connection(database_name)
    database_cursor = connection.cursor()

    database_cursor.execute("SELECT * FROM habits")
    rows = database_cursor.fetchall()
    connection.close()

    # Convert each row to a Habit object using list comprehension
    return [convert_row_to_habit(row) for row in rows]


def get_active_habits(database_name: str = DATABASE_NAME) -> List[Habit]:
    """
    Retrieve all active habits from the database.

    Filters out deactivated habits - used for check-off operations
    where only active habits should be available.

    Args:
        database_name: Name of the database file.

    Returns:
        List of active Habit objects only.
    """
    connection = get_database_connection(database_name)
    database_cursor = connection.cursor()

    # Filter by active = 1 (true in SQLite integer representation)
    database_cursor.execute("SELECT * FROM habits WHERE active = 1")
    rows = database_cursor.fetchall()
    connection.close()

    return [convert_row_to_habit(row) for row in rows]


def delete_habit(habit_id: int, database_name: str = DATABASE_NAME) -> bool:
    """
    Delete a habit and its completions from the database.

    Performs cascading delete: removes all completion records first,
    then removes the habit itself. This maintains referential integrity.

    Args:
        habit_id: ID of the habit to delete.
        database_name: Name of the database file.

    Returns:
        True if habit was deleted, False if not found.
    """
    connection = get_database_connection(database_name)
    database_cursor = connection.cursor()

    # Delete completions first to maintain referential integrity
    # (Foreign key constraint would fail otherwise)
    database_cursor.execute("DELETE FROM completions WHERE habit_id = ?", (habit_id,))

    # Now safe to delete the habit itself
    database_cursor.execute("DELETE FROM habits WHERE id = ?", (habit_id,))

    # Check if any row was affected (habit existed)
    was_deleted = database_cursor.rowcount > 0
    connection.commit()
    connection.close()

    return was_deleted


def add_completion(
    habit_id: int,
    completion_timestamp: Optional[datetime] = None,
    database_name: str = DATABASE_NAME
) -> int:
    """
    Log a completion event for a habit.

    Records when a habit was checked off. The timestamp parameter allows
    backdating for testing/seeding purposes; defaults to current time.

    Args:
        habit_id: ID of the habit being completed.
        completion_timestamp: When the completion occurred (defaults to now).
        database_name: Name of the database file.

    Returns:
        The auto-generated ID of the inserted completion record.
    """
    # Default to current time if no timestamp provided
    if completion_timestamp is None:
        completion_timestamp = datetime.now()

    connection = get_database_connection(database_name)
    database_cursor = connection.cursor()

    # Store timestamp in ISO 8601 format for consistent parsing
    database_cursor.execute(
        "INSERT INTO completions (habit_id, timestamp) VALUES (?, ?)",
        (habit_id, completion_timestamp.isoformat())
    )

    completion_id = database_cursor.lastrowid
    connection.commit()
    connection.close()

    return completion_id


def get_completions(
    habit_id: int,
    database_name: str = DATABASE_NAME
) -> List[Tuple[int, datetime]]:
    """
    Retrieve all completions for a specific habit.

    Returns completions ordered by timestamp for streak calculation.

    Args:
        habit_id: ID of the habit.
        database_name: Name of the database file.

    Returns:
        List of tuples containing (completion_id, timestamp).
    """
    connection = get_database_connection(database_name)
    database_cursor = connection.cursor()

    # Order by timestamp to support sequential streak calculation
    database_cursor.execute(
        "SELECT id, timestamp FROM completions WHERE habit_id = ? ORDER BY timestamp",
        (habit_id,)
    )
    rows = database_cursor.fetchall()
    connection.close()

    # Convert ISO timestamp strings back to datetime objects
    return [(row['id'], datetime.fromisoformat(row['timestamp'])) for row in rows]


def get_all_completions(
    database_name: str = DATABASE_NAME
) -> List[Tuple[int, int, datetime]]:
    """
    Retrieve all completions from the database.

    Useful for testing and verification purposes.

    Args:
        database_name: Name of the database file.

    Returns:
        List of tuples containing (completion_id, habit_id, timestamp).
    """
    connection = get_database_connection(database_name)
    database_cursor = connection.cursor()

    database_cursor.execute("SELECT id, habit_id, timestamp FROM completions ORDER BY timestamp")
    rows = database_cursor.fetchall()
    connection.close()

    return [
        (row['id'], row['habit_id'], datetime.fromisoformat(row['timestamp']))
        for row in rows
    ]


def clear_all_data(database_name: str = DATABASE_NAME) -> None:
    """
    Clear all data from the database.

    Used for testing setup and database reseeding.
    Deletes all records but preserves table structure.

    Args:
        database_name: Name of the database file.
    """
    connection = get_database_connection(database_name)
    database_cursor = connection.cursor()

    # Delete completions first due to foreign key relationship
    database_cursor.execute("DELETE FROM completions")
    database_cursor.execute("DELETE FROM habits")

    connection.commit()
    connection.close()


def convert_row_to_habit(database_row: sqlite3.Row) -> Habit:
    """
    Convert a database row to a Habit object.

    Maps SQLite column values to Habit constructor parameters,
    handling type conversions (ISO string to datetime, int to bool).

    Args:
        database_row: SQLite Row object from query result.

    Returns:
        Fully populated Habit object.
    """
    return Habit(
        id=database_row['id'],
        name=database_row['name'],
        periodicity=database_row['periodicity'],
        target_per_period=database_row['target_per_period'],
        # Convert ISO string back to datetime object
        created_at=datetime.fromisoformat(database_row['created_at']),
        # Convert SQLite integer (0/1) to Python boolean
        active=bool(database_row['active'])
    )

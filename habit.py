"""
Fitter-U Habit Tracker - Habit Module

This module contains the Habit class which represents the core domain model
for the habit tracking application. It uses Object-Oriented Programming (OOP)
principles to encapsulate habit data and validation logic.
"""

from datetime import datetime
from typing import Optional


class Habit:
    """
    Represents a habit with its metadata and tracking information.

    This class serves as the domain model for habits in the Fitter-U Habit Tracker.
    It encapsulates all habit-related data and enforces validation rules such as
    ensuring periodicity is either 'daily' or 'weekly'.

    Attributes:
        name: The name/description of the habit (e.g., "Read 20 minutes").
        periodicity: The tracking frequency - either 'daily' or 'weekly'.
        target_per_period: Number of completions required per period (default: 1).
        created_at: Timestamp when the habit was first created.
        active: Whether the habit is currently being tracked (default: True).
        id: Database ID assigned after persistence (None until saved).
    """

    def __init__(
        self,
        name: str,
        periodicity: str,
        target_per_period: int = 1,
        created_at: Optional[datetime] = None,
        active: bool = True,
        id: Optional[int] = None
    ):
        """
        Initialize a new Habit instance.

        Args:
            name: The name of the habit.
            periodicity: 'daily' or 'weekly' - determines streak calculation.
            target_per_period: Completions required per period (default 1).
            created_at: Creation timestamp (defaults to current time if None).
            active: Whether habit is active (default True).
            id: Database ID (default None, assigned after storage).

        Raises:
            ValueError: If periodicity is not 'daily' or 'weekly'.
        """
        # Validate periodicity to ensure only supported values are accepted
        # This prevents invalid data from entering the system
        if periodicity not in ('daily', 'weekly'):
            raise ValueError("Periodicity must be 'daily' or 'weekly'")

        # Assign database ID (None for new habits, set after persistence)
        self.id = id

        # Core habit attributes
        self.name = name
        self.periodicity = periodicity
        self.target_per_period = target_per_period

        # Set creation timestamp to now if not provided
        # This allows backdating habits when seeding test data
        self.created_at = created_at if created_at else datetime.now()

        # Active flag allows soft-deletion without losing history
        self.active = active

    def __repr__(self) -> str:
        """
        Return string representation of the habit.

        Useful for debugging and logging. Shows key attributes
        in a format that could reconstruct the object.
        """
        return (
            f"Habit(name='{self.name}', periodicity='{self.periodicity}', "
            f"target_per_period={self.target_per_period}, active={self.active})"
        )

    def __eq__(self, other) -> bool:
        """
        Check equality based on id or name.

        Two habits are considered equal if:
        1. Both have IDs and they match (database identity), OR
        2. Neither has an ID and names match (logical identity)

        This supports both persisted and unpersisted habit comparison.
        """
        if isinstance(other, Habit):
            # If both habits have database IDs, compare by ID
            if self.id is not None and other.id is not None:
                return self.id == other.id
            # Otherwise, compare by name (for unpersisted habits)
            return self.name == other.name
        return False

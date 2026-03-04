"""
Fitter-U Habit Tracker - CLI Module

This module provides the command-line interface for user interaction.
It implements a simple menu-driven system using Python's built-in input()
function, keeping the interface minimal and focused on core functionality.

The CLI layer only handles user input/output - all business logic is
delegated to the appropriate modules (storage, analytics).
"""

import sys
from datetime import datetime

from habit import Habit
import storage
import analytics


# Application title displayed at startup
APP_TITLE = "Fitter-U Habit Tracker"


def main():
    """
    Main entry point for the CLI application.

    Initializes the database and runs the main menu loop.
    The loop continues until the user selects Exit (option 6).
    """
    # Ensure database tables exist before any operations
    storage.initialize_database()

    # Display welcome banner
    print(APP_TITLE)
    print("=" * 40)

    # Main application loop - runs until user exits
    while True:
        display_main_menu()
        user_choice = input("Enter choice: ").strip()

        # Route to appropriate handler based on user selection
        if user_choice == "1":
            create_new_habit()
        elif user_choice == "2":
            display_all_habits()
        elif user_choice == "3":
            checkoff_habit_completion()
        elif user_choice == "4":
            remove_habit()
        elif user_choice == "5":
            display_analytics_menu()
        elif user_choice == "6":
            print("Goodbye!")
            sys.exit(0)
        else:
            print("Invalid choice. Please try again.\n")


def display_main_menu():
    """
    Display the main menu options.

    Shows numbered options for all available actions.
    Called at the start of each loop iteration.
    """
    print("\nMain Menu:")
    print("1. Create habit")
    print("2. List habits")
    print("3. Check-off habit")
    print("4. Delete habit")
    print("5. View analytics")
    print("6. Exit")
    print()


def create_new_habit():
    """
    Create a new habit through interactive prompts.

    Collects habit name, periodicity, and target from user input.
    Validates all inputs before creating the habit in the database.
    """
    print("\n--- Create New Habit ---")

    # Collect and validate habit name
    habit_name = input("Enter habit name: ").strip()
    if not habit_name:
        print("Error: Name cannot be empty.")
        return

    # Check for duplicate names to prevent confusion
    existing_habit = storage.get_habit_by_name(habit_name)
    if existing_habit:
        print(f"Error: Habit '{habit_name}' already exists.")
        return

    # Collect periodicity through menu selection
    # Using numbered options instead of free text to prevent typos
    print("Select periodicity:")
    print("1. Daily")
    print("2. Weekly")
    periodicity_choice = input("Enter choice (1 or 2): ").strip()

    # Map menu choice to periodicity value
    if periodicity_choice == "1":
        periodicity = "daily"
    elif periodicity_choice == "2":
        periodicity = "weekly"
    else:
        print("Error: Invalid periodicity choice.")
        return

    # Collect target completions (optional - defaults to 1)
    target_input = input("Target completions per period (default 1): ").strip()
    if target_input:
        try:
            target_per_period = int(target_input)
            # Validate positive value
            if target_per_period < 1:
                print("Error: Target must be at least 1.")
                return
        except ValueError:
            print("Error: Invalid number.")
            return
    else:
        # Default to 1 completion per period
        target_per_period = 1

    # Create Habit object and persist to database
    new_habit = Habit(name=habit_name, periodicity=periodicity, target_per_period=target_per_period)
    habit_id = storage.create_habit(new_habit)

    print(f"Habit '{habit_name}' created successfully with ID {habit_id}.")


def display_all_habits():
    """
    Display all habits in the system.

    Shows habit ID, name, periodicity, target, and active status.
    Includes both active and inactive habits.
    """
    print("\n--- All Habits ---")
    all_habits = storage.get_all_habits()

    # Handle empty database case
    if not all_habits:
        print("No habits found.")
        return

    # Display each habit with formatted details
    for habit in all_habits:
        status_text = "Active" if habit.active else "Inactive"
        print(
            f"[{habit.id}] {habit.name} - {habit.periodicity} "
            f"(target: {habit.target_per_period}/period) [{status_text}]"
        )


def checkoff_habit_completion():
    """
    Check-off (complete) a habit for the current moment.

    Shows active habits, prompts for habit ID, and logs completion
    with current timestamp. Only active habits can be checked off.
    """
    print("\n--- Check-off Habit ---")

    # Only show active habits - inactive habits shouldn't be checked off
    active_habits = storage.get_active_habits()

    if not active_habits:
        print("No active habits to check off.")
        return

    # Display available habits with their IDs
    print("Active habits:")
    for habit in active_habits:
        print(f"[{habit.id}] {habit.name}")

    # Get habit ID from user
    habit_id_input = input("Enter habit ID to check off: ").strip()
    try:
        habit_id = int(habit_id_input)
    except ValueError:
        print("Error: Invalid ID.")
        return

    # Verify habit exists and is valid
    selected_habit = storage.get_habit_by_id(habit_id)
    if not selected_habit:
        print("Error: Habit not found.")
        return

    # Log the completion with current timestamp
    storage.add_completion(habit_id)

    # Display confirmation with formatted timestamp
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"Habit '{selected_habit.name}' checked off at {current_time}.")


def remove_habit():
    """
    Remove a habit from the system.

    Permanently deletes the habit and all its completion history.
    Requires user confirmation before deletion.
    """
    print("\n--- Delete Habit ---")
    all_habits = storage.get_all_habits()

    if not all_habits:
        print("No habits to delete.")
        return

    # Show all habits (including inactive) for deletion
    print("All habits:")
    for habit in all_habits:
        print(f"[{habit.id}] {habit.name}")

    # Get habit ID to delete
    habit_id_input = input("Enter habit ID to delete: ").strip()
    try:
        habit_id = int(habit_id_input)
    except ValueError:
        print("Error: Invalid ID.")
        return

    # Verify habit exists
    habit_to_delete = storage.get_habit_by_id(habit_id)
    if not habit_to_delete:
        print("Error: Habit not found.")
        return

    # Require explicit confirmation - deletion is irreversible
    confirmation = input(f"Delete habit '{habit_to_delete.name}' and all its data? (y/n): ").strip().lower()
    if confirmation == "y":
        storage.delete_habit(habit_id)
        print(f"Habit '{habit_to_delete.name}' deleted.")
    else:
        print("Deletion cancelled.")


def display_analytics_menu():
    """
    Display analytics submenu and handle selection.

    Provides access to the four analytics functions:
    - List tracked habits
    - Filter by periodicity
    - Longest streak (all)
    - Longest streak (specific)
    """
    print("\n--- Analytics Menu ---")
    print("1. List all tracked habits")
    print("2. List habits by periodicity")
    print("3. Longest streak (all habits)")
    print("4. Longest streak (specific habit)")
    print("5. Back to main menu")

    user_choice = input("Enter choice: ").strip()

    # Route to appropriate analytics display function
    if user_choice == "1":
        display_tracked_habits()
    elif user_choice == "2":
        display_habits_by_periodicity()
    elif user_choice == "3":
        display_longest_streak_all_habits()
    elif user_choice == "4":
        display_longest_streak_single_habit()
    elif user_choice == "5":
        return  # Return to main menu
    else:
        print("Invalid choice.")


def display_tracked_habits():
    """
    Display all currently tracked (active) habits.

    Uses analytics module to get active habits.
    Shows habit name and periodicity in simple format.
    """
    print("\n--- Currently Tracked Habits ---")
    tracked_habits = analytics.get_all_tracked_habits()

    if not tracked_habits:
        print("No tracked habits.")
        return

    # Simple bullet-point display
    for habit in tracked_habits:
        print(f"- {habit.name} ({habit.periodicity})")


def display_habits_by_periodicity():
    """
    Display habits filtered by periodicity.

    Prompts user to select daily or weekly, then shows
    matching habits using the analytics filter function.
    """
    print("\nSelect periodicity:")
    print("1. Daily")
    print("2. Weekly")
    user_choice = input("Enter choice: ").strip()

    # Map choice to periodicity value
    if user_choice == "1":
        periodicity = "daily"
    elif user_choice == "2":
        periodicity = "weekly"
    else:
        print("Invalid choice.")
        return

    # Use analytics function to filter habits
    filtered_habits = analytics.get_habits_by_periodicity(periodicity)

    print(f"\n--- {periodicity.capitalize()} Habits ---")
    if not filtered_habits:
        print(f"No {periodicity} habits found.")
        return

    for habit in filtered_habits:
        print(f"- {habit.name}")


def display_longest_streak_all_habits():
    """
    Display the habit with longest streak across all habits.

    Shows which habit has the best consistency record
    and what that streak length is.
    """
    print("\n--- Longest Streak (All Habits) ---")

    # Get the habit with best streak and the streak value
    best_habit, longest_streak = analytics.get_longest_streak_all()

    if best_habit is None:
        print("No habits or no completions recorded.")
    else:
        # Format period name based on periodicity
        period_name = "day" if best_habit.periodicity == "daily" else "week"
        print(f"Habit: {best_habit.name}")
        print(f"Longest streak: {longest_streak} consecutive {period_name}(s)")


def display_longest_streak_single_habit():
    """
    Display the longest streak for a specific habit.

    Prompts user to select a habit by ID, then calculates
    and displays its longest streak.
    """
    print("\n--- Longest Streak (Specific Habit) ---")
    all_habits = storage.get_all_habits()

    if not all_habits:
        print("No habits found.")
        return

    # Show available habits for selection
    for habit in all_habits:
        print(f"[{habit.id}] {habit.name}")

    # Get habit selection from user
    habit_id_input = input("Enter habit ID: ").strip()
    try:
        habit_id = int(habit_id_input)
    except ValueError:
        print("Error: Invalid ID.")
        return

    # Verify habit exists
    selected_habit = storage.get_habit_by_id(habit_id)
    if not selected_habit:
        print("Error: Habit not found.")
        return

    # Calculate streak using analytics function
    longest_streak = analytics.get_longest_streak_for_habit(habit_id)

    # Display result with appropriate period label
    period_name = "day" if selected_habit.periodicity == "daily" else "week"
    print(f"Habit: {selected_habit.name}")
    print(f"Longest streak: {longest_streak} consecutive {period_name}(s)")


# Standard Python idiom - only run main() if this file is executed directly
if __name__ == "__main__":
    main()

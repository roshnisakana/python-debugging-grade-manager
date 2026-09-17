"""
Student Grade Manager
----------------------
A command-line tool for tracking student grades, computing averages,
and assigning letter grades. Grades are persisted to a JSON file
between sessions.
"""

import json
import os

DATA_FILE = "grades.json"


def load_data(filename=DATA_FILE):
    """Load student records from the JSON data file.

    Returns an empty dict if the file doesn't exist yet (first run)
    or if it exists but contains invalid/empty JSON, instead of
    crashing the program.
    """
    if not os.path.exists(filename):
        return {}

    try:
        with open(filename, "r") as file:
            return json.load(file)
    except json.JSONDecodeError:
        print(f"Warning: '{filename}' is empty or corrupted. Starting fresh.")
        return {}


def save_data(data, filename=DATA_FILE):
    """Save student records back to the JSON data file."""
    with open(filename, "w") as file:
        json.dump(data, file, indent=2)


def add_student(name, records):
    """Register a new student with an empty grade list.

    `records` is always required (no mutable default argument) so every
    call operates on the caller's own dictionary instead of a shared,
    accidentally-persistent one.
    """
    if name not in records:
        records[name] = []
    return records


def add_grade(records, name, grade):
    """Add a validated numeric grade (0-100) for a student.

    Returns True if the grade was accepted, False if it was rejected
    (not a number, or outside the valid 0-100 range).
    """
    try:
        numeric_grade = float(grade)
    except ValueError:
        print(f"'{grade}' is not a valid number. Grade not added.")
        return False

    if not (0 <= numeric_grade <= 100):
        print(f"{numeric_grade} is outside the valid 0-100 range. Grade not added.")
        return False

    records[name].append(numeric_grade)
    return True


def compute_average(grades):
    """Compute the average of a list of grades.

    Returns 0.0 for an empty list rather than raising ZeroDivisionError.
    """
    if not grades:
        return 0.0
    return sum(grades) / len(grades)


def letter_grade(average):
    """Convert a numeric average into a letter grade.

    Boundaries are inclusive, so an average of exactly 90 is an 'A',
    exactly 80 is a 'B', and so on.
    """
    if average >= 90:
        return "A"
    elif average >= 80:
        return "B"
    elif average >= 70:
        return "C"
    elif average >= 60:
        return "D"
    else:
        return "F"


def class_summary(records):
    """Print a summary of every student's average and letter grade."""
    if not records:
        print("No students yet.")
        return

    total = 0
    for name, grades in records.items():
        avg = compute_average(grades)
        total = total + avg
        status = "no grades yet" if not grades else f"grade={letter_grade(avg)}"
        print(f"{name}: average={avg:.2f}, {status}")

    class_average = total / len(records)
    print(f"\nClass average: {class_average:.2f}")


def prompt_menu_choice():
    """Read the menu choice as an int, re-prompting on invalid input."""
    raw = input("Choose an option: ").strip()
    try:
        return int(raw)
    except ValueError:
        return None


def main():
    records = load_data()

    while True:
        print("\n1) Add student")
        print("2) Add grade")
        print("3) Show class summary")
        print("4) Save and exit")
        choice = prompt_menu_choice()

        if choice == 1:
            name = input("Student name: ").strip()
            add_student(name, records)
        elif choice == 2:
            name = input("Student name: ").strip()
            if name not in records:
                print(f"'{name}' isn't registered yet. Use option 1 first.")
                continue
            grade = input("Grade (0-100): ").strip()
            add_grade(records, name, grade)
        elif choice == 3:
            class_summary(records)
        elif choice == 4:
            save_data(records)
            print("Saved. Goodbye!")
            break
        else:
            print("Invalid option, try again.")


if __name__ == "__main__":
    main()

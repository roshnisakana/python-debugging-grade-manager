"""
Unit tests for grade_manager_fixed.py

Run with:  python3 -m unittest test_grade_manager.py -v
"""

import json
import os
import unittest

import grade_manager_fixed as gm


TEST_FILE = "test_grades.json"


class TestLoadData(unittest.TestCase):
    def tearDown(self):
        if os.path.exists(TEST_FILE):
            os.remove(TEST_FILE)

    def test_missing_file_returns_empty_dict(self):
        """Bug fix: first run with no data file must not crash."""
        self.assertFalse(os.path.exists(TEST_FILE))
        self.assertEqual(gm.load_data(TEST_FILE), {})

    def test_corrupted_file_returns_empty_dict(self):
        with open(TEST_FILE, "w") as f:
            f.write("{not valid json")
        self.assertEqual(gm.load_data(TEST_FILE), {})

    def test_valid_file_loads_correctly(self):
        sample = {"Amit": [80, 90]}
        with open(TEST_FILE, "w") as f:
            json.dump(sample, f)
        self.assertEqual(gm.load_data(TEST_FILE), sample)

    def test_load_does_not_overwrite_existing_data(self):
        """Bug fix: load must open read-only and never truncate the file."""
        sample = {"Amit": [80, 90]}
        with open(TEST_FILE, "w") as f:
            json.dump(sample, f)
        gm.load_data(TEST_FILE)
        with open(TEST_FILE, "r") as f:
            self.assertEqual(json.load(f), sample)


class TestAddStudent(unittest.TestCase):
    def test_new_student_gets_empty_list(self):
        records = {}
        gm.add_student("Amit", records)
        self.assertEqual(records, {"Amit": []})

    def test_no_state_leaks_between_independent_calls(self):
        """Bug fix: no shared mutable default argument."""
        records_a = {}
        records_b = {}
        gm.add_student("Amit", records_a)
        gm.add_student("Priya", records_b)
        self.assertNotIn("Priya", records_a)
        self.assertNotIn("Amit", records_b)


class TestAddGrade(unittest.TestCase):
    def setUp(self):
        self.records = {"Amit": []}

    def test_valid_grade_is_added_as_float(self):
        ok = gm.add_grade(self.records, "Amit", "88")
        self.assertTrue(ok)
        self.assertEqual(self.records["Amit"], [88.0])

    def test_non_numeric_grade_is_rejected(self):
        ok = gm.add_grade(self.records, "Amit", "abc")
        self.assertFalse(ok)
        self.assertEqual(self.records["Amit"], [])

    def test_out_of_range_grade_is_rejected(self):
        ok = gm.add_grade(self.records, "Amit", "150")
        self.assertFalse(ok)
        self.assertEqual(self.records["Amit"], [])

    def test_boundary_grades_are_accepted(self):
        self.assertTrue(gm.add_grade(self.records, "Amit", "0"))
        self.assertTrue(gm.add_grade(self.records, "Amit", "100"))
        self.assertEqual(self.records["Amit"], [0.0, 100.0])


class TestComputeAverage(unittest.TestCase):
    def test_average_of_multiple_grades(self):
        """Bug fix: loop must include every grade, not skip the last one."""
        self.assertAlmostEqual(gm.compute_average([80, 90, 100]), 90.0)

    def test_average_of_single_grade(self):
        """Bug fix: single-grade lists must not fall through to 0.0."""
        self.assertEqual(gm.compute_average([75]), 75.0)

    def test_average_of_empty_list_is_zero(self):
        """Bug fix: empty grade list must not raise ZeroDivisionError."""
        self.assertEqual(gm.compute_average([]), 0.0)


class TestLetterGrade(unittest.TestCase):
    def test_boundaries_are_inclusive(self):
        """Bug fix: exact boundary scores must round up, not down."""
        self.assertEqual(gm.letter_grade(90), "A")
        self.assertEqual(gm.letter_grade(80), "B")
        self.assertEqual(gm.letter_grade(70), "C")
        self.assertEqual(gm.letter_grade(60), "D")
        self.assertEqual(gm.letter_grade(59.9), "F")

    def test_typical_values(self):
        self.assertEqual(gm.letter_grade(95), "A")
        self.assertEqual(gm.letter_grade(85), "B")
        self.assertEqual(gm.letter_grade(45), "F")


class TestClassSummary(unittest.TestCase):
    def test_empty_roster_does_not_crash(self):
        """Bug fix: class_summary must not divide by zero on an empty roster."""
        try:
            gm.class_summary({})
        except ZeroDivisionError:
            self.fail("class_summary raised ZeroDivisionError on empty roster")


if __name__ == "__main__":
    unittest.main()

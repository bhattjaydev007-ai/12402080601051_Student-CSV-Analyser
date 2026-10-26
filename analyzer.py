"""
analyzer.py - core logic of the Student CSV Data Analyzer.

Only the standard library is used here: csv, io, lists, dictionaries and
functions. Both cli.py and app.py (Streamlit) import from this file, so the
logic is written once and reused by both front ends.
"""

import csv
import io

PASS_MARK = 40          # minimum marks needed in every subject
MAX_MARKS = 100         # each subject is out of 100

# (minimum percentage, grade) - checked from top to bottom
GRADE_SCALE = [(90, "A+"), (80, "A"), (70, "B"), (60, "C"), (50, "D"), (40, "E")]


# ---------------------------------------------------------------- loading
def read_csv_text(text):
    """Turn raw CSV text into a list of dictionaries (one per row)."""
    reader = csv.DictReader(io.StringIO(text))
    rows = []
    for row in reader:
        # tidy headers/values: strip spaces, lower-case the column names
        clean = {}
        for key, value in row.items():
            if key is not None:
                clean[key.strip().lower()] = (value or "").strip()
        rows.append(clean)
    return rows


def read_csv_file(path):
    """Read a CSV file from disk and return the list of row dictionaries."""
    with open(path, newline="", encoding="utf-8-sig") as f:
        return read_csv_text(f.read())


def find_subjects(rows):
    """Every column except roll_no and name is treated as a subject."""
    if not rows:
        return []
    return [col for col in rows[0] if col not in ("roll_no", "name")]


def clean_rows(rows):
    """
    Convert marks to numbers and drop bad rows.
    Returns (students, problems): a list of valid student dictionaries and a
    list of messages explaining why any row was skipped.
    """
    subjects = find_subjects(rows)
    students = []
    problems = []

    for line_no, row in enumerate(rows, start=2):   # line 1 is the header
        name = row.get("name", "")
        if name == "":
            problems.append(f"Line {line_no}: name is missing, row skipped")
            continue

        student = {"roll_no": row.get("roll_no", ""), "name": name}
        valid = True
        for sub in subjects:
            try:
                marks = float(row[sub])
            except (ValueError, KeyError):
                problems.append(f"Line {line_no} ({name}): bad marks in {sub}, row skipped")
                valid = False
                break
            if marks < 0 or marks > MAX_MARKS:
                problems.append(f"Line {line_no} ({name}): {sub} marks out of range, row skipped")
                valid = False
                break
            student[sub] = marks
        if valid:
            students.append(student)

    return students, problems


# ------------------------------------------------------------ calculation
def get_grade(percentage):
    """Return the grade letter for a percentage."""
    for limit, grade in GRADE_SCALE:
        if percentage >= limit:
            return grade
    return "F"


def add_results(students, subjects):
    """Add total, percentage, grade, status and rank to every student."""
    for s in students:
        marks = [s[sub] for sub in subjects]
        s["total"] = sum(marks)
        s["percentage"] = round(s["total"] / (len(subjects) * MAX_MARKS) * 100, 2)
        s["failed_in"] = [sub for sub in subjects if s[sub] < PASS_MARK]
        s["status"] = "Pass" if not s["failed_in"] else "Fail"
        s["grade"] = get_grade(s["percentage"]) if s["status"] == "Pass" else "F"

    # rank by total marks, highest first
    ranked = sorted(students, key=lambda s: s["total"], reverse=True)
    for position, s in enumerate(ranked, start=1):
        s["rank"] = position
    return ranked


def class_summary(students):
    """Overall numbers for the whole class, returned as a dictionary."""
    count = len(students)
    if count == 0:
        return {}
    passed = [s for s in students if s["status"] == "Pass"]
    percentages = [s["percentage"] for s in students]
    return {
        "students": count,
        "average_percentage": round(sum(percentages) / count, 2),
        "highest_percentage": max(percentages),
        "lowest_percentage": min(percentages),
        "passed": len(passed),
        "failed": count - len(passed),
        "pass_percentage": round(len(passed) / count * 100, 2),
    }


def subject_stats(students, subjects):
    """Average, highest, lowest and pass rate for each subject."""
    stats = {}
    for sub in subjects:
        marks = [s[sub] for s in students]
        stats[sub] = {
            "average": round(sum(marks) / len(marks), 2),
            "highest": max(marks),
            "lowest": min(marks),
            "pass_rate": round(len([m for m in marks if m >= PASS_MARK]) / len(marks) * 100, 2),
        }
    return stats


def grade_distribution(students):
    """Count of students in each grade, e.g. {'A+': 3, 'A': 7, ...}."""
    counts = {grade: 0 for _, grade in GRADE_SCALE}
    counts["F"] = 0
    for s in students:
        counts[s["grade"]] += 1
    return counts


def top_students(students, n=5):
    """The n students with the highest totals."""
    return sorted(students, key=lambda s: s["total"], reverse=True)[:n]


def failed_students(students):
    """Students who failed at least one subject."""
    return [s for s in students if s["status"] == "Fail"]


def search_students(students, text):
    """Find students by part of the name or roll number."""
    text = text.strip().lower()
    return [s for s in students
            if text in s["name"].lower() or text in s["roll_no"].lower()]


# ----------------------------------------------------------------- export
def results_to_csv(students, subjects):
    """Build a result CSV (as text) that can be saved or downloaded."""
    columns = ["rank", "roll_no", "name"] + subjects + ["total", "percentage", "grade", "status"]
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=columns, extrasaction="ignore")
    writer.writeheader()
    for s in sorted(students, key=lambda s: s["rank"]):
        writer.writerow(s)
    return buffer.getvalue()


# ------------------------------------------------------------ one-call API
def analyze_text(text):
    """
    Run the whole pipeline on CSV text.
    Returns a dictionary with everything the front ends need.
    """
    rows = read_csv_text(text)
    subjects = find_subjects(rows)
    students, problems = clean_rows(rows)
    if not students:
        return {"students": [], "subjects": subjects, "problems": problems}
    ranked = add_results(students, subjects)
    return {
        "students": ranked,
        "subjects": subjects,
        "problems": problems,
        "summary": class_summary(ranked),
        "subject_stats": subject_stats(ranked, subjects),
        "grades": grade_distribution(ranked),
    }


def analyze_file(path):
    """Same as analyze_text but reads from a file path."""
    with open(path, newline="", encoding="utf-8-sig") as f:
        return analyze_text(f.read())

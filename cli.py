"""
cli.py - simple command line menu for the Student CSV Data Analyzer.

Run:  python cli.py                 (uses students.csv)
      python cli.py my_data.csv     (uses your own file)
"""

import sys
import analyzer


def show_table(students, subjects):
    """Print students as a neat text table."""
    header = f"{'Rank':<5}{'Roll':<7}{'Name':<18}" + "".join(f"{s[:7].title():>8}" for s in subjects)
    header += f"{'Total':>7}{'%':>8}{'Grade':>7}{'Status':>8}"
    print(header)
    print("-" * len(header))
    for s in students:
        line = f"{s['rank']:<5}{s['roll_no']:<7}{s['name']:<18}"
        line += "".join(f"{s[sub]:>8.0f}" for sub in subjects)
        line += f"{s['total']:>7.0f}{s['percentage']:>8.2f}{s['grade']:>7}{s['status']:>8}"
        print(line)


def show_summary(data):
    print("\n--- Class Summary ---")
    for key, value in data["summary"].items():
        print(f"{key.replace('_', ' ').title():<22}: {value}")
    print("\n--- Subject-wise ---")
    for sub, st in data["subject_stats"].items():
        print(f"{sub.title():<10} avg {st['average']:<6} high {st['highest']:<5.0f} "
              f"low {st['lowest']:<5.0f} pass rate {st['pass_rate']}%")


def show_grades(data):
    print("\n--- Grade Distribution ---")
    for grade, count in data["grades"].items():
        print(f"{grade:<3} {'#' * count} ({count})")


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "students.csv"
    try:
        data = analyzer.analyze_file(path)
    except FileNotFoundError:
        print(f"File not found: {path}")
        return
    if not data["students"]:
        print("No valid rows found in the file.")
        return
    for msg in data["problems"]:
        print("Warning:", msg)

    students, subjects = data["students"], data["subjects"]
    menu = """
===== Student CSV Data Analyzer =====
1. Show all results
2. Class summary and subject statistics
3. Top 5 students
4. Failed students
5. Grade distribution
6. Search student
7. Save results to results.csv
0. Exit"""
    while True:
        print(menu)
        choice = input("Choose: ").strip()
        if choice == "1":
            show_table(students, subjects)
        elif choice == "2":
            show_summary(data)
        elif choice == "3":
            show_table(analyzer.top_students(students, 5), subjects)
        elif choice == "4":
            failed = analyzer.failed_students(students)
            if failed:
                show_table(failed, subjects)
            else:
                print("Nobody failed.")
        elif choice == "5":
            show_grades(data)
        elif choice == "6":
            found = analyzer.search_students(students, input("Name or roll no: "))
            if found:
                show_table(found, subjects)
            else:
                print("No match.")
        elif choice == "7":
            with open("results.csv", "w", newline="", encoding="utf-8") as f:
                f.write(analyzer.results_to_csv(students, subjects))
            print("Saved to results.csv")
        elif choice == "0":
            print("Bye!")
            break
        else:
            print("Invalid choice, try again.")


if __name__ == "__main__":
    main()

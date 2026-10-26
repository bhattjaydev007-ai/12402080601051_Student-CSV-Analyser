# Student CSV Data Analyzer

Python mini project - Jaydev Bhatt (12402080601051), ADIT, CVM University.

Reads a CSV of student marks and reports totals, percentages, grades, ranks,
pass/fail, subject-wise statistics, toppers and grade distribution.
Concepts used: CSV, Lists, Dictionaries, Functions.

## Files
- `analyzer.py` - all the logic (standard library only)
- `cli.py`      - command line menu
- `app.py`      - Streamlit web interface
- `students.csv`- sample data (30 students, 5 subjects)

## Run
    pip install streamlit
    streamlit run app.py        # web interface
    python cli.py               # command line (or: python cli.py yourfile.csv)

## CSV format
First two columns must be `roll_no` and `name`. Every other column is a
subject with marks out of 100. Pass mark is 40 in each subject.

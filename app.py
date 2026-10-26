"""
app.py - Streamlit front end for the Student CSV Data Analyzer.

Run:  streamlit run app.py
"""

import os
import streamlit as st
import analyzer

st.set_page_config(page_title="Student CSV Data Analyzer", page_icon="📊", layout="wide")
st.title("📊 Student CSV Data Analyzer")
st.caption("Upload a CSV of student marks (roll_no, name, subject columns...) and get results instantly.")

# ---- choose the data source: uploaded file or the bundled sample ----
uploaded = st.sidebar.file_uploader("Upload CSV file", type="csv")
if uploaded is not None:
    text = uploaded.getvalue().decode("utf-8-sig")
else:
    sample = os.path.join(os.path.dirname(__file__), "students.csv")
    with open(sample, encoding="utf-8-sig") as f:
        text = f.read()
    st.sidebar.info("Showing the sample file students.csv. Upload your own to analyse it.")

data = analyzer.analyze_text(text)

if not data["students"]:
    st.error("No valid student rows found. Check the CSV format.")
    st.stop()

students, subjects = data["students"], data["subjects"]
summary = data["summary"]

if data["problems"]:
    with st.expander(f"⚠️ {len(data['problems'])} row(s) skipped"):
        for msg in data["problems"]:
            st.write(msg)

# ---- headline numbers ----
c1, c2, c3, c4 = st.columns(4)
c1.metric("Students", summary["students"])
c2.metric("Class average", f"{summary['average_percentage']}%")
c3.metric("Pass percentage", f"{summary['pass_percentage']}%")
c4.metric("Highest score", f"{summary['highest_percentage']}%")

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["All results", "Subjects", "Toppers & Fails", "Grades", "Search"])

with tab1:
    st.dataframe(students, use_container_width=True, hide_index=True,
                 column_order=["rank", "roll_no", "name"] + subjects +
                              ["total", "percentage", "grade", "status"])
    st.download_button("⬇️ Download results CSV",
                       analyzer.results_to_csv(students, subjects),
                       file_name="results.csv", mime="text/csv")

with tab2:
    stats = data["subject_stats"]
    st.subheader("Average marks per subject")
    st.bar_chart([{"Subject": sub.title(), "Average": st_["average"]}
                  for sub, st_ in stats.items()], x="Subject", y="Average")
    st.dataframe([{"Subject": sub.title(), **vals} for sub, vals in stats.items()],
                 use_container_width=True, hide_index=True)

with tab3:
    left, right = st.columns(2)
    with left:
        st.subheader("🏆 Top 5 students")
        st.dataframe([{"Rank": s["rank"], "Name": s["name"], "Total": s["total"],
                       "Percentage": s["percentage"]}
                      for s in analyzer.top_students(students, 5)],
                     use_container_width=True, hide_index=True)
    with right:
        st.subheader("❌ Failed students")
        failed = analyzer.failed_students(students)
        if failed:
            st.dataframe([{"Name": s["name"], "Percentage": s["percentage"],
                           "Failed in": ", ".join(f.title() for f in s["failed_in"])}
                          for s in failed],
                         use_container_width=True, hide_index=True)
        else:
            st.success("Nobody failed.")

with tab4:
    st.subheader("Grade distribution")
    st.bar_chart([{"Grade": g, "Students": n} for g, n in data["grades"].items()],
                 x="Grade", y="Students")

with tab5:
    query = st.text_input("Search by name or roll number")
    if query:
        found = analyzer.search_students(students, query)
        if found:
            st.dataframe(found, use_container_width=True, hide_index=True,
                         column_order=["rank", "roll_no", "name"] + subjects +
                                      ["total", "percentage", "grade", "status"])
        else:
            st.warning("No student matched.")

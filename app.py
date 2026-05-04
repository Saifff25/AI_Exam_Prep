import streamlit as st
import pandas as pd
import time
from google import genai

# ------------------ CONFIG ------------------
st.set_page_config(page_title="AI Exam Prep", layout="wide")

# ------------------ STYLING ------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f172a, #020617);
    color: white;
}
[data-testid="stSidebar"] {
    background: #020617;
}
</style>
""", unsafe_allow_html=True)

# ------------------ GEMINI ------------------
client = genai.Client(api_key="AIzaSyC2jh7XpqyphsEU7SMyNHuMxiRQwjNE3KU")

def ask_ai(prompt):
    for _ in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents=prompt
            )
            return response.text
        except Exception as e:
            if "503" in str(e):
                time.sleep(2)
            else:
                return f"AI ERROR:\n{e}"
    return "⚠️ AI busy. Try again."

# ------------------ SIDEBAR ------------------
st.sidebar.title("📚 AI Exam System")

menu = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Progress Analysis", "Study Planner", "AI Prep Assistant"]
)

# ------------------ SESSION STATE ------------------
if "notes_output" not in st.session_state:
    st.session_state.notes_output = ""
if "show_answers" not in st.session_state:
    st.session_state.show_answers = False
if "plan_output" not in st.session_state:
    st.session_state.plan_output = ""

# ------------------ HOME ------------------
if menu == "Dashboard":
    st.markdown("""
    <h1>🎯 AI Exam Preparation System</h1>
    <p style='color:#94a3b8;'>Analyze performance • Detect weak areas • Generate AI strategies</p>
    """, unsafe_allow_html=True)

    st.info("This system uses Generative AI to assist students in exam preparation.")

# ------------------ ANALYZE ------------------
elif menu == "Progress Analysis":
    st.header("📊 Performance Analysis")

    st.subheader("Enter Your Subjects")

    # Number of subjects
    num_subjects = st.number_input("Number of Subjects", min_value=1, max_value=10, value=3)

    subjects = []
    data = {}
    scores = []
    weak_subjects = []

    st.markdown("---")

    # Input loop
    for i in range(num_subjects):
        st.subheader(f"Subject {i+1}")

        name = st.text_input(f"Subject Name {i+1}", key=f"name_{i}")

        marks = st.slider(
            f"{name or 'Subject'} Marks (out of 70)",
            0, 70, 40,
            key=f"marks_{i}"
        )

        hours = st.slider(
            f"{name or 'Subject'} Study Hours",
            0, 10, 2,
            key=f"hours_{i}"
        )

        if name:
            subjects.append(name)
            data[name] = {"Marks": marks, "Hours": hours}

    st.markdown("---")

    # 🔥 ANALYZE BUTTON
    if st.button("Analyze Performance 🚀"):

        for subject in subjects:
            marks = data[subject]["Marks"]
            hours = data[subject]["Hours"]

            # Convert to percentage
            percentage = (marks / 70) * 100

            # Score calculation
            score = (percentage * 0.6) + (hours * 10 * 0.4)
            scores.append(score)

            # Weak logic
            if marks < 35:
                weak_subjects.append(f"{subject} (Low Marks)")
            elif hours < 3:
                weak_subjects.append(f"{subject} (Low Study Time)")

        if scores:
            avg_score = sum(scores) / len(scores)

            # 🔥 METRICS
            col1, col2, col3 = st.columns(3)
            col1.metric("Average Score", f"{int(avg_score)}%")
            col2.metric("Weak Subjects", len(weak_subjects))
            col3.metric("Total Subjects", len(subjects))

            st.markdown("---")

            # 🔥 CHART
            chart_data = pd.DataFrame({
                "Subjects": subjects,
                "Marks": [data[s]["Marks"] for s in subjects],
                "Hours": [data[s]["Hours"] for s in subjects]
            }).set_index("Subjects")

            st.subheader("📈 Performance Chart")
            st.bar_chart(chart_data)

            st.caption("Marks (out of 70) vs Study Hours")

            st.markdown("---")

            # 🔥 SHOW SUBJECT DETAILS
            st.subheader("📌 Subject Details")

            for subject in subjects:
                marks = data[subject]["Marks"]
                percentage = (marks / 70) * 100

                st.write(f"{subject}: {marks}/70 ({round(percentage,1)}%)")

            st.markdown("---")

            # 🔥 WEAK AREAS
            st.subheader("⚠️ Weak Areas")

            if weak_subjects:
                for sub in weak_subjects:
                    st.markdown(f"""
                    <div style="
                        background: rgba(255,0,0,0.1);
                        padding: 12px;
                        border-radius: 10px;
                        margin-bottom: 8px;
                        border-left: 4px solid red;">
                        ⚠️ <b>{sub}</b>
                    </div>
                    """, unsafe_allow_html=True)

                # 🤖 AI RECOMMENDATION
                st.subheader("🤖 AI Recommendation")

                prompt = f"""
                A student is weak in: {', '.join(weak_subjects)}.

                Suggest practical improvement strategies for each subject.
                Keep it short and actionable.
                """

                st.markdown(ask_ai(prompt))

            else:
                st.success("No major weaknesses detected!")

        else:
            st.warning("Please enter at least one subject name.")
# ------------------ STUDY PLAN ------------------
elif menu == "Study Planner":
    st.header("📘 AI Study Plan")

    weak_input = st.text_input("Weak Topics:", key="sp_input")
    study_hours = st.slider("Daily Study Hours", 0, 10, 2, key="sp_hours")
    marks = st.slider("Marks:", 0, 70, 60, key="sp_marks")

    if st.button("Generate Plan", key="plan_btn"):
        prompt = f"""
        You are an expert academic mentor.

        A student studies {study_hours} hours daily,
        has {marks}% marks,
        and weak topics: {weak_input}.

        Generate a structured study plan with:
        - Daily schedule
        - Revision strategy
        - Practice plan
        """

        st.session_state.plan_output = ask_ai(prompt)

    if st.session_state.plan_output:
        st.subheader("📘 Study Plan")
        st.markdown(st.session_state.plan_output)

# ------------------ NOTES AI ------------------
elif menu == "AI Prep Assistant":
    st.header("📚 AI Notes Assistant")

    notes = st.text_area("Paste notes here", key="notes_input")

    col1, col2, col3 = st.columns(3)

    if col1.button("Summarize"):
        st.session_state.notes_output = ask_ai(f"Summarize:\n{notes}")
        st.session_state.show_answers = False

    if col2.button("Key Points"):
        st.session_state.notes_output = ask_ai(f"Extract key points:\n{notes}")
        st.session_state.show_answers = False

    if col3.button("Generate Questions"):
        st.session_state.notes_output = ask_ai(f"""
        Generate only exam questions (no answers), numbered:
        {notes}
        """)
        st.session_state.show_answers = True

    if st.session_state.notes_output:
        st.subheader("📌 Output")
        st.markdown(st.session_state.notes_output)

    if st.session_state.show_answers:
        if st.button("Generate Answers 📖"):
            st.markdown(ask_ai(f"""
            Answer the following questions clearly:
            {st.session_state.notes_output}
            """))
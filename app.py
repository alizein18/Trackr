import streamlit as st
from groq import Groq
import json
import os
from datetime import date, datetime, timedelta
import pandas as pd

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

SYSTEM_PROMPT = """You are a personal health pattern detective called Trackr.
Your job is to find connections between a user's symptoms and their daily habits.

When a user reports a symptom, ask these 6 habit questions ONE AT A TIME:
1. How many hours did you sleep last night?
2. How many glasses of water have you had today?
3. Did you skip any meals today? If yes, which ones?
4. How many hours of screen time did you have today?
5. Did you do any exercise today?
6. On a scale of 1-10, how stressed are you today?

After the 6th answer, say exactly: "Got it, I'm logging this entry now."
Then give ONE specific, small action they can try today based on their answers.
Never give generic advice. Be warm, brief, and specific."""

def get_data_file(username):
    return f"logs_{username.lower().strip()}.json"

def load_logs(username):
    path = get_data_file(username)
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {"logs": []}

def save_log(username, symptom, habits):
    data = load_logs(username)
    entry = {
        "date": str(date.today()),
        "symptom": symptom,
        "habits": habits
    }
    data["logs"].append(entry)
    with open(get_data_file(username), "w") as f:
        json.dump(data, f, indent=2)

def get_pattern_report(username):
    data = load_logs(username)
    logs = data["logs"]
    if len(logs) < 2:
        return "⚠️ Log at least 2 entries to unlock pattern detection."
    log_summary = json.dumps(logs, indent=2)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": f"""You are a health pattern analyst.
Here are a user's symptom and habit logs:
{log_summary}

Find repeating patterns between symptoms and habits.
State each pattern clearly, give a confidence level (Strong/Moderate/Early signal),
and suggest ONE small habit change to test this week."""}]
    )
    return response.choices[0].message.content

def get_weekly_report(username):
    data = load_logs(username)
    logs = data["logs"]
    week_ago = str(date.today() - timedelta(days=7))
    weekly_logs = [l for l in logs if l["date"] >= week_ago]
    if not weekly_logs:
        return "⚠️ No entries found in the past 7 days. Start logging to get your weekly report!"
    log_summary = json.dumps(weekly_logs, indent=2)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": f"""You are a health coach generating a weekly wellness report.
Here are the user's logs from the past 7 days:
{log_summary}

Write a warm, personal weekly report that includes:
1. 📋 Overview — how many entries, what symptoms appeared most
2. 😴 Sleep — average sleep and whether it's affecting symptoms
3. 💧 Hydration — average water intake trend
4. ⚡ Energy & Stress — stress level trend this week
5. 🏆 Win of the week — one positive pattern or improvement
6. 🎯 Focus for next week — one specific habit to improve

Keep it conversational, honest, and encouraging. Under 300 words."""}]
    )
    return response.choices[0].message.content

def build_charts(username):
    data = load_logs(username)
    logs = data["logs"]
    if len(logs) < 2:
        st.info("Log at least 2 entries to see your charts.")
        return

    # Build DataFrame
    rows = []
    for log in logs:
        row = {"date": log["date"], "symptom": log["symptom"]}
        habits = log.get("habits", {})
        try:
            row["sleep"] = float(habits.get("sleep_hours", 0))
        except:
            row["sleep"] = 0
        try:
            row["water"] = float(habits.get("water_glasses", 0))
        except:
            row["water"] = 0
        try:
            row["stress"] = float(habits.get("stress_level", 0))
        except:
            row["stress"] = 0
        rows.append(row)

    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")

    # Symptom frequency
    st.markdown("#### 🤒 Most Common Symptoms")
    symptom_counts = df["symptom"].value_counts()
    st.bar_chart(symptom_counts)

    # Sleep over time
    st.markdown("#### 😴 Sleep Hours Over Time")
    st.line_chart(df.set_index("date")["sleep"])

    # Stress over time
    st.markdown("#### 😰 Stress Level Over Time")
    st.line_chart(df.set_index("date")["stress"])

    # Water over time
    st.markdown("#### 💧 Water Intake Over Time")
    st.line_chart(df.set_index("date")["water"])

# --- Page config ---
st.set_page_config(page_title="Trackr", page_icon="🔍")

# --- Login Screen ---
if "username" not in st.session_state:
    st.session_state.username = None

if not st.session_state.username:
    st.title("🔍 Trackr — Your Health Pattern Detective")
    st.caption("by Ali Zein")
    st.markdown("### Welcome! Who are you?")
    st.caption("Enter a username to access your personal health logs.")
    col1, col2 = st.columns([3, 1])
    with col1:
        username_input = st.text_input("Username", placeholder="e.g. ali, sara, john...")
    with col2:
        st.write("")
        st.write("")
        if st.button("Enter →", use_container_width=True):
            if username_input.strip():
                st.session_state.username = username_input.strip()
                st.rerun()
            else:
                st.error("Please enter a username.")
    st.stop()

# --- Main App ---
username = st.session_state.username
st.title("🔍 Trackr — Your Health Pattern Detective")
st.caption("by Ali Zein")
col1, col2 = st.columns([4, 1])
with col1:
    st.caption(f"Logged in as **{username}**")
with col2:
    if st.button("Log out"):
        st.session_state.clear()
        st.rerun()

# --- Session state init ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
if "habits" not in st.session_state:
    st.session_state.habits = {}
if "question_count" not in st.session_state:
    st.session_state.question_count = 0
if "symptom" not in st.session_state:
    st.session_state.symptom = ""
if "logged" not in st.session_state:
    st.session_state.logged = False

tab1, tab2, tab3 = st.tabs(["💬 Log Symptom", "📊 Patterns & Report", "📈 My Stats"])

with tab1:
    # Show reset button if entry was already logged
    if st.session_state.logged:
        st.success("✅ Entry saved! Ready to log another?")
        if st.button("➕ Log New Symptom"):
            st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            st.session_state.habits = {}
            st.session_state.question_count = 0
            st.session_state.symptom = ""
            st.session_state.logged = False
            st.rerun()
    else:
        # Display chat history
        chat_container = st.container()
        with chat_container:
            for msg in st.session_state.messages:
                if msg["role"] == "user":
                    st.chat_message("user").write(msg["content"])
                elif msg["role"] == "assistant":
                    st.chat_message("assistant").write(msg["content"])

        if user_input := st.chat_input("Type your symptom or answer..."):
            if not st.session_state.symptom:
                st.session_state.symptom = user_input
            st.session_state.messages.append({"role": "user", "content": user_input})

            habit_keys = ["sleep_hours", "water_glasses", "meals_skipped",
                          "screen_time_hours", "exercised", "stress_level"]
            if st.session_state.question_count < len(habit_keys):
                st.session_state.habits[habit_keys[st.session_state.question_count]] = user_input
                st.session_state.question_count += 1

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=st.session_state.messages
            )
            reply = response.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": reply})

            if "logging this entry now" in reply.lower() and not st.session_state.logged:
                save_log(username, st.session_state.symptom, st.session_state.habits)
                st.session_state.logged = True

            st.rerun()

with tab2:
    data = load_logs(username)
    st.caption(f"Total entries logged: {len(data['logs'])}")

    st.markdown("### 🔍 Pattern Detection")
    if st.button("Analyze My Patterns"):
        with st.spinner("Finding your patterns..."):
            report = get_pattern_report(username)
        st.markdown(report)

    st.divider()

    st.markdown("### 📋 Weekly Report")
    if st.button("Generate This Week's Report"):
        with st.spinner("Writing your weekly report..."):
            weekly = get_weekly_report(username)
        st.markdown(weekly)

with tab3:
    st.markdown("### 📈 Your Health Stats")
    build_charts(username)
# 🔍 Trackr — Your Health Pattern Detective

An AI agent that finds behavioral patterns behind your health symptoms.

## What It Does

Tell Trackr you have a headache. It asks 6 quick questions about your sleep, water intake, meals, screen time, exercise, and stress. Over time it connects the dots — "Every time you report fatigue, you slept under 6 hours AND skipped lunch."

Not generic wellness advice. Insights from **your own data**.

## Features

- 💬 Conversational AI intake flow
- 🔍 Pattern detection across your history
- 📋 Weekly AI wellness report
- 📈 Symptom & habit charts
- 👤 Multi-user accounts with separate logs

## Live Demo

👉 **[trackr-yourhealthagent.streamlit.app](https://trackr-yourhealthagent.streamlit.app)**

## Built With

- [Groq API](https://groq.com) — Llama 3 (free tier)
- [Streamlit](https://streamlit.io) — UI & deployment
- Python

## Run Locally

```bash
git clone https://github.com/alizein18/Trackr.git
cd Trackr
pip install -r requirements.txt
streamlit run app.py
```

Add your Groq API key to `.streamlit/secrets.toml`:
```toml
GROQ_API_KEY = "your_key_here"
```

## Author

**Ali Zein** — Computer Engineering Student @ LAU
[LinkedIn](www.linkedin.com/in/ali-zein-01183b368)
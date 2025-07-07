import os, re, json
import streamlit as st
from datetime import date
from dotenv import load_dotenv
from openai import OpenAI

# Try to load from .env (for local use)
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

# Prefer st.secrets (for cloud), fallback to os.getenv (for local)
API_KEY = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")

# Now use the API_KEY variable
st.write("API key loaded:", API_KEY[:5] + "..." if API_KEY else "❌ Not found")


client = OpenAI(api_key=API_KEY)

# --- OpenAI Function ---
def generate_ai_fields(ctx: dict) -> dict:
    prompt = f"""
You are an expert product manager assistant. Fill the AI sections of a PRD based on:

Feature Name: {ctx['feature_name']}
Task Code: {ctx['task_code']}
Owner: {ctx['owner']}
Creation Date: {ctx['creation_date']}

Return ONLY valid JSON with keys:
- business_goals
- pain_points
- technical_dependencies
- acceptance_criteria
- negative_cases
- glossary
- translations
"""
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You fill PRD AI sections in JSON."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
    )
    text = resp.choices[0].message.content
    m = re.search(r"(\{.*\})", text, re.DOTALL)
    return json.loads(m.group(1)) if m else {}

# --- App Layout ---
st.set_page_config("PRD Generator", layout="centered")
st.title("📜 PRD Brief Generator")

# --- Manual Form ---
with st.form("prd_form"):
    st.subheader("1. Загальна інформація")
    feature_name  = st.text_input("1.1 Назва фічі *", key="feature_name")
    task_code     = st.text_input("1.2 Task Code *", key="task_code")
    owner         = st.text_input("1.3 Відповідальний *", key="owner")
    creation_date = st.date_input("1.4 Дата створення", value=date.today(), key="creation_date")

    st.subheader("2. Опис та мотивація")
    st.text_area("2.1 Бізнес-цілі та метрики ✪", key="business_goals", height=100, disabled=True)
    st.text_area("2.2 Pain Points ✪", key="pain_points", height=100, disabled=True)

    st.subheader("3. Цільова аудиторія та контекст")
    st.text_area("3.1 User Segments", key="user_segments", height=100)
    st.text_area("3.2 Usage Scenarios", key="usage_scenarios", height=100)

    st.subheader("4. Передумови")
    st.text_area("Передумови (Preconditions)", key="preconditions", height=80)

    st.subheader("5. Основний сценарій")
    st.text_area("Main Flow", key="main_flow", height=120)

    st.subheader("6. Альтернативні сценарії")
    st.text_area("6.1 Alternative Flow A", key="alt_flow_a", height=80)
    st.text_area("6.2 Alternative Flow B", key="alt_flow_b", height=80)
    st.text_area("6.3 Edge Case C", key="edge_case_c", height=80)

    st.subheader("7. Технічні залежності ✪")
    st.text_area("Technical Dependencies", key="technical_dependencies", height=100, disabled=True)

    st.subheader("8. Acceptance Criteria ✪")
    st.text_area("Acceptance Criteria", key="acceptance_criteria", height=100, disabled=True)

    st.subheader("9. Negative Cases ✪")
    st.text_area("Negative Cases", key="negative_cases", height=100, disabled=True)

    st.subheader("10. Глосарій та переклади ✪")
    st.text_area("Glossary + Translations", key="glossary", height=100, disabled=True)

    submit = st.form_submit_button("🔁 Згенерувати AI-поля")

# --- On Submit ---
if submit:
    required = ["feature_name", "task_code", "owner"]
    if not all(st.session_state.get(k) for k in required):
        st.error("❗ Обов’язково заповніть поля: Назва фічі, Task Code, Відповідальний.")
    else:
        with st.spinner("⏳ Генеруємо поля за допомогою AI..."):
            ctx = {k: str(st.session_state[k]) for k in ["feature_name", "task_code", "owner", "creation_date"]}
            ai_fields = generate_ai_fields(ctx)

            for k, v in ai_fields.items():
                st.session_state[k] = v

        st.success("✅ Поля заповнено AI!")

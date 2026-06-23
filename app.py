import streamlit as st
import pandas as pd
from g4f.client import Client
import nest_asyncio
import re

nest_asyncio.apply()

st.set_page_config(
    page_title="InsightBot AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stApp {
        background-color: #16161a;
        color: #fffffe;
    }

    [data-testid="stSidebar"] {
        background-color: #0f0f12;
        border-right: 1px solid #24242b;
    }

    [data-testid="stChatMessage"]:nth-child(even) {
        background-color: #24242b !important;
        border-radius: 16px !important;
        padding: 15px !important;
        margin-bottom: 15px !important;
        border: 1px solid #2d2d38;
    }

    [data-testid="stChatMessage"]:nth-child(odd) {
        background-color: transparent !important;
        padding: 15px !important;
        margin-bottom: 15px !important;
    }

    [data-testid="stChatInput"] {
        background-color: #24242b !important;
        border: 1px solid #3c3c4d !important;
        border-radius: 24px !important;
    }

    [data-testid="stChatInput"] textarea {
        color: #ffffff !important;
    }

    h1, h2, h3 {
        color: #ffffff !important;
        font-family: 'Segoe UI', system-ui, sans-serif;
    }

    .company-title {
        text-align: center;
        font-weight: 700;
        color: #ffffff !important;
        margin-top: 10px;
    }

    .company-sub {
        text-align: center;
        color: #94a1b2;
        font-size: 13px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<h2 class='company-title'>🧠 InsightBot AI</h2>", unsafe_allow_html=True)
    st.markdown("<p class='company-sub'>BOT Data Analysis System</p>", unsafe_allow_html=True)
    st.markdown("---")

    st.subheader("🛠️ التحكم")

    if st.button("🔄 مسح الشات الحالي", use_container_width=True):
        st.session_state.messages = [{
            "role": "assistant",
            "content": "أهلاً بك في نظام معالجة وتحليل البيانات الذكي! تم تصفير المحادثة وجاهز لتحليل بياناتك الآن."
        }]
        st.rerun()

    st.markdown("---")
    st.caption("📊 الملف النشط: `walmart_USA_Terms.xlsx`")
    st.caption("🤖 المحرك الحر: `GPT-4o Engine`")

st.markdown(
    "<h1 style='font-size:2.2rem;font-weight:700;'>⚡ Smart Data Assistant</h1>",
    unsafe_allow_html=True
)

st.markdown(
    "<p style='color:#94a1b2;font-size:15px;'>The fastest engine in data analysis and business intelligence.</p>",
    unsafe_allow_html=True
)

st.markdown("---")

client = Client()

@st.cache_data
def load_data():
    try:
        df = pd.read_excel("D:\\walmart_USA_Terms.xlsx")
        df.columns = df.columns.str.strip()
        return df
    except:
        return None

df = load_data()

if df is None:
    st.error("❌ مش قادر ألاقي ملف البيانات في المسار المكتوب D:\\walmart_USA_Terms.xlsx")
    st.stop()

def ask_ai_to_generate_code(user_query, df_columns):
    # فحص سريع إذا كانت الرسالة عبارة عن كلمة شكر قبل استهلاك الـ API
    thanks_words = ['شكرا', 'شكراً', 'شكر', 'تسلم', 'كتر خيرك', 'مشكور', 'thanks', 'thank you', 'تسلم ايدك']
    if any(word in user_query.lower() for word in thanks_words):
        return "USER_SAY_THANKS"

    prompt = f"""
You are an expert data analyst.
Write ONLY python pandas code to answer the user's query.

DataFrame name: df
Columns: {list(df_columns)}

User Query:
{user_query}

Return ONLY one python markdown block.
Store the final answer in a variable called result.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"ERROR_FROM_SYSTEM: {e}"

def execute_generated_code(code_string, df):
    # التعامل مع الرد على كلمات الشكر بشكل ذكي ومباشر
    if code_string == "USER_SAY_THANKS":
        return "العفو يا غالي! أنا هنا لمساعدتك في أي وقت. لو عندك أي أسئلة تانية عن البيانات اتفضل اسألني فوراً! 😉"

    if "ERROR_FROM_SYSTEM" in code_string:
        return "⚠️ السيرفر مضغوط، حاول مرة أخرى."

    code_match = re.search(r"```python\s*(.*?)\s*```", code_string, re.DOTALL)
    code_to_run = code_match.group(1) if code_match else code_string.strip()

    if not code_to_run or len(code_to_run) < 5:
        return "⚠️ لم أفهم السؤال."

    local_vars = {
        "df": df,
        "pd": pd
    }

    try:
        exec(code_to_run, {}, local_vars)
        return local_vars.get("result", "لا توجد نتيجة.")
    except:
        return "⚠️ لا أستطيع تنفيذ هذا السؤال على البيانات الحالية."

if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "أهلاً بك في نظام معالجة وتحليل البيانات الذكي! اسألني أي سؤال عن البيانات."
    }]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if isinstance(message["content"], (pd.DataFrame, pd.Series)):
            st.dataframe(message["content"], use_container_width=True)
        else:
            st.write(str(message["content"]))

if user_query := st.chat_input("اسألني عن المبيعات أو الأرباح أو العملاء..."):

    with st.chat_message("user"):
        st.write(user_query)

    st.session_state.messages.append({
        "role": "user",
        "content": user_query
    })

    with st.spinner("📊 جاري تحليل البيانات..."):
        generated_code = ask_ai_to_generate_code(user_query, df.columns)
        bot_response = execute_generated_code(generated_code, df)

    with st.chat_message("assistant"):
        if isinstance(bot_response, (pd.DataFrame, pd.Series)):
            st.dataframe(bot_response, use_container_width=True)
        else:
            st.write(str(bot_response))

    st.session_state.messages.append({
        "role": "assistant",
        "content": bot_response
    })

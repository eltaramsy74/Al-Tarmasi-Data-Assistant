import streamlit as st
import pandas as pd
from g4f.client import Client
import nest_asyncio
import re

# تفعيل الـ asyncio عشان يشتغل مع ستريمليت المستقر
nest_asyncio.apply()

# إعدادات واجهة ستريمليت
st.set_page_config(page_title="Al-Tarmasi Data Assistant", page_icon="🧠", layout="centered")

st.title("🧠 (Al-Tarmasi Company)")
st.write("The fastest company in data analysis!")

# تشغيل العميل البديل الحر بدون API Key خالص!
client = Client()

# تحميل البيانات وتخزينها
@st.cache_data
def load_data():
    try:
        df = pd.read_excel('D:\\walmart_USA_Terms.xlsx')
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        return None

df = load_data()

if df is None:
    st.error("❌ مش قادر ألاقي ملف البيانات في المسار المكتوب D:\\walmart_USA_Terms.xlsx")
    st.stop()

def ask_ai_to_generate_code(user_query, df_columns):
    prompt = f"""
    You are an expert data analyst. Write ONLY python pandas code to answer the user's query based on a DataFrame named `df`.
    DataFrame Columns: {list(df_columns)}
    User Query: {user_query}
    
    CRITICAL: Output ONLY valid python code wrapped inside a single ```python ``` markdown block. No explanations, no talk. Save the final output to a variable named `result`.
    """
    try:
        # السحب من موديل gpt-4o المفتوح المستقر والمجاني بالكامل
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"ERROR_FROM_SYSTEM: {str(e)}"

def execute_generated_code(code_string, df):
    if "ERROR_FROM_SYSTEM" in code_string:
        return "⚠️ السيرفر مضغوط ثواني، جرب اضغط إنتر تاني حالا."
        
    code_match = re.search(r"```python\s*(.*?)\s*```", code_string, re.DOTALL)
    code_to_run = code_match.group(1) if code_match else code_string.strip()
    
    if not code_to_run or len(code_to_run) < 5:
        return "⚠️ مأفهمتش سؤالك بالظبط بخصوص الداتا، ممكن توضح سؤالك أكتر؟"

    local_vars = {'df': df, 'pd': pd}
    try:
        exec(code_to_run, {}, local_vars)
        return local_vars.get('result', "لم يتم العثور على نتيجة.")
    except Exception as e:
        return "⚠️ اكتبلي السؤال بشكل تاني أو أوضح (مثال: أعلى ولاية مبيعات)."

# إدارة جلسة الشات وتأمينها - تم تعديل الرسالة الترحيبية لتكون رسمية
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "أهلاً بك في نظام Al-Tarmasi الذكي! يمكنك البدء بطرح أي سؤال بخصوص ملف البيانات وسأقوم بتحليله فوراً."}]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if isinstance(message["content"], (pd.DataFrame, pd.Series)):
            st.dataframe(message["content"], use_container_width=True)
        else:
            st.write(str(message["content"]))

if user_query := st.chat_input("اكتب سؤالك هنا..."):
    with st.chat_message("user"): 
        st.write(user_query)
    st.session_state.messages.append({"role": "user", "content": user_query})
    
    with st.spinner("بحلل البيانات في ثواني... 📊"):
        generated_code = ask_ai_to_generate_code(user_query, df.columns)
        bot_response = execute_generated_code(generated_code, df)
            
    with st.chat_message("assistant"):
        if isinstance(bot_response, (pd.DataFrame, pd.Series)):
            st.dataframe(bot_response, use_container_width=True)
        else:
            st.write(str(bot_response))
            
    st.session_state.messages.append({"role": "assistant", "content": bot_response})
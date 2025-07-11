import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from fuzzywuzzy import process

# ========== Google Sheet Setup ==========
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

try:
    sheet = client.open("AniGPT_DB").worksheet("Memory")
except Exception as e:
    st.error(f"❌ Sheet open error: {e}")
    st.stop()

# ========== Load Previous Prompts ==========
data = sheet.get_all_records()
prompts = [row["Prompt"] for row in data]
responses = [row["Response"] for row in data]

# ========== AniGPT Reply Logic ==========
def anigpt_reply(user_input):
    if not prompts:
        return "Mujhe kuch bhi yaad nahi bhai... tu kuch sikhade!"

    match = process.extractOne(user_input, prompts)
    if match and match[1] >= 70:
        return responses[prompts.index(match[0])]
    else:
        return "Mujhe iska jawab nahi pata bhai... tu sikha de?"

# ========== UI ==========
st.set_page_config(page_title="AniGPT", page_icon="🤖")
st.title("🤖 AniGPT - Tera Bhai AI")

msg = st.text_input("🧑 Tu:", key="input")
if msg:
    reply = anigpt_reply(msg)
    st.write("🤖 AniGPT:", reply)

    # Teach AniGPT if it doesn't know
    if "sikha de" in reply:
        new_response = st.text_input("🧠 Tu (iska jawab likh):", key="teach")
        if new_response:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sheet.append_row([msg, new_response, now])
            st.success("✅ Bhai yaad rakh liya maine!")

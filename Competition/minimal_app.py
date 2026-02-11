import streamlit as st

st.set_page_config(page_title="Minimal Test", page_icon="🧪")

st.title("🧪 Minimal Test App")
st.write("If you see this, Streamlit Cloud is working correctly!")
st.write("The issue is likely inside `app.py` dependencies.")

print("✅ Minimal app started successfully!", flush=True)

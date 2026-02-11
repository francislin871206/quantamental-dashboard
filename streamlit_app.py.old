"""
Streamlit App Entry Point
This file serves as the entry point for Streamlit Cloud deployment.
It adds the necessary paths and loads the main dashboard.
"""

import sys
import os

print("Starting Streamlit App...")

# Add quant_engine directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
quant_engine_dir = os.path.join(current_dir, 'quant_engine')
sys.path.insert(0, current_dir)
sys.path.insert(0, quant_engine_dir)

print(f"Added {quant_engine_dir} to sys.path")

dashboard_path = os.path.join(quant_engine_dir, 'dashboard.py')
print(f"Loading dashboard from {dashboard_path}")

try:
    with open(dashboard_path, encoding='utf-8') as f:
        code = f.read()
    exec(code)
    print("Dashboard loaded successfully")
except Exception as e:
    print(f"Error loading dashboard: {e}")
    import traceback
    traceback.print_exc()
    import streamlit as st
    st.error(f"Critical Error: {e}")
    st.code(traceback.format_exc())


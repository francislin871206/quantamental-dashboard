"""
Streamlit App Entry Point
This file serves as the entry point for Streamlit Cloud deployment.
It adds the necessary paths and imports the main dashboard.
"""

import sys
import os
import importlib.util

# Add quant_engine directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
quant_engine_dir = os.path.join(current_dir, 'quant_engine')

# Add paths to sys.path
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
if quant_engine_dir not in sys.path:
    sys.path.insert(0, quant_engine_dir)

# Import the dashboard module directly
# This is safer than exec() and preserves the module namespace
try:
    from quant_engine import dashboard
except ImportError as e:
    import streamlit as st
    st.error(f"Failed to import dashboard module: {e}")
    st.stop()
except Exception as e:
    import streamlit as st
    st.error(f"An error occurred while loading the dashboard: {e}")
    st.stop()


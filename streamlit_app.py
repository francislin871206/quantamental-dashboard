"""
Streamlit App Entry Point
This file serves as the entry point for Streamlit Cloud deployment.
It adds the necessary paths and imports the main dashboard.
"""

import sys
import os

# Add quant_engine directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
quant_engine_dir = os.path.join(current_dir, 'quant_engine')
sys.path.insert(0, current_dir)
sys.path.insert(0, quant_engine_dir)

# Now run the dashboard by executing its code
exec(open(os.path.join(quant_engine_dir, 'dashboard.py')).read())

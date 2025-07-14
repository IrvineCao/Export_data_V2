# utils/session.py
import streamlit as st

def initialize_session():
    """Khởi tạo các giá trị cần thiết trong session state nếu chúng chưa tồn tại."""
    defaults = {
        'username': None,
        'stage': 'initial',
        'params': {},
        'df_preview': None,
        'download_info': {},
        'user_message': None,
        'dev_logs': [],
        'dev_mode_activated': False
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
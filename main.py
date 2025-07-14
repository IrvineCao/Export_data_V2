# main.py
import streamlit as st
from utils.session import initialize_session
from utils.auth import Authenticator

st.set_page_config(
    page_title="Data Exporter Pro",
    page_icon="🚀",
    layout="wide"
)

initialize_session()
auth = Authenticator()

def render_homepage():
    st.markdown("<h1 style='text-align: center;'>Welcome to Data Exporter Pro</h1>", unsafe_allow_html=True)
    st.divider()
    # Thêm phần giới thiệu...
    st.info("👈 **Ready to start?** Select a report from the navigation menu on the left!", icon="🎉")

auth.render_sidebar()

if st.session_state.get('username'):
    render_homepage()
else:
    st.warning("Please log in from the sidebar to continue.")

auth.render_dev_mode()
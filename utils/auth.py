# utils/auth.py
import streamlit as st
import os
import base64

class Authenticator:
    """Xử lý logic đăng nhập/đăng xuất và chế độ nhà phát triển."""

    def render_sidebar(self):
        """Hiển thị sidebar đăng nhập/đăng xuất."""
        st.sidebar.markdown("---")
        if st.session_state.get('username'):
            st.sidebar.success(f"Logged in as: **{st.session_state.username}**")
            if st.sidebar.button("Logout"):
                self._logout()
        else:
            self._show_login_form()

    def _logout(self):
        # Giữ lại log khi logout
        dev_logs = st.session_state.get('dev_logs', [])
        dev_activated = st.session_state.get('dev_mode_activated', False)
        
        st.session_state.clear() # Xóa toàn bộ session
        
        # Khôi phục lại các giá trị cần thiết
        st.session_state.dev_logs = dev_logs
        st.session_state.dev_mode_activated = dev_activated
        st.rerun()

    def _show_login_form(self):
        st.sidebar.subheader("Login")
        name_input = st.sidebar.text_input("Please enter your name", key="name_input")
        if st.sidebar.button("Start Session"):
            if name_input:
                st.session_state.username = name_input
                st.rerun()
            else:
                st.sidebar.warning("Name cannot be empty.")

    def render_dev_mode(self):
        st.sidebar.markdown("---")
        SECRET_CODE = "irvine" 
        dev_code = st.sidebar.text_input("Developer Access", type="password", key="dev_access_code")

        if dev_code == SECRET_CODE:
            st.session_state.dev_mode_activated = True

        if st.session_state.get('dev_mode_activated', False):
            st.sidebar.subheader("🛠️ Developer Log")
            if st.sidebar.button("Clear Logs & Deactivate"):
                st.session_state.dev_logs = []
                st.session_state.dev_mode_activated = False
                st.rerun()
                
            if not st.session_state.get('dev_logs'):
                st.sidebar.info("No technical errors have been logged.")
            else:
                for log in st.session_state.dev_logs:
                    with st.sidebar.expander(f"**{log['timestamp']} - {log['error_type']}**"):
                        st.error(log['message'])
                        st.code(log['traceback'], language='python')
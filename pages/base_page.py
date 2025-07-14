import streamlit as st
from abc import ABC, abstractmethod
from utils.managers import SessionManager, DataManager
from utils.ui import UIManager

class Page(ABC):
    """Lớp cơ sở trừu tượng cho tất cả các trang trong ứng dụng."""
    def __init__(self):
        self.session_manager = SessionManager
        self.data_manager = DataManager()
        self.ui_manager = UIManager
        self.session_manager.initialize() # Đảm bảo state được khởi tạo

    def render(self):
        """Phương thức chính để render trang."""
        if not self.session_manager.get('username'):
            st.warning("Vui lòng đăng nhập ở thanh bên để bắt đầu.")
            st.stop()
        
        self._render_content()

    @abstractmethod
    def _render_content(self):
        """Phương thức trừu tượng, các lớp con phải triển khai."""
        pass
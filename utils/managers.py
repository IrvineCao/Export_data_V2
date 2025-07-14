import streamlit as st
import pandas as pd
from sqlalchemy import text
from .database import DatabaseManager # <-- Sửa lại thành relative import cho gọn
from data_logic import kwl_data, kw_pfm_data, product_tracking_data

class SessionManager:
    """
    Quản lý st.session_state một cách có cấu trúc.
    Tất cả các phương thức đều là static để có thể gọi trực tiếp từ lớp.
    """
    @staticmethod
    def initialize():
        """Khởi tạo các giá trị cần thiết trong session state nếu chúng chưa tồn tại."""
        defaults = {
            'stage': 'initial',
            'df_preview': None,
            'params': {},
            'username': None
        }
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

    @staticmethod
    def get(key, default=None):
        """Lấy một giá trị từ session state."""
        return st.session_state.get(key, default)

    @staticmethod
    def set(key, value):
        """Gán một giá trị vào session state."""
        st.session_state[key] = value

    @staticmethod
    def clear_export_state():
        """
        Reset các state liên quan đến quy trình export.
        ✅ ĐÚNG: Phương thức này không nhận bất kỳ tham số nào.
        """
        st.session_state['stage'] = 'initial'
        st.session_state['df_preview'] = None
        st.session_state['params'] = {}

class DataManager:
    """Chịu trách nhiệm xử lý logic lấy và xử lý dữ liệu."""
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.query_map = {
            'kwl': kwl_data.get_query,
            'kw_pfm': kw_pfm_data.get_query,
            'pt': product_tracking_data.get_query,
        }

    # ... (Các phương thức còn lại của DataManager giữ nguyên) ...
    def _get_query_string(self, data_source: str, query_type: str) -> str:
        get_query_func = self.query_map.get(data_source)
        if not get_query_func:
            raise ValueError(f"Nguồn dữ liệu không hợp lệ: {data_source}")
        return get_query_func(query_type)

    def fetch_data(self, query_type: str, data_source: str, limit: int = None, **kwargs):
        """Thực hiện truy vấn và trả về DataFrame."""
        query_str = self._get_query_string(data_source, query_type)
        params_to_bind = kwargs.copy()

        if 'storefront_ids' in params_to_bind:
            ids = params_to_bind['storefront_ids']
            if not ids: # Xử lý trường hợp list rỗng
                return pd.DataFrame()
            ids_string = str(tuple(ids)) if len(ids) > 1 else f"('{ids[0]}')"
            query_str = query_str.replace(':storefront_ids', ids_string)
            del params_to_bind['storefront_ids']

        if limit and query_type == 'data':
            query_str += f" LIMIT {limit}"

        try:
            with self.db_manager.get_session() as db:
                df = pd.read_sql(text(query_str), db.connection(), params=params_to_bind)
                return df
        except Exception as e:
            st.error(f"Lỗi khi truy vấn dữ liệu: {e}")
            return pd.DataFrame()

    def count_rows(self, data_source: str, **kwargs) -> int:
        """Đếm số dòng dữ liệu."""
        count_df = self.fetch_data('count', data_source, **kwargs)
        if not count_df.empty:
            return count_df.iloc[0, 0]
        return 0
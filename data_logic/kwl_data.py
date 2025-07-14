from pathlib import Path
import streamlit as st

def _get_query_from_file(file_path: str) -> str:
    """Helper function to read SQL file safely."""
    try:
        # Xây dựng đường dẫn tuyệt đối từ file hiện tại để đảm bảo luôn đúng
        path = Path(__file__).resolve().parent.parent / "sql" / file_path
        if not path.is_file():
            raise FileNotFoundError(f"SQL file not found at the constructed path: {path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError as e:
        # Hiển thị lỗi ngay trên giao diện để dễ dàng debug
        st.error(f"Fatal Error: Could not read a critical SQL file. Details: {e}")
        return "" 

query_params = {
    "count": _get_query_from_file("kwl_count.sql"),
    "data": _get_query_from_file("kwl_data.sql"),
}

def get_query(query_name: str) -> str:
    """Gets a query by name from the pre-loaded dictionary."""
    return query_params.get(query_name, "")
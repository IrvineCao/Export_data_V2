import os
import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
from dotenv import load_dotenv

class DatabaseManager:
    """
    Quản lý kết nối đến cơ sở dữ liệu SingleStoreDB.
    Sử dụng mẫu Singleton để đảm bảo chỉ có một instance được tạo.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            load_dotenv()
            cls._instance._connect()
        return cls._instance

    def _connect(self):
        """Khởi tạo engine và SessionLocal."""
        DB_USER = os.getenv("DB_USER")
        DB_PASSWORD = os.getenv("DB_PASSWORD")
        DB_HOST = os.getenv("DB_HOST")
        DB_PORT = os.getenv("DB_PORT")
        DB_NAME = os.getenv("DB_NAME")

        if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME]):
            st.error("Lỗi cấu hình CSDL: Một hoặc nhiều biến môi trường bị thiếu.")
            st.stop()

        db_url = f"singlestoredb://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

        try:
            self.engine = create_engine(
                db_url,
                poolclass=QueuePool,
                pool_size=10,
                max_overflow=5,
                pool_timeout=30,
                pool_recycle=1800
            )
            self._SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            # Kiểm tra kết nối
            with self.engine.connect() as connection:
                st.sidebar.info("Database Connected Successfully.")
        except Exception as e:
            st.error(f"Không thể kết nối CSDL: {e}")
            st.stop()


    @contextmanager
    def get_session(self):
        """Cung cấp một session CSDL và tự động đóng nó."""
        db = self._SessionLocal()
        try:
            yield db
        finally:
            db.close()

# Cách sử dụng:
# db_manager = DatabaseManager()
# with db_manager.get_session() as session:
    # thực hiện truy vấn
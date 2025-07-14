# utils/managers.py
import streamlit as st
import pandas as pd
from sqlalchemy import text
from sqlalchemy.exc import OperationalError, ProgrammingError
from utils.database import DatabaseManager # Đảm bảo bạn có file này
from data_logic import kwl_data, kw_pfm_data, product_tracking_data


class ValidationManager:
    """Chịu trách nhiệm xác thực tất cả các đầu vào của người dùng."""
    def __init__(self, workspace_id, storefront_input, start_date, end_date):
        self.workspace_id = workspace_id
        self.storefront_input = storefront_input
        self.start_date = start_date
        self.end_date = end_date
        self.errors = []

    def validate(self):
        self._validate_workspace()
        self._validate_storefronts()
        self._validate_dates()
        return self.errors

    def _validate_workspace(self):
        workspace_id_list = [s.strip() for s in self.workspace_id.split(",") if s.strip()]
        if not workspace_id_list:
            self.errors.append("Workspace ID is required")
        elif len(workspace_id_list) > 1:
            self.errors.append("You can only enter one workspace ID.")
        elif not all(s.isdigit() for s in workspace_id_list):
            self.errors.append("Workspace ID must be numeric.")

    def _validate_storefronts(self):
        storefront_input_list = [s.strip() for s in self.storefront_input.split(",") if s.strip()]
        if not storefront_input_list:
            self.errors.append("Storefront EID is required")
        elif len(storefront_input_list) > 5:
            self.errors.append("You can only enter up to 5 storefront IDs.")
        elif not all(s.isdigit() for s in storefront_input_list):
            self.errors.append("Storefront EID must be numeric.")
    
    def _validate_dates(self):
        if self.start_date > self.end_date:
            self.errors.append("Start date cannot be after end date.")
        else:
            ids = [s.strip() for s in self.storefront_input.split(',') if s.strip()]
            num_storefronts = len(ids)
            date_range_days = (self.end_date - self.start_date).days
            max_days_allowed = 60 if num_storefronts <= 2 else 30
            if date_range_days > max_days_allowed:
                self.errors.append(f"With {num_storefronts} storefront(s), the max period is {max_days_allowed} days.")

class DataManager:
    """Chịu trách nhiệm cho tất cả các hoạt động truy vấn CSDL."""
    QUERY_MAP = {'kwl': kwl_data.get_query, 'kw_pfm': kw_pfm_data.get_query, 'pt': product_tracking_data.get_query}

    def __init__(self, data_source: str):
        self.data_source = data_source
        self.db_manager = DatabaseManager()
        if data_source not in self.QUERY_MAP: raise ValueError(f"Unknown data source: {data_source}")
        self.get_query_func = self.QUERY_MAP[data_source]

    def _fetch(self, query_type: str, params: dict, limit: int = None):
        query_str = self.get_query_func(query_type)
        if not query_str or not query_str.strip(): raise FileNotFoundError(f"SQL query for '{self.data_source}' ('{query_type}') is empty.")
        if limit: query_str += f" LIMIT {int(limit)}"
        with self.db_manager.get_session() as db:
            return pd.read_sql(text(query_str), db.connection(), params=params)

    def get_count(self, params: dict):
        count_df = self._fetch('count', params)
        return count_df.iloc[0, 0] if not count_df.empty else 0

    def get_data(self, params: dict, limit: int = None):
        return self._fetch('data', params, limit=limit)

class ExportProcessManager:
    """Điều phối toàn bộ quy trình từ input đến khi sẵn sàng export."""
    def __init__(self, data_source: str, inputs: dict):
        self.data_source = data_source
        self.inputs = inputs
        self.params = {}

    def run(self):
        validator = ValidationManager(self.inputs.get('workspace_id'), self.inputs.get('storefront_input'), self.inputs.get('start_date'), self.inputs.get('end_date'))
        errors = validator.validate()
        if errors:
            st.session_state.user_message = {"type": "error", "text": "\n\n".join(errors)}
            st.session_state.stage = 'initial'
            return
        self._build_params()
        try:
            with st.spinner("Checking data size..."):
                data_manager = DataManager(self.data_source)
                num_row = data_manager.get_count(self.params)
                st.session_state.params['num_row'] = num_row
            if num_row == 0:
                st.session_state.user_message = {"type": "warning", "text": "No data found."}
                st.session_state.stage = 'initial'
            elif num_row > 50000:
                st.session_state.user_message = {"type": "error", "text": f"Data is too large ({num_row:,} rows)."}
                st.session_state.stage = 'initial'
            else:
                st.session_state.stage = 'loading_preview'
        except (OperationalError, ProgrammingError, Exception) as e:
            st.session_state.user_message = {"type": "error", "text": "A technical error occurred. See Dev Log."}
            st.session_state.stage = 'initial'

    def _build_params(self):
        self.params = {
            "workspace_id": int(self.inputs.get('workspace_id')),
            "storefront_ids": [int(eid.strip()) for eid in self.inputs.get('storefront_input').split(',')],
            "start_date": self.inputs.get('start_date').strftime('%Y-%m-%d'),
            "end_date": self.inputs.get('end_date').strftime('%Y-%m-%d'),
            "data_source": self.data_source,
            **self.inputs.get('options', {})
        }
        st.session_state.params = self.params
# pages/1_Keyword_Lab.py
import streamlit as st
from utils.session import initialize_session
from utils.managers import DataManager, ExportProcessManager
from utils.ui import (
    create_input_form, 
    display_user_message, 
    display_data_summary_and_preview,
    display_export_buttons,
    display_download_section
)

# Giả sử bạn có hàm tiện ích này trong một file logic riêng
# utils/logic.py hoặc có thể đặt nó ở đây nếu chỉ dùng cho export
def convert_df_to_csv(df):
    return df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')

st.set_page_config(page_title="Keyword Lab", layout="wide")
initialize_session()

DATA_SOURCE_KEY = 'kwl'

st.title("📊 Keyword Level Data Export")
st.markdown("---")

display_user_message()

workspace_id, storefront_input, start_date, end_date, _ = create_input_form(source_key=DATA_SOURCE_KEY)

if st.button("Get Data", key=f'get_data_{DATA_SOURCE_KEY}'):
    st.session_state.user_message = None
    if st.session_state.params.get('data_source') != DATA_SOURCE_KEY: st.session_state.stage = 'initial'
    process_inputs = {"workspace_id": workspace_id, "storefront_input": storefront_input, "start_date": start_date, "end_date": end_date}
    process_manager = ExportProcessManager(DATA_SOURCE_KEY, process_inputs)
    process_manager.run()
    st.rerun()

if st.session_state.params.get('data_source') == DATA_SOURCE_KEY:
    stage = st.session_state.get('stage', 'initial')
    if stage == 'loading_preview':
        with st.spinner("Loading preview..."):
            data_manager = DataManager(DATA_SOURCE_KEY)
            df_preview = data_manager.get_data(st.session_state.params, limit=500)
            st.session_state.df_preview = df_preview
            st.session_state.stage = 'loaded'
        st.rerun()
    elif stage == 'loaded' and st.session_state.df_preview is not None:
        display_data_summary_and_preview(st.session_state.df_preview, st.session_state.params)
        display_export_buttons()
    elif stage == 'exporting_full':
        with st.spinner("Exporting full data..."):
            data_manager = DataManager(DATA_SOURCE_KEY)
            full_df = data_manager.get_data(st.session_state.params)
            csv_data = convert_df_to_csv(full_df)
            st.session_state.download_info = {"data": csv_data, "file_name": f"{DATA_SOURCE_KEY}.csv"}
            st.session_state.stage = 'download_ready'
        st.rerun()
    elif stage == 'download_ready':
        display_download_section()
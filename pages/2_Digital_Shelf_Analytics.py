# pages/2_Digital_Shelf_Analytics.py
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

def convert_df_to_csv(df):
    return df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')

st.set_page_config(page_title="Digital Shelf Analytics", layout="wide")
initialize_session()

st.title("📈 Digital Shelf Analytics")

display_user_message()

tab1, tab2, tab3 = st.tabs(["Keyword Performance", "Product Tracking", "Competition Landscape"])

with tab1:
    st.header("Keyword Performance Data Export")
    DATA_SOURCE_KEY = 'kw_pfm'
    workspace_id, sf_input, s_date, e_date, pfm_opts = create_input_form(source_key=DATA_SOURCE_KEY, show_kw_pfm_options=True)
    if st.button("Get Keyword Performance Data", key=f'get_data_{DATA_SOURCE_KEY}'):
        if st.session_state.params.get('data_source') != DATA_SOURCE_KEY: st.session_state.stage = 'initial'
        inputs = {"workspace_id": workspace_id, "storefront_input": sf_input, "start_date": s_date, "end_date": e_date, "options": pfm_opts}
        process = ExportProcessManager(DATA_SOURCE_KEY, inputs)
        process.run()
        st.rerun()

with tab2:
    st.header("Product Tracking Data Export")
    DATA_SOURCE_KEY = 'pt'
    workspace_id, sf_input, s_date, e_date, _ = create_input_form(source_key=DATA_SOURCE_KEY)
    if st.button("Get Product Tracking Data", key=f'get_data_{DATA_SOURCE_KEY}'):
        if st.session_state.params.get('data_source') != DATA_SOURCE_KEY: st.session_state.stage = 'initial'
        inputs = {"workspace_id": workspace_id, "storefront_input": sf_input, "start_date": s_date, "end_date": e_date}
        process = ExportProcessManager(DATA_SOURCE_KEY, inputs)
        process.run()
        st.rerun()

with tab3:
    st.header("Competition Landscape")
    st.info("💡 Coming soon...")

current_data_source = st.session_state.params.get('data_source')
if current_data_source in ['kw_pfm', 'pt']:
    stage = st.session_state.get('stage', 'initial')
    if stage == 'loading_preview':
        with st.spinner("Loading preview..."):
            data_manager = DataManager(current_data_source)
            df_preview = data_manager.get_data(st.session_state.params, limit=500)
            st.session_state.df_preview = df_preview
            st.session_state.stage = 'loaded'
        st.rerun()
    elif stage == 'loaded' and st.session_state.df_preview is not None:
        display_data_summary_and_preview(st.session_state.df_preview, st.session_state.params)
        display_export_buttons()
    elif stage == 'exporting_full':
        with st.spinner("Exporting full data..."):
            data_manager = DataManager(current_data_source)
            full_df = data_manager.get_data(st.session_state.params)
            csv_data = convert_df_to_csv(full_df)
            st.session_state.download_info = {"data": csv_data, "file_name": f"{current_data_source}.csv"}
            st.session_state.stage = 'download_ready'
        st.rerun()
    elif stage == 'download_ready':
        display_download_section()
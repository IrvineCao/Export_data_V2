# utils/ui.py
import streamlit as st
from datetime import datetime, timedelta

def create_input_form(source_key: str, show_kw_pfm_options: bool = False):
    """Tạo form nhập liệu chuẩn."""
    ws_key = f"ws_id_{source_key}"
    sf_key = f"sf_id_{source_key}"
    
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    date_options = {
        "Last 30 days": {"start": today - timedelta(days=30), "end": yesterday},
        "This month": {"start": today.replace(day=1), "end": yesterday},
        "Last month": {
            "start": (today.replace(day=1) - timedelta(days=1)).replace(day=1),
            "end": today.replace(day=1) - timedelta(days=1)
        },
        "Custom time range": None
    }
    start_date, end_date, pfm_options = None, None, {}

    with st.container():
        main_cols = st.columns(3)
        with main_cols[0]:
            workspace_id = st.text_input("Workspace ID *", key=ws_key)
        with main_cols[1]:
            storefront_input = st.text_input("Storefront EID *", key=sf_key)
        with main_cols[2]:
            selected_option = st.selectbox(
                "Select time range *", options=list(date_options.keys()), index=0, key=f"date_preset_{source_key}"
            )

        if selected_option == "Custom time range":
            custom_date_cols = st.columns(2)
            with custom_date_cols[0]:
                start_date = st.date_input("Start Date", value=yesterday, max_value=yesterday, key=f"start_date_{source_key}")
            with custom_date_cols[1]:
                end_date = st.date_input("End Date", value=yesterday, max_value=yesterday, key=f"end_date_{source_key}")
        else:
            dates = date_options[selected_option]
            start_date, end_date = dates["start"], dates["end"]
        
        if show_kw_pfm_options:
            st.write("---")
            st.write("**Additional options:**")
            extra_cols = st.columns(3)
            with extra_cols[0]:
                pfm_options['device_type'] = st.selectbox("Device Type", ('Mobile', 'Desktop', 'All'), key=f'device_type_{source_key}')
            with extra_cols[1]:
                pfm_options['display_type'] = st.selectbox("Display Type", ('Paid', 'Organic','Top', 'All'), key=f'display_type_{source_key}')
            with extra_cols[2]:
                pfm_options['product_position'] = st.number_input("Product Position", min_value=-1, value=-1, key=f'product_pos_{source_key}')

    st.write("---")
    return workspace_id, storefront_input, start_date, end_date, pfm_options

def display_user_message():
    """Hiển thị thông báo (lỗi, cảnh báo) cho người dùng nếu có."""
    if 'user_message' in st.session_state and st.session_state.user_message:
        msg = st.session_state.user_message
        if msg['type'] == 'error':
            st.error(msg['text'])
        elif msg['type'] == 'warning':
            st.warning(msg['text'])
        st.session_state.user_message = None

def display_data_summary_and_preview(df_preview, params):
    """Hiển thị tóm tắt và bảng dữ liệu xem trước."""
    st.success("✅ Preview loaded successfully!")
    with st.expander("**Data Summary**", expanded=True):
        cols = st.columns(4)
        cols[0].metric("Total Rows", f"{params.get('num_row', 0):,}")
        cols[1].metric("Total Columns", len(df_preview.columns))
        cols[2].metric("Date Range", f"{(datetime.strptime(params['end_date'], '%Y-%m-%d') - datetime.strptime(params['start_date'], '%Y-%m-%d')).days + 1} days")
        cols[3].metric("Storefronts", len(params.get('storefront_ids', [])))
    st.subheader("Preview Data (first 500 rows)")
    st.dataframe(df_preview, use_container_width=True, height=350)

def display_export_buttons():
    """Hiển thị các nút để Export hoặc bắt đầu lại."""
    cols = st.columns(2)
    with cols[0]:
        if st.button("🚀 Export Full Data", use_container_width=True, type="primary"):
            st.session_state.stage = 'exporting_full'
            st.rerun()
    with cols[1]:
        if st.button("🔄 Start New Export", use_container_width=True):
            st.session_state.stage = 'initial'
            st.session_state.params = {}
            st.session_state.df_preview = None
            st.rerun()

def display_download_section():
    """Hiển thị nút Download và nút bắt đầu lại."""
    st.success("✅ Your full data export is ready to download!")
    info = st.session_state.get('download_info', {})
    st.download_button(
        label="📥 Download CSV Now",
        data=info.get('data', b''),
        file_name=info.get('file_name', 'export.csv'),
        mime='text/csv',
        use_container_width=True,
        type="primary",
    )
    if st.button("🔄 Start New Export", use_container_width=True):
        st.session_state.stage = 'initial'
        st.session_state.params = {}
        st.session_state.df_preview = None
        st.rerun()
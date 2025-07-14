import streamlit as st
from pages.base_page import Page

class DigitalShelfPage(Page):
    """
    Lớp "bộ điều khiển" cho trang Digital Shelf.
    Quản lý nhiều tab, mỗi tab là một nguồn dữ liệu khác nhau.
    """
    def __init__(self):
        super().__init__()
        # Không cần self.DATA_SOURCE_KEY ở đây vì mỗi tab sẽ có key riêng.

    def _render_content(self):
        """Dựng giao diện chính và các tab."""
        st.set_page_config(page_title="Digital Shelf", layout="wide")
        st.title("📈 Digital Shelf Analytics")
        st.markdown("---")

        tab1, tab2, tab3 = st.tabs(["Keyword Performance", "Product Tracking", "Competition Landscape"])

        # Tab 1: Keyword Performance
        with tab1:
            self._render_kw_performance_tab()

        # Tab 2: Product Tracking
        with tab2:
            self._render_product_tracking_tab()

        # Tab 3: Competition Landscape
        with tab3:
            st.header("Competition Landscape Data Export")
            st.info("💡 Coming soon...")

    def _render_kw_performance_tab(self):
        """Dựng nội dung cho tab Keyword Performance."""
        source_key = 'kw_pfm'
        st.header("Keyword Performance Data Export")

        # 1. Dựng UI: Gọi phương thức từ UIManager
        workspace_id, storefront_input, start_date, end_date, pfm_options = self.ui_manager.create_input_form(
            source_key=source_key,
            show_kw_pfm_options=True
        )

        # 2. Xử lý tương tác: Gắn logic xử lý cho nút bấm của riêng tab này
        if st.button("Preview KW Performance Data", key=f'preview_{source_key}'):
            self._handle_preview_click(
                workspace_id=workspace_id,
                storefront_input=storefront_input,
                start_date=start_date,
                end_date=end_date,
                data_source=source_key,
                options=pfm_options
            )

        # 3. Hiển thị kết quả: Chỉ hiển thị nếu data_source trong state khớp với tab này
        if self.session_manager.get('params', {}).get('data_source') == source_key:
            self.ui_manager.display_data_exporter(self.data_manager)


    def _render_product_tracking_tab(self):
        """Dựng nội dung cho tab Product Tracking."""
        source_key = 'pt'
        st.header("Product Tracking Data Export")

        # 1. Dựng UI
        workspace_id, storefront_input, start_date, end_date, _ = self.ui_manager.create_input_form(
            source_key=source_key
        )

        # 2. Xử lý tương tác
        if st.button("Preview Product Tracking Data", key=f'preview_{source_key}'):
            self._handle_preview_click(
                workspace_id=workspace_id,
                storefront_input=storefront_input,
                start_date=start_date,
                end_date=end_date,
                data_source=source_key
            )

        # 3. Hiển thị kết quả
        if self.session_manager.get('params', {}).get('data_source') == source_key:
            self.ui_manager.display_data_exporter(self.data_manager)


    def _handle_preview_click(self, workspace_id, storefront_input, start_date, end_date, data_source, options=None):
        """
        Phương thức xử lý chung cho CẢ HAI nút bấm.
        Nó nhận data_source để biết request đến từ tab nào.
        """
        self.session_manager.clear_export_state()

        if not all([workspace_id, storefront_input, start_date, end_date]):
            st.error("Vui lòng điền đầy đủ tất cả các trường.")
            return

        storefront_list = [eid.strip() for eid in storefront_input.split(',')]
        params = {
            "ws_id": workspace_id,
            "storefront_ids": storefront_list,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "data_source": data_source  # <-- Sử dụng data_source được truyền vào
        }
        
        # Thêm các options đặc biệt nếu có (từ tab kw_pfm)
        if options:
            params.update(options)

        log_activity("PREVIEW_DATA", details=f"Source: {data_source.upper()}, Params: {params}")

        self.session_manager.set('params', params)
        self.session_manager.set('stage', 'loading_preview')
        st.rerun()

# --- Entry Point của trang ---
if __name__ == "__main__":
    page = DigitalShelfPage()
    page.render()
import streamlit as st
from pages.base_page import Page 

class KeywordLabPage(Page):
    """
    Lớp này là "bộ điều khiển" cho trang Keyword Lab.
    Nó kế thừa tất cả các manager (data, session, ui) từ lớp Page cơ sở.
    """
    def __init__(self):
        # Kế thừa __init__ từ lớp cha (Page) để có sẵn các manager
        super().__init__()
        # Định danh duy nhất cho nguồn dữ liệu của trang này
        self.DATA_SOURCE_KEY = 'kwl'

    def _render_content(self):
        """
        Phương thức chính để dựng toàn bộ giao diện của trang.
        """
        st.set_page_config(page_title="Keyword Lab", layout="wide")
        st.title("📊 Keyword Level Data Export")
        st.markdown("---")

        # VIỆC 1: DỰNG GIAO DIỆN
        # Ủy thác việc tạo form cho UIManager.
        # Nó chỉ nhận về kết quả người dùng nhập vào.
        workspace_id, storefront_input, start_date, end_date, _ = self.ui_manager.create_input_form(
            source_key=self.DATA_SOURCE_KEY
        )

        # VIỆC 2: XỬ LÝ TƯƠNG TÁC
        # Gắn logic xử lý cho nút bấm.
        if st.button("Preview Data", key=f'preview_{self.DATA_SOURCE_KEY}'):
            self._handle_preview_click(
                workspace_id=workspace_id,
                storefront_input=storefront_input,
                start_date=start_date,
                end_date=end_date
            )

        # VIỆC 3: HIỂN THỊ KẾT QUẢ DỰA TRÊN STATE
        # Chỉ hiển thị phần kết quả nếu nó thuộc về trang này.
        if self.session_manager.get('params', {}).get('data_source') == self.DATA_SOURCE_KEY:
            self.ui_manager.display_data_exporter(self.data_manager)


    def _handle_preview_click(self, workspace_id, storefront_input, start_date, end_date):
        """
        Đây là logic cốt lõi của trang: Xử lý khi người dùng nhấn nút.
        """
        # Xóa trạng thái export cũ để bắt đầu luồng mới
        self.session_manager.clear_export_state()

        # 1. Kiểm tra đầu vào
        if not all([workspace_id, storefront_input, start_date, end_date]):
            st.error("Vui lòng điền đầy đủ tất cả các trường.")
            return

        storefront_list = [eid.strip() for eid in storefront_input.split(',')]
        params = {
            "ws_id": workspace_id,
            "storefront_ids": storefront_list,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "data_source": self.DATA_SOURCE_KEY # Đánh dấu đây là request từ trang KWL
        }

        # 2. Lưu tham số và chuyển stage sang 'loading_preview'
        self.session_manager.set('params', params)
        self.session_manager.set('stage', 'loading_preview')

        # 3. Yêu cầu Streamlit chạy lại để hiển thị spinner và bắt đầu tải dữ liệu
        st.rerun()

# --- Entry Point của trang ---
# Code này sẽ chạy khi người dùng điều hướng đến trang "Keyword Lab"
if __name__ == "__main__":
    page = KeywordLabPage()
    page.render() # Phương thức render() sẽ kiểm tra đăng nhập trước khi chạy _render_content()
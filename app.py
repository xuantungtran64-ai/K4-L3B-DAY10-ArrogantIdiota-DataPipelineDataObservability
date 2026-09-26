import sys
import os
import json
from datetime import datetime, UTC
import warnings
warnings.filterwarnings("ignore")

# Thêm thư mục src vào PYTHONPATH để import dễ dàng
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

import streamlit as st
from core.config import load_settings, require_llm_credentials
from pipelines.phase1 import main as run_phase1
from pipelines.corruption_flow import main as run_corruption_flow
from retrieval.index import LocalEmbeddingIndex
from retrieval.agent import build_agent, run_agent_question
from ingestion.crossref import load_raw_records
from ingestion.cleaning import build_clean_dataframe

st.set_page_config(page_title="Lab 10 Demo: Data Observability", layout="wide")

st.sidebar.title("Tính năng Demo")
page = st.sidebar.radio("Điều hướng", [
    "Mục Tiêu Lab (Intro)", 
    "1. Minh Họa Data Flow", 
    "2. Data Observability (Metrics Drop)", 
    "3. Trải nghiệm RAG Agent"
])

settings = load_settings()

if page == "Mục Tiêu Lab (Intro)":
    st.title("Data Pipeline & Data Observability for RAG")
    st.markdown("""
    Demo này được thiết kế để sát với mục tiêu của kho lưu trữ (Repo), giúp giám sát và đảm bảo chất lượng dữ liệu khi đưa vào hệ thống RAG:
    
    ### 🎯 Các điểm chính của Lab:
    1. **Data Quality Gate:** Sử dụng Great Expectations để kiểm tra chất lượng dữ liệu (Null, định dạng).
    2. **Freshness Check:** Đảm bảo tính "tươi mới" của bài báo (`age_days`), chặn các bài quá cũ.
    3. **Corruption Flow:** Mô phỏng sự cố dữ liệu (Data Drift / Data Corruption) và quan sát chỉ số độ chính xác (Ragas Metrics) sụt giảm như thế nào.
    4. **Repair:** Phục hồi lại dữ liệu sạch và đo đạc để thấy điểm số trở về như Baseline.
    
    👈 Hãy sử dụng thanh menu bên trái để đi qua từng phần minh họa!
    """)

elif page == "1. Minh Họa Data Flow":
    st.title("So sánh Đầu vào / Đầu ra của Dữ Liệu")
    st.write("Quan sát sự biến đổi của 1 bài báo CrossRef qua từng giai đoạn để hiểu cách làm sạch và phá hủy dữ liệu (để test).")
    
    raw_path = settings.paths.raw_records_json
    clean_path = settings.paths.clean_json
    corrupted_path = settings.paths.corrupted_clean_json
    embed_path = settings.paths.embeddings_json
    
    if os.path.exists(clean_path):
        import pandas as pd
        import json
        
        with open(raw_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
            
        clean_df = pd.read_json(clean_path)
        clean_data = clean_df.to_dict(orient="records")
        
        sample_id = clean_data[0]['paper_id']
        st.info(f"Đang theo dõi bài báo: **{sample_id}**")
        
        # Hàng 1: Raw vs Clean
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("1. Dữ liệu thô (Trước khi làm sạch)")
            st.write("Dữ liệu gốc từ API CrossRef.")
            raw_sample = next((item for item in raw_data if item["paper_id"] == sample_id), None)
            st.json(raw_sample)
            
        with col2:
            st.subheader("2. Dữ liệu (Sau khi làm sạch)")
            st.write("Đã sinh ra trường `age_days`, `authors_joined`, `text_for_embedding`.")
            clean_sample = clean_data[0]
            st.json(clean_sample)
            
        st.divider()
        
        # Hàng 2: Vector vs Corrupted
        col3, col4 = st.columns(2)
        with col3:
            st.subheader("3. Dữ liệu đưa vào Vector DB")
            st.write("Đóng gói metadata chuẩn bị Embedding.")
            if os.path.exists(embed_path):
                with open(embed_path, 'r', encoding='utf-8') as f:
                    embed_data = json.load(f)
                    docs = embed_data.get("documents", [])
                    embed_sample = next((item for item in docs if item["paper_id"] == sample_id), None)
                    st.json(embed_sample)
                    
        with col4:
            st.subheader("4. Dữ liệu lỗi (Corrupted Data)")
            st.write("Mô phỏng: Cố tình xóa `summary`, làm hỏng ngày xuất bản về `1999` để qua mặt pipeline.")
            if os.path.exists(corrupted_path):
                corrupted_df = pd.read_json(corrupted_path)
                corrupted_data = corrupted_df.to_dict(orient="records")
                corrupted_sample = next((item for item in corrupted_data if item["paper_id"] == sample_id), None)
                st.json(corrupted_sample)
    else:
        st.error("Chưa có dữ liệu hệ thống (thiếu clean.json).")

elif page == "2. Data Observability (Metrics Drop)":
    st.title("Báo cáo Giám sát Data Observability")
    st.write("Bảng dưới đây minh chứng việc: **Khi dữ liệu đầu vào bị hỏng (Corrupted), hệ thống Great Expectations sẽ phát hiện ra, đồng thời điểm số Ragas/Evaluation của LLM lập tức cắm đầu.** Khi phục hồi (Repaired), điểm số lại bình thường.")
    
    if os.path.exists(settings.paths.comparison_report):
        st.success("Tải thành công báo cáo so sánh 3 trạng thái: Baseline - Corrupted - Repaired.")
        with open(settings.paths.comparison_report, "r", encoding="utf-8") as f:
            st.markdown(f.read())
    else:
        st.warning("Chưa có báo cáo Corruption (`data/reports/corruption_report.md`).")
        
    with st.expander("Chạy lại toàn bộ luồng Pipeline & Corruption (Cực kỳ tốn thời gian)"):
        st.warning("Nếu bạn muốn chạy lại từ đầu để LLM chấm điểm lại, nhấn nút bên dưới. Sẽ tốn nhiều phút.")
        if st.button("🚀 Chạy lại Phase 1 & Corruption Flow"):
            with st.spinner("Đang chạy Phase 1..."):
                run_phase1()
            with st.spinner("Đang chạy Corruption Flow..."):
                run_corruption_flow()
            st.success("Hoàn thành! Hãy F5 trang.")

elif page == "3. Trải nghiệm RAG Agent":
    st.title("Hỏi đáp với RAG Agent")
    st.write("Tương tác thực tế với kho dữ liệu các bài báo khoa học đã qua kiểm định chất lượng (Phase 1).")
    
    @st.cache_resource
    def get_agent():
        require_llm_credentials(settings)
        if not os.path.exists(settings.paths.embeddings_json):
            return None
        index = LocalEmbeddingIndex.load(settings, settings.paths.embeddings_json)
        return build_agent(settings, index)
    
    with st.spinner("Đang tải Agent..."):
        agent = get_agent()
        
    if agent is None:
        st.warning("Chưa có file Index. Hãy chạy Phase 1 trước.")
    else:
        if "messages" not in st.session_state:
            st.session_state.messages = []
            
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                
        if prompt := st.chat_input("Hỏi tôi về luận văn AI/ML..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
                
            with st.chat_message("assistant"):
                with st.spinner("Đang truy vấn ChromaDB..."):
                    try:
                        answer = run_agent_question(agent, prompt)
                        st.markdown(answer)
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                    except Exception as e:
                        st.error(f"Lỗi: {e}")

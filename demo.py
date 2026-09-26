import sys
import os
import json
import argparse
from datetime import datetime, UTC
import warnings
warnings.filterwarnings("ignore")

# Thêm thư mục src vào PYTHONPATH để import dễ dàng
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from core.config import load_settings, require_llm_credentials
from pipelines.phase1 import main as run_phase1
from pipelines.corruption_flow import main as run_corruption_flow
from retrieval.index import LocalEmbeddingIndex
from retrieval.agent import build_agent, run_agent_question
from ingestion.crossref import load_raw_records
from ingestion.cleaning import build_clean_dataframe

def interactive_qa():
    print("\n--- Khởi động Interactive QA Agent ---")
    settings = load_settings()
    require_llm_credentials(settings)
    
    print("Đang tải dữ liệu sạch...")
    records = load_raw_records(settings.paths.raw_records_json)
    if not records:
        print("Chưa có dữ liệu raw. Vui lòng chạy Phase 1 Pipeline trước.")
        return
        
    clean_df = build_clean_dataframe(records, datetime.now(UTC))
    print("Đang khởi tạo Vector Index...")
    index = LocalEmbeddingIndex.build(clean_df, settings, settings.paths.embeddings_json)
    
    print("Đang tạo Agent...")
    agent = build_agent(settings, index)
    
    print("\nAgent đã sẵn sàng. Gõ 'exit' hoặc 'quit' để thoát.")
    while True:
        try:
            question = input("\nBạn hỏi: ")
            if question.strip().lower() in ['exit', 'quit']:
                break
            if not question.strip():
                continue
                
            print("Agent đang suy nghĩ...")
            answer = run_agent_question(agent, question)
            print(f"\n[Agent Trả Lời]:\n{answer}")
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Lỗi: {e}")

def main():
    parser = argparse.ArgumentParser(description="Data Pipeline & Data Observability Demo")
    parser.add_argument("--phase1", action="store_true", help="Chạy luồng Phase 1")
    parser.add_argument("--corruption", action="store_true", help="Chạy luồng Corruption & Repair")
    parser.add_argument("--qa", action="store_true", help="Chạy Interactive QA Agent")
    args = parser.parse_args()
    
    if args.phase1:
        print(">>> BẮT ĐẦU CHẠY PHASE 1 PIPELINE")
        run_phase1()
        print(">>> KẾT THÚC PHASE 1 PIPELINE\n")
    elif args.corruption:
        print(">>> BẮT ĐẦU CHẠY CORRUPTION FLOW")
        run_corruption_flow()
        print(">>> KẾT THÚC CORRUPTION FLOW\n")
    elif args.qa:
        interactive_qa()
    else:
        # Nếu không truyền tham số, hiện menu tương tác
        while True:
            print("\n=============================================")
            print(" DATA PIPELINE & OBSERVABILITY DEMO")
            print("=============================================")
            print("1. Chạy Phase 1 Pipeline (Ingestion, Cleaning, Embeddings, Ragas Eval, Data Quality)")
            print("2. Chạy Corruption Flow (Data Drift, Re-Eval, Repair, Comparison)")
            print("3. Hỏi đáp tương tác với Agent (RAG QA)")
            print("4. Thoát")
            print("=============================================")
            choice = input("Chọn chức năng (1-4): ")
            
            if choice == '1':
                print("\n>>> BẮT ĐẦU CHẠY PHASE 1 PIPELINE")
                run_phase1()
            elif choice == '2':
                print("\n>>> BẮT ĐẦU CHẠY CORRUPTION FLOW")
                run_corruption_flow()
            elif choice == '3':
                interactive_qa()
            elif choice == '4':
                print("Tạm biệt!")
                break
            else:
                print("Lựa chọn không hợp lệ, vui lòng thử lại.")

if __name__ == "__main__":
    main()

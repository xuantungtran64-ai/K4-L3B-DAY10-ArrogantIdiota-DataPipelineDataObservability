from __future__ import annotations

import json
from datetime import datetime, UTC

from core.config import load_settings, require_llm_credentials
from ingestion.crossref import fetch_source_records, load_raw_records
from ingestion.cleaning import build_clean_dataframe
from retrieval.index import LocalEmbeddingIndex
from evaluation.testset import build_test_set
from evaluation.metrics import evaluate_pipeline
from observability.quality import run_data_quality_checks, build_freshness_report
from observability.reporting import generate_phase1_report


def main() -> None:
    settings = load_settings()
    require_llm_credentials(settings)
    
    if settings.refresh_source or not settings.paths.raw_records_json.exists():
        records = fetch_source_records(settings)
    else:
        records = load_raw_records(settings.paths.raw_records_json)
        
    source_summary = {"raw_records": len(records)}
    
    run_date = datetime.now(UTC)
    clean_df = build_clean_dataframe(records, run_date)
    source_summary["clean_records"] = len(clean_df)
    
    settings.paths.clean_csv.parent.mkdir(parents=True, exist_ok=True)
    clean_df.to_csv(settings.paths.clean_csv, index=False)
    clean_df.to_json(settings.paths.clean_json, orient="records", indent=2, force_ascii=False)
    
    index = LocalEmbeddingIndex.build(clean_df, settings, settings.paths.embeddings_json)
    
    if settings.refresh_test_set or not settings.paths.eval_testset.exists():
        build_test_set(clean_df, settings.paths.eval_testset)
        
    bundle = evaluate_pipeline(
        settings=settings,
        index=index,
        test_set_path=settings.paths.eval_testset,
        metrics_output_path=settings.paths.baseline_metrics,
        answers_output_path=settings.paths.baseline_answers
    )
    
    quality = run_data_quality_checks(clean_df, settings, "baseline_quality_report.json")
    freshness = build_freshness_report(clean_df, settings, settings.paths.freshness_report)
    
    generate_phase1_report(
        settings.paths.baseline_report,
        source_summary,
        bundle.summary,
        quality,
        freshness
    )
    
    print(f"Phase 1 completed. Report saved to {settings.paths.baseline_report}")

if __name__ == "__main__":
    main()

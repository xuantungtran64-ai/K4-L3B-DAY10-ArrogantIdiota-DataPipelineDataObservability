from __future__ import annotations

import json
from datetime import datetime, UTC

from core.config import load_settings, require_llm_credentials
from ingestion.crossref import load_raw_records
from ingestion.cleaning import build_clean_dataframe
from ingestion.corruption import corrupt_clean_dataframe
from retrieval.index import LocalEmbeddingIndex
from evaluation.metrics import evaluate_pipeline
from observability.quality import run_data_quality_checks, build_freshness_report
from observability.reporting import generate_corruption_report


def main() -> None:
    settings = load_settings()
    require_llm_credentials(settings)
    
    with open(settings.paths.baseline_metrics, "r", encoding="utf-8") as f:
        baseline_metrics = json.load(f)
        
    records = load_raw_records(settings.paths.raw_records_json)
    clean_df = build_clean_dataframe(records, datetime.now(UTC))
    
    corrupted_df = corrupt_clean_dataframe(clean_df, settings.paths.corruption_log)
    
    corrupted_df.to_csv(settings.paths.corrupted_clean_csv, index=False)
    corrupted_df.to_json(settings.paths.corrupted_clean_json, orient="records", indent=2, force_ascii=False)
    
    corrupted_index = LocalEmbeddingIndex.build(corrupted_df, settings, settings.paths.corrupted_embeddings_json)
    corrupted_bundle = evaluate_pipeline(
        settings, corrupted_index, settings.paths.eval_testset,
        settings.paths.corrupted_metrics, settings.paths.corrupted_answers
    )
    
    corrupted_quality = run_data_quality_checks(corrupted_df, settings, "corrupted_quality_report.json")
    corrupted_freshness = build_freshness_report(corrupted_df, settings, settings.paths.quality_dir / "corrupted_freshness_report.json")
    
    repaired_df = build_clean_dataframe(records, datetime.now(UTC))
    repaired_df.to_csv(settings.paths.repaired_clean_csv, index=False)
    repaired_df.to_json(settings.paths.repaired_clean_json, orient="records", indent=2, force_ascii=False)
    
    repaired_index = LocalEmbeddingIndex.build(repaired_df, settings, settings.paths.repaired_embeddings_json)
    repaired_bundle = evaluate_pipeline(
        settings, repaired_index, settings.paths.eval_testset,
        settings.paths.repaired_metrics, settings.paths.repaired_answers
    )
    repaired_quality = run_data_quality_checks(repaired_df, settings, "repaired_quality_report.json")
    repaired_freshness = build_freshness_report(repaired_df, settings, settings.paths.quality_dir / "repaired_freshness_report.json")
    
    generate_corruption_report(
        settings.paths.comparison_report,
        baseline_metrics,
        corrupted_bundle.summary,
        repaired_bundle.summary,
        corrupted_quality,
        repaired_quality,
        corrupted_freshness,
        repaired_freshness
    )
    
    print(f"Corruption flow completed. Comparison report saved to {settings.paths.comparison_report}")

if __name__ == "__main__":
    main()

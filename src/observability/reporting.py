import json
from pathlib import Path
from typing import Any

def generate_phase1_report(
    report_path,
    source_summary: dict[str, Any],
    metrics: dict[str, Any],
    quality: dict[str, Any],
    freshness: dict[str, Any],
) -> None:
    ragas = metrics.get('ragas', {})
    md_content = f"""# Phase 1: Baseline Report

## 1. Source Summary
- Total raw records: {source_summary.get('raw_records', 0)}
- Total clean records: {source_summary.get('clean_records', 0)}

## 2. Evaluation Metrics
- Retrieval Hit Rate: {metrics.get('retrieval_hit_rate', 'N/A')}
- Judge Accuracy: {metrics.get('judge_accuracy', 'N/A')}
- Mean Token F1: {metrics.get('mean_token_f1', 'N/A')}
- Context Precision: {ragas.get('context_precision', 'N/A')}
- Context Recall: {ragas.get('context_recall', 'N/A')}
- Answer Relevancy: {ragas.get('answer_relevancy', 'N/A')}
- Faithfulness: {ragas.get('faithfulness', 'N/A')}

## 3. Data Quality & Freshness
- Quality Checks Passed: {quality.get('success', False)}
- Is Fresh: {freshness.get('is_fresh', False)}
- Stale Rows: {freshness.get('stale_rows', 0)}
- Oldest Published: {freshness.get('oldest_published', 'N/A')}
- Latest Published: {freshness.get('latest_published', 'N/A')}
"""
    Path(report_path).parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(md_content)


def generate_corruption_report(
    report_path,
    baseline_metrics: dict[str, Any],
    corrupted_metrics: dict[str, Any],
    repaired_metrics: dict[str, Any],
    corrupted_quality: dict[str, Any],
    repaired_quality: dict[str, Any],
    corrupted_freshness: dict[str, Any],
    repaired_freshness: dict[str, Any],
) -> None:
    b_ragas = baseline_metrics.get('ragas', {})
    c_ragas = corrupted_metrics.get('ragas', {})
    r_ragas = repaired_metrics.get('ragas', {})
    
    md_content = f"""# Phase 2: Corruption & Repair Report

## 1. Quality Comparison

| Status | Quality Passed | Freshness Passed | Stale Rows |
|---|---|---|---|
| Corrupted | {corrupted_quality.get('success', False)} | {corrupted_freshness.get('is_fresh', False)} | {corrupted_freshness.get('stale_rows', 0)} |
| Repaired | {repaired_quality.get('success', False)} | {repaired_freshness.get('is_fresh', False)} | {repaired_freshness.get('stale_rows', 0)} |

## 2. Evaluation Metrics Comparison

| Metric | Baseline | Corrupted | Repaired |
|---|---|---|---|
| Retrieval Hit Rate | {baseline_metrics.get('retrieval_hit_rate', 'N/A')} | {corrupted_metrics.get('retrieval_hit_rate', 'N/A')} | {repaired_metrics.get('retrieval_hit_rate', 'N/A')} |
| Judge Accuracy | {baseline_metrics.get('judge_accuracy', 'N/A')} | {corrupted_metrics.get('judge_accuracy', 'N/A')} | {repaired_metrics.get('judge_accuracy', 'N/A')} |
| Mean Token F1 | {baseline_metrics.get('mean_token_f1', 'N/A')} | {corrupted_metrics.get('mean_token_f1', 'N/A')} | {repaired_metrics.get('mean_token_f1', 'N/A')} |
| Context Precision | {b_ragas.get('context_precision', 'N/A')} | {c_ragas.get('context_precision', 'N/A')} | {r_ragas.get('context_precision', 'N/A')} |
| Context Recall | {b_ragas.get('context_recall', 'N/A')} | {c_ragas.get('context_recall', 'N/A')} | {r_ragas.get('context_recall', 'N/A')} |
| Answer Relevancy | {b_ragas.get('answer_relevancy', 'N/A')} | {c_ragas.get('answer_relevancy', 'N/A')} | {r_ragas.get('answer_relevancy', 'N/A')} |
| Faithfulness | {b_ragas.get('faithfulness', 'N/A')} | {c_ragas.get('faithfulness', 'N/A')} | {r_ragas.get('faithfulness', 'N/A')} |
"""
    Path(report_path).parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(md_content)

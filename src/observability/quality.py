from __future__ import annotations

from typing import Any

import pandas as pd

from core.config import Settings


import great_expectations as gx
import json
from pathlib import Path

def run_data_quality_checks(df: pd.DataFrame, settings: Settings, report_name: str) -> dict[str, Any]:
    context = gx.get_context(mode="ephemeral")
    
    data_source = context.data_sources.add_pandas("pandas_source")
    data_asset = data_source.add_dataframe_asset("df_asset")
    batch_definition = data_asset.add_batch_definition_whole_dataframe("batch_def")
    
    suite = context.suites.add(gx.ExpectationSuite(name="quality_suite"))
    
    suite.add_expectation(gx.expectations.ExpectTableRowCountToBeBetween(min_value=1))
    suite.add_expectation(gx.expectations.ExpectColumnValuesToNotBeNull(column="paper_id"))
    suite.add_expectation(gx.expectations.ExpectColumnValuesToBeUnique(column="paper_id"))
    suite.add_expectation(gx.expectations.ExpectColumnValuesToNotBeNull(column="title"))
    suite.add_expectation(gx.expectations.ExpectColumnValueLengthsToBeBetween(column="summary", min_value=10))
    suite.add_expectation(gx.expectations.ExpectColumnValuesToBeBetween(column="age_days", min_value=0, max_value=settings.freshness_threshold_days))
    
    validation_definition = gx.ValidationDefinition(
        name="quality_validation",
        data=batch_definition,
        suite=suite,
    )
    context.validation_definitions.add(validation_definition)
    
    validation_result = validation_definition.run(batch_parameters={"dataframe": df})
    result_dict = validation_result.to_json_dict()
    
    success = result_dict.get("success", False)
    
    report_path = settings.paths.quality_dir / report_name
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(result_dict, f, indent=2)
        
    return {"success": success, "details": result_dict}


def build_freshness_report(df: pd.DataFrame, settings: Settings, report_path) -> dict[str, Any]:
    if df.empty:
        report = {
            "latest_published": None,
            "oldest_published": None,
            "stale_rows": 0,
            "total_rows": 0,
            "is_fresh": False
        }
    else:
        latest = df["published"].max()
        oldest = df["published"].min()
        stale_rows = int((df["age_days"] > settings.freshness_threshold_days).sum())
        total_rows = len(df)
        is_fresh = (stale_rows == 0)
        
        report = {
            "latest_published": str(latest),
            "oldest_published": str(oldest),
            "stale_rows": stale_rows,
            "total_rows": total_rows,
            "is_fresh": is_fresh
        }
        
    Path(report_path).parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
        
    return report

from __future__ import annotations

import pandas as pd
import numpy as np
import json
from pathlib import Path


def corrupt_clean_dataframe(df: pd.DataFrame, output_log_path: Path) -> pd.DataFrame:
    df_corrupted = df.copy()
    logs = {}
    
    if len(df_corrupted) == 0:
        return df_corrupted
        
    np.random.seed(42)
    
    if len(df_corrupted) > 2:
        df_corrupted = df_corrupted.iloc[2:].reset_index(drop=True)
        logs["dropped_records"] = 2
        
    num_blank = max(1, int(len(df_corrupted) * 0.1))
    blank_idx = np.random.choice(df_corrupted.index, size=num_blank, replace=False)
    df_corrupted.loc[blank_idx, "summary"] = ""
    logs["blank_summaries"] = num_blank
    
    noise_idx = np.random.choice(df_corrupted.index, size=num_blank, replace=False)
    df_corrupted.loc[noise_idx, "summary"] = df_corrupted.loc[noise_idx, "summary"].apply(lambda x: x + " xyz_NOISE_123" if isinstance(x, str) else str(x))
    logs["noise_injected"] = num_blank
    
    trunc_idx = np.random.choice(df_corrupted.index, size=num_blank, replace=False)
    df_corrupted.loc[trunc_idx, "title"] = df_corrupted.loc[trunc_idx, "title"].apply(lambda x: x[:10] + "..." if isinstance(x, str) and len(x) > 10 else x)
    logs["truncated_titles"] = num_blank
    
    date_idx = np.random.choice(df_corrupted.index, size=num_blank, replace=False)
    df_corrupted.loc[date_idx, "published"] = "1999-01-01"
    df_corrupted.loc[date_idx, "age_days"] = 9999
    logs["old_dates_injected"] = num_blank
    
    if len(df_corrupted) > 0:
        dup_row = df_corrupted.iloc[[0]].copy()
        df_corrupted = pd.concat([df_corrupted, dup_row], ignore_index=True)
        logs["duplicate_rows_added"] = 1
        
    df_corrupted["text_for_embedding"] = (
        "Title: " + df_corrupted["title"].astype(str) + "\n" +
        "Authors: " + df_corrupted["authors_joined"].astype(str) + "\n" +
        "Categories: " + df_corrupted["categories_joined"].astype(str) + "\n" +
        "Summary: " + df_corrupted["summary"].astype(str)
    )
    
    Path(output_log_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_log_path, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2)
        
    return df_corrupted

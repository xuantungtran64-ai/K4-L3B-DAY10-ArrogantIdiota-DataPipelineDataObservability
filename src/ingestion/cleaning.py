from __future__ import annotations

from datetime import datetime

import pandas as pd

from ingestion.crossref import PaperRecord


def build_clean_dataframe(records: list[PaperRecord], run_date: datetime) -> pd.DataFrame:
    if not records:
        return pd.DataFrame()
        
    df = pd.DataFrame([r.__dict__ for r in records])
    
    df["title"] = df["title"].astype(str).str.strip().str.replace(r"\s+", " ", regex=True)
    df["summary"] = df["summary"].astype(str).str.strip().str.replace(r"\s+", " ", regex=True)
    
    df["published"] = pd.to_datetime(df["published"], errors="coerce")
    df["updated"] = pd.to_datetime(df["updated"], errors="coerce")
    
    df["published"] = df["published"].fillna(pd.Timestamp("2000-01-01"))
    
    run_dt_naive = pd.Timestamp(run_date).tz_localize(None)
    df["published_naive"] = df["published"].dt.tz_localize(None)
    df["age_days"] = (run_dt_naive - df["published_naive"]).dt.days
    df = df.drop(columns=["published_naive"])
    
    df["authors_joined"] = df["authors"].apply(lambda x: ", ".join(x) if isinstance(x, list) else "")
    df["categories_joined"] = df["categories"].apply(lambda x: ", ".join(x) if isinstance(x, list) else "")
    df["summary_chars"] = df["summary"].str.len().fillna(0).astype(int)
    
    df["text_for_embedding"] = (
        "Title: " + df["title"] + "\n" +
        "Authors: " + df["authors_joined"] + "\n" +
        "Categories: " + df["categories_joined"] + "\n" +
        "Summary: " + df["summary"]
    )
    
    df = df.drop_duplicates(subset=["paper_id"], keep="first")
    df = df[df["title"].str.len() > 0]
    df = df[df["summary_chars"] > 10]
    
    df = df.sort_values(by="published", ascending=False).reset_index(drop=True)
    
    df["published"] = df["published"].dt.strftime("%Y-%m-%d")
    df["updated"] = df["updated"].dt.strftime("%Y-%m-%d")
    
    return df

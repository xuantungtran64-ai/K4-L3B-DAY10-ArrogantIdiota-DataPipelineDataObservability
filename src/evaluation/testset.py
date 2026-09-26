from __future__ import annotations

from typing import Any

import pandas as pd


import json
import uuid
from pathlib import Path

def build_test_set(df: pd.DataFrame, output_path) -> list[dict[str, Any]]:
    testset = []
    
    if len(df) == 0:
        return testset
        
    samples = df.head(5)
    
    for _, row in samples.iterrows():
        paper_id = str(row['paper_id'])
        title = str(row['title'])
        authors = str(row.get('authors_joined', ''))
        pub_date = str(row['published'])
        summary = str(row['summary'])
        
        testset.append({
            "id": str(uuid.uuid4()),
            "question_type": "summary",
            "question": f"What is the paper '{title}' about?",
            "ground_truth": summary,
            "ground_truth_doc_ids": [paper_id]
        })
        
        if authors:
            testset.append({
                "id": str(uuid.uuid4()),
                "question_type": "authors",
                "question": f"Who are the authors of '{title}'?",
                "ground_truth": f"The authors are {authors}.",
                "ground_truth_doc_ids": [paper_id]
            })
            
        testset.append({
            "id": str(uuid.uuid4()),
            "question_type": "date",
            "question": f"When was the paper '{title}' published?",
            "ground_truth": f"It was published on {pub_date}.",
            "ground_truth_doc_ids": [paper_id]
        })

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(testset, f, indent=2, ensure_ascii=False)
        
    return testset

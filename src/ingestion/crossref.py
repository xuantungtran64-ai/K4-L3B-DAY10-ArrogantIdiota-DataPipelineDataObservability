from __future__ import annotations

import json
import requests
import time
from urllib.parse import urlencode
from dataclasses import dataclass
from pathlib import Path

from core.config import Settings


@dataclass(frozen=True)
class PaperRecord:
    paper_id: str
    title: str
    summary: str
    authors: list[str]
    categories: list[str]
    primary_category: str
    published: str
    updated: str
    abs_url: str
    pdf_url: str
    comment: str


def parse_crossref_payload(payload: dict) -> list[PaperRecord]:
    records = []
    items = payload.get("message", {}).get("items", [])
    for item in items:
        try:
            paper_id = item.get("DOI", "")
            title_list = item.get("title", [])
            title = title_list[0] if title_list else ""
            
            abstract = item.get("abstract", "")
            abstract = abstract.replace("<jats:p>", "").replace("</jats:p>", "").strip()
            
            authors = []
            for author in item.get("author", []):
                given = author.get("given", "")
                family = author.get("family", "")
                authors.append(f"{given} {family}".strip())
                
            categories = item.get("subject", [])
            primary_category = categories[0] if categories else ""
            
            pub = item.get("published") or item.get("created", {})
            date_parts = pub.get("date-parts", [[None]])[0]
            if date_parts and date_parts[0]:
                if len(date_parts) >= 3:
                    published = f"{date_parts[0]:04d}-{date_parts[1]:02d}-{date_parts[2]:02d}"
                elif len(date_parts) == 2:
                    published = f"{date_parts[0]:04d}-{date_parts[1]:02d}-01"
                else:
                    published = f"{date_parts[0]:04d}-01-01"
            else:
                published = "2000-01-01"
            
            abs_url = item.get("URL", "")
            
            if not paper_id or not title:
                continue
                
            records.append(PaperRecord(
                paper_id=paper_id,
                title=title,
                summary=abstract,
                authors=authors,
                categories=categories,
                primary_category=primary_category,
                published=published,
                updated=published,
                abs_url=abs_url,
                pdf_url="",
                comment=""
            ))
        except Exception:
            continue
    return records


def fetch_source_records(settings: Settings) -> list[PaperRecord]:
    params = {
        "query": settings.source_query,
        "filter": settings.source_filter,
        "rows": settings.max_results
    }
    url = f"https://api.crossref.org/works?{urlencode(params)}"
    
    for attempt in range(3):
        response = requests.get(url)
        if response.status_code in [429, 502, 503, 504]:
            time.sleep(2 ** attempt)
            continue
        response.raise_for_status()
        break
        
    payload = response.json()
    
    settings.paths.raw_api_response.parent.mkdir(parents=True, exist_ok=True)
    with open(settings.paths.raw_api_response, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
        
    records = parse_crossref_payload(payload)
    
    with open(settings.paths.raw_records_json, "w", encoding="utf-8") as f:
        json.dump([r.__dict__ for r in records], f, indent=2, ensure_ascii=False)
        
    return records


def load_raw_records(path: Path) -> list[PaperRecord]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict) and "message" in data:
        return parse_crossref_payload(data)
    elif isinstance(data, list):
        return [PaperRecord(**d) for d in data]
    return []

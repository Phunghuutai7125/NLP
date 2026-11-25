from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
QUERY_PATH = ROOT / "data" / "queries.csv"
PREDICTION_DIR = ROOT / "evaluation" / "candidate_runs"
POOL_AUDIT_PATH = ROOT / "evaluation" / "candidate_pool_audit.csv"
OUTPUT_PATH = ROOT / "evaluation" / "query_candidate_review.csv"
METHODS = {
    "E0_tfidf": "E0",
    "E1_dense": "E1",
    "E2_rrf_fusion": "E2",
}


def lock_test_query(queries: pd.DataFrame, query_id: str) -> pd.DataFrame:
    matches = queries["query_id"].astype(str).eq(str(query_id))
    if matches.sum() != 1:
        raise ValueError(f"Phải có đúng một query_id khớp: {query_id}")
    if not queries.loc[matches, "split"].eq("test").all():
        raise ValueError("Chỉ được khóa truy vấn thuộc split test.")
    if not str(queries.loc[matches, "query"].iloc[0]).strip():
        raise ValueError("Không thể khóa truy vấn rỗng.")
    locked = queries.copy()
    locked.loc[matches, "review_status"] = "locked"
    return locked


def build_review_table(
    queries: pd.DataFrame,
    predictions: dict[str, pd.DataFrame],
    pool_audit: pd.DataFrame,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    pool_counts = pool_audit.groupby("query_id")["doc_id"].nunique().to_dict()
    top_hits: dict[str, dict[str, pd.DataFrame]] = {}
    for method, frame in predictions.items():
        top_hits[method] = {
            str(query_id): group.sort_values("rank").head(3)
            for query_id, group in frame.groupby("query_id")
        }

    for query in queries.to_dict("records"):
        query_id = str(query["query_id"])
        row: dict[str, object] = {
            "query_id": query_id,
            "split": query["split"],
            "topic": query["topic"],
            "query": query["query"],
            "query_status": query["review_status"],
            "candidate_pool_size": int(pool_counts.get(query_id, 0)),
            "top1_agreement_count": 0,
            "review_note": "Machine-ranked candidates only; not relevance judgments.",
        }
        top1_ids: list[str] = []
        for method, short_name in METHODS.items():
            hits = top_hits[method].get(query_id, pd.DataFrame())
            serialized = []
            for hit in hits.to_dict("records"):
                serialized.append(
                    {
                        "rank": int(hit["rank"]),
                        "doc_id": str(hit["doc_id"]),
                        "title": str(hit["title"]),
                        "source": str(hit["source"]),
                    }
                )
            row[f"{short_name}_top3_json"] = json.dumps(serialized, ensure_ascii=False)
            if serialized:
                top1_ids.append(serialized[0]["doc_id"])
        row["top1_agreement_count"] = max(
            (top1_ids.count(doc_id) for doc_id in set(top1_ids)), default=0
        )
        rows.append(row)
    return pd.DataFrame(rows)


def main() -> None:
    queries = pd.read_csv(QUERY_PATH).fillna("")
    predictions = {
        method: pd.read_csv(PREDICTION_DIR / f"topk_{method}.csv").fillna("")
        for method in METHODS
    }
    pool_audit = pd.read_csv(POOL_AUDIT_PATH).fillna("")
    result = build_review_table(queries, predictions, pool_audit)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
    print(f"Saved query candidate review: {OUTPUT_PATH} ({len(result)} queries)")


if __name__ == "__main__":
    main()

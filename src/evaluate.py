from __future__ import annotations

import math
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
QUERY_PATH = ROOT / "data" / "queries.csv"
JUDGMENT_PATH = ROOT / "data" / "relevance_judgments.csv"
POOL_PATH = ROOT / "data" / "relevance_judgments_template.csv"
PREDICTION_DIR = ROOT / "evaluation" / "candidate_runs"
METHODS = ("E0_tfidf", "E1_dense", "E2_rrf_fusion")


def dcg(grades: list[int]) -> float:
    return sum((2**grade - 1) / math.log2(rank + 1) for rank, grade in enumerate(grades, 1))


def main() -> None:
    queries = pd.read_csv(QUERY_PATH)
    test = queries.loc[queries["split"].eq("test")]
    test_queries = test["query_id"].astype(str).tolist()
    if "review_status" not in test.columns or not test["review_status"].eq("locked").all():
        pending = (
            int(test["review_status"].ne("locked").sum())
            if "review_status" in test.columns
            else len(test)
        )
        raise ValueError(
            f"{pending} truy vấn test chưa được nhóm duyệt và khóa "
            "(review_status=locked); chưa thể tính metric test."
        )
    if not JUDGMENT_PATH.exists():
        raise FileNotFoundError(
            "Chưa có data/relevance_judgments.csv. Chấm, phân xử và xuất gold trước khi đánh giá."
        )
    judgments = pd.read_csv(JUDGMENT_PATH).fillna("")
    required_judgment_columns = {
        "query_id",
        "split",
        "query_text",
        "doc_id",
        "relevance",
        "review_status",
    }
    if not required_judgment_columns.issubset(judgments.columns):
        raise ValueError(
            "Gold thiếu các cột bắt buộc: "
            f"{sorted(required_judgment_columns - set(judgments.columns))}"
        )
    if "split" not in judgments.columns:
        raise ValueError("Judgments thiếu cột split; hãy tạo lại candidate pool.")
    judgments = judgments.loc[judgments["split"].eq("test")].copy()
    if judgments.empty:
        raise ValueError("Chưa có judgments cho tập test.")
    if judgments["relevance"].eq("").any():
        raise ValueError(
            "Còn relevance của candidate test chưa chấm; cần chấm toàn bộ test pool "
            "để tính nDCG mà không coi tài liệu chưa chấm là không liên quan."
        )
    if not judgments["review_status"].isin(
        ["consensus", "adjudicated", "single_annotator"]
    ).all():
        raise ValueError(
            "Judgment phải được đồng thuận, phân xử hoặc xác nhận theo chế độ một người."
        )
    current_queries = queries.set_index("query_id")["query"].astype(str)
    for row in judgments[["query_id", "query_text"]].drop_duplicates().itertuples(index=False):
        if row.query_id not in current_queries.index:
            raise ValueError(f"Gold có query_id không tồn tại: {row.query_id}")
        if str(row.query_text) != current_queries.loc[row.query_id]:
            raise ValueError(
                f"Truy vấn {row.query_id} đã đổi sau khi gắn nhãn; cần rà soát và chấm lại."
            )
    judgments["relevance"] = pd.to_numeric(judgments["relevance"], errors="raise").astype(int)
    if not judgments["relevance"].between(0, 3).all():
        raise ValueError("Relevance phải là số nguyên 0..3.")
    if judgments.duplicated(["query_id", "doc_id"]).any():
        raise ValueError("Có judgment trùng query_id/doc_id.")
    candidate_pool = pd.read_csv(POOL_PATH)
    expected_pairs = set(
        zip(
            candidate_pool.loc[candidate_pool["split"].eq("test"), "query_id"].astype(str),
            candidate_pool.loc[candidate_pool["split"].eq("test"), "doc_id"].astype(str),
        )
    )
    judged_pairs = set(
        zip(judgments["query_id"].astype(str), judgments["doc_id"].astype(str))
    )
    missing_pool_pairs = expected_pairs - judged_pairs
    extra_judgments = judged_pairs - expected_pairs
    if missing_pool_pairs or extra_judgments:
        raise ValueError(
            "Gold không khớp candidate test pool: "
            f"thiếu {len(missing_pool_pairs)}, thừa {len(extra_judgments)} cặp query/doc."
        )
    judged = judgments.set_index(["query_id", "doc_id"])["relevance"]
    missing_test_queries = set(test_queries) - set(judgments["query_id"].astype(str))
    if missing_test_queries:
        raise ValueError(f"Thiếu judgments cho test queries: {sorted(missing_test_queries)}")
    result_rows: list[dict[str, object]] = []

    for method in METHODS:
        predictions = pd.read_csv(PREDICTION_DIR / f"topk_{method}.csv")
        predictions = predictions.loc[predictions["split"].eq("test")]
        query_ndcgs: list[float] = []
        query_mrrs: list[float] = []
        for query_id in test_queries:
            ranked = predictions.loc[predictions["query_id"].astype(str).eq(query_id)].sort_values("rank")
            top5 = ranked.head(5)
            if len(top5) != 5:
                raise ValueError(f"{method}: query {query_id} không có đủ 5 kết quả.")
            keys = [(query_id, str(doc_id)) for doc_id in top5["doc_id"]]
            missing = [doc_id for (_, doc_id) in keys if (_, doc_id) not in judged.index]
            if missing:
                raise ValueError(
                    f"{method}: query {query_id} có tài liệu top-5 chưa được chấm: {missing}. "
                    "Cần bổ sung judgment trước khi tính metric."
                )
            grades = [int(judged.loc[key]) for key in keys]
            ideal = sorted(
                [int(grade) for (qid, _), grade in judged.items() if str(qid) == query_id],
                reverse=True,
            )[:5]
            ideal_dcg = dcg(ideal)
            query_ndcgs.append(dcg(grades) / ideal_dcg if ideal_dcg else 0.0)
            reciprocal_rank = next(
                (1 / rank for rank, grade in enumerate(grades, 1) if grade >= 2), 0.0
            )
            query_mrrs.append(reciprocal_rank)
        result_rows.append(
            {
                "method": method,
                "split": "test",
                "queries": len(test_queries),
                "nDCG@5": sum(query_ndcgs) / len(query_ndcgs),
                "MRR@5": sum(query_mrrs) / len(query_mrrs),
            }
        )

    output = pd.DataFrame(result_rows)
    output_path = ROOT / "evaluation" / "metrics_summary.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(output.to_string(index=False))
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()

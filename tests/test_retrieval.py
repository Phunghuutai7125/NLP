import numpy as np
import pandas as pd
import pytest

from src import evaluate, run_retrieval
from src import annotation_workbench
from src import audit_queries
from src.evaluate import dcg
from src.run_retrieval import ranked_ids, rrf_fusion


def test_rrf_prefers_documents_ranked_near_top_by_both_systems() -> None:
    lexical = np.array([[0.9, 0.8, 0.1, 0.0]])
    dense = np.array([[0.1, 0.95, 0.9, 0.0]])

    fused = rrf_fusion(lexical, dense)

    assert int(np.argmax(fused[0])) == 1


def test_ranked_ids_limits_result_count() -> None:
    scores = np.array([[0.2, 0.9, 0.4]])
    corpus = pd.DataFrame({"id": ["a", "b", "c"]})

    assert ranked_ids(scores, corpus, top_k=2) == [[1, 2]]


def test_dcg_uses_gain_and_rank_discount() -> None:
    assert dcg([3, 0]) == pytest.approx(7.0)
    assert dcg([0, 3]) == pytest.approx(7.0 / np.log2(3))


def test_candidate_pool_preserves_labels_only_for_unchanged_query(
    tmp_path, monkeypatch
) -> None:
    monkeypatch.setattr(run_retrieval, "ROOT", tmp_path)
    (tmp_path / "data").mkdir()
    existing = pd.DataFrame(
        [
            {
                "query_id": "q1",
                "split": "dev",
                "query_text": "original query",
                "doc_id": "d0",
                "relevance": 3,
                "annotator": "reviewer",
                "notes": "verified",
            }
        ]
    )
    existing.to_csv(
        tmp_path / "data" / "relevance_judgments_template.csv",
        index=False,
        encoding="utf-8-sig",
    )
    corpus = pd.DataFrame(
        [
            {
                "id": f"d{i}",
                "title": f"title {i}",
                "content": f"content {i}",
                "source": "source",
                "url": f"https://example.test/{i}",
            }
            for i in range(5)
        ]
    )
    scores = np.array([[1.0, 0.8, 0.6, 0.4, 0.2]])
    queries = pd.DataFrame(
        [{"query_id": "q1", "split": "dev", "query": "original query"}]
    )

    run_retrieval.write_judgment_pool(queries, corpus, {"E0": scores}, pool_depth=2)
    pool = pd.read_csv(tmp_path / "data" / "relevance_judgments_template.csv")
    preserved = pool.loc[pool["doc_id"].eq("d0")].iloc[0]
    assert preserved["relevance"] == 3
    assert preserved["annotator"] == "reviewer"

    queries.loc[0, "query"] = "changed query"
    run_retrieval.write_judgment_pool(queries, corpus, {"E0": scores}, pool_depth=2)
    refreshed = pd.read_csv(tmp_path / "data" / "relevance_judgments_template.csv")
    assert refreshed["relevance"].isna().all()


def test_evaluator_rejects_partially_judged_test_pool(tmp_path, monkeypatch) -> None:
    query_path = tmp_path / "queries.csv"
    judgments_path = tmp_path / "judgments.csv"
    pd.DataFrame(
        [
            {
                "query_id": "q1",
                "split": "test",
                "query": "query",
                "review_status": "locked",
            }
        ]
    ).to_csv(query_path, index=False)
    pd.DataFrame(
        [
            {
                "query_id": "q1",
                "split": "test",
                "query_text": "query",
                "doc_id": "d1",
                "relevance": 3,
                "review_status": "consensus",
            },
            {
                "query_id": "q1",
                "split": "test",
                "query_text": "query",
                "doc_id": "d2",
                "relevance": "",
                "review_status": "unjudged",
            },
        ]
    ).to_csv(judgments_path, index=False)
    pool_path = tmp_path / "pool.csv"
    pd.DataFrame(
        [
            {"query_id": "q1", "split": "test", "doc_id": "d1"},
            {"query_id": "q1", "split": "test", "doc_id": "d2"},
        ]
    ).to_csv(pool_path, index=False)
    monkeypatch.setattr(evaluate, "QUERY_PATH", query_path)
    monkeypatch.setattr(evaluate, "JUDGMENT_PATH", judgments_path)
    monkeypatch.setattr(evaluate, "POOL_PATH", pool_path)

    with pytest.raises(ValueError, match="toàn bộ test pool"):
        evaluate.main()


def test_evaluator_scores_complete_test_pool(tmp_path, monkeypatch) -> None:
    evaluation_dir = tmp_path / "evaluation"
    predictions_dir = evaluation_dir / "candidate_runs"
    predictions_dir.mkdir(parents=True)
    queries_path = tmp_path / "queries.csv"
    judgments_path = tmp_path / "judgments.csv"
    pd.DataFrame(
        [
            {
                "query_id": "q1",
                "split": "test",
                "query": "query",
                "review_status": "locked",
            }
        ]
    ).to_csv(queries_path, index=False)
    grades = {"d1": 3, "d2": 2, "d3": 1, "d4": 0, "d5": 0}
    pd.DataFrame(
        [
            {
                "query_id": "q1",
                "split": "test",
                "query_text": "query",
                "doc_id": doc_id,
                "relevance": grade,
                "review_status": (
                    "single_annotator" if doc_id == "d1" else "consensus"
                ),
            }
            for doc_id, grade in grades.items()
        ]
    ).to_csv(judgments_path, index=False)
    pool_path = tmp_path / "pool.csv"
    pd.DataFrame(
        [
            {"query_id": "q1", "split": "test", "doc_id": doc_id}
            for doc_id in grades
        ]
    ).to_csv(pool_path, index=False)
    methods = ("E0_tfidf", "E1_dense", "E2_rrf_fusion")
    for method in methods:
        order = ["d1", "d2", "d3", "d4", "d5"] if method == "E0_tfidf" else [
            "d3",
            "d4",
            "d5",
            "d2",
            "d1",
        ]
        pd.DataFrame(
            [
                {"query_id": "q1", "split": "test", "doc_id": doc_id, "rank": rank}
                for rank, doc_id in enumerate(order, start=1)
            ]
        ).to_csv(predictions_dir / f"topk_{method}.csv", index=False)

    monkeypatch.setattr(evaluate, "ROOT", tmp_path)
    monkeypatch.setattr(evaluate, "QUERY_PATH", queries_path)
    monkeypatch.setattr(evaluate, "JUDGMENT_PATH", judgments_path)
    monkeypatch.setattr(evaluate, "POOL_PATH", pool_path)
    monkeypatch.setattr(evaluate, "PREDICTION_DIR", predictions_dir)

    evaluate.main()
    result = pd.read_csv(evaluation_dir / "metrics_summary.csv").set_index("method")
    assert result.loc["E0_tfidf", "nDCG@5"] == pytest.approx(1.0)
    assert result.loc["E0_tfidf", "MRR@5"] == pytest.approx(1.0)


def test_annotation_export_requires_consensus_or_adjudication(
    tmp_path, monkeypatch
) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    pool_path = data_dir / "pool.csv"
    database_path = data_dir / "annotations.sqlite3"
    monkeypatch.setattr(annotation_workbench, "POOL_PATH", pool_path)
    export_path = data_dir / "gold.csv"
    monkeypatch.setattr(annotation_workbench, "EXPORT_PATH", export_path)
    monkeypatch.setattr(annotation_workbench, "DATABASE_PATH", database_path)
    pd.DataFrame(
        [
            {
                "query_id": "q1",
                "split": "test",
                "query_text": "query",
                "doc_id": "d1",
                "relevance": "",
            }
        ]
    ).to_csv(pool_path, index=False)

    annotation_workbench.save_rating(
        "q1", "d1", "query", "A", 3, "direct evidence"
    )
    annotation_workbench.save_rating(
        "q1", "d1", "query", "B", 2, "partial match"
    )
    exported = annotation_workbench.export_consensus()
    assert exported.iloc[0]["review_status"] == "disagreement"
    assert exported.iloc[0]["relevance"] == ""
    original_pool = pd.read_csv(pool_path)
    assert "review_status" not in original_pool.columns
    gold = pd.read_csv(export_path)
    assert gold.iloc[0]["review_status"] == "disagreement"
    assert pd.isna(gold.iloc[0]["relevance"])

    annotation_workbench.save_adjudication(
        "q1", "d1", "query", "C", 3, "article answers query"
    )
    exported = annotation_workbench.export_consensus()
    assert exported.iloc[0]["review_status"] == "adjudicated"
    assert exported.iloc[0]["relevance"] == 3


def test_annotation_export_marks_old_query_ratings_stale(
    tmp_path, monkeypatch
) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    pool_path = data_dir / "pool.csv"
    monkeypatch.setattr(annotation_workbench, "POOL_PATH", pool_path)
    monkeypatch.setattr(annotation_workbench, "EXPORT_PATH", data_dir / "gold.csv")
    monkeypatch.setattr(
        annotation_workbench, "DATABASE_PATH", data_dir / "annotations.sqlite3"
    )
    pd.DataFrame(
        [
            {
                "query_id": "q1",
                "split": "test",
                "query_text": "new wording",
                "doc_id": "d1",
                "relevance": "",
            }
        ]
    ).to_csv(pool_path, index=False)
    annotation_workbench.save_rating(
        "q1", "d1", "old wording", "A", 3, "old evidence"
    )
    annotation_workbench.save_rating(
        "q1", "d1", "old wording", "B", 3, "old evidence"
    )
    annotation_workbench.save_adjudication(
        "q1", "d1", "old wording", "C", 3, "old adjudication"
    )

    exported = annotation_workbench.export_consensus()

    assert exported.iloc[0]["review_status"] == "stale_query_requires_reannotation"
    assert exported.iloc[0]["relevance"] == ""


def test_build_consensus_does_not_write_gold_export(tmp_path, monkeypatch) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    pool_path = data_dir / "pool.csv"
    export_path = data_dir / "gold.csv"
    monkeypatch.setattr(annotation_workbench, "POOL_PATH", pool_path)
    monkeypatch.setattr(annotation_workbench, "EXPORT_PATH", export_path)
    monkeypatch.setattr(
        annotation_workbench, "DATABASE_PATH", data_dir / "annotations.sqlite3"
    )
    pd.DataFrame(
        [
            {
                "query_id": "q1",
                "split": "test",
                "query_text": "query",
                "doc_id": "d1",
                "relevance": "",
            }
        ]
    ).to_csv(pool_path, index=False)

    consensus = annotation_workbench.build_consensus()

    assert consensus.iloc[0]["review_status"] == "unjudged"
    assert not export_path.exists()


def test_single_annotator_requires_explicit_opt_in(tmp_path, monkeypatch) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    pool_path = data_dir / "pool.csv"
    monkeypatch.setattr(annotation_workbench, "POOL_PATH", pool_path)
    monkeypatch.setattr(annotation_workbench, "EXPORT_PATH", data_dir / "gold.csv")
    monkeypatch.setattr(
        annotation_workbench, "DATABASE_PATH", data_dir / "annotations.sqlite3"
    )
    pd.DataFrame(
        [
            {
                "query_id": "q1",
                "split": "test",
                "query_text": "query",
                "doc_id": "d1",
                "relevance": "",
            }
        ]
    ).to_csv(pool_path, index=False)
    annotation_workbench.save_rating(
        "q1", "d1", "query", "reviewer", 2, "useful partial answer"
    )

    conservative = annotation_workbench.build_consensus()
    single_reviewer = annotation_workbench.build_consensus(
        allow_single_annotator=True
    )
    exported = annotation_workbench.export_consensus(allow_single_annotator=True)

    assert conservative.iloc[0]["review_status"] == "needs_second_annotator"
    assert conservative.iloc[0]["relevance"] == ""
    assert single_reviewer.iloc[0]["review_status"] == "single_annotator"
    assert single_reviewer.iloc[0]["relevance"] == 2
    assert exported.iloc[0]["review_status"] == "single_annotator"


def test_annotation_consensus_requires_all_annotators_to_agree(
    tmp_path, monkeypatch
) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    pool_path = data_dir / "pool.csv"
    monkeypatch.setattr(annotation_workbench, "POOL_PATH", pool_path)
    monkeypatch.setattr(annotation_workbench, "EXPORT_PATH", data_dir / "gold.csv")
    monkeypatch.setattr(
        annotation_workbench, "DATABASE_PATH", data_dir / "annotations.sqlite3"
    )
    pd.DataFrame(
        [
            {
                "query_id": "q1",
                "split": "test",
                "query_text": "query",
                "doc_id": "d1",
                "relevance": "",
            }
        ]
    ).to_csv(pool_path, index=False)
    for annotator, grade in [("A", 3), ("B", 3), ("C", 2)]:
        annotation_workbench.save_rating(
            "q1", "d1", "query", annotator, grade, "evidence"
        )

    exported = annotation_workbench.export_consensus()

    assert exported.iloc[0]["review_status"] == "disagreement"
    assert exported.iloc[0]["relevance"] == ""
    assert "C: 2" in exported.iloc[0]["ratings_summary"]


def test_query_audit_reports_candidates_without_labels() -> None:
    queries = pd.DataFrame(
        [
            {
                "query_id": "q1",
                "split": "test",
                "topic": "topic",
                "query": "question",
                "review_status": "draft",
            }
        ]
    )
    predictions = {
        method: pd.DataFrame(
            [
                {
                    "query_id": "q1",
                    "rank": rank,
                    "doc_id": doc_id,
                    "title": f"title {doc_id}",
                    "source": "source",
                }
                for rank, doc_id in enumerate(doc_ids, start=1)
            ]
        )
        for method, doc_ids in {
            "E0_tfidf": ["d1", "d2"],
            "E1_dense": ["d1", "d3"],
            "E2_rrf_fusion": ["d2", "d1"],
        }.items()
    }
    pool_audit = pd.DataFrame(
        [
            {"query_id": "q1", "doc_id": doc_id}
            for doc_id in ["d1", "d2", "d3"]
        ]
    )

    result = audit_queries.build_review_table(queries, predictions, pool_audit)

    assert result.iloc[0]["candidate_pool_size"] == 3
    assert result.iloc[0]["top1_agreement_count"] == 2
    assert "not relevance judgments" in result.iloc[0]["review_note"]


def test_query_lock_only_accepts_nonempty_test_queries() -> None:
    queries = pd.DataFrame(
        [
            {
                "query_id": "test1",
                "split": "test",
                "query": "question",
                "review_status": "draft",
            },
            {
                "query_id": "dev1",
                "split": "dev",
                "query": "dev question",
                "review_status": "draft",
            },
        ]
    )

    locked = audit_queries.lock_test_query(queries, "test1")

    assert locked.loc[locked["query_id"].eq("test1"), "review_status"].iloc[0] == "locked"
    assert locked.loc[locked["query_id"].eq("dev1"), "review_status"].iloc[0] == "draft"
    assert queries.loc[queries["query_id"].eq("test1"), "review_status"].iloc[0] == "draft"
    with pytest.raises(ValueError, match="split test"):
        audit_queries.lock_test_query(queries, "dev1")


def test_evaluator_rejects_judgments_for_changed_query(tmp_path, monkeypatch) -> None:
    queries_path = tmp_path / "queries.csv"
    judgments_path = tmp_path / "judgments.csv"
    pd.DataFrame(
        [
            {
                "query_id": "q1",
                "split": "test",
                "query": "new wording",
                "review_status": "locked",
            }
        ]
    ).to_csv(queries_path, index=False)
    pd.DataFrame(
        [
            {
                "query_id": "q1",
                "split": "test",
                "query_text": "old wording",
                "doc_id": "d1",
                "relevance": 3,
                "review_status": "consensus",
            }
        ]
    ).to_csv(judgments_path, index=False)
    pool_path = tmp_path / "pool.csv"
    pd.DataFrame([{"query_id": "q1", "split": "test", "doc_id": "d1"}]).to_csv(
        pool_path, index=False
    )
    monkeypatch.setattr(evaluate, "QUERY_PATH", queries_path)
    monkeypatch.setattr(evaluate, "JUDGMENT_PATH", judgments_path)
    monkeypatch.setattr(evaluate, "POOL_PATH", pool_path)

    with pytest.raises(ValueError, match="đã đổi sau khi gắn nhãn"):
        evaluate.main()


def test_evaluator_rejects_unlocked_test_queries(tmp_path, monkeypatch) -> None:
    queries_path = tmp_path / "queries.csv"
    pd.DataFrame(
        [
            {
                "query_id": "q1",
                "split": "test",
                "query": "query",
                "review_status": "draft_needs_human_review",
            }
        ]
    ).to_csv(queries_path, index=False)
    monkeypatch.setattr(evaluate, "QUERY_PATH", queries_path)

    with pytest.raises(ValueError, match="chưa được nhóm duyệt và khóa"):
        evaluate.main()

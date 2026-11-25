from __future__ import annotations

import argparse
import hashlib
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


ROOT = Path(__file__).resolve().parents[1]
CORPUS_PATH = ROOT / "data" / "processed" / "corpus.csv"
QUERIES_PATH = ROOT / "data" / "queries.csv"
OUTPUT_DIR = ROOT / "evaluation" / "candidate_runs"
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
QUERY_VERSION = "draft-v2-prelock"


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame]:
    corpus = pd.read_csv(CORPUS_PATH).fillna("")
    queries = pd.read_csv(QUERIES_PATH).fillna("")
    required_corpus = {"id", "title", "content", "source", "url", "publish_date"}
    required_queries = {"query_id", "split", "query"}
    if not required_corpus.issubset(corpus.columns):
        raise ValueError(f"Corpus thiếu cột: {sorted(required_corpus - set(corpus.columns))}")
    if not required_queries.issubset(queries.columns):
        raise ValueError(f"Queries thiếu cột: {sorted(required_queries - set(queries.columns))}")
    if corpus["id"].duplicated().any():
        raise ValueError("ID corpus không duy nhất.")
    if queries["query_id"].duplicated().any():
        raise ValueError("query_id không duy nhất.")
    corpus = corpus.drop_duplicates(subset=["title", "content"], keep="first").reset_index(drop=True)
    return corpus, queries


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def package_version(package: str) -> str:
    try:
        return version(package)
    except PackageNotFoundError:
        return "not-installed"


def lexical_scores(corpus: pd.DataFrame, query_texts: list[str]) -> np.ndarray:
    documents = (corpus["title"] + " " + corpus["content"]).tolist()
    vectorizer = TfidfVectorizer(
        analyzer="word",
        token_pattern=r"(?u)\b\w+\b",
        ngram_range=(1, 2),
        sublinear_tf=True,
        max_features=300_000,
    )
    document_matrix = vectorizer.fit_transform(documents)
    query_matrix = vectorizer.transform(query_texts)
    return cosine_similarity(query_matrix, document_matrix, dense_output=True)


def dense_scores(corpus: pd.DataFrame, query_texts: list[str]) -> np.ndarray:
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        raise RuntimeError(
            "Thiếu sentence-transformers. Cài dependencies bằng: "
            "python -m pip install -r requirements.txt"
        ) from exc

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = SentenceTransformer(MODEL_NAME, device=device)
    model.max_seq_length = 256
    documents = (
        "Tiêu đề: " + corpus["title"] + "\nNội dung: " + corpus["content"].str.slice(0, 1600)
    ).tolist()
    document_embeddings = model.encode(
        documents,
        batch_size=32,
        show_progress_bar=True,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )
    query_embeddings = model.encode(
        query_texts,
        batch_size=32,
        show_progress_bar=True,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )
    return query_embeddings @ document_embeddings.T


def ranked_ids(scores: np.ndarray, corpus: pd.DataFrame, top_k: int) -> list[list[int]]:
    count = min(top_k, len(corpus))
    return [np.argsort(row)[::-1][:count].tolist() for row in scores]


def write_predictions(
    queries: pd.DataFrame,
    corpus: pd.DataFrame,
    scores_by_method: dict[str, np.ndarray],
    top_k: int,
) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    corpus_rows = corpus.reset_index(drop=True)
    for method, scores in scores_by_method.items():
        rows: list[dict[str, object]] = []
        for query_index, indices in enumerate(ranked_ids(scores, corpus_rows, top_k)):
            for rank, doc_index in enumerate(indices, start=1):
                doc = corpus_rows.iloc[doc_index]
                rows.append(
                    {
                        "query_id": queries.iloc[query_index]["query_id"],
                        "split": queries.iloc[query_index]["split"],
                        "rank": rank,
                        "doc_id": doc["id"],
                        "score": float(scores[query_index, doc_index]),
                        "title": doc["title"],
                        "source": doc["source"],
                        "url": doc["url"],
                        "snippet": str(doc["content"])[:500],
                    }
                )
        pd.DataFrame(rows).to_csv(
            OUTPUT_DIR / f"topk_{method}.csv", index=False, encoding="utf-8-sig"
        )


def rrf_fusion(
    lexical: np.ndarray, dense: np.ndarray, constant: int = 60
) -> np.ndarray:
    lexical_order = np.argsort(-lexical, axis=1)
    dense_order = np.argsort(-dense, axis=1)
    fused = np.zeros_like(lexical, dtype=np.float64)
    rows = np.arange(lexical.shape[0])[:, None]
    ranks = np.arange(1, lexical.shape[1] + 1, dtype=np.float64)
    fused[rows, lexical_order] += 1.0 / (constant + ranks)
    fused[rows, dense_order] += 1.0 / (constant + ranks)
    return fused


def write_judgment_pool(
    queries: pd.DataFrame,
    corpus: pd.DataFrame,
    scores_by_method: dict[str, np.ndarray],
    pool_depth: int,
) -> None:
    corpus_rows = corpus.reset_index(drop=True)
    judgment_path = ROOT / "data" / "relevance_judgments_template.csv"
    previous_judgments: dict[tuple[str, str], dict[str, object]] = {}
    if judgment_path.exists():
        existing = pd.read_csv(judgment_path).fillna("")
        if {"query_id", "doc_id", "query_text"}.issubset(existing.columns):
            previous_judgments = {
                (str(row["query_id"]), str(row["doc_id"])): row
                for row in existing.to_dict("records")
            }

    rows: dict[tuple[str, str], dict[str, object]] = {}
    audit_rows: list[dict[str, object]] = []
    for method, scores in scores_by_method.items():
        for query_index, indices in enumerate(ranked_ids(scores, corpus_rows, pool_depth)):
            query_id = queries.iloc[query_index]["query_id"]
            for rank, doc_index in enumerate(indices, start=1):
                doc = corpus_rows.iloc[doc_index]
                key = (query_id, str(doc["id"]))
                audit_rows.append(
                    {
                        "query_id": query_id,
                        "doc_id": doc["id"],
                        "method": method,
                        "rank": rank,
                    }
                )
                if key not in rows:
                    query_text = str(queries.iloc[query_index]["query"])
                    previous = previous_judgments.get(key, {})
                    same_query = previous.get("query_text") == query_text
                    rows[key] = {
                        "query_id": query_id,
                        "split": queries.iloc[query_index]["split"],
                        "query_text": query_text,
                        "doc_id": doc["id"],
                        "title": doc["title"],
                        "source": doc["source"],
                        "url": doc["url"],
                        "snippet": str(doc["content"])[:1000],
                        "relevance": previous.get("relevance", "") if same_query else "",
                        "annotator": previous.get("annotator", "") if same_query else "",
                        "notes": previous.get("notes", "") if same_query else "",
                    }
    pool = pd.DataFrame(rows.values())
    query_order = {query_id: i for i, query_id in enumerate(queries["query_id"])}
    pool["_query_order"] = pool["query_id"].map(query_order)
    pool = pool.sort_values(["_query_order", "doc_id"])
    pool["_shuffle_key"] = (
        pool["query_id"].astype(str) + ":" + pool["doc_id"].astype(str)
    ).map(lambda value: hashlib.sha256(value.encode("utf-8")).hexdigest())
    pool = pool.sort_values(["_query_order", "_shuffle_key"]).drop(
        columns=["_query_order", "_shuffle_key"]
    )
    pool.to_csv(
        judgment_path,
        index=False,
        encoding="utf-8-sig",
    )
    (ROOT / "evaluation").mkdir(parents=True, exist_ok=True)
    pd.DataFrame(audit_rows).to_csv(
        ROOT / "evaluation" / "candidate_pool_audit.csv",
        index=False,
        encoding="utf-8-sig",
    )


def write_experiment_log(
    queries: pd.DataFrame,
    indexed_documents: int,
    scores_by_method: dict[str, np.ndarray],
    top_k: int,
    pool_depth: int,
) -> None:
    run_time = datetime.now(timezone.utc).isoformat()
    corpus_hash = sha256_file(CORPUS_PATH)
    query_hash = sha256_file(QUERIES_PATH)
    hypotheses = {
        "E0_tfidf": "Lexical TF-IDF baseline; exact economic terms may rank well.",
        "E1_dense": "Multilingual sentence embeddings may retrieve paraphrases.",
        "E2_rrf_fusion": "RRF may combine lexical precision with dense semantic recall.",
    }
    rows = []
    for method in scores_by_method:
        rows.append(
            {
                "run_timestamp_utc": run_time,
                "method": method,
                "hypothesis": hypotheses[method],
                "corpus_file": "data/processed/corpus.csv",
                "corpus_sha256": corpus_hash,
                "corpus_rows_indexed": indexed_documents,
                "query_file": "data/queries.csv",
                "query_sha256": query_hash,
                "script_sha256": sha256_file(Path(__file__)),
                "query_version": QUERY_VERSION,
                "queries_dev": int(queries["split"].eq("dev").sum()),
                "queries_test": int(queries["split"].eq("test").sum()),
                "tfidf_config": "word ngrams 1-2; sublinear_tf; max_features=300000; cosine",
                "dense_model": MODEL_NAME if method != "E0_tfidf" else "",
                "dense_device": (
                    f"cuda:{torch.cuda.get_device_name(0)}"
                    if method != "E0_tfidf" and torch.cuda.is_available()
                    else "cpu" if method != "E0_tfidf" else ""
                ),
                "dense_max_seq_length": 256 if method != "E0_tfidf" else "",
                "fusion": "RRF k=60" if method == "E2_rrf_fusion" else "",
                "scikit_learn": package_version("scikit-learn"),
                "sentence_transformers": package_version("sentence-transformers"),
                "top_k": top_k,
                "pool_depth_per_method": pool_depth,
                "prediction_file": f"evaluation/candidate_runs/topk_{method}.csv",
                "metrics": "pending human relevance judgments",
            }
        )
    pd.DataFrame(rows).to_csv(
        ROOT / "evaluation" / "experiments.csv", index=False, encoding="utf-8-sig"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run E0/E1/E2 retrieval and pool candidates.")
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument("--pool-depth", type=int, default=5)
    args = parser.parse_args()
    if args.top_k < 5 or args.pool_depth < 5:
        raise ValueError("top-k và pool-depth phải ít nhất là 5.")

    original_corpus_rows = len(pd.read_csv(CORPUS_PATH))
    corpus, queries = load_inputs()
    query_texts = queries["query"].tolist()
    print(
        f"Corpus: {original_corpus_rows} bài, {len(corpus)} bài sau loại trùng chính xác; "
        f"queries: {len(queries)}"
    )

    lexical = lexical_scores(corpus, query_texts)
    dense = dense_scores(corpus, query_texts)
    fused = rrf_fusion(lexical, dense)
    scores = {"E0_tfidf": lexical, "E1_dense": dense, "E2_rrf_fusion": fused}
    write_predictions(queries, corpus, scores, args.top_k)
    write_judgment_pool(queries, corpus, scores, args.pool_depth)
    write_experiment_log(queries, len(corpus), scores, args.top_k, args.pool_depth)
    print(f"Đã ghi predictions tại {OUTPUT_DIR}")
    print(f"Đã tạo pool chấm tại {ROOT / 'data' / 'relevance_judgments_template.csv'}")


if __name__ == "__main__":
    main()

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
POOL_PATH = ROOT / "data" / "relevance_judgments_template.csv"
EXPORT_PATH = ROOT / "data" / "relevance_judgments.csv"
DATABASE_PATH = ROOT / "data" / "annotations.sqlite3"


def connect() -> sqlite3.Connection:
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH, timeout=30)
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS ratings (
            query_id TEXT NOT NULL,
            doc_id TEXT NOT NULL,
            query_text TEXT NOT NULL DEFAULT '',
            annotator TEXT NOT NULL,
            relevance INTEGER NOT NULL CHECK (relevance BETWEEN 0 AND 3),
            notes TEXT NOT NULL DEFAULT '',
            updated_at TEXT NOT NULL,
            PRIMARY KEY (query_id, doc_id, annotator)
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS adjudications (
            query_id TEXT NOT NULL,
            doc_id TEXT NOT NULL,
            query_text TEXT NOT NULL DEFAULT '',
            adjudicator TEXT NOT NULL,
            relevance INTEGER NOT NULL CHECK (relevance BETWEEN 0 AND 3),
            notes TEXT NOT NULL DEFAULT '',
            updated_at TEXT NOT NULL,
            PRIMARY KEY (query_id, doc_id)
        )
        """
    )
    for table in ("ratings", "adjudications"):
        columns = {
            str(row[1]) for row in connection.execute(f"PRAGMA table_info({table})")
        }
        if "query_text" not in columns:
            connection.execute(
                f"ALTER TABLE {table} ADD COLUMN query_text TEXT NOT NULL DEFAULT ''"
            )
    connection.commit()
    return connection


def load_pool() -> pd.DataFrame:
    if not POOL_PATH.exists():
        raise FileNotFoundError(f"Chưa có candidate pool: {POOL_PATH}")
    return pd.read_csv(POOL_PATH).fillna("")


def load_ratings() -> tuple[pd.DataFrame, pd.DataFrame]:
    with connect() as connection:
        ratings = pd.read_sql_query("SELECT * FROM ratings", connection)
        adjudications = pd.read_sql_query("SELECT * FROM adjudications", connection)
    return ratings, adjudications


def save_rating(
    query_id: str,
    doc_id: str,
    query_text: str,
    annotator: str,
    relevance: int,
    notes: str,
) -> None:
    if relevance not in range(4):
        raise ValueError("Relevance phải là số nguyên 0..3.")
    annotator = annotator.strip()
    if not annotator:
        raise ValueError("Cần ghi tên/mã người gắn nhãn.")
    now = datetime.now(timezone.utc).isoformat()
    with connect() as connection:
        connection.execute(
            """
            INSERT INTO ratings
                (query_id, doc_id, query_text, annotator, relevance, notes, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(query_id, doc_id, annotator) DO UPDATE SET
                query_text = excluded.query_text,
                relevance = excluded.relevance,
                notes = excluded.notes,
                updated_at = excluded.updated_at
            """,
            (query_id, doc_id, query_text, annotator, relevance, notes.strip(), now),
        )
        connection.commit()


def save_adjudication(
    query_id: str,
    doc_id: str,
    query_text: str,
    adjudicator: str,
    relevance: int,
    notes: str,
) -> None:
    if relevance not in range(4):
        raise ValueError("Relevance cuối phải là số nguyên 0..3.")
    adjudicator = adjudicator.strip()
    if not adjudicator:
        raise ValueError("Cần ghi tên/mã người phân xử.")
    now = datetime.now(timezone.utc).isoformat()
    with connect() as connection:
        connection.execute(
            """
            INSERT INTO adjudications
                (query_id, doc_id, query_text, adjudicator, relevance, notes, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(query_id, doc_id) DO UPDATE SET
                query_text = excluded.query_text,
                adjudicator = excluded.adjudicator,
                relevance = excluded.relevance,
                notes = excluded.notes,
                updated_at = excluded.updated_at
            """,
            (query_id, doc_id, query_text, adjudicator, relevance, notes.strip(), now),
        )
        connection.commit()


def build_consensus(allow_single_annotator: bool = False) -> pd.DataFrame:
    pool = load_pool()
    ratings, adjudications = load_ratings()
    pool["final_relevance"] = pd.Series("", index=pool.index, dtype=object)
    if "review_status" not in pool:
        pool["review_status"] = ""
    pool["annotator_a"] = pd.Series("", index=pool.index, dtype=object)
    pool["annotator_a_relevance"] = pd.Series("", index=pool.index, dtype=object)
    pool["annotator_b"] = pd.Series("", index=pool.index, dtype=object)
    pool["annotator_b_relevance"] = pd.Series("", index=pool.index, dtype=object)
    pool["ratings_summary"] = ""
    pool["adjudicator"] = ""
    pool["adjudication_notes"] = ""
    if "relevance" in pool:
        pool["relevance"] = pool["relevance"].astype(object)
    rating_groups: dict[tuple[str, str, str], list[dict[str, object]]] = {}
    for row in ratings.to_dict("records"):
        key = (
            str(row["query_id"]),
            str(row["doc_id"]),
            str(row["query_text"]),
        )
        rating_groups.setdefault(key, []).append(row)
    adjudication_map = {
        (str(row["query_id"]), str(row["doc_id"]), str(row["query_text"])): row
        for row in adjudications.to_dict("records")
    }

    for index, row in pool.iterrows():
        key = (
            str(row["query_id"]),
            str(row["doc_id"]),
            str(row.get("query_text", "")),
        )
        latest_by_annotator: dict[str, dict[str, object]] = {}
        for rating in rating_groups.get(key, []):
            annotator_id = str(rating["annotator"])
            previous = latest_by_annotator.get(annotator_id)
            if previous is None or str(rating["updated_at"]) > str(previous["updated_at"]):
                latest_by_annotator[annotator_id] = rating
        candidate_ratings = [
            latest_by_annotator[annotator_id] for annotator_id in sorted(latest_by_annotator)
        ]
        labels: list[int] = []
        annotators: list[str] = []
        for rating in candidate_ratings:
            annotator = str(rating["annotator"])
            label = int(rating["relevance"])
            annotators.append(annotator)
            labels.append(label)
        if labels:
            pool.at[index, "annotator_a"] = annotators[0]
            pool.at[index, "annotator_a_relevance"] = labels[0]
        if len(labels) >= 2:
            pool.at[index, "annotator_b"] = annotators[1]
            pool.at[index, "annotator_b_relevance"] = labels[1]
        if labels:
            pool.at[index, "ratings_summary"] = "; ".join(
                f"{annotator}: {label}" for annotator, label in zip(annotators, labels)
            )

        adjudication = adjudication_map.get(key)
        if adjudication:
            pool.at[index, "adjudicator"] = adjudication["adjudicator"]
            pool.at[index, "adjudication_notes"] = adjudication["notes"]
            final_label = int(adjudication["relevance"])
            pool.at[index, "final_relevance"] = final_label
            pool.at[index, "relevance"] = final_label
            pool.at[index, "review_status"] = "adjudicated"
        elif len(labels) >= 2 and len(set(labels)) == 1:
            pool.at[index, "final_relevance"] = labels[0]
            pool.at[index, "relevance"] = labels[0]
            pool.at[index, "review_status"] = "consensus"
        elif len(labels) >= 2:
            pool.at[index, "final_relevance"] = ""
            pool.at[index, "relevance"] = ""
            pool.at[index, "review_status"] = "disagreement"
        elif labels:
            if allow_single_annotator:
                pool.at[index, "final_relevance"] = labels[0]
                pool.at[index, "relevance"] = labels[0]
                pool.at[index, "review_status"] = "single_annotator"
            else:
                pool.at[index, "final_relevance"] = ""
                pool.at[index, "relevance"] = ""
                pool.at[index, "review_status"] = "needs_second_annotator"
        else:
            has_stale_rating = any(
                rating_query_id == key[0]
                and rating_doc_id == key[1]
                and rating_query_text != key[2]
                for rating_query_id, rating_doc_id, rating_query_text in rating_groups
            )
            has_stale_adjudication = any(
                adjudication_query_id == key[0]
                and adjudication_doc_id == key[1]
                and adjudication_query_text != key[2]
                for adjudication_query_id, adjudication_doc_id, adjudication_query_text
                in adjudication_map
            )
            pool.at[index, "final_relevance"] = ""
            pool.at[index, "relevance"] = ""
            pool.at[index, "review_status"] = (
                "stale_query_requires_reannotation"
                if has_stale_rating or has_stale_adjudication
                else "unjudged"
            )

    return pool


def export_consensus(allow_single_annotator: bool = False) -> pd.DataFrame:
    pool = build_consensus(allow_single_annotator=allow_single_annotator)
    pool.to_csv(EXPORT_PATH, index=False, encoding="utf-8-sig")
    return pool

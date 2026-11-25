from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
import torch
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.run_retrieval import MODEL_NAME, rrf_fusion


CORPUS_PATH = ROOT / "data" / "processed" / "corpus.csv"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


@st.cache_data(show_spinner=False)
def load_corpus() -> pd.DataFrame:
    corpus = pd.read_csv(CORPUS_PATH).fillna("")
    return corpus.drop_duplicates(subset=["title", "content"], keep="first").reset_index(
        drop=True
    )


@st.cache_resource(show_spinner="Đang dựng chỉ mục từ vựng...")
def load_lexical_index() -> tuple[TfidfVectorizer, object]:
    corpus = load_corpus()
    documents = (corpus["title"] + " " + corpus["content"]).tolist()
    vectorizer = TfidfVectorizer(
        analyzer="word",
        token_pattern=r"(?u)\b\w+\b",
        ngram_range=(1, 2),
        sublinear_tf=True,
        max_features=300_000,
    )
    return vectorizer, vectorizer.fit_transform(documents)


@st.cache_resource(show_spinner="Đang tải mô hình embedding...")
def load_embedding_model() -> SentenceTransformer:
    model = SentenceTransformer(MODEL_NAME, device=DEVICE)
    model.max_seq_length = 256
    return model


@st.cache_resource(show_spinner="Đang mã hóa corpus trên GPU/CPU lần đầu...")
def load_document_embeddings() -> np.ndarray:
    corpus = load_corpus()
    documents = (
        "Tiêu đề: " + corpus["title"] + "\nNội dung: " + corpus["content"].str.slice(0, 1600)
    ).tolist()
    return load_embedding_model().encode(
        documents,
        batch_size=32,
        show_progress_bar=False,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )


def retrieve(query: str, method: str, top_k: int) -> tuple[pd.DataFrame, np.ndarray]:
    corpus = load_corpus()
    vectorizer, document_matrix = load_lexical_index()
    lexical_scores = cosine_similarity(
        vectorizer.transform([query]), document_matrix, dense_output=True
    )[0]

    if method == "E0 - TF-IDF":
        scores = lexical_scores
    else:
        model = load_embedding_model()
        query_embedding = model.encode(
            [query], normalize_embeddings=True, convert_to_numpy=True, show_progress_bar=False
        )
        dense_scores = (query_embedding @ load_document_embeddings().T)[0]
        if method == "E1 - Dense":
            scores = dense_scores
        else:
            scores = rrf_fusion(lexical_scores[None, :], dense_scores[None, :])[0]

    indices = np.argsort(scores)[::-1][:top_k]
    return corpus.iloc[indices].copy().reset_index(drop=True), scores[indices]


st.set_page_config(page_title="Tìm kiếm tin kinh tế", page_icon="🔎", layout="wide")
st.title("Tìm kiếm ngữ nghĩa tin tức kinh tế")
st.caption(
    "Demo CSC4007 · UVN-1 · Kết quả là tài liệu truy hồi, không phải tư vấn đầu tư."
)

corpus = load_corpus()
with st.sidebar:
    st.header("Cấu hình")
    method = st.selectbox("Phương pháp", ["E0 - TF-IDF", "E1 - Dense", "E2 - Fusion"])
    top_k = st.slider("Số kết quả", min_value=3, max_value=10, value=5)
    st.caption(f"Corpus: {len(corpus):,} bài sau loại trùng chính xác")
    st.caption(f"Thiết bị embedding: {torch.cuda.get_device_name(0) if DEVICE == 'cuda' else 'CPU'}")
    st.caption("Dense model: paraphrase-multilingual-MiniLM-L12-v2")

query = st.text_input(
    "Nhập câu hỏi hoặc nhu cầu tìm tin",
    placeholder="Ví dụ: Ngân hàng nào điều chỉnh lãi suất tiền gửi gần đây?",
)

if st.button("Tìm kiếm", type="primary", disabled=not query.strip()):
    with st.spinner("Đang tìm trong corpus..."):
        results, scores = retrieve(query.strip(), method, top_k)
    st.subheader(f"Kết quả cho: “{query.strip()}”")
    for rank, (_, row) in enumerate(results.iterrows(), start=1):
        with st.container(border=True):
            st.markdown(f"**{rank}. {row['title']}**")
            st.caption(
                f"Nguồn: {row['source']} · Ngày: {row['publish_date']} · "
                f"ID: {row['id']} · Retrieval score: {scores[rank - 1]:.4f}"
            )
            st.write(str(row["content"])[:700] + ("..." if len(str(row["content"])) > 700 else ""))
            st.markdown(f"[Mở bài gốc]({row['url']})")
    st.caption(
        "Retrieval score chỉ dùng để xếp hạng trong phương pháp đã chọn; không phải "
        "xác suất liên quan hay nhãn gold."
    )
else:
    st.info("Nhập truy vấn để xem top-k bài báo, trích đoạn và nguồn.")

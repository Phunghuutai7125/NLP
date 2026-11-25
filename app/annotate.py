from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.annotation_workbench import (  # noqa: E402
    build_consensus,
    export_consensus,
    load_pool,
    load_ratings,
    save_adjudication,
    save_rating,
)
from src.audit_queries import lock_test_query  # noqa: E402


st.set_page_config(page_title="Chấm relevance", page_icon="📝", layout="wide")
st.title("Bàn chấm relevance cho Đề tài 3")
st.caption(
    "Chấm mức độ bài báo đáp ứng nhu cầu truy vấn; không xem rank/score của các mô hình."
)

pool = load_pool()
ratings, adjudications = load_ratings()
if "query_text" not in pool:
    queries = pd.read_csv(ROOT / "data" / "queries.csv").fillna("")
    pool = pool.merge(queries[["query_id", "query"]], on="query_id", how="left")
    pool.rename(columns={"query": "query_text"}, inplace=True)
left, right = st.columns(2)
with left:
    st.metric("Ứng viên trong pool", len(pool))
    st.metric("Ứng viên test", int(pool["split"].eq("test").sum()))
with right:
    st.metric("Lượt chấm đã lưu", len(ratings))
    st.metric("Đã phân xử", len(adjudications))

mode = st.radio(
    "Chế độ",
    [
        "Duyệt truy vấn test",
        "Gắn nhãn độc lập",
        "Hậu kiểm mẫu 20% (83 ứng viên)",
        "Phân xử bất đồng",
        "Xuất nhãn đồng thuận",
    ],
    horizontal=True,
    key="annotation_mode",
)
if mode == "Hậu kiểm mẫu 20% (83 ứng viên)":
    split_filter = "test"
else:
    split_filter = st.selectbox("Split cần chấm", ["test", "dev", "all"], index=0)

if mode == "Duyệt truy vấn test":
    query_path = ROOT / "data" / "queries.csv"
    review_path = ROOT / "evaluation" / "query_candidate_review.csv"
    queries = pd.read_csv(query_path).fillna("")
    review = pd.read_csv(review_path).fillna("")
    test_queries = queries.loc[queries["split"].eq("test")]
    locked_count = int(test_queries["review_status"].eq("locked").sum())
    st.progress(locked_count / max(len(test_queries), 1))
    st.caption(f"Đã duyệt và khóa {locked_count}/{len(test_queries)} truy vấn test.")
    query_id = st.selectbox("Chọn truy vấn cần xem", test_queries["query_id"].tolist())
    query = test_queries.loc[test_queries["query_id"].eq(query_id)].iloc[0]
    query_review = review.loc[review["query_id"].eq(query_id)].iloc[0]
    st.markdown(f"### {query['topic']}")
    st.info(str(query["query"]))
    st.caption(
        f"Candidate pool: {int(query_review['candidate_pool_size'])} bài · "
        f"Trạng thái: {query['review_status']}"
    )
    st.warning(
        "Các kết quả dưới đây chỉ hỗ trợ kiểm tra truy vấn có câu trả lời khả dĩ; "
        "không phải nhãn relevance. Chỉ bấm khóa sau khi bạn đã duyệt nội dung."
    )
    columns = st.columns(3)
    for column, method, label in zip(
        columns, ("E0_top3_json", "E1_top3_json", "E2_top3_json"), ("E0", "E1", "E2")
    ):
        with column:
            st.markdown(f"**{label} — top 3 ứng viên**")
            candidates = json.loads(query_review[method])
            st.dataframe(
                pd.DataFrame(candidates)[["rank", "title", "source", "doc_id"]],
                hide_index=True,
                width="stretch",
            )
    if query["review_status"] == "locked":
        st.success("Truy vấn này đã được khóa.")
    elif st.button("Xác nhận đã duyệt và khóa truy vấn này"):
        queries = lock_test_query(queries, str(query_id))
        queries.to_csv(query_path, index=False, encoding="utf-8-sig")
        review.loc[review["query_id"].eq(query_id), "query_status"] = "locked"
        review.to_csv(review_path, index=False, encoding="utf-8-sig")
        st.rerun()
    st.stop()

if mode == "Xuất nhãn đồng thuận":
    annotation_policy = st.radio(
        "Quy trình gắn nhãn",
        [
            "Hậu kiểm 20% (giữ nhãn một người cho phần còn lại)",
            "Một người chấm toàn bộ",
            "Hai người chấm độc lập toàn bộ pool",
        ],
        help=(
            "Với mẫu hậu kiểm 20%, chọn lựa chọn đầu: các ứng viên ngoài mẫu vẫn "
            "giữ nhãn single_annotator; bất đồng trong mẫu cần được phân xử."
        ),
    )
    allow_single_annotator = not annotation_policy.startswith("Hai người")
    if st.button("Cập nhật file judgments"):
        updated = export_consensus(allow_single_annotator=allow_single_annotator)
        accepted_statuses = ["consensus", "adjudicated"]
        if allow_single_annotator:
            accepted_statuses.append("single_annotator")
        consensus = int(updated["review_status"].isin(accepted_statuses).sum())
        disagreements = int(updated["review_status"].eq("disagreement").sum())
        st.success(
            f"Đã xuất {consensus} nhãn hợp lệ theo quy trình đã chọn vào "
            "`data/relevance_judgments.csv`; "
            f"{disagreements} trường hợp còn bất đồng."
        )
    st.info(
        "Với hậu kiểm mẫu, chọn chính sách 20% để giữ nhãn single_annotator ở "
        "những ứng viên ngoài mẫu. Các bất đồng trong mẫu phải được phân xử "
        "trước khi dùng nhãn cuối. Dev có thể còn trống."
    )
    st.stop()

if mode == "Phân xử bất đồng":
    consensus = build_consensus()
    candidates = consensus.loc[consensus["review_status"].eq("disagreement")].copy()
    actor_label = "Người phân xử"
    if candidates.empty:
        st.success("Hiện không có bất đồng nào cần phân xử.")
        st.stop()
elif mode == "Hậu kiểm mẫu 20% (83 ứng viên)":
    sample_path = ROOT / "evaluation" / "second_reviewer_sample.csv"
    candidates = pd.read_csv(sample_path).fillna("")
    if len(candidates) != 83:
        raise ValueError(
            f"Mẫu hậu kiểm phải có 83 ứng viên; hiện có {len(candidates)}."
        )
    actor_label = "Người hậu kiểm thứ hai"
else:
    candidates = pool.copy()
    actor_label = "Người chấm"

independent_mode = mode in (
    "Gắn nhãn độc lập",
    "Hậu kiểm mẫu 20% (83 ứng viên)",
)
if split_filter != "all" and "split" in candidates.columns:
    candidates = candidates.loc[candidates["split"].eq(split_filter)].copy()

annotator = st.text_input(actor_label + " (tên hoặc mã)", placeholder="Ví dụ: SV01")
if not annotator.strip():
    st.warning("Nhập tên/mã người chấm để bắt đầu.")
    st.stop()
if (
    mode == "Hậu kiểm mẫu 20% (83 ứng viên)"
    and annotator.strip().casefold() == "duy"
):
    st.error("Hãy dùng tên/mã riêng của người hậu kiểm, không nhập mã của Duy.")
    st.stop()

if independent_mode:
    own_keys = set(
        zip(
            ratings.loc[ratings["annotator"].eq(annotator.strip()), "query_id"].astype(str),
            ratings.loc[ratings["annotator"].eq(annotator.strip()), "doc_id"].astype(str),
            ratings.loc[ratings["annotator"].eq(annotator.strip()), "query_text"].astype(str),
        )
    )
    candidates["_key"] = list(
        zip(
            candidates["query_id"].astype(str),
            candidates["doc_id"].astype(str),
            candidates["query_text"].astype(str),
        )
    )
    candidates = candidates.loc[~candidates["_key"].isin(own_keys)].copy()
    candidates.drop(columns="_key", inplace=True)
else:
    candidates = candidates.loc[candidates["review_status"].eq("disagreement")].copy()

if candidates.empty:
    st.success("Không còn ứng viên chưa chấm cho mã này.")
    st.stop()

if independent_mode:
    if mode == "Gắn nhãn độc lập":
        st.caption(
            "Mỗi người chấm thấy toàn bộ pool độc lập; các nhãn của người khác không hiện "
            "để giảm ảnh hưởng lẫn nhau."
        )
    else:
        st.caption(
            "Chỉ hiện 83 mẫu hậu kiểm; điểm/ghi chú của Duy và AI không được hiển thị. "
            "Hãy chấm độc lập rồi lưu từng mục."
        )

query_ids = candidates["query_id"].drop_duplicates().tolist()
selected_query = st.selectbox("Truy vấn", query_ids)
query_candidates = candidates.loc[candidates["query_id"].eq(selected_query)].reset_index(drop=True)
query_text = str(query_candidates.iloc[0].get("query_text", ""))
if query_text:
    st.info(query_text)

candidate_index = st.number_input(
    "Ứng viên trong truy vấn (đánh số từ 1)",
    min_value=1,
    max_value=len(query_candidates),
    value=1,
    step=1,
)
candidate = query_candidates.iloc[int(candidate_index) - 1]

st.markdown(f"### {candidate['title']}")
st.caption(f"ID: {candidate['doc_id']} · Nguồn: {candidate['source']}")
st.write(str(candidate["snippet"]))
st.markdown(f"[Mở bài gốc]({candidate['url']})")

if independent_mode:
    st.markdown(
        "**0** không liên quan · **1** ít liên quan · **2** liên quan · **3** rất liên quan"
    )
    saved = ratings.loc[
        ratings["query_id"].astype(str).eq(str(candidate["query_id"]))
        & ratings["doc_id"].astype(str).eq(str(candidate["doc_id"]))
        & ratings["query_text"].astype(str).eq(str(candidate["query_text"]))
        & ratings["annotator"].eq(annotator.strip())
    ]
    default_label = int(saved.iloc[0]["relevance"]) if not saved.empty else 0
    label = st.radio(
        "Mức relevance",
        options=[0, 1, 2, 3],
        index=default_label,
        horizontal=True,
        format_func=lambda value: {
            0: "0 - Không liên quan",
            1: "1 - Ít liên quan",
            2: "2 - Liên quan",
            3: "3 - Rất liên quan",
        }[value],
    )
    notes = st.text_area("Ghi chú/bằng chứng (tùy chọn)")
    if st.button("Lưu nhãn"):
        save_rating(
            str(candidate["query_id"]),
            str(candidate["doc_id"]),
            str(candidate["query_text"]),
            annotator,
            int(label),
            notes,
        )
        st.success("Đã lưu lượt chấm riêng của bạn.")
        st.rerun()
else:
    st.write(f"Các lượt chấm độc lập: **{candidate['ratings_summary']}**")
    final_label = st.radio(
        "Nhãn cuối sau khi xem xét chứng cứ",
        options=[0, 1, 2, 3],
        horizontal=True,
        format_func=lambda value: {
            0: "0 - Không liên quan",
            1: "1 - Ít liên quan",
            2: "2 - Liên quan",
            3: "3 - Rất liên quan",
        }[value],
    )
    notes = st.text_area("Lý do phân xử (bắt buộc)")
    if st.button("Lưu phân xử", disabled=not notes.strip()):
        save_adjudication(
            str(candidate["query_id"]),
            str(candidate["doc_id"]),
            str(candidate["query_text"]),
            annotator,
            int(final_label),
            notes,
        )
        st.success("Đã lưu quyết định phân xử.")
        st.rerun()

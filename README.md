# De tai 3 - Tim kiem ngu nghia tin tuc kinh te tieng Viet

Du an CSC4007 ve truy hoi tin tuc kinh te theo truy van tu nhien. Corpus ban dau
duoc tai tu [UVN-1 tren Hugging Face](https://huggingface.co/datasets/undertheseanlp/UVN-1).

## Trang thai

- Da tai snapshot UVN-1 va tach 1.113 bai co category `Kinh doanh`.
- Da tao 50 truy van nhap (10 dev, 40 test); 15 truy van duoc sua truoc khi khoa, xem `data/query_revision_log.csv`.
- Test split da khoa du 40 cau ngay 2026-11-11 theo yeu cau nguoi dung sau khi duyet wording va top-3 ung vien; wording khong thay doi. Moi thay doi tiep theo can duoc ghi log va xu ly nhu mot lan danh gia exploratory.
- Da chay E0 TF-IDF, E1 multilingual sentence embeddings va E2 RRF; top-10 va candidate pool da tao.
- AI da tao goi y cho 411 ung vien test trong `evaluation/ai_provisional_judgments.csv`; day khong phai gold. Duy da cham ca 411 ung vien test. Thanh vien thu hai (Tai) da hoan thanh hau kiem doc lap 83 ung vien (20,2%) tai `evaluation/second_reviewer_sample.csv` va `evaluation/second_reviewer_audit.csv`. Ket qua hau kiem: dong thuan chinh xac 21/83 (25,30%), linear weighted Cohen's Kappa = 0,0778. Yeu cau hau kiem nguoi thu hai (>=20%) da duoc thuc hien hop le. Metric chinh thuc da duoc tinh tren candidate pool bang `src/evaluate.py`.
- Diem AI tham khao duoc luu rieng trong `evaluation/ai_provisional_metrics.csv`; khong trinh bay nhu ket qua chinh thuc.
- Khong dung nhan category `Kinh doanh` lam relevance label.

## Du lieu va quyen su dung

Xem [data/README.md](data/README.md), [data_card.md](data_card.md) va
[data_quality_report.md](data_quality_report.md). Dataset card tren Hugging Face
khai bao CC BY-NC 4.0. Ban tin goc co the co quyen rieng cua cac toa soan; khong
cong khai lai snapshot/noi dung bai bao neu chua xac minh quyen tai phan phoi.

## Cau truc

- `data/raw/uvn1_train.parquet`: snapshot goc da tai (3.268 bai).
- `data/processed/corpus.csv`: tap con category `Kinh doanh`.
- `data/data_manifest.csv`: metadata va ID on dinh cua tap con.
- `data/queries.csv`: 50 truy van nhap, chia dev/test.
- `data/query_revision_log.csv`: lich su sua truy van truoc khi khoa test.
- `data/annotation_guideline.md`: huong dan cham relevance va ghi chu quy trinh nhan.
- `src/run_retrieval.py`: chay E0 lexical, E1 sentence embeddings, E2 RRF va tao pool.
- `src/evaluate.py`: tinh nDCG@5/MRR@5 khi judgments day du.
- `evaluation/candidate_runs/`: top-10 ket qua cho 3 he thong.
- `data/relevance_judgments_template.csv`: pool da xao tron, chua gan nhan.
- `evaluation/candidate_pool_audit.csv`: doi ung ung vien voi he thong/rank (khong dung khi cham).
- `evaluation/experiments.csv`: cau hinh va dau vao cua lan chay gan nhat.
- `evaluation/query_candidate_review.csv`: top-3 candidates de nhom duyet truy van truoc khi khoa.
- `evaluation/query_review_notes.md`: ghi ro gioi han cua qua trinh duyet query.
- `evaluation/ai_provisional_judgments.csv` va `evaluation/ai_provisional_metrics.csv`: ban de xuat AI ban dau, luu de doi chieu provenance.
- `evaluation/metrics_summary.csv`: bang metric chinh thuc tinh boi `src/evaluate.py` cho E0, E1, E2.
- `evaluation/second_reviewer_sample.csv` va `evaluation/second_reviewer_audit.csv`: phieu 83 muc (20,2%) Tai da hau kiem doc lap va bang so sanh, danh gia do dong thuan lien-cham voi Duy.
- `evaluation/ai_second_reviewer_assessment.csv`: danh gia AI provisional rieng cho 83 muc; khong phai nhan nguoi hoac phan xu cuoi cung.
- `evaluation/duy_review_queue.csv`: phieu 409 ung vien Duy da cham; diem va ghi chu Duy duoc doi chieu tu `duy_judgments.csv`, trang thai da cap nhat.
- `app/app.py`: demo Streamlit; chay bang `streamlit run app/app.py`.
- `app/annotate.py`: giao dien cham doc lap, phan xu bat dong va xuat nhan dong thuan.
- `data/annotations.sqlite3`: lich su ratings/adjudications duoc tao khi dung cong cu cham.
- `data/relevance_judgments.csv`: trang thai cham hien tai; ca 411 ung vien test co nhan Duy va duoc danh dau `single_annotator`, cac muc dev con trong.
- `evaluation/ai_provisional_metrics.csv`: diem exploratory tinh tren goi y AI; khong phai ket qua chinh thuc.
- `tests/`: kiem thu retrieval va metric.
- `evaluation/error_analysis_template.md`: 10 mau ket qua relevance thap da doi chieu voi nhan va ghi chu cua Duy; cac nguyen nhan loi la nhan dinh phan tich.
- `.gitignore`: loai bo Python cache va virtualenv khoi repository.

## Chay demo

Tu thu muc nay:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install torch --index-url https://download.pytorch.org/whl/cpu
python -m pip install -r requirements.txt
streamlit run app/app.py
```

Mo cua so terminal khac de cham nhan:

```powershell
.\.venv\Scripts\Activate.ps1
streamlit run app/annotate.py --server.port 8502
```

Test split đã được nhóm duyệt và khóa; không cần chạy lại bước duyệt truy vấn.
Hậu kiểm độc lập 83/411 nhãn (20,2%) đã hoàn tất và được lưu tại
`evaluation/second_reviewer_sample.csv` cùng
`evaluation/second_reviewer_audit.csv`. Độ đồng thuận chính xác là 21/83
(25,30%); kết quả này được báo cáo như kiểm tra độ nhất quán, không tự động thay
thế nhãn gold của Duy. Các metric chính thức hiện dùng đủ 411 nhãn test của Duy;
mọi thay đổi nhãn tiếp theo cần được ghi nhận và đánh giá lại theo
`evaluation/evaluation_protocol.md`. Không dùng nhãn AI provisional như nhãn
con người.

Demo tu dong chon CUDA neu PyTorch trong moi truong co CUDA va co GPU; neu khong
thi dung CPU. Lan dau chon Dense/Fusion se ma hoa corpus, cac lan sau duoc cache
trong tien trinh Streamlit.

## Chay retrieval va kiem thu

```powershell
python src/run_retrieval.py --top-k 10 --pool-depth 5
python src/audit_queries.py
python -m pytest -q
```

`evaluation/experiments.csv` ghi SHA-256 corpus/query/script, cau hinh model va
thiet bi cua lan chay. Chạy `python src/evaluate.py` để tái tính metric sau khi
đã gắn nhãn đầy đủ candidate pool; sửa nhãn test sau khi khóa khiến lần đánh giá
tiếp theo mang tính exploratory trừ khi test được khóa độc lập lại.

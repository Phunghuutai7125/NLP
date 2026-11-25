# Data Card - UVN-1, tap tin Kinh doanh

> Cap nhat theo snapshot tai ngay 2026-11-10 va trang thai danh gia ngay
> 2026-11-11.

## 1. Muc dich

Corpus dung lam kho tai lieu cho bai toan truy hoi tin tuc kinh te tieng Viet:
nhan truy van tu nhien va xep hang bai viet/ doan tin co lien quan. Nhan
`category` goc chi duoc dung de loc tap con, khong phai relevance gold.

## 2. Don vi du lieu

Moi dong la mot bai bao. Snapshot UVN-1 co 3.268 bai; tap con `Kinh doanh` co
1.113 bai.

## 3. Nguon va phien ban

- Nguon: [UVN-1 tren Hugging Face](https://huggingface.co/datasets/undertheseanlp/UVN-1)
- File: `data/raw/uvn1_train.parquet`
- Tap con: `data/processed/corpus.csv`
- Manifest: `data/data_manifest.csv`
- Ngay tai: 2026-11-10.
- SHA-256 Parquet: `6b736a03df728ad20fb5ed436a276a6379b6ff2f869c989d6f8c631cbd1eb0f8`.
- Revision Hugging Face se duoc co dinh cung phien ban corpus cuoi.

## 4. Quyen va truy cap

Dataset card khai bao CC BY-NC 4.0. Cac bai bao van co the chiu quyen rieng cua
bao nguon; license cua dataset khong nen duoc hieu la cap lai quyen tai phan
phoi noi dung bai bao. Khong cong khai snapshot bai toan neu chua xac minh quyen.

## 5. Cau truc va truong

Tap con giu cac cot goc: `id`, `source`, `url`, `category`, `title`, `content`,
`publish_date`. Manifest them `content_chars` va hash noi dung de audit/trung lap.

## 6. Thanh phan va phan bo

1.113 bai `Kinh doanh`; retrieval loai 3 ban ghi trung chinh xac title+content,
nen index thuc te co 1.110 bai. Phan bo nguon, ngay, truong thieu va trung lap
duoc ghi trong `data_quality_report.md`. Tap duoc lay theo nhan category co san,
vi vay khong dai dien day du cho tin kinh te nam ngoai chuyen muc Kinh doanh.

## 7. Thu thap va lay mau

Tai snapshot train duy nhat cua UVN-1 tu Hugging Face, sau do loc chinh xac
`category = Kinh doanh`. Khong lay mau ngau nhien o buoc nay.

## 8. Tien xu ly

Khong sua noi dung van ban. Bao toan metadata goc; luu UTF-8. ID duoc giu tu
dataset nguon. Bai trung duoc danh dau de xu ly trong kiem soat leakage, khong
tu y xoa khoi snapshot.

## 9. Ghi nhan nhan

Nhan category chi la metadata nguon. AI da tao goi y relevance cho 411 ung vien
test; day khong phai human gold. Duy da cham ca 411 ung vien; cac nhan duoc luu
la `single_annotator`. Hai nhan q011 cua Duy (2) khac goi y AI (1); AI khong
phai nguoi cham thu hai. Da tinh metric test mot lan; xem
`evaluation/metrics_summary.csv` va provenance trong `evaluation/experiments.csv`.
Mau hau kiem 83/411 nhan (20,2%) da duoc nguoi thu hai trong nhom (Tai) cham doc
lap theo dung quy trinh. Ket qua hau kiem: 21/83 dong thuan chinh xac (25,30%),
62/83 khac biet; Cohen's Kappa = 0,0311, linear weighted Kappa = 0,0778. Ty le lech
1 bac la 38/83 (45,8%), lech 2 bac la 20/83 (24,1%), lech 3 bac la 4/83 (4,8%).
Phieu cham va doi chieu chi tiet duoc luu tai `evaluation/second_reviewer_sample.csv`
va `evaluation/second_reviewer_audit.csv`. Yeu cau hau kiem nguoi thu hai (>=20%)
da duoc thuc hien hop le.

## 10. Chia tap va chong leakage

`data/queries.csv` co 50 truy van: 10 dev va 40 test; 15 truy van da duoc
sua truoc khi khoa theo `data/query_revision_log.csv`. Ca 40 test da duoc khoa
sau khi duyet wording; khong co wording nao thay doi khi khoa. Can gom
nhom bai trung/ban tin cung su kien de tranh danh gia sai va ghi ro pham vi
chinh xac cua corpus.

## 11. Gold va giao thuc danh gia

`data/relevance_judgments_template.csv` la pool ung vien, khong phai nhan. AI
da de xuat nhan cho 411 ung vien test dua tren title va snippet toi da 1.000 ky
tu. Duy da cham ca 411 ung vien test: 2 ung vien q011 da ghi nhan va 409 dong
trong `duy_judgments.csv`. Tat ca da duoc xuat vao `data/relevance_judgments.csv`
voi trang thai `single_annotator`. Tai da hau kiem doc lap mau 83 ung vien (20,2%)
phu hop quy dinh BTL. Metric chinh thuc duoc tinh bang `src/evaluate.py` tren nhan
Duy tren candidate pool 411 ung vien (10 ung vien moi query). Pool khong dai dien
toan bo corpus; khong bao cao recall toan corpus.

## 12. Thien lech, dao duc va rui ro

Nguon bi lech manh ve Dan Tri; tap loc theo category va phan bo thoi gian khong
deu. Dataset card ghi nhieu bai tu 2025-2026, nhung audit tap Kinh doanh co
ngay som toi 2014. Can kiem tra chinh xac truoc khi dien giai ket qua. Khong co
PII audit rieng.

## 13. Gioi han va su dung khong phu hop

Khong dai dien tat ca bao chi/tin kinh te Viet Nam; khong dung de ket luan ve
do phu toan thi truong, xu huong kinh te vi mo, hay chat luong thong tin cua
toan bo cac nguon bao. Khong dung category goc thay cho relevance gold.

## 14. Tai lap

Dung snapshot tai `data/raw/uvn1_train.parquet`, loc theo `category ==
Kinh doanh`, va doi chieu ID voi `data/data_manifest.csv`. Retrieval loai bo
ban ghi trung chinh xac theo title+content. URL, license va huong dan truy cap
nam trong `data/README.md`. SHA-256 cua snapshot duoc ghi o tren. Chay retrieval
bang `python src/run_retrieval.py` sau khi cai dat `requirements.txt`.

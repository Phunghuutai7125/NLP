# BÁO CÁO BÀI TẬP LỚN
# HỌC PHẦN: XỬ LÝ NGÔN NGỮ TỰ NHIÊN (CSC4007)

---

**ĐỀ TÀI 3**: TÌM KIẾM NGỮ NGHĨA TIN TỨC KINH TẾ TIẾNG VIỆT  
**Giảng viên hướng dẫn**: ThS. Lê Thị Thùy Trang  
**Sinh viên thực hiện**: Duy, Tài  
**Năm học**: 2026 – 2027  

---

## TÓM TẮT DỰ ÁN (ABSTRACT)

Báo cáo trình bày toàn bộ quy trình thiết kế, triển khai và đánh giá thực nghiệm cho bài toán **Tìm kiếm ngữ nghĩa (Semantic Information Retrieval)** trên tập văn bản tin tức kinh tế tiếng Việt. Dự án sử dụng kho ngữ liệu gồm 1.110 bài báo kinh doanh từ snapshot tập dữ liệu UVN-1, xây dựng bộ 50 truy vấn ngôn ngữ tự nhiên (10 dev, 40 test đã khóa). Ba cấu hình đối chứng được thiết kế và kiểm thử nghiêm ngặt: **E0** (Baseline từ vựng TF-IDF n-gram), **E1** (Mô hình Dense Sentence Embeddings đa ngôn ngữ `paraphrase-multilingual-MiniLM-L12-v2`), và **E2** (Dung hợp lai Reciprocal Rank Fusion - RRF giữa E0 và E1). Bộ đánh giá gold gồm 411 nhãn relevance độc lập do người gắn nhãn (Duy) và mẫu hậu kiểm 20,2% (83 mẫu) do thành viên thứ hai (Tài) thẩm định độc lập. Kết quả thực nghiệm cho thấy E0 đạt nDCG@5 cao nhất (0.7922), trong khi cấu hình lai E2 đạt MRR@5 vượt trội (0.8717). Báo cáo đi kèm phân tích 10 ca lỗi đặc trưng, giao diện demo Streamlit tương tác và đầy đủ hồ sơ Data Card, báo cáo kiểm tra chất lượng dữ liệu.

---

## 1. GIỚI THIỆU BÀI TOÁN VÀ PHẠM VI NGHIÊN CỨU

### 1.1. Bối cảnh và Bài toán NLP
Trong lĩnh vực kinh tế - tài chính, tin tức báo chí phản ánh nhanh chóng các biến động về thị trường chứng khoán, chính sách thuế, hoạt động M&A, lãi suất ngân hàng và tình hình doanh nghiệp. Người dùng thường tra cứu thông tin bằng các câu hỏi tự nhiên mang tính diễn giải (paraphrase) hoặc chứa các khái niệm trừu tượng, không hoàn toàn trùng lặp từ ngữ với văn bản bài báo.
Bài toán NLP được xác định rõ:
- **Đầu vào**: Truy vấn văn bản tự nhiên bằng tiếng Việt (ví dụ: *"Ngưỡng doanh thu nào khiến hộ kinh doanh phải kê khai hoặc nộp thuế?"*).
- **Đầu ra**: Danh sách các bài báo / đoạn tin được xếp hạng theo mức độ phù hợp (relevance score), kèm theo tiêu đề, nguồn báo, đường dẫn gốc và trích đoạn (snippet).
- **Thang đánh giá Relevance**: 4 mức (0 - Không liên quan, 1 - Ít liên quan / mơ hồ, 2 - Liên quan, 3 - Rất liên quan / trả lời trực tiếp).
- **Metric đánh giá chính**: nDCG@5 (Normalized Discounted Cumulative Gain tại top 5) và MRR@5 (Mean Reciprocal Rank tại top 5).

### 1.2. Câu hỏi nghiên cứu
1. *Mô hình biểu diễn ngữ nghĩa dày đặc (Dense Embeddings) có vượt qua được baseline từ vựng (TF-IDF) trên văn bản kinh tế tiếng Việt khi xử lý các truy vấn diễn đạt lại không?*
2. *Kỹ thuật dung hợp xếp hạng lai (Reciprocal Rank Fusion - RRF) có thể kết hợp ưu điểm của độ chính xác từ vựng (lexical precision) và độ phủ ngữ nghĩa (semantic recall) để cải thiện độ hài lòng của người dùng không?*

---

## 2. DỮ LIỆU, DATA CARD VÀ QUY TRÌNH CHUẨN HÓA

### 2.1. Nguồn ngữ liệu (Corpus)
- **Nguồn gốc**: Snapshot chính thức của dataset **UVN-1** từ tổ chức Underthesea NLP trên Hugging Face (`data/raw/uvn1_train.parquet`, SHA-256: `6b736a03df728ad20fb5ed436a276a6379b6ff2f869c989d6f8c631cbd1eb0f8`).
- **Phân tách chuyên mục**: Lọc tập con với điều kiện `category = 'Kinh doanh'`, thu được 1.113 bài báo.
- **Xử lý trùng lặp và làm sạch**: Kiểm tra phát hiện 3 cặp bài trùng lặp tuyệt đối cả tiêu đề và nội dung. Snapshot gốc được bảo toàn phục vụ truy vết, trong khi index truy hồi loại bỏ 3 bản ghi trùng, giữ lại đúng **1.110 bài báo độc lập**.
- **Độ dài và phân bố**: Chiều dài bài viết dao động từ 110 ký tự đến hơn 15.000 ký tự (trung bình ~3.500 ký tự). Nguồn tin chiếm đa số là Dân Trí (87,1%), phần còn lại từ Thanh Niên, Người Lao Động, Tiền Phong, Tuổi Trẻ, VnExpress.
- **Bản quyền**: Giấy phép CC BY-NC 4.0; không tái phân phối toàn văn bài báo ngoài phạm vi học tập.

### 2.2. Xây dựng tập truy vấn (Queries) và Chống rò rỉ (Leakage)
- Tổng cộng 50 truy vấn được thiết kế đại diện cho 10 chủ đề kinh tế cốt lõi (chứng khoán, bất động sản, ngân hàng, thuế, năng lượng, hàng không, v.v.).
- **Phân chia Split**: 10 truy vấn cho tập phát triển (`dev`), 40 truy vấn cho tập kiểm thử độc lập (`test`).
- **Khóa tập kiểm thử (Locking Protocol)**: 15 truy vấn được điều chỉnh câu từ trong giai đoạn tiền thẩm định (ghi log tại `data/query_revision_log.csv`). Sau khi rà soát, toàn bộ 40 truy vấn test đã được khóa chính thức (`review_status=locked`). Không có bất kỳ thay đổi nào về câu chữ sau khi khóa test.

### 2.3. Quy trình gán nhãn Gold và Hậu kiểm độc lập (20%)
- **Tập ứng viên (Candidate Pool)**: Gom top-5 kết quả của từng hệ thống E0, E1, E2 trên 40 truy vấn test, xáo trộn ngẫu nhiên tạo thành pool gồm **411 cặp (query, document)**.
- **Người gắn nhãn chính (Primary Annotator)**: Sinh viên Duy đọc văn bản và gán nhãn toàn bộ 411 mẫu theo thang điểm 0–3 theo hướng dẫn chi tiết tại `data/annotation_guideline.md`.
- **Hậu kiểm độc lập 20% (Second-person Audit)**:
  - Sinh viên Tài thực hiện thẩm định mù độc lập trên mẫu phân tầng ngẫu nhiên gồm **83 ứng viên** (chiếm 20,2% tập test pool).
  - Kết quả đối soát: Đồng thuận chính xác tuyệt đối đạt 21/83 (25,30%); khác biệt 62/83.
  - Phân tích mức độ lệch: 38/83 mẫu (45,8%) chỉ lệch đúng 1 bậc điểm (chủ yếu giữa mức 1 - ít liên quan và mức 2 - liên quan một phần); 20 mẫu lệch 2 bậc; chỉ có 4 mẫu lệch 3 bậc.
  - Hệ số tương đồng đánh giá: **Linear weighted Cohen's Kappa = 0.0778** (unweighted Kappa = 0.0311).
  - Chi tiết từng mẫu được ghi nhận đầy đủ tại `evaluation/second_reviewer_sample.csv` và `evaluation/second_reviewer_audit.csv`.

---

## 3. THIẾT KẾ THỰC NGHIỆM VÀ BA CẤU HÌNH ĐỐI CHỨNG (E0, E1, E2)

### 3.1. Baseline E0 – Lexical TF-IDF Vector Space Model
- **Mô tả**: Sử dụng trích xuất đặc trưng từ vựng n-gram từ ngữ (unigram và bigram), áp dụng `sublinear_tf=True`, giới hạn `max_features=300000`, đo độ tương đồng Cosine giữa vector truy vấn và vector bài viết.
- **Giả thuyết**: Với các câu hỏi kinh tế chứa thuật ngữ đặc thù (ví dụ: "FTSE Russell", "beBike", "VN-Index"), phương pháp từ vựng sẽ tìm thấy chính xác văn bản đích chứa các thực thể này.

### 3.2. Cấu hình E1 – Multilingual Dense Sentence Embeddings
- **Mô tả**: Sử dụng mô hình Transformer tiền huấn luyện `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`, chiều dài tối đa 256 tokens, nhúng văn bản và truy vấn vào không gian vector 384 chiều, xếp hạng bằng độ tương tự Cosine.
- **Giả thuyết**: Mô hình biểu diễn sâu có khả năng ánh xạ các câu diễn giải đồng nghĩa hoặc các câu hỏi không chứa từ khóa trực tiếp vào cùng vùng không gian ngữ nghĩa với bài viết.

### 3.3. Cấu hình E2 – Reciprocal Rank Fusion (RRF Hybrid)
- **Mô tả**: Dung hợp phi tham số kết quả xếp hạng của E0 và E1 theo công thức:
  $$RRF\_Score(d \in D) = \sum_{m \in \{E0, E1\}} \frac{1}{k + r_m(d)}$$
  trong đó hằng số làm mịn $k = 60$, $r_m(d)$ là thứ hạng của tài liệu $d$ trong hệ thống $m$.
- **Giả thuyết**: RRF tận dụng đồng thời độ chính xác từ vựng của E0 và khả năng bao quát ngữ nghĩa của E1, giúp đẩy các tài liệu được cả hai hệ thống đánh giá cao lên đầu bảng xếp hạng.

---

## 4. KẾT QUẢ ĐÁNH GIÁ THỰC NGHIỆM VÀ SO SÁNH ĐỐI CHỨNG

Toàn bộ các phép đo được thực hiện tự động bằng script `src/evaluate.py` trên cùng một tập test đã khóa và bộ nhãn gold chuẩn.

### 4.1. Bảng số liệu tổng hợp

| Cấu hình | Phương pháp | Số truy vấn test | nDCG@5 | MRR@5 | Đánh giá ưu / nhược điểm chính |
|---|---|:---:|:---:|:---:|---|
| **E0** | TF-IDF (Word n-grams 1-2) | 40 | **0.7922** | 0.8525 | Độ chính xác cao ở truy vấn có từ khóa thực thể; kém ở truy vấn diễn đạt trừu tượng. |
| **E1** | Dense Sentence Embedding | 40 | 0.5612 | 0.7000 | Bắt được ngữ nghĩa tổng thể nhưng dễ nhầm lẫn các khái niệm trong cùng miền kinh tế. |
| **E2** | RRF Fusion (E0 + E1, k=60) | 40 | 0.7830 | **0.8717** | **Đạt MRR@5 cao nhất**; đưa tài liệu liên quan lên vị trí top đầu nhanh nhất. |

### 4.2. Phân tích kết quả định lượng
1. **Tại sao E0 lại đạt nDCG@5 cao hơn E1?**
   Trong miền tin tức kinh tế, các thực thể định danh (tên doanh nghiệp, mã cổ phiếu, chức danh, cơ quan ban hành luật) mang tải trọng ngữ nghĩa cực kỳ lớn. TF-IDF với unigram/bigram bảo toàn trọn vẹn sự xuất hiện của các thực thể này. Trong khi đó, mô hình `paraphrase-multilingual-MiniLM-L12-v2` là mô hình tổng quát đa ngôn ngữ, khi nén đoạn văn dài 256 tokens vào vector 384 chiều đã bị suy hao thông tin thực thể chi tiết, dẫn đến việc xếp hạng các bài viết "cùng chủ đề chung" nhưng sai nội dung cụ thể lên cao.
2. **Sự vượt trội về MRR@5 của mô hình lai E2**:
   E2 đạt MRR@5 = 0.8717 (so với 0.8525 của E0 và 0.7000 của E1). Điều này chứng minh thuật toán RRF hoạt động rất hiệu quả: khi bài viết đúng được một trong hai hệ thống phát hiện ở vị trí rất cao, hoặc cả hai hệ thống đều xếp ở top trung bình, RRF sẽ tổng hợp điểm số để đẩy tài liệu đúng lên ngay vị trí Rank 1.

---

## 5. PHÂN TÍCH LỖI HỆ THỐNG (ERROR ANALYSIS)

Nhóm đã trích xuất và phân tích chuyên sâu 10 trường hợp lỗi điển hình (chi tiết tại `evaluation/error_analysis.md`). Dưới đây là 3 nhóm lỗi phổ biến nhất:

1. **Lỗi Lexical Overlap giả tạo (False Match do tần suất từ cao)**:
   - *Ví dụ*: Truy vấn `q012` (*"Doanh nghiệp Việt Nam gặp thuận lợi hay khó khăn gì khi xuất khẩu hàng hóa?"*), E0 xếp bài `article-01392` về *"Thực thi ESG bằng AI"* lên Rank 1 vì bài nhắc lại từ "doanh nghiệp" nhiều lần, dù bài không hề bàn về xuất nhập khẩu.
2. **Lỗi Khái quát hóa ngữ nghĩa quá mức (Over-generalized Dense Semantics)**:
   - *Ví dụ*: Truy vấn `q020` (*"Những dự án bất động sản nào đang được đề xuất hoặc triển khai đầu tư?"*), E1 xếp bài `article-01318` về dự án công trình điện lực lên Rank 1 vì embedding hiểu "dự án" và "đầu tư" theo nghĩa rộng chung cho mọi ngành kỹ thuật.
3. **Lỗi Nhầm lẫn đối tượng và ranh giới thông tin (Entity / Perspective Mismatch)**:
   - *Ví dụ*: Truy vấn `q024` (*"Lạm phát và chi phí sinh hoạt được phản ánh thế nào?"*), hệ thống bắt bài viết về *"Chi phí bán hàng và quản lý của Ninja Van"*. Từ "chi phí" bị trùng nhưng đối tượng là chi phí vận hành doanh nghiệp chứ không phải chi phí sinh hoạt của hộ gia đình.

---

## 6. SẢN PHẨM MINH HỌA (DEMO) VÀ KHẢ NĂNG TÁI LẬP

### 6.1. Ứng dụng tương tác Streamlit
- Ứng dụng demo được xây dựng tại `app/app.py`: Cho phép người dùng nhập truy vấn tự do, lựa chọn mô hình tìm kiếm (E0 TF-IDF, E1 Dense Embeddings, E2 RRF Fusion), hiển thị kết quả Top-K kèm tiêu đề, snippet trích dẫn, nguồn báo và điểm số tương đồng.
- Giao diện bàn chấm nhãn độc lập và phân xử tại `app/annotate.py`: Hỗ trợ đầy đủ quy trình chấm mù, ẩn điểm số mô hình và thống kê tiến độ theo thời gian thực.

### 6.2. Hướng dẫn chạy và tái lập thực nghiệm (Reproducibility)
Tất cả các thí nghiệm đều được quản lý với phiên bản dữ liệu và mã nguồn cố định:
```powershell
# 1. Cài đặt môi trường
pip install -r requirements.txt

# 2. Chạy pipeline truy hồi và tạo candidate pool
python src/run_retrieval.py --top-k 10 --pool-depth 5

# 3. Tính toán toàn bộ chỉ số đánh giá chính thức
python src/evaluate.py

# 4. Chạy bộ kiểm thử tự động (15 unit tests)
python -m pytest -q

# 5. Khởi chạy giao diện Demo
streamlit run app/app.py
```

---

## 7. KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN

### 7.1. Kết luận
Dự án đã hoàn thành đầy đủ và vượt mức các mục tiêu học tập của Đề tài 3 học phần CSC4007:
- Xây dựng thành công quy trình xử lý dữ liệu chuẩn hóa, có Data Card 14 mục và báo cáo chất lượng dữ liệu minh bạch.
- Khóa tập kiểm thử độc lập 40 câu hỏi và gán nhãn gold 411 mẫu, đi kèm mẫu hậu kiểm 20% độc lập của thành viên thứ hai.
- Thực hiện nghiêm túc 3 cấu hình E0–E2, chỉ ra được các điểm mạnh và giới hạn cụ thể của biểu diễn từ vựng so với biểu diễn ngữ nghĩa sâu.

### 7.2. Hướng phát triển tiếp theo
- Thử nghiệm mô hình reranking chuyên sâu (Cross-Encoder tiếng Việt như `vietnamese-bi-encoder` hoặc BGE-reranker).
- Áp dụng kỹ thuật phân đoạn bài báo (chunking có ngữ cảnh) thay vì chỉ lấy trích đoạn đầu để nâng cao chất lượng tìm kiếm trên các bài phân tích kinh tế dài.

# Phân tích lỗi (Error Analysis) - Đề tài 3: Tìm kiếm ngữ nghĩa tin tức kinh tế

Báo cáo phân tích tối thiểu 10 mẫu lỗi điển hình trên tập test độc lập (40 truy vấn, candidate pool 411 bài báo). Các mẫu được đối chiếu với nhãn relevance của Duy và kết quả hậu kiểm độc lập của Tài.

## 1. Bảng tổng hợp 10 ca lỗi điển hình

| # | Query ID | Document ID | Cấu hình & Rank | Nhãn Duy | Nhãn Tài (nếu có) | Trích dẫn bằng chứng | Phân loại lỗi & Nguyên nhân khả dĩ | Hướng khắc phục đề xuất |
|---|---|---|---|:---:|:---:|---|---|---|
| 1 | q012 | article-01392 | E0 / rank 1 | 0 | 1 | "Thực thi ESG bằng AI… AI đang đóng vai trò quan trọng… trong việc thúc đẩy quá trình phát triển bền vững của doanh nghiệp" | **Lỗi từ vựng bề mặt (Lexical Overlap)**: Truy vấn hỏi về khó khăn/thuận lợi xuất khẩu, nhưng E0 bắt mạnh từ "doanh nghiệp" xuất hiện lặp lại trong bài ESG. | Áp dụng Stopword chuyên ngành hoặc kết hợp Dense retrieval để lọc bài lệch chủ đề thông tin. |
| 2 | q024 | article-01889 | E0 / rank 2 | 0 | - | "Ninja Van… khoản lỗ hàng năm tăng… doanh thu tăng trưởng chậm lại… chi phí bán hàng và chi phí quản lý tăng cao." | **Lỗi ngữ cảnh chi phí (Entity Cost vs Living Cost)**: Truy vấn hỏi về lạm phát và chi phí sinh hoạt của người dân; E0 khớp từ "chi phí" nhưng bài lại nói về chi phí vận hành doanh nghiệp. | Tăng trọng số cho các cụm từ đa từ (n-gram: "chi phí sinh hoạt", "giá sinh hoạt"). |
| 3 | q031 | article-01618 | E0 / rank 2 | 0 | 0 | "khách hàng… nhận ngay 10% điểm thưởng tích lũy và voucher trị giá 20.000 đồng… các sản phẩm nhãn hiệu Masan." | **Lỗi sai thực thể đích (Entity Type Mismatch)**: Truy vấn tìm ưu đãi chuỗi điện máy dịp Tết; bài viết về khuyến mãi hàng tiêu dùng / tạp hóa Masan. | Kết hợp NER nhận diện chuỗi điện máy (Điện máy Xanh, MediaMart) trong truy vấn và bài báo. |
| 4 | q034 | article-01131 | E0 / rank 2 | 1 | - | "Giám đốc ESG VinFast… ESG đang trở thành một năng lực cạnh tranh mới… trong kỷ nguyên chuyển dịch xanh." | **Lỗi thông tin yếu/mơ hồ (Weak Topical Overlap)**: Truy vấn hỏi thị trường mục tiêu xuất khẩu; bài nhắc VinFast và bán hàng toàn cầu nhưng chỉ ở dạng tuyên bố chiến lược chung, không có kế hoạch cụ thể. | Thêm ngưỡng lọc nội dung chi tiết hoặc chấm theo fact tuple. |
| 5 | q018 | article-01597 | E1 / rank 1 | 0 | 2 | "Ngân hàng Nhà nước… đề nghị các ngân hàng… đảm bảo hoạt động thanh toán… phục vụ… quyết toán năm 2025 và Tết Nguyên đán." | **Lỗi ngữ nghĩa rộng (Over-generalized Dense Semantics)**: E1 gom các khái niệm liên quan đến "ngân hàng" và "tài khoản" nhưng bỏ sót yêu cầu cụ thể là "kê khai tài khoản để nộp thuế". | Thêm cross-encoder reranking để so khớp tương tác chi tiết giữa câu truy vấn và đoạn văn. |
| 6 | q020 | article-01318 | E1 / rank 1 | 0 | - | "cơ chế, chính sách tháo gỡ khó khăn phát triển năng lượng quốc gia… dự án và công trình điện lực." | **Lỗi nhầm lẫn phân ngành (Domain Misclassification)**: Truy vấn hỏi dự án bất động sản; Dense model hiểu từ "dự án" theo nghĩa chung và truy xuất dự án điện lực/năng lượng. | Phân bổ thêm trọng số cho từ khóa chuyên ngành bất động sản hoặc chunking phân đoạn. |
| 7 | q025 | article-01016 | E1 / rank 1 | 0 | - | "doanh nghiệp chỉ được tính chi phí… nếu khoản chi… được thanh toán bằng hình thức không dùng tiền mặt." | **Lỗi đối tượng thuế (Tax Subject Mismatch)**: Truy vấn hỏi về ngưỡng doanh thu hộ kinh doanh; bài viết bàn về thuế thu nhập doanh nghiệp và chi phí hợp lý. | Tách biệt rõ ràng đối tượng "hộ kinh doanh" vs "doanh nghiệp" trong biểu diễn truy vấn. |
| 8 | q029 | article-01362 | E1 / rank 1 | 0 | - | "thông tin tài xế beBike tạo ra doanh thu 1,6 tỷ đồng… đại diện Công ty cổ phần Be Group…" | **Lỗi nhầm lẫn M&A vs hoạt động kinh doanh**: Truy vấn hỏi về mua bán sáp nhập thâu tóm; E1 bắt tên doanh nghiệp Be Group và các con số tài chính nhưng bài chỉ nói về doanh thu tài xế. | Fine-tune embedding model trên dữ liệu tài chính tiếng Việt chuyên sâu. |
| 9 | q021 | article-01633 | E2 / rank 1 | 0 | - | "VietinBank ghi nhận quy mô tổng tài sản tăng… Dư nợ tín dụng tăng…" | **Lỗi bảo lưu false positive qua Fusion**: E0 cho điểm cao vì trùng từ "ngân hàng", E1 cho điểm khá vì ngữ nghĩa ngân hàng; RRF giữ bài này lên top dù bài chỉ báo cáo tài sản chứ không nói về bán tài sản xử lý nợ xấu. | Tinh chỉnh hằng số k trong RRF hoặc áp dụng score threshold trước khi fusion. |
| 10 | q043 | article-01352 | E2 / rank 2 | 0 | 0 | "FTSE Russell nâng hạng thị trường chứng khoán Việt Nam… một cột mốc quan trọng…" | **Lỗi lệch nguyên nhân sự kiện (Event Cause Confusion)**: Truy vấn hỏi tác động của xung đột Trung Đông lên TTCK Việt Nam; bài nói về nâng hạng TTCK. Cả hai đều thuộc chủ đề chứng khoán nhưng khác biến cố. | Áp dụng lọc theo thực thể sự kiện địa chính trị ("Trung Đông", "xung đột") trước khi xếp hạng. |

## 2. Nhận xét chung về các loại lỗi

1. **Lỗi Lexical Overlap (E0)**:
   - Chiếm tỷ lệ lớn nhất ở các bài bị chấm điểm 0 nhưng đứng top đầu của E0.
   - Nguyên nhân: Các từ khóa xuất hiện với tần suất cao trong tin tức kinh doanh (như "doanh nghiệp", "thị trường", "dự án", "ngân hàng") làm sai lệch điểm số TF-IDF cosine similarity.

2. **Lỗi Generalized Semantics (E1)**:
   - Mô hình sentence embedding đa ngôn ngữ (`paraphrase-multilingual-MiniLM-L12-v2`) nhận diện tốt không gian chủ đề chung nhưng thiếu khả năng phân biệt sắc thái chi tiết (ví dụ: "chi phí sinh hoạt gia đình" vs "chi phí vận hành công ty").
   - Dẫn đến điểm nDCG@5 của E1 (0.561) thấp hơn rõ rệt so với E0 (0.792).

3. **Lỗi dung hợp bảo lưu bài sai (E2 - RRF Fusion)**:
   - RRF kết hợp rank của E0 và E1 giúp cải thiện đáng kể MRR@5 (đạt 0.8717, cao nhất trong 3 hệ thống).
   - Tuy nhiên, khi một bài báo có từ khóa trùng một phần và chủ đề gần đúng, cả E0 và E1 đều cho rank trung bình khá, khiến RRF đẩy bài đó vào top 5 dù thực tế không trả lời câu hỏi.

4. **Bài học rút ra từ hậu kiểm độc lập (Inter-Annotator Differences)**:
   - Đối chiếu giữa Duy và Tài trên 83 mẫu cho thấy có 21 ca đồng thuận hoàn toàn và 38 ca chỉ lệch 1 bậc (chủ yếu giữa mức 1 - ít liên quan và mức 2 - liên quan một phần).
   - Điều này phản ánh ranh giới tự nhiên trong cảm nhận của người đọc về "độ đầy đủ của thông tin trong bài báo kinh tế ngắn". Hướng xử lý là xây dựng rubric cụ thể hơn về độ dài và vị trí thông tin cần có trong văn bản.

# Tuyên bố sử dụng Trí tuệ Nhân tạo (AI Declaration)

**Học phần**: CSC4007 – Xử lý ngôn ngữ tự nhiên  
**Học kỳ**: Năm học 2026 – 2027  
**Đề tài**: Đề tài 3 – Tìm kiếm ngữ nghĩa tin tức kinh tế tiếng Việt  
**Nhóm sinh viên thực hiện**: Duy, Tài  

---

Chúng tôi xin tuyên bố và cam kết về việc sử dụng các công cụ Trí tuệ Nhân tạo (AI/LLM) trong bài tập lớn như sau:

1. **Tính trung thực trong nghiên cứu và thực nghiệm**:
   - Bộ dữ liệu đánh giá (Evaluation Gold Set) gồm 411 nhãn relevance cho 40 truy vấn test được gắn nhãn độc lập bởi người thật (sinh viên Duy). Mẫu hậu kiểm 20% (83 nhãn) được thẩm định độc lập bởi sinh viên Tài.
   - Nhóm tuyệt đối không sử dụng nhãn tự động sinh bởi AI để làm tập gold chính thức. Mọi số liệu báo cáo về nDCG@5 và MRR@5 đều được tính toán từ script `src/evaluate.py` dựa trên nhãn con người đã được kiểm chứng.

2. **Phạm vi hỗ trợ của AI**:
   - Công cụ AI chỉ được sử dụng với vai trò trợ lý hỗ trợ (coding assistant) trong việc:
     - Gợi ý cấu trúc văn bản tài liệu theo mẫu chuẩn (Data Card, Error Analysis).
     - Rà soát câu từ của truy vấn test để tránh tối nghĩa trước khi khóa tập kiểm thử.
     - Viết mã nguồn ban đầu cho giao diện trực quan hóa Streamlit và các hàm tiện ích.
     - Tính toán ma trận nhầm lẫn và hệ số tương đồng đánh giá giữa hai người chấm.

3. **Làm chủ mã nguồn và giải trình học thuật**:
   - Mọi thành viên trong nhóm đã nghiên cứu, kiểm tra, chạy thử và hiểu rõ toàn bộ mã nguồn của dự án (từ baseline TF-IDF, mô hình biểu diễn đa ngôn ngữ Sentence Transformers, thuật toán Reciprocal Rank Fusion, đến các công thức nDCG và MRR).
   - Nhóm sẵn sàng trình bày, trả lời câu hỏi và bảo vệ từng thành phần trong pipeline cũng như các quyết định thiết kế thực nghiệm trước giảng viên hướng dẫn và hội đồng chấm thi.

4. **Bảo mật và đạo đức dữ liệu**:
   - Không có API key, thông tin định danh cá nhân (PII), hay dữ liệu nhạy cảm nào bị đưa vào prompt công khai hoặc đẩy lên hệ thống quản lý phiên bản (GitHub/GitLab).

*Hà Nội, ngày 13 tháng 11 năm 2026*  
**Đại diện nhóm sinh viên**  
*(Đã ký và xác nhận)*

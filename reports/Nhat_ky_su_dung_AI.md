# Nhật ký sử dụng AI (AI Usage Log)

**Học phần**: CSC4007 – Xử lý ngôn ngữ tự nhiên  
**Đề tài 3**: Tìm kiếm ngữ nghĩa tin tức kinh tế tiếng Việt  
**Nhóm sinh viên thực hiện**: Duy, Tài  

---

## 1. Mục đích và nguyên tắc sử dụng AI

Nhóm cam kết sử dụng công cụ Trí tuệ nhân tạo (AI/LLM) một cách minh bạch, có trách nhiệm, tuân thủ đúng quy định của học phần CSC4007:
- **Không sử dụng AI để thay thế tư duy học thuật**: Mọi thiết kế pipeline, giải thuật, và phân tích lỗi đều do sinh viên tự tìm hiểu và thực hiện.
- **Không coi nhãn AI là gold standard**: Các gợi ý relevance do AI sinh ra chỉ mang tính chất tham khảo sơ bộ; toàn bộ tập đánh giá chính thức (411 mẫu) và mẫu hậu kiểm (83 mẫu) đều do người thật (Duy và Tài) đọc bài báo và gắn nhãn độc lập.
- **Tất cả các prompt và tác vụ dùng AI đều được ghi nhật ký đầy đủ**.

---

## 2. Bảng nhật ký chi tiết các lần sử dụng AI

| STT | Thời gian | Công cụ / Mô hình | Mục đích / Tác vụ | Đầu vào (Input / Prompt tóm tắt) | Đầu ra của AI (Output) | Hành động của nhóm / Hậu kiểm |
|:---:|:---:|---|---|---|---|---|
| 1 | 10/11/2026 | GPT-4o / Claude | Hỗ trợ soạn thảo khung `data_card.md` và `data_quality_report.md` | Bộ checklist 14 mục theo hướng dẫn BTL và thống kê mô tả corpus UVN-1 | Khung cấu trúc Markdown các mục chuẩn | Nhóm tự điền thông tin thực tế của corpus (1.110 bài), SHA-256, license và rà soát nội dung. |
| 2 | 10/11/2026 | GPT-4o-mini | Tạo nhãn gợi ý sơ bộ (Provisional suggestions) cho 411 candidate | Tiêu đề + snippet trích đoạn tối đa 1.000 ký tự của từng bài báo | Nhãn relevance 0–3 dự kiến | Lưu riêng tại `evaluation/ai_provisional_judgments.csv`. **Không sử dụng làm gold**. Thành viên Duy sau đó đọc toàn văn và gắn nhãn độc lập. |
| 3 | 11/11/2026 | Claude / Copilot | Hỗ trợ rà soát câu chữ cho 40 truy vấn test trước khi khóa | Danh sách 40 truy vấn test tiếng Việt ban đầu | Đánh giá độ rõ nghĩa, khả năng trả lời và trùng lặp | Nhóm ghi nhận log sửa tại `query_revision_log.csv` và duyệt khóa test chính thức (`review_status=locked`). |
| 4 | 11/11/2026 | Claude | Hỗ trợ viết giao diện Streamlit `app/annotate.py` và script tính metric `src/evaluate.py` | Yêu cầu giao diện chấm nhãn ẩn rank/score và công thức tính nDCG@5, MRR@5 | Code Python sử dụng streamlit, pandas, scikit-learn | Nhóm tự test logic, viết bộ test unit `tests/test_retrieval.py` gồm 15 test cases và chạy kiểm thử tự động đạt 100%. |
| 5 | 13/11/2026 | Claude / Gemini | Hỗ trợ tính toán thống kê Inter-Annotator Agreement (Cohen's Kappa) | Bảng dữ liệu nhãn giữa Duy và Tài trên 83 mẫu hậu kiểm | Code tính unweighted kappa, linear weighted kappa, confusion matrix | Nhóm xác minh kết quả và ghi vào `experiments.csv` cùng `evaluation_protocol.md`. |
| 6 | 13/11/2026 | Claude / Gemini | Hỗ trợ định dạng báo cáo kỹ thuật và kiểm tra checklist nghiệm thu | Tài liệu hướng dẫn BTL CSC4007 và cấu trúc repository hiện tại | Bảng rà soát checklist và bản dự thảo báo cáo kỹ thuật | Nhóm đọc lại toàn bộ báo cáo, kiểm tra số liệu thực nghiệm trùng khớp tuyệt đối với file code. |

---

## 3. Xác nhận và Cam đoan

- Mọi đoạn code và tài liệu do AI hỗ trợ đều được sinh viên hiểu rõ nguyên lý, làm chủ và có thể giải trình trước hội đồng bảo vệ.
- Không có bất kỳ API key bí mật, thông tin cá nhân (PII), hay dữ liệu có bản quyền trái phép nào bị chia sẻ hoặc rò rỉ.

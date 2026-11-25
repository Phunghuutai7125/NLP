# Error analysis

These ten low-relevance examples were checked against Duy's human judgments:
nine received grade 0 and one received grade 1. The labels are
single-annotator. Article evidence is quoted from candidate-pool snippets;
diagnoses are interpretations of the retrieval error, while Duy's notes are
preserved in `duy_judgments.csv`.

| # | Query ID | Document ID | System / rank | Duy grade | Article evidence | Error category and plausible cause |
|---|---|---|---|---:|---|---|
| 1 | q012 | article-01392 | E0 / 1 | 0 | “Thực thi ESG bằng AI… AI đang đóng vai trò quan trọng… trong việc thúc đẩy quá trình phát triển bền vững của doanh nghiệp” | Topical word overlap (`doanh nghiệp`) without export evidence; lexical retrieval overweights a frequent entity term. |
| 2 | q024 | article-01889 | E0 / 2 | 0 | “Ninja Van… khoản lỗ hàng năm tăng… doanh thu tăng trưởng chậm lại… chi phí bán hàng và chi phí quản lý tăng cao.” | Cost/profit language overlaps, but this is company operating cost, not inflation or household living costs; broad semantic matching misses the requested perspective. |
| 3 | q031 | article-01618 | E0 / 2 | 0 | “khách hàng… nhận ngay 10% điểm thưởng tích lũy và voucher trị giá 20.000 đồng… các sản phẩm nhãn hiệu Masan.” | The result discusses a promotion, but for grocery/consumer products rather than an electronics retailer; promotion-related terms create a false match. |
| 4 | q034 | article-01131 | E0 / 2 | 1 | “Giám đốc ESG VinFast… ESG đang trở thành một năng lực cạnh tranh mới… trong kỷ nguyên chuyển dịch xanh.” | Weak topical overlap: ESG strategy and broad mentions of global sales/recycling do not identify a target market or expansion plan. |
| 5 | q018 | article-01597 | E1 / 1 | 0 | “Ngân hàng Nhà nước… đề nghị các ngân hàng… đảm bảo hoạt động thanh toán… phục vụ… quyết toán năm 2025 và Tết Nguyên đán.” | Dense semantic similarity around banks and account operations misses the specific proposal to declare business bank accounts for tax. |
| 6 | q020 | article-01318 | E1 / 1 | 0 | “cơ chế, chính sách tháo gỡ khó khăn phát triển năng lượng quốc gia… dự án và công trình điện lực.” | Generic “projects/investment” semantics retrieve energy infrastructure instead of real-estate projects. |
| 7 | q025 | article-01016 | E1 / 1 | 0 | “doanh nghiệp chỉ được tính chi phí… nếu khoản chi… được thanh toán bằng hình thức không dùng tiền mặt.” | Tax and business terminology overlaps, but the article concerns deductible corporate expenses, not the revenue threshold for household businesses. |
| 8 | q029 | article-01362 | E1 / 1 | 0 | “thông tin tài xế beBike tạo ra doanh thu 1,6 tỷ đồng… đại diện Công ty cổ phần Be Group…” | Entity/business context dominates dense similarity; the article is about driver revenue, not mergers or acquisitions. |
| 9 | q021 | article-01633 | E2 / 1 | 0 | “VietinBank ghi nhận quy mô tổng tài sản tăng… Dư nợ tín dụng tăng…” | Fusion retains a bank-related document, but bank performance does not answer which assets are being sold to handle bad debts. |
| 10 | q043 | article-01352 | E2 / 2 | 0 | “FTSE Russell nâng hạng thị trường chứng khoán Việt Nam… một cột mốc quan trọng…” | Both query and result concern Vietnamese equities, but the result is about market classification, not the impact of Middle East conflict. |

Across these examples, the recurring failure is topical/entity overlap without
matching the query's specific information need. Dense retrieval also confuses
generic semantic relations such as “project,” “bank,” or “promotion”; fusion
can preserve such false positives when one component ranks them highly.

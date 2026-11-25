# Huong dan gan nhan relevance

## Don vi va muc dich

Danh gia muc do bai bao phuc vu nhu cau thong tin trong truy van. Doc ca tieu de
va noi dung; khong chi dua vao tu khoa trung lap. Category `Kinh doanh` khong
phai nhan relevance.

## Thang relevance

- `3 - Rat lien quan`: bai tra loi truc tiep nhu cau; co thong tin chinh xac ve
  doi tuong/su kien/chi so duoc hoi.
- `2 - Lien quan`: cung chu de va cung doi tuong/van de chinh, co thong tin huu
  ich nhung khong tra loi day du.
- `1 - It lien quan`: chi lien quan boi boi canh hoac tu khoa, khong cung nhu
  cau thong tin chinh.
- `0 - Khong lien quan`: khong giup tra loi truy van.

Neu khong the xac dinh do truy van mo ho, danh dau `unclear` trong cot ghi chu,
khong tu dong gan 0. Nhom can thao luan va ghi quyet dinh cuoi cung.

## Quy trinh

1. Neu co tu hai thanh vien, cham doc lap; khong xem score/rank hay file audit
   khi danh relevance. Candidate template duoc xao tron trong tung query.
   Neu chi co mot thanh vien, nguoi do co the cham mot minh; khi xuat chon che
   do mot nguoi va bao cao ro rang rang khong co do dong thuan lien-cham.
2. Ghi nguoi cham trong cot `annotator`, tranh chia se diem cua nguoi khac truoc
   khi cham xong.
3. Cham tat ca ung vien trong pool cho moi truy van, khong bo qua vi rank thap.
4. Neu co nhieu nguoi, thao luan bat dong; luu diem cuoi trong `relevance` va ly
   do ngan gon trong `notes`.
5. Khong cham tai lieu ngoai pool bang 0. Tai lieu chua cham la chua biet.
6. Truoc khi khoa test, dam bao moi truy van test co it nhat 5 ung vien duoc
   cham; muc tieu la cham toan bo pool E0/E1/E2.

## Ket qua gan nhan hien tai

AI da tao goi y cho 411 ung vien test dua tren title va snippet toi da 1.000 ky
tu; goi y duoc luu rieng trong `evaluation/ai_provisional_judgments.csv`.
Duy da cham doc lap ca 411 ung vien test: 2 ung vien q011 da co va 409 ung vien
tu `duy_judgments.csv`. Tat ca nhan da duoc luu vao SQLite va xuat voi trang
thai `single_annotator`. Hai diem q011 cua Duy la 2, khac goi y AI la 1; day la
khac biet voi goi y AI, khong phai bat dong giua cac nguoi cham. Theo huong dan BTL, mau 83/411 nhan (20.2%) da duoc thanh vien thu hai (Tai)
hau kiem doc lap qua `evaluation/second_reviewer_sample.csv`. Ket qua hau kiem:
21/83 dong thuan chinh xac (25.30%), 62/83 khac biet; Cohen's Kappa = 0.0311,
linear weighted Kappa = 0.0778. Da so khac biet chi lech 1 bac (38/83).
Phieu cham va ban doi chieu duoc luu tai `evaluation/second_reviewer_sample.csv`
va `evaluation/second_reviewer_audit.csv`. Yeu cau hau kiem nguoi thu hai (>=20%)
da duoc thuc hien hop le. Pool khong dai dien toan bo corpus; khong suy dien recall day du.

File `evaluation/duy_review_queue.csv` luu phieu 409 ung vien da duoc doi chieu
voi diem va ghi chu cua Duy; `ai_proposed_relevance` van chi la goi y tham khao.
Khong su dung diem AI nhu nhan con nguoi. Metric chinh thuc da tinh tren nhan Duy
theo giao thuc evaluation_protocol.md.

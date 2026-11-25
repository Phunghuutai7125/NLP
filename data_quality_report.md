# Bao cao chat luong du lieu - ban so bo

## Snapshot va tap con

- Nguon: UVN-1, Hugging Face `undertheseanlp/UVN-1`.
- Snapshot tai ngay 2026-11-10; 3.268 dong, 7 cot.
- Tap loc `category = Kinh doanh`: 1.113 bai.
- Tap con nam trong muc tieu 500-2.000 bai cua De tai 3.

## Kiem tra truong va trung lap

- Khong thieu `id`, `source`, `url`, `category`, `title`, `content` hoac
  `publish_date` trong 1.113 bai.
- Khong trung ID va khong trung URL trong tap con.
- Co 3 ban ghi trung cap `title` + `content`; giu nguyen trong snapshot de co
  the truy vet, nhung phai xu ly/gom nhom khi lap retrieval pool va danh gia.
- Do dai content: nho nhat 110 ky tu; khong co bai nao duoi 200 ky tu.

## Phan bo nguon

| Nguon | So bai |
|---|---:|
| dantri | 969 |
| thanhnien | 50 |
| nguoilaodong | 37 |
| tienphong | 35 |
| tuoitre | 16 |
| vnexpress | 6 |
| **Tong** | **1.113** |

Tap con rat lech nguon (dantri chiem khoang 87,1%). Ket qua can duoc dien giai
la tren snapshot nay, khong phai tren toan bo tin tuc kinh te Viet Nam. Nen uu
tien danh gia loi theo nguon va can nhac giam anh huong cua bai trung/su kien
gan trung.

## Thoi gian

- Ngay som nhat: 2014-11-02.
- Ngay muon nhat: 2026-01-29.
- 249 ngay xuat ban khac nhau.
- Phan bo ngay khong deu; dataset card mo ta tap chung chu yeu 2025-2026 nhung
  tap Kinh doanh co du lieu tu 2014. Can xac minh snapshot/card va khong dung
  thoi gian nhu mot mau dai dien.

## Trang thai relevance va ket qua hau kiem

- AI tao 411 goi y relevance; day la nhan provisional, khong phai human gold.
- Duy da cham ca 411 ung vien test (2 dong q011 da co va 409 dong trong
  `duy_judgments.csv`); tat ca duoc luu la `single_annotator`.
- Duy da cham day du 411 ung vien test; metric tren nhan Duy duoc luu
  trong `evaluation/metrics_summary.csv`.
- Mau hau kiem 83/411 nhan (20,2%) da duoc thanh vien thu hai trong nhom (Tai)
  cham doc lap theo quy trinh. Ket qua hau kiem:
  - Dong thuan chinh xac: 21/83 (25,30%).
  - Khac biet: 62/83 (74,70%). Trong do lech 1 bac: 38/83 (45,8%), lech 2 bac: 20/83 (24,1%), lech 3 bac: 4/83 (4,8%).
  - Cohen's Kappa: 0,0311; Linear weighted Kappa: 0,0778.
  - Phieu cham va audit doi chieu duoc luu tai `evaluation/second_reviewer_sample.csv` va `evaluation/second_reviewer_audit.csv`.
- Yeu cau hau kiem nguoi thu hai (>=20%) theo huong dan BTL da duoc thuc hien hop le.

## Han che va viec can lam tiep

1. Xac minh cac ban ghi trung lap/bai cap nhat va gom theo bai/su kien khi tao
   candidate pool.
2. Kiem tra mot mau URL va noi dung, ghi nhan bai khong truy cap duoc hoac
   metadata sai.
3. Phan tich them nguyen nhan lech nhan giua Duy va Tai (phan lon lech 1 bac giua lien quan it va lien quan).
4. Ghi SHA-256 va revision cua snapshot khi chot phien ban.
5. Xac minh quy dinh quyen su dung/noi dung bai bao truoc khi chia se corpus.

# Du lieu

## Nguon va tai xuong

- Dataset: [UVN-1 - Vietnamese News Dataset](https://huggingface.co/datasets/undertheseanlp/UVN-1)
- File da tai: `raw/uvn1_train.parquet`
- URL file: https://huggingface.co/datasets/undertheseanlp/UVN-1/resolve/main/data/train-00000-of-00001.parquet
- Snapshot tai ngay 2026-11-10.
- SHA-256 Parquet: `6b736a03df728ad20fb5ed436a276a6379b6ff2f869c989d6f8c631cbd1eb0f8`.
- Dataset card ghi 3.268 bai, 6 nguon bao va license CC BY-NC 4.0.

## Tap con su dung

`processed/corpus.csv` gom cac ban ghi co `category = Kinh doanh` (1.113 bai
trong snapshot hien tai). Tap con giu nguyen noi dung va metadata goc; khong lay
nhan category lam nhan do lien quan truy hoi. `data_manifest.csv` cung cap ID,
URL nguon va cac truong metadata de doi chieu.

Audit ban dau cho thay nguon phan bo khong deu (969/1.113 bai tu Dan Tri), co
3 cap/bai trung title va content, va thoi gian bai bao tu 2014-11-02 den
2026-01-29. Xem `../data_quality_report.md` truoc khi su dung.

## Dieu kien su dung

Hugging Face khai bao CC BY-NC 4.0 cho dataset. Dieu nay khong tu dong xac nhan
quyen tai phan phoi toan van bai bao cua cac toa soan. Chi dung cho muc dich hoc
tap/nghien cuu phi thuong mai, giu attribution va URL goc, va khong dua noi dung
toan van len repository cong khai neu chua duoc phep. Neu nop repository, can
kiem tra quy dinh cua giang vien; co the can nop manifest/URL thay cho noi dung.

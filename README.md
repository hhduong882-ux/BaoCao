# 🎬 Nghiên Cứu Trích Xuất Metadata, Kiểm Tra Tính Toàn Vẹn Trong Forensic Video

> 🏫 Khoa An toàn thông tin, Học viện Kỹ thuật Mật mã
> 📍 Hà Nội, 2026

---

## 📖 Giới thiệu

Video ngày càng đóng vai trò là một nguồn **chứng cứ số** quan trọng trong điều tra số (Digital Forensics). Tuy nhiên, sự phổ biến của các công cụ chỉnh sửa — đặc biệt với sự hỗ trợ của AI — khiến việc cắt ghép, chỉnh sửa hoặc tái mã hóa video ngày càng khó phát hiện bằng mắt thường, ảnh hưởng nghiêm trọng đến độ tin cậy và giá trị pháp lý của video khi dùng làm chứng cứ.

Đề tài xây dựng một hệ thống hỗ trợ **kiểm tra tính xác thực của video** dựa trên ba trụ cột kỹ thuật chính.

---

## ✨ Tính năng chính

- 🔍 **Trích xuất Metadata** — thu thập thông tin kỹ thuật của video: định dạng, codec, FPS, bitrate, thời gian tạo file...
- 🔐 **Kiểm tra tính toàn vẹn dữ liệu** bằng hàm băm mật mã **SHA-256**, hỗ trợ so sánh và giám sát thay đổi file
- 📈 **Phân tích Bitrate theo thời gian** và cấu trúc **GOP** để phát hiện dấu hiệu bất thường do chỉnh sửa/tái mã hóa
- 🖥️ Giao diện **CLI** và **GUI (Tkinter)** trực quan, dễ thao tác

---

## 🛠️ Công nghệ & môi trường

| Loại | Chi tiết |
|---|---|
| 💻 Hệ điều hành | Windows 10 / 11 |
| 🐍 Ngôn ngữ | Python 3.6+ |
| 📦 Thư viện chuẩn | `datetime`, `zoneinfo`, `pathlib`, `json`, `subprocess`, `hashlib`, `tkinter`, `csv`, `statistics` |
| 📊 Xử lý số liệu | `numpy`, `matplotlib.pyplot` |
| 🎞️ Công cụ ngoài | **FFmpeg**, **FFprobe** |

---

## ⚙️ Cài đặt

```bash
# 1. Clone/tải project về máy
git clone <https://github.com/hhduong882-ux/BaoCao.git>

# 2. Cài các thư viện Python cần thiết
pip install numpy matplotlib

# 3. Cài FFmpeg/FFprobe và thêm vào PATH hệ thống
# Tải tại: https://www.gyan.dev/ffmpeg/builds/
```

## ▶️ Sử dụng

```bash
python main.py
```

- Chọn video cần kiểm tra qua giao diện chọn file
- Xem kết quả trích xuất metadata, kiểm tra hash SHA-256, và đồ thị phân tích bitrate/GOP
- Kết quả được xuất ra dạng `bitrate_series.csv`, `gop_series.csv`, `metadata.json`

---

## 📚 Tài liệu tham khảo

Xem chi tiết trong mục **Tài liệu tham khảo** và **Phụ lục** của báo cáo gốc.

## 👥 Tác giả

Sinh viên đồng thực hiện — Khoa An toàn thông tin, Học viện Kỹ thuật Mật mã, 2026

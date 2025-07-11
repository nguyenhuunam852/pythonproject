# 🧠 Django Spell Checker for Web Pages

Dự án Django này cho phép bạn **phân tích chính tả trên nội dung trang web**, đặc biệt là HTML và các nội dung render từ trình duyệt. Dự án hỗ trợ hai chế độ:

- ✅ **Phân tích trực tiếp HTML source**
- 🕵️‍♂️ **Phân tích nội dung hiển thị bằng trình duyệt thông qua Selenium**

Các lỗi chính tả sẽ được **highlight trực tiếp trong mã nguồn HTML hoặc nội dung hiển thị**, giúp bạn dễ dàng xác định và sửa lỗi.

---

## 🚀 Tính năng chính

- 📑 Đọc nội dung từ URL hoặc HTML file
- 🧪 Kiểm tra lỗi chính tả trong nội dung tiếng Việt
- 🌐 Dùng `Selenium` để phân tích chính tả ngay trên nội dung hiển thị thực tế (dynamic content)
- 🔍 Highlight các từ sai chính tả trong HTML bằng `<mark>` hoặc CSS
- 🛠️ Giao diện quản lý đơn giản trên Django admin

---

## 🏗️ Công nghệ sử dụng

- Python 3.8+
- Django (>=3.x)
- Selenium + WebDriver (Chrome hoặc Firefox)
- Thư viện kiểm tra chính tả: `pyvi`, `underthesea`, hoặc custom

---

## 🖥️ Hướng dẫn cài đặt

### 1. Clone repo

```bash
git clone https://github.com/nguyenhuunam852/pythonproject.git
cd pythonproject

📺 Video demo
👉 Xem video demo: https://youtu.be/OtRbBeFsFaU

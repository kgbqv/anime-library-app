
# Báo cáo Dự Án Cuối Kỳ - SQL Project

**Ngày nộp:** 22/04/2025  
**Thành viên thực hiện:** Bùi Quốc Vĩnh Khang 230312 (`kgbqv`), Võ Kế Hoài 230309 (`hoaivoke`)

Link GitHub: https://github.com/kgbqv/anime-library-app

Link Deploy: https://animelibrarytestkhgb.netlify.app/

Link Admin Panel: https://khgb.pythonanywhere.com/admin?password=adminpanel123


## 1. Mô tả đề tài

- **Tên ứng dụng:** 
    LibraryManagement – Hệ thống quản lý thư viện cho học sinh.
- **Mục đích & lý do chọn đề tài:**  
  Đề tài này giúp số hóa quá trình quản lý thư viện, giúp việc mượn và trả sách dễ dàng hơn, tiết kiệm thời gian và giảm thiểu sai sót trong việc ghi chép thủ công.
  Ngoài ra, nếu được phát triển thêm thì nó có thể sẽ nâng cao số lượng người đọc sách trong trường học.
- **Đối tượng sử dụng:**  
  Học sinh, sinh viên và nhân viên thư viện.

## 2. Ý tưởng và chức năng

- **Ý tưởng tổng thể:**  
  LibraryManagement là hệ thống quản lý thư viện giúp học sinh, sinh viên tra cứu sách, mượn sách và theo dõi quá trình mượn.

- **Tính năng chính:**  
  - Đăng ký / Đăng nhập  
  - Tìm kiếm sách  
  - Mượn/trả sách  
  - Gửi thông báo qua email  
  - Thêm, chỉnh sửa và xoá sách (dành cho admin)

- **Luồng sử dụng (User Journey):**  
  1. Người dùng đăng ký và đăng nhập vào hệ thống  
  2. Người dùng tìm kiếm sách cần mượn  
  3. Mượn sách qua web
  4. Người dùng nhận thông báo qua email
  5. Người dùng trả sách


## 3. Cơ sở dữ liệu (sử dụng SQLite)


| Tên Bảng  | Tên Cột    | Kiểu Dữ Liệu        | Mô Tả                                          |
|-----------|------------|---------------------|------------------------------------------------|
| `Sach`    | MaSach     | INTEGER (PRIMARY KEY, AUTOINCREMENT) | Mã sách, tự động tăng                           |
|           | TenSach    | TEXT (NOT NULL)      | Tên sách                                       |
|           | TacGia     | TEXT                 | Tác giả sách                                   |
|           | TheLoai    | TEXT                 | Thể loại sách                                 |
|           | SoLuong    | INTEGER (DEFAULT 0)  | Số lượng sách có trong thư viện, mặc định là 0 |
|           | LinkSach   | TEXT                 | Liên kết đến sách (nếu có)                     |
| `HocSinh` | MaHS         | INTEGER (PRIMARY KEY) | Mã học sinh, tự động tăng                       |
|           | TenHS        | TEXT (NOT NULL)      | Tên học sinh                                    |
|           | Lop          | TEXT                 | Lớp của học sinh                                |
|           | SoDienThoai  | TEXT                 | Số điện thoại của học sinh                      |
|           | Email        | TEXT                 | Email của học sinh                               |
|           | password     | TEXT (NOT NULL)      | Mật khẩu học sinh (được lưu trữ bằng hash)                                |
| `MuonSach`| MaMuon     | INTEGER (PRIMARY KEY, AUTOINCREMENT) | Mã mượn sách, tự động tăng                      |
|           | MaHS       | INTEGER (NOT NULL, FOREIGN KEY) | Mã học sinh (tham chiếu từ bảng `HocSinh`)      |
|           | MaSach     | INTEGER (NOT NULL, FOREIGN KEY) | Mã sách (tham chiếu từ bảng `Sach`)             |
|           | NgayMuon   | TEXT (DEFAULT CURRENT_TIMESTAMP) | Ngày mượn sách, mặc định là thời gian hiện tại  |
|           | NgayTra    | TEXT                  | Ngày trả sách                                   |
|           | TrangThai  | TEXT (DEFAULT 'Chưa trả') | Trạng thái mượn sách (mặc định 'Chưa trả')     |

### Quan Hệ Giữa Các Bảng:
- **1-Nhiều** giữa bảng `HocSinh` và bảng `MuonSach`: Mỗi học sinh có thể mượn nhiều sách.
- **1-Nhiều** giữa bảng `Sach` và bảng `MuonSach`: Mỗi sách có thể được mượn nhiều lần.



- **Quan hệ giữa các bảng:**  
  - Một người dùng có thể có nhiều yêu cầu mượn (1-N).  
  - Một sách có thể được mượn nhiều lần (1-N).  

## 4. Cách ứng dụng sử dụng CSDL

- **Truy vấn cho các chức năng chính:**

| Chức năng            | Câu lệnh SQL                                            |
|----------------------|---------------------------------------------------------|
| Đăng ký người dùng   | `INSERT INTO users (name, email, password, is_admin) VALUES (?, ?, ?, ?);` |
| Đăng nhập            | `SELECT * FROM users WHERE email = ? AND password = ?;` |
| Tìm kiếm sách        | `SELECT * FROM books WHERE title LIKE ? OR author LIKE ?;` |
| ...                  | ...                                                     |


## 5. Kết quả thực hiện

- **Giao diện người dùng:**  
    ![giao diện người dùng](https://files.catbox.moe/m2saa9.png)
    ![giao diện đăng nhập](https://files.catbox.moe/4e2k93.png)

- **Dữ liệu mẫu trong database:**  
    ![dữ liệu mẫu](https://files.catbox.moe/iv1npj.png)


## 6. Đánh giá & hướng phát triển

- **Khó khăn gặp phải:**  
  - Quản lý phân quyền giữa người dùng và admin.  
  - Gửi email

- **Giải pháp:**  
  - Phân quyền qua `admin panel`
  - Sử dụng Gmail SMTP để gửi email thông báo.

- **Điểm mạnh:**  
  - Giao diện dễ sử dụng.  
  - Quản lý dữ liệu mượn sách nhanh chóng và chính xác.  
  - Tính năng thông báo qua email giúp người dùng theo dõi tình trạng yêu cầu.

- **Hướng cải tiến:**  
  - Thêm tính năng đánh giá sách.  
  - Sử dụng cơ sở dữ liệu MySQL thay vì SQLite khi ứng dụng được triển khai rộng rãi.
  - Thêm tính năng LLM để người dùng có thể hỏi về sách và nhận được câu trả lời tự động.
  - Tích hợp với các dịch vụ bên ngoài để cung cấp thông tin sách phong phú hơn.
  - Thêm tính năng `gameification` để khuyến khích người dùng mượn và đọc sách nhiều hơn.

## 7. Hướng dẫn chạy ứng dụng

- **Phần mềm và thư viện cần cài đặt:**  
  - Python 3.x  
  - SQLite3  
  - Thư viện: Flask, Flask-Mail,..

- **Cài đặt thư viện:**  
  ```bash
  pip install Flask flask-cors werkzeug Flask-Mail

  ```

- **Chạy ứng dụng:**  
  ```bash
  python app.py
  ```

# 8. Một số lưu ý

Backend của em được viết bằng `python` và `flask`, còn frontend được viết bằng `html`, `css` và `js`.

Backend được host trên `pythonanywhere` và frontend được host trên `netlify`.

# Roles and Permissions Specification

## 1. Mục đích tài liệu
Tài liệu này xác định rõ:
- hệ thống có những actor nào,
- mỗi actor được làm gì,
- mỗi actor không được làm gì,
- nguyên tắc phân quyền và bảo mật dữ liệu.

Đây là tài liệu cực kỳ quan trọng vì project liên quan trực tiếp đến **dữ liệu tài chính cá nhân**, nên nếu phân quyền sai thì hệ thống bị lỗi nghiêm trọng cả về nghiệp vụ lẫn bảo mật.

---

## 2. Danh sách actor chính
Hệ thống chốt 3 actor:
1. **Guest**
2. **User**
3. **Admin**

---

## 3. Mô tả actor

### 3.1. Guest
Guest là người chưa đăng nhập vào hệ thống.

**Đặc điểm:**
- Không có phiên xác thực.
- Không có dữ liệu tài chính cá nhân trong hệ thống hoặc chưa truy cập dữ liệu đó.

**Mục tiêu sử dụng:**
- Tìm hiểu về hệ thống.
- Đăng ký tài khoản mới.
- Đăng nhập nếu đã có tài khoản.

---

### 3.2. User
User là người đã đăng nhập thành công và sử dụng hệ thống để quản lý tài chính cá nhân.

**Đặc điểm:**
- Có tài khoản hợp lệ.
- Chỉ được thao tác trên dữ liệu của chính mình.
- Có thể sử dụng các module lõi như income, expense, category, bank account, budget, reports.

**Mục tiêu sử dụng:**
- Theo dõi tài chính cá nhân.
- Xem báo cáo chi tiêu.
- Kiểm soát ngân sách.
- Nhận cảnh báo.

---

### 3.3. Admin
Admin là người quản trị hệ thống.

**Đặc điểm:**
- Có quyền cao hơn User.
- Có thể quản lý người dùng, category mặc định, logs, trạng thái hệ thống.
- Không được dùng quyền quản trị để xem tùy tiện dữ liệu tài chính riêng tư nếu chính sách hệ thống không cho phép.

**Mục tiêu sử dụng:**
- Quản lý vận hành hệ thống.
- Kiểm tra người dùng.
- Kiểm tra lỗi và log.
- Theo dõi backup/recovery.

---

## 4. Nguyên tắc phân quyền tổng quát

### 4.1. Principle of Least Privilege
Mỗi actor chỉ được cấp **đúng mức quyền cần thiết** để hoàn thành công việc của mình.

### 4.2. Ownership-based Access Control
Đối với dữ liệu tài chính cá nhân, quyền truy cập phải dựa trên nguyên tắc **sở hữu dữ liệu**:
- bản ghi income thuộc user nào thì chỉ user đó được xem/sửa/xóa,
- expense thuộc user nào thì chỉ user đó được xem/sửa/xóa,
- budget thuộc user nào thì chỉ user đó được xem/sửa/xóa,
- bank account thuộc user nào thì chỉ user đó được xem/sửa/xóa.

### 4.3. Authentication before Authorization
Muốn kiểm tra quyền thì trước hết phải xác thực người dùng là ai.

### 4.4. Default Deny
Nếu một quyền chưa được cấp rõ ràng, hệ thống phải mặc định từ chối.

---

## 5. Bảng quyền theo actor

| Chức năng | Guest | User | Admin |
|---|---|---|---|
| Xem landing page | Có | Có | Có |
| Đăng ký | Có | Không cần | Có thể tạo user thủ công nếu hỗ trợ |
| Đăng nhập | Có | Có | Có |
| Đăng xuất | Không | Có | Có |
| Xem/sửa hồ sơ cá nhân | Không | Có (chỉ của mình) | Có (hồ sơ admin của chính mình) |
| Quản lý income | Không | Có (chỉ của mình) | Không mặc định |
| Quản lý expenses | Không | Có (chỉ của mình) | Không mặc định |
| Quản lý categories cá nhân | Không | Có (chỉ của mình) | Có thể quản lý category hệ thống |
| Quản lý bank accounts | Không | Có (chỉ của mình) | Không mặc định |
| Quản lý budgets | Không | Có (chỉ của mình) | Không mặc định |
| Xem alerts | Không | Có (chỉ của mình) | Có thể xem alert hệ thống |
| Xem dashboard | Không | Có (chỉ của mình) | Có dashboard quản trị |
| Xem reports | Không | Có (chỉ của mình) | Chỉ báo cáo quản trị nếu có |
| Theo dõi debts | Không | Có (chỉ của mình) | Không mặc định |
| Tham gia sharing groups | Không | Có | Không mặc định |
| Export Excel/PDF | Không | Có (dữ liệu của mình) | Có thể export báo cáo quản trị |
| Quản lý users | Không | Không | Có |
| Quản lý logs | Không | Không | Có |
| Backup/Recovery operations | Không | Không | Có |

---

## 6. Quyền chi tiết theo actor

# 6.1. Guest permissions

### Guest được phép
- Truy cập landing page.
- Xem giới thiệu hệ thống.
- Truy cập trang đăng ký.
- Truy cập trang đăng nhập.

### Guest không được phép
- Xem dashboard.
- Xem báo cáo.
- Xem hoặc tạo income/expense.
- Xem bất kỳ dữ liệu tài chính nào.
- Gọi API yêu cầu xác thực.

### Hành vi hệ thống khi Guest cố truy cập trái phép
- Chuyển hướng đến trang login.
- Hoặc trả về HTTP 401/403 tùy kiến trúc.

---

# 6.2. User permissions

## 6.2.1. Quyền với hồ sơ cá nhân
User được phép:
- xem hồ sơ,
- sửa hồ sơ,
- đổi mật khẩu,
- thay đổi một số cài đặt cá nhân.

User không được:
- sửa hồ sơ của người khác,
- xem hồ sơ chi tiết của người khác.

---

## 6.2.2. Quyền với income
User được phép:
- tạo income,
- xem danh sách income của mình,
- xem chi tiết income của mình,
- sửa income của mình,
- xóa income của mình.

User không được:
- xem income của user khác,
- sửa/xóa income của user khác,
- truyền `user_id` tùy ý để chiếm quyền bản ghi.

---

## 6.2.3. Quyền với expenses
User được phép:
- tạo expense,
- xem expense của mình,
- sửa expense của mình,
- xóa expense của mình,
- lọc expense theo category/date/account.

User không được:
- truy cập expense của user khác,
- xem category usage của user khác.

---

## 6.2.4. Quyền với categories
User được phép:
- tạo category cá nhân,
- sửa category cá nhân,
- vô hiệu hóa category cá nhân,
- dùng category hệ thống mặc định nếu được cung cấp.

User không được:
- chỉnh sửa category hệ thống nếu không phải admin,
- chỉnh sửa category cá nhân của người khác.

---

## 6.2.5. Quyền với bank accounts
User được phép:
- tạo bank account,
- sửa thông tin tài khoản,
- xem số dư,
- xem giao dịch liên quan.

User không được:
- xem hoặc thay đổi bank account của người khác,
- rút/trừ số dư của người khác.

---

## 6.2.6. Quyền với budgets
User được phép:
- tạo budget,
- sửa budget,
- đóng budget,
- xem mức sử dụng budget,
- xem cảnh báo phát sinh từ budget.

User không được:
- truy cập budget của người khác.

---

## 6.2.7. Quyền với alerts
User được phép:
- xem alert của mình,
- đánh dấu đã đọc,
- lọc theo loại alert.

User không được:
- xem alert của user khác.

---

## 6.2.8. Quyền với reports/dashboard
User được phép:
- xem dashboard cá nhân,
- xem báo cáo ngày/tháng/năm của mình,
- xem biểu đồ và bảng dữ liệu của mình,
- export dữ liệu của mình.

User không được:
- xem báo cáo tổng của người khác,
- export dữ liệu người khác.

---

## 6.2.9. Quyền với debts
User được phép:
- tạo debt record,
- cập nhật trạng thái,
- ghi payment,
- xem debt của mình.

User không được:
- xem debt của người khác trừ khi có mô hình chia sẻ hợp lệ.

---

## 6.2.10. Quyền với sharing groups
User được phép:
- tạo group nếu hệ thống cho phép,
- tham gia group,
- xem shared transactions của nhóm mình là thành viên,
- thêm shared transaction nếu có quyền trong nhóm.

User không được:
- xem giao dịch của group khác,
- thêm thành viên trái phép nếu không phải owner/admin nhóm,
- xem transaction private không được chia sẻ.

---

# 6.3. Admin permissions

## 6.3.1. Quyền với người dùng
Admin được phép:
- xem danh sách user,
- kích hoạt / vô hiệu hóa user,
- tìm kiếm user,
- xem trạng thái tài khoản.

Admin cần thận trọng với:
- việc chỉnh sửa dữ liệu tài chính cá nhân,
- việc truy cập dữ liệu riêng tư không nằm trong chính sách.

---

## 6.3.2. Quyền với category hệ thống
Admin được phép:
- tạo default categories,
- chỉnh sửa category dùng chung,
- vô hiệu hóa category hệ thống.

---

## 6.3.3. Quyền với logs và vận hành
Admin được phép:
- xem authentication logs,
- xem error logs,
- xem log của các job định kỳ,
- theo dõi backup/recovery,
- kiểm tra tác vụ hệ thống.

---

## 6.3.4. Quyền với backup/recovery
Admin được phép:
- chạy backup thủ công,
- phục hồi dữ liệu theo quy trình,
- kiểm tra tình trạng file backup,
- xác minh tính toàn vẹn cơ bản.

---

## 6.3.5. Hạn chế của Admin
Admin không nên mặc định có quyền xem toàn bộ transaction cá nhân chi tiết trừ khi:
- có chính sách môn học/đề tài cho phép,
- hoặc cần phục vụ debug có kiểm soát,
- hoặc dữ liệu chỉ là dữ liệu demo.

Khuyến nghị tốt hơn:
- Admin quản trị user và hệ thống,
- dữ liệu tài chính chi tiết của user vẫn nên được bảo vệ.

---

## 7. Quy tắc bảo mật cốt lõi

### 7.1. Mỗi user chỉ xem dữ liệu tài chính của chính mình
Đây là nguyên tắc quan trọng nhất của hệ thống.

Áp dụng cho:
- income,
- expenses,
- categories cá nhân,
- bank accounts,
- budgets,
- alerts,
- reports,
- debts.

### 7.2. Không được lộ income/expense của người khác
Điều này áp dụng ở cả:
- giao diện,
- API,
- export,
- báo cáo,
- query DB.

### 7.3. Không tin dữ liệu từ phía client
Dù client gửi `user_id`, backend vẫn phải lấy user từ session/token hiện tại và kiểm tra ownership.

### 7.4. Cần log các hành vi quan trọng
Các hành vi nên log:
- login thành công/thất bại,
- đổi mật khẩu,
- khóa/mở user,
- backup/recovery,
- lỗi hệ thống,
- chạy job nền.

---

## 8. Hướng đăng nhập được chốt

### Giai đoạn đầu
- **Login thường** bằng email/username + password.

### Giai đoạn sau
- **Google Login** có thể thêm sau.

### Lý do chốt như vậy
- Login thường dễ triển khai và ổn định cho MVP.
- Google login là mở rộng tốt nhưng không nên làm ngay khi schema/chức năng lõi chưa xong.

---

## 9. Quy tắc phân quyền ở backend Django
Trong Django, cần thực hiện kiểm soát ở các mức sau:

### 9.1. Route-level protection
- Trang cần đăng nhập phải có `login_required` hoặc equivalent.
- API phải chặn truy cập chưa xác thực.

### 9.2. Object-level permission
Không chỉ kiểm tra user đã login hay chưa, mà còn phải kiểm tra:
- object này có thuộc user hiện tại không.

Ví dụ:
- `/expenses/15/edit/` chỉ hợp lệ nếu expense id=15 thuộc user đang đăng nhập.

### 9.3. Admin panel separation
- Admin panel chỉ cho admin truy cập.
- User thường không được truy cập chức năng quản trị.

---

## 10. Permission matrix chi tiết hơn theo module

| Module | Guest | User | Admin |
|---|---|---|---|
| Accounts | register/login | profile/update/logout | manage users |
| Income | không | CRUD own | không mặc định |
| Expenses | không | CRUD own | không mặc định |
| Categories | không | CRUD own categories | manage default categories |
| Bank Accounts | không | CRUD own | không mặc định |
| Budgets | không | CRUD own | không mặc định |
| Alerts | không | view own | system-level only |
| Reports | không | view/export own | admin reports only |
| Debts | không | CRUD own | không mặc định |
| Sharing | không | access groups of membership | moderate if designed |
| Logs | không | không | view/manage |
| Backup/Recovery | không | không | manage |

---

## 11. Các tình huống kiểm thử phân quyền

### Test case 1
User A đăng nhập và cố xem expense của User B bằng cách sửa URL.

**Kết quả mong đợi:**
- Bị từ chối truy cập.
- Trả 403 hoặc redirect hợp lý.

### Test case 2
Guest truy cập `/dashboard/`.

**Kết quả mong đợi:**
- Bị chuyển đến login.

### Test case 3
User thường truy cập `/admin/`.

**Kết quả mong đợi:**
- Không vào được vùng quản trị.

### Test case 4
Admin vô hiệu hóa user.

**Kết quả mong đợi:**
- User bị vô hiệu hóa không thể đăng nhập tiếp.

### Test case 5
User export report tháng.

**Kết quả mong đợi:**
- Chỉ dữ liệu của user đó được đưa vào file export.

---

## 12. Kết luận
Tài liệu phân quyền này là nền móng cho toàn bộ hệ thống vì bài toán quản lý tài chính cá nhân cực kỳ nhạy cảm về dữ liệu. Từ thời điểm này trở đi, mọi thiết kế schema, API, query, dashboard và report đều phải tuân theo nguyên tắc:

**mỗi user chỉ được xem và thao tác trên dữ liệu tài chính của chính mình**.

Đây là rule không được phá vỡ trong bất kỳ module nào của hệ thống.

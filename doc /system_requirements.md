# System Requirements — Personal Finance Management System

## 1. Mục đích tài liệu
Tài liệu này mô tả chi tiết các yêu cầu chức năng và phi chức năng của hệ thống **NUFI**. Mục tiêu là giúp nhóm thống nhất:
- hệ thống cần làm gì,
- mức độ ưu tiên của từng chức năng,
- phạm vi MVP và phạm vi mở rộng,
- tiêu chí kiểm thử và nghiệm thu.

---

## 2. Phạm vi yêu cầu
Hệ thống là một ứng dụng web hỗ trợ người dùng cá nhân quản lý tài chính hằng ngày, gồm:
- quản lý hồ sơ cá nhân,
- ghi nhận thu nhập và chi tiêu,
- quản lý danh mục thu nhập và chi tiêu,
- theo dõi tài khoản ngân hàng,
- lập ngân sách,
- nhận cảnh báo,
- xem báo cáo bảng/biểu đồ,
- mở rộng sang nợ, nhóm chia sẻ, xuất file và đồng bộ cloud.

---

## 3. Phân loại yêu cầu
Tài liệu chia yêu cầu thành 4 nhóm:
1. **Functional Requirements (FR)** — hệ thống phải làm gì.
2. **Non-functional Requirements (NFR)** — hệ thống phải chạy như thế nào.
3. **Business Constraints / Assumptions** — các ràng buộc và giả định.
4. **Acceptance Criteria** — tiêu chí chấp nhận để nghiệm thu.

---

## 4. Functional Requirements (FR)

# 4.1. Nhóm yêu cầu tài khoản và xác thực

### FR-01 — User Registration
Hệ thống phải cho phép Guest đăng ký tài khoản mới.

**Đầu vào:**
- full_name
- email
- username (nếu dùng)
- password
- confirm_password

**Xử lý:**
- Kiểm tra email/username chưa tồn tại.
- Kiểm tra định dạng email hợp lệ.
- Kiểm tra mật khẩu đạt yêu cầu tối thiểu.
- Tạo tài khoản người dùng mới.

**Đầu ra:**
- Thông báo đăng ký thành công hoặc lỗi chi tiết.

**Ưu tiên:** Cao.

---

### FR-02 — User Login
Hệ thống phải cho phép User đăng nhập bằng thông tin xác thực hợp lệ.

**Đầu vào:**
- email hoặc username
- password

**Xử lý:**
- Kiểm tra tài khoản tồn tại.
- Kiểm tra mật khẩu đúng.
- Kiểm tra tài khoản có active hay không.

**Đầu ra:**
- Tạo phiên đăng nhập và chuyển đến dashboard.

**Ưu tiên:** Cao.

---

### FR-03 — User Logout
Hệ thống phải cho phép User đăng xuất an toàn.

**Ưu tiên:** Cao.

---

### FR-04 — Manage Profile
Hệ thống phải cho phép User xem và cập nhật hồ sơ cá nhân.

**Thông tin có thể cập nhật:**
- họ tên
- số điện thoại
- ảnh đại diện
- giới tính (tùy chọn)
- ngày sinh (tùy chọn)
- múi giờ (tùy chọn)
- tiền tệ mặc định (tùy chọn)

**Ưu tiên:** Cao.

---

### FR-05 — Change Password
User phải đổi được mật khẩu sau khi xác thực mật khẩu cũ.

**Ưu tiên:** Trung bình.

---

### FR-06 — Google Login (future extension)
Hệ thống có thể hỗ trợ đăng nhập Google ở giai đoạn mở rộng.

**Ưu tiên:** Thấp / làm sau.

---

# 4.2. Nhóm yêu cầu quản lý thu nhập

### FR-07 — Create Income
User phải tạo được khoản thu nhập.

**Thuộc tính tối thiểu:**
- user
- title / description
- amount
- income_date
- category
- bank_account (optional)
- note

**Xử lý:**
- Validate amount > 0.
- Validate category hợp lệ cho income (`income` hoặc `both`).
- Nếu có bank account, cập nhật số dư tăng tương ứng.
- Ghi log giao dịch.

**Ưu tiên:** Cao.

---

### FR-08 — Update Income
User phải sửa được khoản thu nhập do chính mình tạo.

**Xử lý:**
- Nếu số tiền hoặc bank account thay đổi, phải điều chỉnh lại balance cho chính xác.

**Ưu tiên:** Cao.

---

### FR-09 — Delete Income
User phải xóa được khoản thu nhập của mình.

**Xử lý:**
- Nếu khoản thu đã từng cộng vào bank account thì phải rollback lại balance.
- Nên dùng soft delete nếu muốn bảo toàn lịch sử.

**Ưu tiên:** Trung bình.

---

### FR-10 — View Income List
User phải xem được danh sách income của chính mình.

**Bộ lọc:**
- theo ngày
- theo tháng
- theo năm
- theo category
- theo bank account

**Sắp xếp:**
- mới nhất
- cũ nhất
- số tiền tăng/giảm

**Ưu tiên:** Cao.

---

# 4.3. Nhóm yêu cầu quản lý chi tiêu

### FR-11 — Create Expense
User phải tạo được khoản chi tiêu.

**Thuộc tính tối thiểu:**
- user
- category
- amount
- expense_date
- description
- bank_account (optional)
- payment_method (cash/bank/e-wallet/other)
- note

**Xử lý:**
- Validate amount > 0.
- Nếu có bank account, giảm balance tương ứng.
- Kích hoạt check budget.
- Có thể tạo alert nếu vượt ngưỡng.

**Ưu tiên:** Cao.

---

### FR-12 — Update Expense
User phải sửa được khoản chi của chính mình.

**Xử lý:**
- Nếu đổi amount, category hoặc bank account, hệ thống phải điều chỉnh lại balance và budget usage.

**Ưu tiên:** Cao.

---

### FR-13 — Delete Expense
User phải xóa được khoản chi của mình.

**Xử lý:**
- Nếu khoản này từng trừ vào balance thì phải cộng ngược lại.
- Nếu khoản này ảnh hưởng budget thì phải cập nhật lại budget usage.

**Ưu tiên:** Trung bình.

---

### FR-14 — View Expense List
User phải xem được danh sách expenses của chính mình.

**Bộ lọc:**
- theo ngày/tháng/năm
- theo category
- theo bank account
- theo payment method
- theo khoảng tiền

**Ưu tiên:** Cao.

---

# 4.4. Nhóm yêu cầu quản lý category

### FR-15 — Create Category
User phải tạo được category phục vụ phân loại thu nhập và chi tiêu.

**Thuộc tính:**
- category_name
- category_type (income / expense / both)
- color
- icon
- description
- is_default
- is_active

**Ưu tiên:** Cao.

---

### FR-16 — Update Category
User phải sửa được category do mình sở hữu hoặc category được phép sửa.

**Ưu tiên:** Cao.

---

### FR-17 — Disable Category
User/Admin phải có thể vô hiệu hóa category thay vì xóa cứng.

**Lý do:**
- tránh làm hỏng lịch sử expense cũ.

**Ưu tiên:** Trung bình.

---

### FR-18 — View Categories
User phải xem được danh sách category đang hoạt động theo phạm vi được phép sử dụng.

**Ưu tiên:** Cao.

---

# 4.5. Nhóm yêu cầu quản lý bank accounts

### FR-19 — Create Bank Account
User phải tạo được tài khoản ngân hàng / ví / cash wallet.

**Thuộc tính:**
- account_name
- account_type
- provider_name
- account_number_masked (optional)
- current_balance
- currency
- note

**Ưu tiên:** Cao.

---

### FR-20 — Update Bank Account
User phải sửa được thông tin bank account của mình.

**Lưu ý:**
- nếu sửa opening balance hoặc current balance thì cần cơ chế kiểm soát rõ ràng.

**Ưu tiên:** Cao.

---

### FR-21 — View Bank Accounts
User phải xem được danh sách tài khoản cùng số dư hiện tại.

**Ưu tiên:** Cao.

---

### FR-22 — View Account Transactions
User phải xem được danh sách income/expense liên quan đến từng bank account.

**Ưu tiên:** Trung bình.

---

# 4.6. Nhóm yêu cầu quản lý budgets

### FR-23 — Create Overall Budget
User phải tạo được budget tổng cho một tháng cụ thể.

**Thuộc tính:**
- budget_name
- period_month
- period_year
- spending_limit
- warning_percent

**Ưu tiên:** Cao.

---

### FR-24 — Create Category Budget
User phải tạo được budget cho một category trong tháng.

**Thuộc tính:**
- category
- month/year
- spending_limit

**Ưu tiên:** Cao.

---

### FR-25 — Track Budget Usage
Hệ thống phải tự tính tổng chi đã dùng trong phạm vi budget.

**Đầu ra:**
- amount_used
- amount_remaining
- usage_percent
- over_limit_flag

**Ưu tiên:** Cao.

---

### FR-26 — Update Budget
User phải sửa được hạn mức và cảnh báo của budget.

**Ưu tiên:** Trung bình.

---

### FR-27 — Disable Budget
User phải có thể đóng / vô hiệu hóa budget cũ.

**Ưu tiên:** Trung bình.

---

# 4.7. Nhóm yêu cầu cảnh báo (alerts)

### FR-28 — Generate Spending Alert
Hệ thống phải tạo cảnh báo khi:
- mức dùng đạt ngưỡng cảnh báo (ví dụ 80%).
- mức dùng vượt ngân sách (100%+).

**Loại alert:**
- budget_warning
- budget_exceeded
- debt_overdue
- system_info

**Ưu tiên:** Cao.

---

### FR-29 — View Alerts
User phải xem được các alert của mình.

**Ưu tiên:** Cao.

---

### FR-30 — Mark Alert as Read
User phải đánh dấu alert là đã đọc.

**Ưu tiên:** Trung bình.

---

# 4.8. Nhóm yêu cầu báo cáo và dashboard

### FR-31 — Daily Summary
Hệ thống phải cung cấp tổng hợp theo ngày.

**Nội dung:**
- tổng income ngày
- tổng expense ngày
- net cash flow ngày

**Ưu tiên:** Cao.

---

### FR-32 — Monthly Summary
Hệ thống phải cung cấp tổng hợp theo tháng.

**Nội dung:**
- tổng thu tháng
- tổng chi tháng
- category chi nhiều nhất
- số dư cuối tháng (ước tính hoặc theo account)

**Ưu tiên:** Cao.

---

### FR-33 — Yearly Summary
Hệ thống phải cung cấp tổng hợp theo năm.

**Ưu tiên:** Trung bình đến cao.

---

### FR-34 — Graphical Reports
Hệ thống phải hiển thị báo cáo dạng biểu đồ như:
- pie chart theo category
- bar chart theo tháng
- line chart xu hướng thu/chi

**Ưu tiên:** Cao.

---

### FR-35 — Tabular Reports
Hệ thống phải hiển thị báo cáo dạng bảng, hỗ trợ lọc và sắp xếp.

**Ưu tiên:** Cao.

---

### FR-36 — Dashboard Overview
Dashboard phải hiển thị nhanh:
- tổng balance các tài khoản
- tổng income tháng này
- tổng expense tháng này
- remaining budget
- recent transactions
- unread alerts

**Ưu tiên:** Cao.

---

# 4.9. Nhóm yêu cầu quản lý nợ (extension)

### FR-37 — Create Debt
User phải ghi được khoản nợ.

**Phân loại:**
- mình nợ người khác
- người khác nợ mình

**Thuộc tính:**
- debt_type
- counterparty_name
- original_amount
- due_date
- status
- note

**Ưu tiên:** Giai đoạn 2.

---

### FR-38 — Record Debt Payment
User phải ghi được lịch sử thanh toán nợ.

**Ưu tiên:** Giai đoạn 2.

---

### FR-39 — Debt Status Tracking
Hệ thống phải xác định trạng thái:
- pending
- partially_paid
- paid
- overdue

**Ưu tiên:** Giai đoạn 2.

---

# 4.10. Nhóm yêu cầu sharing groups (extension)

### FR-40 — Create Group
User phải tạo được nhóm chia sẻ tài chính.

**Ưu tiên:** Giai đoạn 2.

---

### FR-41 — Invite / Add Group Members
Group owner phải thêm thành viên được.

**Ưu tiên:** Giai đoạn 2.

---

### FR-42 — Share Transactions
User phải gắn một số giao dịch thành shared transaction trong group.

**Ưu tiên:** Giai đoạn 2.

---

### FR-43 — Restrict Group Visibility
Chỉ thành viên nhóm mới xem được giao dịch chia sẻ trong nhóm đó.

**Ưu tiên:** Giai đoạn 2.

---

# 4.11. Nhóm yêu cầu export và cloud sync

### FR-44 — Export Excel
User phải xuất được báo cáo ra Excel.

**Ưu tiên:** Giai đoạn 2.

---

### FR-45 — Export PDF
User phải xuất được báo cáo ra PDF.

**Ưu tiên:** Giai đoạn 2.

---

### FR-46 — Scheduled Backup
Hệ thống phải hỗ trợ backup định kỳ.

**Ưu tiên:** Cao về hạ tầng, có thể triển khai tối thiểu trong demo.

---

### FR-47 — Cloud Sync
Hệ thống có thể đồng bộ dữ liệu / file backup lên cloud.

**Ưu tiên:** Giai đoạn 2.

---

# 4.12. Nhóm yêu cầu quản trị

### FR-48 — Admin Manage Users
Admin phải xem danh sách user, kích hoạt/vô hiệu hóa tài khoản, kiểm tra trạng thái.

**Ưu tiên:** Cao.

---

### FR-49 — Admin Manage Default Categories
Admin phải quản lý danh mục mặc định của hệ thống.

**Ưu tiên:** Trung bình.

---

### FR-50 — Admin View Logs
Admin phải xem được log hệ thống, log đăng nhập, log lỗi, log tác vụ nền.

**Ưu tiên:** Trung bình.

---

## 5. Non-functional Requirements (NFR)

### NFR-01 — Security
- Mỗi user chỉ truy cập dữ liệu của chính mình.
- Tất cả route cần kiểm tra authentication/authorization.
- Password phải được hash.
- Không expose ID nhạy cảm theo cách thiếu kiểm soát.
- Có CSRF protection cho form web.
- Có validation đầu vào.

### NFR-02 — Performance
- Truy vấn danh sách giao dịch phổ biến phải phản hồi tốt.
- Cần index các cột được lọc nhiều như user_id, date, category_id, bank_account_id, status.
- Báo cáo tháng/năm cần được tối ưu bằng aggregate query hoặc view.

### NFR-03 — Reliability
- Hệ thống phải hạn chế mất dữ liệu khi lỗi.
- Các thay đổi balance phải có tính nhất quán.
- Các thao tác tạo/sửa/xóa transaction nên chạy trong transaction an toàn.

### NFR-04 — Scalability
- Có thể mở rộng thêm module debts, sharing, exports mà không phá schema cũ.
- Có thể triển khai tách service sau này nếu cần.

### NFR-05 — Maintainability
- Code chia module rõ ràng theo Django app.
- Schema đặt tên nhất quán.
- Có tài liệu mô tả bảng, rule, API, workflow.

### NFR-06 — Usability
- Giao diện phải dễ hiểu với người dùng phổ thông.
- Form nhập liệu cần rõ trường bắt buộc/không bắt buộc.
- Dashboard và báo cáo phải đọc dễ.

### NFR-07 — Backup & Recovery
- Có backup định kỳ DB.
- Có tài liệu phục hồi dữ liệu.
- File backup được lưu an toàn.

### NFR-08 — Auditability
- Các thay đổi quan trọng nên ghi nhận log.
- Các alert và tác vụ tự động cần truy vết được nguồn sinh ra.

---

## 6. Business Constraints / Assumptions
- Hệ thống phục vụ người dùng cá nhân, không phải kế toán doanh nghiệp phức tạp.
- Dữ liệu bank account ban đầu do user nhập thủ công.
- Không tích hợp live API ngân hàng ở bản đầu.
- Một expense thuộc đúng một category chính.
- Một income/expense có thể gắn một bank account hoặc không.
- Balance hiện tại là dữ liệu có thể được hệ thống tính từ giao dịch hoặc cập nhật theo rule thống nhất.
- Budget hiện ưu tiên cho chu kỳ tháng.
- Currency mặc định là một loại tiền cho mỗi user ở bản đầu.

---

## 7. In-scope / Out-of-scope tóm tắt

### 7.1. In-scope
- user profile management
- income/expense entry
- bank account tracking
- daily/monthly/yearly summaries
- budget planning
- spending limit alerts
- graphical and tabular reports
- indexes/views/procedures/functions/triggers
- security, backup, recovery
- debt tracking (phase 2 nếu kịp)
- sharing groups (phase 2 nếu kịp)
- export Excel/PDF (phase 2 nếu kịp)
- cloud sync (phase 2)

### 7.2. Out-of-scope
- live banking integration
- AI financial prediction
- OCR receipt scan
- multi-currency exchange engine real-time
- full mobile native app

---

## 8. Acceptance Criteria

### 8.1. MVP acceptance criteria
Project được xem là đạt mức MVP nếu:
1. User đăng ký, đăng nhập, cập nhật hồ sơ được.
2. User CRUD được income.
3. User CRUD được expenses.
4. User CRUD được categories.
5. User CRUD được bank accounts.
6. User tạo và theo dõi được budget.
7. Hệ thống sinh được alert khi chi tiêu vượt ngưỡng.
8. Dashboard hiển thị được thông tin tổng quan.
9. Báo cáo ngày/tháng/năm chạy được.
10. Dữ liệu giữa các user tách biệt chính xác.

### 8.2. Database acceptance criteria
1. Có schema relational rõ ràng.
2. Có PK/FK đầy đủ.
3. Có index cho các bảng chính.
4. Có ít nhất một view.
5. Có ít nhất một procedure hoặc function.
6. Có ít nhất một trigger liên quan balance/alert/log.

### 8.3. Deployment acceptance criteria
1. Ứng dụng chạy bằng Docker.
2. Kết nối MySQL thành công.
3. Có mô tả Airflow job hoặc demo được ít nhất một DAG.
4. Có phương án backup/recovery.

---

## 9. Mức độ ưu tiên triển khai

### Ưu tiên 1 — Phải có
- auth
- profile
- categories
- income
- expenses
- bank accounts
- budgets
- alerts
- dashboard
- reports
- schema DB
- security cơ bản

### Ưu tiên 2 — Nên có
- admin logs
- export Excel/PDF
- debt tracking
- view/procedure/function/trigger hoàn chỉnh
- backup automation

### Ưu tiên 3 — Có thể có nếu còn thời gian
- sharing groups
- cloud sync nâng cao
- Google login
- báo cáo nâng cao

---

## 10. Kết luận
Tài liệu yêu cầu này là cơ sở để nhóm tiếp tục đi sang các bước:
- chốt actor và quyền,
- chốt module,
- viết business rules,
- vẽ use case,
- vẽ ERD,
- thiết kế relational schema,
- sau đó mới sang code Django và database implementation.

Càng chốt rõ requirement ở giai đoạn đầu thì càng ít lệch hướng khi triển khai code, giao diện và cơ sở dữ liệu.

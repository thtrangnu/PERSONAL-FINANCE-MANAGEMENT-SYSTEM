# Relational Schema Design

## 1. Mục đích tài liệu
Tài liệu này mô tả lược đồ quan hệ logic của hệ thống **Personal Finance Management System (PFMS)**, bao gồm:
- danh sách bảng,
- ý nghĩa từng bảng,
- các cột và kiểu dữ liệu,
- khóa chính (PK), khóa ngoại (FK), ràng buộc,
- trường hệ thống,
- index đề xuất,
- quan hệ giữa các bảng.

Mục tiêu là tạo nền tảng rõ ràng trước khi viết:
- Django models,
- migrations,
- SQL DDL,
- view/procedure/function/trigger.

---

## 2. Quy ước thiết kế chung

### 2.1. Quy ước đặt tên bảng
- Dùng danh từ số nhiều, viết theo snake_case nếu triển khai SQL trực tiếp.
- Trong tài liệu này vẫn giữ tên theo dạng dễ đọc như đề bài:
  - Users
  - ExpenseCategories
  - BankAccounts
  - Income
  - Expenses
  - Budgets
  - Alerts
  - Debts
  - DebtPayments
  - Groups
  - GroupMembers
  - SharedTransactions

### 2.2. Quy ước khóa chính
- Mỗi bảng có khóa chính dạng `BIGINT AUTO_INCREMENT` hoặc `UUID`.
- Với project môn học, `BIGINT AUTO_INCREMENT` thường dễ thao tác hơn.

### 2.3. Quy ước thời gian hệ thống
Các bảng nghiệp vụ chính nên có:
- `created_at`
- `updated_at`
- có thể thêm `deleted_at` nếu dùng soft delete

### 2.4. Quy ước trạng thái
Nhiều bảng nên có:
- `is_active`
- hoặc `status`

### 2.5. Kiểu tiền tệ
- Dùng `DECIMAL(18,2)` để tránh sai số số thực.

### 2.6. Quy ước bảo mật
- Không lưu plaintext password.
- Không lưu đầy đủ thông tin tài khoản nhạy cảm nếu không cần.
- Các trường nhạy cảm nên được masked hoặc rút gọn.

---

## 3. Danh sách bảng đã chốt
Các bảng chính:
1. Users
2. ExpenseCategories
3. BankAccounts
4. Income
5. Expenses
6. Budgets
7. Alerts
8. Debts
9. DebtPayments
10. Groups
11. GroupMembers
12. SharedTransactions

---

# 4. Chi tiết từng bảng

# 4.1. Users

## Vai trò
Lưu thông tin tài khoản người dùng.

## Gợi ý triển khai
Nếu dùng Django, có 2 hướng:
1. dùng `auth_user` mặc định + bảng profile riêng,
2. hoặc tạo custom user model.

Trong tài liệu logic này, ta mô tả bảng **Users** như bảng người dùng thống nhất.

## Cấu trúc đề xuất
| Cột | Kiểu dữ liệu | Null | Key | Mô tả |
|---|---|---:|---|---|
| user_id | BIGINT AUTO_INCREMENT | No | PK | Khóa chính |
| username | VARCHAR(50) | No | UNIQUE | Tên đăng nhập |
| email | VARCHAR(150) | No | UNIQUE | Email người dùng |
| password_hash | VARCHAR(255) | No |  | Mật khẩu đã băm |
| full_name | VARCHAR(120) | No |  | Họ tên |
| phone_number | VARCHAR(20) | Yes |  | Số điện thoại |
| avatar_url | VARCHAR(255) | Yes |  | Ảnh đại diện |
| default_currency | VARCHAR(10) | Yes |  | Ví dụ VND, USD |
| timezone | VARCHAR(50) | Yes |  | Múi giờ người dùng |
| role | ENUM('user','admin') | No |  | Vai trò |
| is_active | BOOLEAN | No |  | Trạng thái tài khoản |
| last_login_at | DATETIME | Yes |  | Lần đăng nhập cuối |
| created_at | DATETIME | No |  | Thời điểm tạo |
| updated_at | DATETIME | No |  | Thời điểm cập nhật |

## Ràng buộc
- `username` unique
- `email` unique
- `role` chỉ nhận `user` hoặc `admin`

## Index đề xuất
- index on `email`
- index on `username`
- index on `role`
- index on `is_active`

---

# 4.2. ExpenseCategories

## Vai trò
Lưu danh mục chi tiêu của user hoặc danh mục mặc định của hệ thống.

## Cấu trúc đề xuất
| Cột | Kiểu dữ liệu | Null | Key | Mô tả |
|---|---|---:|---|---|
| category_id | BIGINT AUTO_INCREMENT | No | PK | Khóa chính |
| user_id | BIGINT | Yes | FK | Null nếu là category hệ thống |
| category_name | VARCHAR(100) | No |  | Tên danh mục |
| description | VARCHAR(255) | Yes |  | Mô tả |
| color_code | VARCHAR(20) | Yes |  | Mã màu UI |
| icon_name | VARCHAR(50) | Yes |  | Tên icon |
| is_default | BOOLEAN | No |  | Category hệ thống hay không |
| is_active | BOOLEAN | No |  | Đang dùng hay không |
| created_at | DATETIME | No |  | Thời điểm tạo |
| updated_at | DATETIME | No |  | Thời điểm cập nhật |

## Khóa ngoại
- `user_id` → `Users.user_id`

## Ràng buộc nghiệp vụ đề xuất
- Nếu `is_default = true` thì `user_id` có thể null.
- Nếu là category cá nhân thì `user_id` bắt buộc có.

## Unique gợi ý
- `(user_id, category_name)` unique cho category cá nhân.

## Index đề xuất
- index on `user_id`
- index on `is_default`
- index on `is_active`

---

# 4.3. BankAccounts

## Vai trò
Lưu tài khoản ngân hàng, ví điện tử hoặc ví tiền mặt của user.

## Cấu trúc đề xuất
| Cột | Kiểu dữ liệu | Null | Key | Mô tả |
|---|---|---:|---|---|
| bank_account_id | BIGINT AUTO_INCREMENT | No | PK | Khóa chính |
| user_id | BIGINT | No | FK | Chủ sở hữu |
| account_name | VARCHAR(100) | No |  | Tên tài khoản |
| account_type | ENUM('bank','cash','e_wallet','other') | No |  | Loại tài khoản |
| provider_name | VARCHAR(100) | Yes |  | Ngân hàng / ví |
| account_number_masked | VARCHAR(30) | Yes |  | Số tài khoản che bớt |
| currency | VARCHAR(10) | No |  | Loại tiền |
| opening_balance | DECIMAL(18,2) | No |  | Số dư ban đầu |
| current_balance | DECIMAL(18,2) | No |  | Số dư hiện tại |
| note | VARCHAR(255) | Yes |  | Ghi chú |
| is_active | BOOLEAN | No |  | Có còn dùng không |
| created_at | DATETIME | No |  | Thời điểm tạo |
| updated_at | DATETIME | No |  | Thời điểm cập nhật |

## Khóa ngoại
- `user_id` → `Users.user_id`

## Index đề xuất
- index on `user_id`
- index on `account_type`
- index on `is_active`

---

# 4.4. Income

## Vai trò
Lưu các khoản thu nhập của người dùng.

## Cấu trúc đề xuất
| Cột | Kiểu dữ liệu | Null | Key | Mô tả |
|---|---|---:|---|---|
| income_id | BIGINT AUTO_INCREMENT | No | PK | Khóa chính |
| user_id | BIGINT | No | FK | Chủ sở hữu |
| bank_account_id | BIGINT | Yes | FK | Tài khoản nhận tiền |
| title | VARCHAR(150) | No |  | Tên giao dịch |
| source_type | ENUM('salary','bonus','gift','freelance','investment','refund','other') | No |  | Loại thu |
| amount | DECIMAL(18,2) | No |  | Số tiền |
| income_date | DATE | No |  | Ngày phát sinh |
| description | VARCHAR(255) | Yes |  | Mô tả |
| note | TEXT | Yes |  | Ghi chú |
| status | ENUM('active','deleted') | No |  | Trạng thái |
| created_at | DATETIME | No |  | Thời điểm tạo |
| updated_at | DATETIME | No |  | Thời điểm cập nhật |

## Khóa ngoại
- `user_id` → `Users.user_id`
- `bank_account_id` → `BankAccounts.bank_account_id`

## Ràng buộc đề xuất
- `amount > 0`
- `income_date` bắt buộc

## Index đề xuất
- index on `user_id`
- index on `income_date`
- index on `bank_account_id`
- index on `source_type`
- composite index `(user_id, income_date)`

---

# 4.5. Expenses

## Vai trò
Lưu các khoản chi tiêu của người dùng.

## Cấu trúc đề xuất
| Cột | Kiểu dữ liệu | Null | Key | Mô tả |
|---|---|---:|---|---|
| expense_id | BIGINT AUTO_INCREMENT | No | PK | Khóa chính |
| user_id | BIGINT | No | FK | Chủ sở hữu |
| category_id | BIGINT | No | FK | Danh mục chi tiêu |
| bank_account_id | BIGINT | Yes | FK | Tài khoản thanh toán |
| amount | DECIMAL(18,2) | No |  | Số tiền |
| expense_date | DATE | No |  | Ngày phát sinh |
| payment_method | ENUM('cash','bank','e_wallet','credit_card','other') | Yes |  | Cách thanh toán |
| description | VARCHAR(255) | Yes |  | Mô tả |
| note | TEXT | Yes |  | Ghi chú |
| status | ENUM('active','deleted') | No |  | Trạng thái |
| created_at | DATETIME | No |  | Thời điểm tạo |
| updated_at | DATETIME | No |  | Thời điểm cập nhật |

## Khóa ngoại
- `user_id` → `Users.user_id`
- `category_id` → `ExpenseCategories.category_id`
- `bank_account_id` → `BankAccounts.bank_account_id`

## Ràng buộc đề xuất
- `amount > 0`
- `expense_date` bắt buộc

## Index đề xuất
- index on `user_id`
- index on `category_id`
- index on `bank_account_id`
- index on `expense_date`
- composite index `(user_id, expense_date)`
- composite index `(user_id, category_id, expense_date)`

---

# 4.6. Budgets

## Vai trò
Lưu thông tin ngân sách theo tháng hoặc theo category.

## Cấu trúc đề xuất
| Cột | Kiểu dữ liệu | Null | Key | Mô tả |
|---|---|---:|---|---|
| budget_id | BIGINT AUTO_INCREMENT | No | PK | Khóa chính |
| user_id | BIGINT | No | FK | Chủ sở hữu |
| budget_name | VARCHAR(120) | No |  | Tên budget |
| budget_scope | ENUM('monthly','category') | No |  | Phạm vi budget |
| category_id | BIGINT | Yes | FK | Chỉ dùng nếu scope=category |
| period_month | TINYINT | No |  | 1..12 |
| period_year | SMALLINT | No |  | Ví dụ 2026 |
| spending_limit | DECIMAL(18,2) | No |  | Hạn mức |
| warning_percent | DECIMAL(5,2) | No |  | Ví dụ 80.00 |
| status | ENUM('active','inactive','closed') | No |  | Trạng thái |
| created_at | DATETIME | No |  | Thời điểm tạo |
| updated_at | DATETIME | No |  | Thời điểm cập nhật |

## Khóa ngoại
- `user_id` → `Users.user_id`
- `category_id` → `ExpenseCategories.category_id`

## Ràng buộc đề xuất
- `period_month BETWEEN 1 AND 12`
- `spending_limit > 0`
- `warning_percent > 0 AND warning_percent <= 100`
- nếu `budget_scope = 'category'` thì `category_id` không được null

## Unique nghiệp vụ gợi ý
- unique `(user_id, budget_scope, category_id, period_month, period_year, status)` ở mức active logic

## Index đề xuất
- index on `user_id`
- index on `category_id`
- index on `(period_year, period_month)`
- composite index `(user_id, period_year, period_month)`

---

# 4.7. Alerts

## Vai trò
Lưu các cảnh báo gửi cho user.

## Cấu trúc đề xuất
| Cột | Kiểu dữ liệu | Null | Key | Mô tả |
|---|---|---:|---|---|
| alert_id | BIGINT AUTO_INCREMENT | No | PK | Khóa chính |
| user_id | BIGINT | No | FK | Người nhận alert |
| alert_type | ENUM('budget_warning','budget_exceeded','debt_overdue','system_info','other') | No |  | Loại cảnh báo |
| severity | ENUM('info','warning','critical') | No |  | Mức độ |
| title | VARCHAR(150) | No |  | Tiêu đề |
| message | TEXT | No |  | Nội dung |
| related_budget_id | BIGINT | Yes | FK | Budget liên quan |
| related_expense_id | BIGINT | Yes | FK | Expense liên quan |
| related_debt_id | BIGINT | Yes | FK | Debt liên quan |
| is_read | BOOLEAN | No |  | Đã đọc hay chưa |
| created_at | DATETIME | No |  | Thời điểm tạo |

## Khóa ngoại
- `user_id` → `Users.user_id`
- `related_budget_id` → `Budgets.budget_id`
- `related_expense_id` → `Expenses.expense_id`
- `related_debt_id` → `Debts.debt_id`

## Index đề xuất
- index on `user_id`
- index on `alert_type`
- index on `is_read`
- index on `created_at`
- composite index `(user_id, is_read, created_at)`

---

# 4.8. Debts

## Vai trò
Lưu khoản nợ của user.

## Cấu trúc đề xuất
| Cột | Kiểu dữ liệu | Null | Key | Mô tả |
|---|---|---:|---|---|
| debt_id | BIGINT AUTO_INCREMENT | No | PK | Khóa chính |
| user_id | BIGINT | No | FK | Chủ sở hữu |
| debt_type | ENUM('i_owe','owed_to_me') | No |  | Mình nợ hay người khác nợ mình |
| counterparty_name | VARCHAR(150) | No |  | Bên liên quan |
| original_amount | DECIMAL(18,2) | No |  | Số tiền gốc |
| remaining_amount | DECIMAL(18,2) | No |  | Còn lại |
| due_date | DATE | Yes |  | Hạn trả |
| status | ENUM('pending','partially_paid','paid','overdue') | No |  | Trạng thái |
| description | VARCHAR(255) | Yes |  | Mô tả |
| note | TEXT | Yes |  | Ghi chú |
| created_at | DATETIME | No |  | Thời điểm tạo |
| updated_at | DATETIME | No |  | Thời điểm cập nhật |
| is_active | BOOLEAN | No |  | Còn theo dõi không |

## Khóa ngoại
- `user_id` → `Users.user_id`

## Ràng buộc đề xuất
- `original_amount > 0`
- `remaining_amount >= 0`

## Index đề xuất
- index on `user_id`
- index on `status`
- index on `due_date`
- composite index `(user_id, status, due_date)`

---

# 4.9. DebtPayments

## Vai trò
Lưu lịch sử thanh toán cho từng khoản nợ.

## Cấu trúc đề xuất
| Cột | Kiểu dữ liệu | Null | Key | Mô tả |
|---|---|---:|---|---|
| debt_payment_id | BIGINT AUTO_INCREMENT | No | PK | Khóa chính |
| debt_id | BIGINT | No | FK | Khoản nợ liên quan |
| bank_account_id | BIGINT | Yes | FK | Tài khoản dùng để thanh toán |
| payment_date | DATE | No |  | Ngày trả |
| amount | DECIMAL(18,2) | No |  | Số tiền trả |
| note | TEXT | Yes |  | Ghi chú |
| created_at | DATETIME | No |  | Thời điểm tạo |

## Khóa ngoại
- `debt_id` → `Debts.debt_id`
- `bank_account_id` → `BankAccounts.bank_account_id`

## Ràng buộc đề xuất
- `amount > 0`

## Index đề xuất
- index on `debt_id`
- index on `payment_date`
- index on `bank_account_id`

---

# 4.10. Groups

## Vai trò
Lưu thông tin nhóm chia sẻ tài chính.

## Cấu trúc đề xuất
| Cột | Kiểu dữ liệu | Null | Key | Mô tả |
|---|---|---:|---|---|
| group_id | BIGINT AUTO_INCREMENT | No | PK | Khóa chính |
| owner_user_id | BIGINT | No | FK | Người tạo nhóm |
| group_name | VARCHAR(120) | No |  | Tên nhóm |
| description | VARCHAR(255) | Yes |  | Mô tả |
| status | ENUM('active','inactive','archived') | No |  | Trạng thái |
| created_at | DATETIME | No |  | Thời điểm tạo |
| updated_at | DATETIME | No |  | Thời điểm cập nhật |

## Khóa ngoại
- `owner_user_id` → `Users.user_id`

## Index đề xuất
- index on `owner_user_id`
- index on `status`

---

# 4.11. GroupMembers

## Vai trò
Lưu thành viên của từng nhóm.

## Cấu trúc đề xuất
| Cột | Kiểu dữ liệu | Null | Key | Mô tả |
|---|---|---:|---|---|
| group_member_id | BIGINT AUTO_INCREMENT | No | PK | Khóa chính |
| group_id | BIGINT | No | FK | Nhóm |
| user_id | BIGINT | No | FK | Thành viên |
| member_role | ENUM('owner','member') | No |  | Vai trò trong nhóm |
| joined_at | DATETIME | No |  | Ngày tham gia |
| status | ENUM('active','left','removed') | No |  | Trạng thái |

## Khóa ngoại
- `group_id` → `Groups.group_id`
- `user_id` → `Users.user_id`

## Unique đề xuất
- unique `(group_id, user_id)`

## Index đề xuất
- index on `group_id`
- index on `user_id`
- index on `status`

---

# 4.12. SharedTransactions

## Vai trò
Liên kết giao dịch cá nhân với nhóm chia sẻ.

## Thiết kế gợi ý
Có nhiều cách thiết kế. Cách đơn giản nhất trong project này là cho phép một bản ghi shared transaction tham chiếu đến **một expense hoặc income** đã tồn tại.

## Cấu trúc đề xuất
| Cột | Kiểu dữ liệu | Null | Key | Mô tả |
|---|---|---:|---|---|
| shared_transaction_id | BIGINT AUTO_INCREMENT | No | PK | Khóa chính |
| group_id | BIGINT | No | FK | Nhóm được chia sẻ |
| shared_by_user_id | BIGINT | No | FK | Ai chia sẻ giao dịch |
| expense_id | BIGINT | Yes | FK | Giao dịch expense được chia sẻ |
| income_id | BIGINT | Yes | FK | Giao dịch income được chia sẻ |
| visibility_status | ENUM('visible','hidden') | No |  | Trạng thái hiển thị |
| note | VARCHAR(255) | Yes |  | Ghi chú |
| created_at | DATETIME | No |  | Thời điểm tạo |

## Khóa ngoại
- `group_id` → `Groups.group_id`
- `shared_by_user_id` → `Users.user_id`
- `expense_id` → `Expenses.expense_id`
- `income_id` → `Income.income_id`

## Ràng buộc nghiệp vụ
- Ít nhất một trong hai `expense_id` hoặc `income_id` phải khác null.
- Không được để cả hai cùng null.
- Chỉ member của group mới tạo được bản ghi này.

## Index đề xuất
- index on `group_id`
- index on `shared_by_user_id`
- index on `expense_id`
- index on `income_id`

---

## 5. Quan hệ chính giữa các bảng

### 5.1. User và dữ liệu cá nhân
- Users 1 — N ExpenseCategories
- Users 1 — N BankAccounts
- Users 1 — N Income
- Users 1 — N Expenses
- Users 1 — N Budgets
- Users 1 — N Alerts
- Users 1 — N Debts
- Users 1 — N Groups (owner)
- Users 1 — N GroupMembers

### 5.2. Category và Expense
- ExpenseCategories 1 — N Expenses
- ExpenseCategories 1 — N Budgets (khi budget theo category)

### 5.3. BankAccount và Transaction
- BankAccounts 1 — N Income
- BankAccounts 1 — N Expenses
- BankAccounts 1 — N DebtPayments

### 5.4. Budget và Alerts
- Budgets 1 — N Alerts

### 5.5. Debt và DebtPayments
- Debts 1 — N DebtPayments
- Debts 1 — N Alerts (nếu cảnh báo overdue)

### 5.6. Groups và SharedTransactions
- Groups 1 — N GroupMembers
- Groups 1 — N SharedTransactions

---

## 6. Trường hệ thống đã chốt
Các trường hệ thống quan trọng cần xuất hiện ở các bảng chính:
- `created_at`
- `updated_at`
- `is_active`
- `status`

### Gợi ý áp dụng
- `created_at`, `updated_at`: gần như tất cả bảng chính.
- `is_active`: Users, ExpenseCategories, BankAccounts, Debts.
- `status`: Income, Expenses, Budgets, Debts, Groups, GroupMembers.

---

## 7. Index strategy đề xuất
Vì đề bài yêu cầu có **indexes**, nên các index cần được thiết kế theo đúng nhu cầu truy vấn.

### 7.1. Index bắt buộc nên có
- Users(email)
- Users(username)
- Income(user_id, income_date)
- Expenses(user_id, expense_date)
- Expenses(user_id, category_id, expense_date)
- BankAccounts(user_id)
- Budgets(user_id, period_year, period_month)
- Alerts(user_id, is_read, created_at)
- Debts(user_id, status, due_date)
- GroupMembers(group_id, user_id)

### 7.2. Lợi ích
- Tăng tốc lọc theo user.
- Tăng tốc dashboard và reports.
- Tăng tốc truy vấn budget tháng.
- Tăng tốc truy vấn alert chưa đọc.
- Tăng tốc kiểm tra membership trong sharing.

---

## 8. View / Procedure / Function / Trigger gợi ý
Đề bài yêu cầu sử dụng các đối tượng CSDL nâng cao, nên ngay từ schema logic cần định hướng sẵn.

# 8.1. Views gợi ý

### View 1 — vw_monthly_expense_summary
Tổng hợp chi tiêu theo user, tháng, năm, category.

### View 2 — vw_budget_usage
Hiển thị budget limit, amount used, remaining, usage percent.

### View 3 — vw_dashboard_snapshot
Tổng hợp dữ liệu nhanh cho dashboard của từng user.

---

# 8.2. Stored Procedures gợi ý

### Procedure 1 — sp_create_expense
Mục tiêu:
- thêm expense,
- cập nhật balance,
- kiểm tra budget,
- sinh alert nếu cần.

### Procedure 2 — sp_create_income
Mục tiêu:
- thêm income,
- cập nhật balance.

### Procedure 3 — sp_monthly_summary
Mục tiêu:
- trả summary theo user/tháng/năm.

---

# 8.3. Functions gợi ý

### Function 1 — fn_budget_usage_percent(budget_id)
Trả về phần trăm ngân sách đã dùng.

### Function 2 — fn_remaining_budget(budget_id)
Trả về hạn mức còn lại.

### Function 3 — fn_debt_remaining(debt_id)
Trả về số nợ còn lại.

---

# 8.4. Triggers gợi ý

### Trigger 1 — after insert on Income
- tăng `current_balance` của `BankAccounts`

### Trigger 2 — after insert on Expenses
- giảm `current_balance` của `BankAccounts`

### Trigger 3 — after insert/update on DebtPayments
- cập nhật `remaining_amount` và `status` của `Debts`

### Trigger 4 — after insert/update on Expenses
- có thể gọi logic check budget hoặc đánh dấu dữ liệu cần cảnh báo

---

## 9. Ghi chú thiết kế với Django

### 9.1. Với bảng Users
Khuyến nghị thực tế khi code Django:
- dùng custom user model hoặc Django auth mặc định,
- sau đó map logic tài liệu vào model implementation.

### 9.2. Với soft delete
Có thể dùng:
- `status = 'deleted'`
- hoặc `is_active = false`
- hoặc `deleted_at`

### 9.3. Với shared transactions
Nếu code phức tạp, có thể chỉ hỗ trợ chia sẻ **expenses** ở phase đầu để đơn giản hóa schema.

---

## 10. Kết luận
Lược đồ quan hệ này đáp ứng tốt các mục tiêu của project vì đã bao phủ:
- người dùng,
- giao dịch thu,
- giao dịch chi,
- danh mục,
- tài khoản tiền,
- ngân sách,
- cảnh báo,
- nợ,
- nhóm chia sẻ.

Ngoài ra, schema này còn phù hợp với yêu cầu học thuật vì có thể mở rộng để cài đặt:
- PK/FK,
- index,
- view,
- procedure,
- function,
- trigger,
- security,
- backup và recovery.
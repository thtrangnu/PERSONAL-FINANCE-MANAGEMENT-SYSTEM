# Relational Schema Design

## 1. Mục đích tài liệu
Tài liệu này mô tả lược đồ quan hệ logic của hệ thống **NUFI**, bao gồm:
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
- Dùng danh từ số nhiều, viết theo `snake_case` khi triển khai SQL.
- Các bảng chính đã chốt:
  - `users`
  - `categories`
  - `bank_accounts`
  - `incomes`
  - `expenses`
  - `budgets`
  - `alerts`
  - `debts`
  - `debt_payments`
  - `groups`
  - `group_members`
  - `shared_transactions`

### 2.2. Quy ước khóa chính
- Mỗi bảng dùng khóa chính dạng `BIGINT UNSIGNED AUTO_INCREMENT`.
- Tên khóa chính theo đúng entity:
  - `user_id`
  - `category_id`
  - `income_id`
  - `expense_id`
  - ...

### 2.3. Quy ước thời gian hệ thống
Các bảng nghiệp vụ chính nên có:
- `created_at`
- `updated_at`

Ngoài ra một số bảng có thêm ngày nghiệp vụ riêng:
- `income_date`
- `expense_date`
- `payment_date`
- `due_date`
- `joined_at`

### 2.4. Quy ước trạng thái
- Dùng `is_active` cho trạng thái bật/tắt đơn giản.
- Dùng `status` cho trạng thái nghiệp vụ nhiều nhánh.

### 2.5. Kiểu tiền tệ
- Dùng `DECIMAL(18,2)` cho toàn bộ giá trị tiền để tránh sai số số thực.

### 2.6. Quy ước bảo mật
- Không lưu plaintext password.
- Không lưu số tài khoản đầy đủ nếu không cần.
- Chỉ lưu `account_number_masked` khi phù hợp với nhu cầu demo/học tập.

### 2.7. Quy ước ràng buộc nghiệp vụ
- Các ràng buộc đơn giản như `amount > 0`, `period_month BETWEEN 1 AND 12` có thể đặt bằng `CHECK`.
- Các rule chéo nhiều cột hoặc phụ thuộc loại bản ghi nên ghi rõ trong thiết kế và enforce bằng:
  - backend,
  - stored procedure,
  - trigger.

Ví dụ:
- `categories.is_default` đi cùng `user_id`,
- `budgets.budget_scope` đi cùng `category_id`,
- `shared_transactions.expense_id` / `income_id`,
- `alerts` chỉ nên tham chiếu một đối tượng liên quan tại một thời điểm.

---

## 3. Danh sách bảng đã chốt
Các bảng chính:
1. `users`
2. `categories`
3. `bank_accounts`
4. `incomes`
5. `expenses`
6. `budgets`
7. `alerts`
8. `debts`
9. `debt_payments`
10. `groups`
11. `group_members`
12. `shared_transactions`

---

# 4. Chi tiết từng bảng

# 4.1. `users`

## Vai trò
Lưu thông tin tài khoản người dùng.

## Cấu trúc đề xuất
| Cột | Kiểu dữ liệu | Null | Key | Mô tả |
|---|---|---:|---|---|
| user_id | BIGINT UNSIGNED AUTO_INCREMENT | No | PK | Khóa chính |
| username | VARCHAR(50) | No | UNIQUE | Tên đăng nhập |
| email | VARCHAR(150) | No | UNIQUE | Email người dùng |
| password_hash | VARCHAR(255) | No |  | Mật khẩu đã băm |
| full_name | VARCHAR(120) | No |  | Họ tên |
| phone_number | VARCHAR(20) | Yes |  | Số điện thoại |
| avatar_url | VARCHAR(255) | Yes |  | Ảnh đại diện |
| default_currency | VARCHAR(10) | Yes |  | Ví dụ `VND`, `USD` |
| timezone | VARCHAR(50) | Yes |  | Múi giờ người dùng |
| role | ENUM('user','admin') | No |  | Vai trò |
| is_active | BOOLEAN | No |  | Trạng thái tài khoản |
| last_login_at | DATETIME | Yes |  | Lần đăng nhập cuối |
| created_at | DATETIME | No |  | Thời điểm tạo |
| updated_at | DATETIME | No |  | Thời điểm cập nhật |

## Index đề xuất
- unique `username`
- unique `email`
- index `role`
- index `is_active`

---

# 4.2. `categories`

## Vai trò
Lưu danh mục dùng chung cho:
- thu nhập,
- chi tiêu,
- hoặc cả hai.

## Cấu trúc đề xuất
| Cột | Kiểu dữ liệu | Null | Key | Mô tả |
|---|---|---:|---|---|
| category_id | BIGINT UNSIGNED AUTO_INCREMENT | No | PK | Khóa chính |
| user_id | BIGINT UNSIGNED | Yes | FK | Null nếu là category hệ thống |
| category_name | VARCHAR(100) | No |  | Tên danh mục |
| category_type | ENUM('income','expense','both') | No |  | Loại danh mục |
| description | VARCHAR(255) | Yes |  | Mô tả |
| color_code | VARCHAR(20) | Yes |  | Mã màu UI |
| icon_name | VARCHAR(50) | Yes |  | Tên icon |
| is_default | BOOLEAN | No |  | Category hệ thống hay không |
| is_active | BOOLEAN | No |  | Đang dùng hay không |
| created_at | DATETIME | No |  | Thời điểm tạo |
| updated_at | DATETIME | No |  | Thời điểm cập nhật |

## Khóa ngoại
- `user_id` → `users.user_id`

## Ràng buộc nghiệp vụ đề xuất
- Nếu `is_default = true` thì `user_id` nên là `NULL`.
- Nếu là category cá nhân thì `user_id` phải có giá trị.
- Nếu dùng cho `incomes`, category nên có `category_type = 'income'` hoặc `'both'`.
- Nếu dùng cho `expenses` hoặc `budgets`, category nên có `category_type = 'expense'` hoặc `'both'`.

## Unique gợi ý
- unique `(user_id, category_name)` cho category cá nhân.
- category hệ thống nên được seed và kiểm soát bởi admin/backend.

## Index đề xuất
- index `user_id`
- index `category_type`
- index `is_default`
- index `is_active`

---

# 4.3. `bank_accounts`

## Vai trò
Lưu tài khoản ngân hàng, ví điện tử hoặc ví tiền mặt của user.

## Cấu trúc đề xuất
| Cột | Kiểu dữ liệu | Null | Key | Mô tả |
|---|---|---:|---|---|
| bank_account_id | BIGINT UNSIGNED AUTO_INCREMENT | No | PK | Khóa chính |
| user_id | BIGINT UNSIGNED | No | FK | Chủ sở hữu |
| account_name | VARCHAR(100) | No |  | Tên tài khoản |
| account_type | ENUM('bank','cash','e_wallet','other') | No |  | Loại tài khoản |
| provider_name | VARCHAR(100) | Yes |  | Ngân hàng / ví |
| account_number_masked | VARCHAR(30) | Yes |  | Số tài khoản đã che bớt |
| currency | VARCHAR(10) | No |  | Loại tiền |
| opening_balance | DECIMAL(18,2) | No |  | Số dư ban đầu |
| current_balance | DECIMAL(18,2) | No |  | Số dư hiện tại |
| note | VARCHAR(255) | Yes |  | Ghi chú |
| is_active | BOOLEAN | No |  | Có còn dùng không |
| created_at | DATETIME | No |  | Thời điểm tạo |
| updated_at | DATETIME | No |  | Thời điểm cập nhật |

## Khóa ngoại
- `user_id` → `users.user_id`

## Index đề xuất
- index `user_id`
- index `account_type`
- index `is_active`

---

# 4.4. `incomes`

## Vai trò
Lưu các khoản thu nhập của người dùng.

## Cấu trúc đề xuất
| Cột | Kiểu dữ liệu | Null | Key | Mô tả |
|---|---|---:|---|---|
| income_id | BIGINT UNSIGNED AUTO_INCREMENT | No | PK | Khóa chính |
| user_id | BIGINT UNSIGNED | No | FK | Chủ sở hữu |
| category_id | BIGINT UNSIGNED | No | FK | Danh mục thu nhập |
| bank_account_id | BIGINT UNSIGNED | Yes | FK | Tài khoản nhận tiền |
| title | VARCHAR(150) | No |  | Tên giao dịch |
| amount | DECIMAL(18,2) | No |  | Số tiền |
| income_date | DATE | No |  | Ngày phát sinh |
| description | VARCHAR(255) | Yes |  | Mô tả |
| note | TEXT | Yes |  | Ghi chú |
| status | ENUM('active','deleted') | No |  | Trạng thái |
| created_at | DATETIME | No |  | Thời điểm tạo |
| updated_at | DATETIME | No |  | Thời điểm cập nhật |

## Khóa ngoại
- `user_id` → `users.user_id`
- `category_id` → `categories.category_id`
- `bank_account_id` → `bank_accounts.bank_account_id`

## Ràng buộc đề xuất
- `amount > 0`
- `income_date` bắt buộc

## Index đề xuất
- index `user_id`
- index `category_id`
- index `income_date`
- index `bank_account_id`
- composite index `(user_id, income_date)`

---

# 4.5. `expenses`

## Vai trò
Lưu các khoản chi tiêu của người dùng.

## Cấu trúc đề xuất
| Cột | Kiểu dữ liệu | Null | Key | Mô tả |
|---|---|---:|---|---|
| expense_id | BIGINT UNSIGNED AUTO_INCREMENT | No | PK | Khóa chính |
| user_id | BIGINT UNSIGNED | No | FK | Chủ sở hữu |
| category_id | BIGINT UNSIGNED | No | FK | Danh mục chi tiêu |
| bank_account_id | BIGINT UNSIGNED | Yes | FK | Tài khoản thanh toán |
| amount | DECIMAL(18,2) | No |  | Số tiền |
| expense_date | DATE | No |  | Ngày phát sinh |
| payment_method | ENUM('cash','bank','e_wallet','credit_card','other') | Yes |  | Cách thanh toán |
| description | VARCHAR(255) | Yes |  | Mô tả |
| note | TEXT | Yes |  | Ghi chú |
| status | ENUM('active','deleted') | No |  | Trạng thái |
| created_at | DATETIME | No |  | Thời điểm tạo |
| updated_at | DATETIME | No |  | Thời điểm cập nhật |

## Khóa ngoại
- `user_id` → `users.user_id`
- `category_id` → `categories.category_id`
- `bank_account_id` → `bank_accounts.bank_account_id`

## Ràng buộc đề xuất
- `amount > 0`
- `expense_date` bắt buộc

## Index đề xuất
- index `user_id`
- index `category_id`
- index `bank_account_id`
- index `expense_date`
- composite index `(user_id, expense_date)`
- composite index `(user_id, category_id, expense_date)`

---

# 4.6. `budgets`

## Vai trò
Lưu thông tin ngân sách theo tháng ở 2 dạng:
- ngân sách tổng tháng,
- ngân sách theo category.

## Cấu trúc đề xuất
| Cột | Kiểu dữ liệu | Null | Key | Mô tả |
|---|---|---:|---|---|
| budget_id | BIGINT UNSIGNED AUTO_INCREMENT | No | PK | Khóa chính |
| user_id | BIGINT UNSIGNED | No | FK | Chủ sở hữu |
| budget_name | VARCHAR(120) | No |  | Tên budget |
| budget_scope | ENUM('overall','category') | No |  | Phạm vi budget |
| category_id | BIGINT UNSIGNED | Yes | FK | Chỉ dùng nếu scope=`category` |
| period_month | TINYINT UNSIGNED | No |  | 1..12 |
| period_year | SMALLINT UNSIGNED | No |  | Ví dụ 2026 |
| spending_limit | DECIMAL(18,2) | No |  | Hạn mức |
| warning_percent | DECIMAL(5,2) | No |  | Ví dụ 80.00 |
| status | ENUM('active','inactive','closed') | No |  | Trạng thái |
| created_at | DATETIME | No |  | Thời điểm tạo |
| updated_at | DATETIME | No |  | Thời điểm cập nhật |

## Khóa ngoại
- `user_id` → `users.user_id`
- `category_id` → `categories.category_id`

## Ràng buộc đề xuất
- `period_month BETWEEN 1 AND 12`
- `spending_limit > 0`
- `warning_percent > 0 AND warning_percent <= 100`
- nếu `budget_scope = 'category'` thì `category_id` không được null
- nếu `budget_scope = 'overall'` thì `category_id` nên là null

## Unique nghiệp vụ gợi ý
- không nên có 2 budget `active` trùng logic cho cùng:
  - user,
  - scope,
  - category,
  - tháng,
  - năm.

## Index đề xuất
- index `user_id`
- index `category_id`
- index `(period_year, period_month)`
- composite index `(user_id, period_year, period_month)`

---

# 4.7. `alerts`

## Vai trò
Lưu các cảnh báo gửi cho user.

## Cấu trúc đề xuất
| Cột | Kiểu dữ liệu | Null | Key | Mô tả |
|---|---|---:|---|---|
| alert_id | BIGINT UNSIGNED AUTO_INCREMENT | No | PK | Khóa chính |
| user_id | BIGINT UNSIGNED | No | FK | Người nhận alert |
| alert_type | ENUM('budget_warning','budget_exceeded','debt_overdue','system_info','other') | No |  | Loại cảnh báo |
| severity | ENUM('info','warning','critical') | No |  | Mức độ |
| title | VARCHAR(150) | No |  | Tiêu đề |
| message | TEXT | No |  | Nội dung |
| related_budget_id | BIGINT UNSIGNED | Yes | FK | Budget liên quan |
| related_expense_id | BIGINT UNSIGNED | Yes | FK | Expense liên quan |
| related_debt_id | BIGINT UNSIGNED | Yes | FK | Debt liên quan |
| is_read | BOOLEAN | No |  | Đã đọc hay chưa |
| created_at | DATETIME | No |  | Thời điểm tạo |

## Khóa ngoại
- `user_id` → `users.user_id`
- `related_budget_id` → `budgets.budget_id`
- `related_expense_id` → `expenses.expense_id`
- `related_debt_id` → `debts.debt_id`

## Quy ước nghiệp vụ cần chốt
- alert loại budget chỉ nên dùng `related_budget_id`
- alert loại debt chỉ nên dùng `related_debt_id`
- một alert không nên đồng thời tham chiếu nhiều đối tượng liên quan

## Index đề xuất
- index `user_id`
- index `alert_type`
- index `is_read`
- index `created_at`
- composite index `(user_id, is_read, created_at)`

---

# 4.8. `debts`

## Vai trò
Lưu khoản nợ của user.

## Cấu trúc đề xuất
| Cột | Kiểu dữ liệu | Null | Key | Mô tả |
|---|---|---:|---|---|
| debt_id | BIGINT UNSIGNED AUTO_INCREMENT | No | PK | Khóa chính |
| user_id | BIGINT UNSIGNED | No | FK | Chủ sở hữu |
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
- `user_id` → `users.user_id`

## Ràng buộc đề xuất
- `original_amount > 0`
- `remaining_amount >= 0`
- `remaining_amount <= original_amount`

## Index đề xuất
- index `user_id`
- index `status`
- index `due_date`
- composite index `(user_id, status, due_date)`

---

# 4.9. `debt_payments`

## Vai trò
Lưu lịch sử thanh toán cho từng khoản nợ.

## Cấu trúc đề xuất
| Cột | Kiểu dữ liệu | Null | Key | Mô tả |
|---|---|---:|---|---|
| debt_payment_id | BIGINT UNSIGNED AUTO_INCREMENT | No | PK | Khóa chính |
| debt_id | BIGINT UNSIGNED | No | FK | Khoản nợ liên quan |
| bank_account_id | BIGINT UNSIGNED | Yes | FK | Tài khoản dùng để thanh toán |
| payment_date | DATE | No |  | Ngày trả |
| amount | DECIMAL(18,2) | No |  | Số tiền trả |
| note | TEXT | Yes |  | Ghi chú |
| created_at | DATETIME | No |  | Thời điểm tạo |

## Khóa ngoại
- `debt_id` → `debts.debt_id`
- `bank_account_id` → `bank_accounts.bank_account_id`

## Ràng buộc đề xuất
- `amount > 0`

## Index đề xuất
- index `debt_id`
- index `payment_date`
- index `bank_account_id`

---

# 4.10. `groups`

## Vai trò
Lưu thông tin nhóm chia sẻ tài chính.

## Cấu trúc đề xuất
| Cột | Kiểu dữ liệu | Null | Key | Mô tả |
|---|---|---:|---|---|
| group_id | BIGINT UNSIGNED AUTO_INCREMENT | No | PK | Khóa chính |
| owner_user_id | BIGINT UNSIGNED | No | FK | Người tạo nhóm |
| group_name | VARCHAR(120) | No |  | Tên nhóm |
| description | VARCHAR(255) | Yes |  | Mô tả |
| status | ENUM('active','inactive','archived') | No |  | Trạng thái |
| created_at | DATETIME | No |  | Thời điểm tạo |
| updated_at | DATETIME | No |  | Thời điểm cập nhật |

## Khóa ngoại
- `owner_user_id` → `users.user_id`

## Index đề xuất
- index `owner_user_id`
- index `status`

---

# 4.11. `group_members`

## Vai trò
Lưu thành viên của từng nhóm.

## Cấu trúc đề xuất
| Cột | Kiểu dữ liệu | Null | Key | Mô tả |
|---|---|---:|---|---|
| group_member_id | BIGINT UNSIGNED AUTO_INCREMENT | No | PK | Khóa chính |
| group_id | BIGINT UNSIGNED | No | FK | Nhóm |
| user_id | BIGINT UNSIGNED | No | FK | Thành viên |
| member_role | ENUM('owner','member') | No |  | Vai trò trong nhóm |
| joined_at | DATETIME | No |  | Ngày tham gia |
| status | ENUM('active','left','removed') | No |  | Trạng thái |

## Khóa ngoại
- `group_id` → `groups.group_id`
- `user_id` → `users.user_id`

## Unique đề xuất
- unique `(group_id, user_id)`

## Index đề xuất
- index `group_id`
- index `user_id`
- index `status`

---

# 4.12. `shared_transactions`

## Vai trò
Liên kết giao dịch cá nhân với nhóm chia sẻ.

## Thiết kế gợi ý
Cách đơn giản nhất trong project này là cho phép một bản ghi `shared_transactions` tham chiếu đến **một expense hoặc một income** đã tồn tại.

## Cấu trúc đề xuất
| Cột | Kiểu dữ liệu | Null | Key | Mô tả |
|---|---|---:|---|---|
| shared_transaction_id | BIGINT UNSIGNED AUTO_INCREMENT | No | PK | Khóa chính |
| group_id | BIGINT UNSIGNED | No | FK | Nhóm được chia sẻ |
| shared_by_user_id | BIGINT UNSIGNED | No | FK | Ai chia sẻ giao dịch |
| expense_id | BIGINT UNSIGNED | Yes | FK | Giao dịch expense được chia sẻ |
| income_id | BIGINT UNSIGNED | Yes | FK | Giao dịch income được chia sẻ |
| visibility_status | ENUM('visible','hidden') | No |  | Trạng thái hiển thị |
| note | VARCHAR(255) | Yes |  | Ghi chú |
| created_at | DATETIME | No |  | Thời điểm tạo |

## Khóa ngoại
- `group_id` → `groups.group_id`
- `shared_by_user_id` → `users.user_id`
- `(group_id, shared_by_user_id)` → `group_members(group_id, user_id)`
- `expense_id` → `expenses.expense_id`
- `income_id` → `incomes.income_id`

## Ràng buộc nghiệp vụ
- Chỉ một trong hai `expense_id` hoặc `income_id` được có giá trị.
- Không được để cả hai cùng null.
- Chỉ member của group mới tạo được bản ghi này.

## Index đề xuất
- index `group_id`
- index `shared_by_user_id`
- index `expense_id`
- index `income_id`

---

## 5. Quan hệ chính giữa các bảng

### 5.1. User và dữ liệu cá nhân
- `users` 1 — N `categories`
- `users` 1 — N `bank_accounts`
- `users` 1 — N `incomes`
- `users` 1 — N `expenses`
- `users` 1 — N `budgets`
- `users` 1 — N `alerts`
- `users` 1 — N `debts`
- `users` 1 — N `groups` (owner)
- `users` 1 — N `group_members`

### 5.2. Category và Transaction
- `categories` 1 — N `incomes`
- `categories` 1 — N `expenses`
- `categories` 1 — N `budgets` (khi budget theo category)

### 5.3. BankAccount và Transaction
- `bank_accounts` 1 — N `incomes`
- `bank_accounts` 1 — N `expenses`
- `bank_accounts` 1 — N `debt_payments`

### 5.4. Budget và Alerts
- `budgets` 1 — N `alerts`

### 5.5. Debt và DebtPayments
- `debts` 1 — N `debt_payments`
- `debts` 1 — N `alerts`

### 5.6. Groups và Sharing
- `groups` 1 — N `group_members`
- `groups` 1 — N `shared_transactions`

---

## 6. Trường hệ thống đã chốt
Các trường hệ thống quan trọng cần xuất hiện ở các bảng chính:
- `created_at`
- `updated_at`
- `is_active`
- `status`

### Gợi ý áp dụng
- `created_at`, `updated_at`: gần như tất cả bảng chính.
- `is_active`: `users`, `categories`, `bank_accounts`, `debts`.
- `status`: `incomes`, `expenses`, `budgets`, `debts`, `groups`, `group_members`.

---

## 7. Index strategy đề xuất
Vì đề bài yêu cầu có **indexes**, nên các index cần được thiết kế theo đúng nhu cầu truy vấn.

### 7.1. Index bắt buộc nên có
- `users(email)`
- `users(username)`
- `categories(user_id)`
- `categories(category_type)`
- `incomes(user_id, income_date)`
- `expenses(user_id, expense_date)`
- `expenses(user_id, category_id, expense_date)`
- `bank_accounts(user_id)`
- `budgets(user_id, period_year, period_month)`
- `alerts(user_id, is_read, created_at)`
- `debts(user_id, status, due_date)`
- `group_members(group_id, user_id)`

### 7.2. Lợi ích
- Tăng tốc lọc theo user.
- Tăng tốc dashboard và reports.
- Tăng tốc truy vấn budget tháng.
- Tăng tốc truy vấn alert chưa đọc.
- Tăng tốc kiểm tra membership trong sharing.

---

## 8. View / Procedure / Function / Trigger gợi ý

### 8.1. Views gợi ý
**View 1 — `vw_monthly_expense_summary`**
- Tổng hợp chi tiêu theo user, tháng, năm, category.

**View 2 — `vw_budget_usage`**
- Hiển thị budget limit, amount used, remaining, usage percent.

**View 3 — `vw_dashboard_snapshot`**
- Tổng hợp dữ liệu nhanh cho dashboard của từng user.

### 8.2. Stored Procedures gợi ý
**Procedure 1 — `sp_create_expense`**
- thêm expense,
- cập nhật balance,
- kiểm tra budget,
- sinh alert nếu cần.

**Procedure 2 — `sp_create_income`**
- thêm income,
- cập nhật balance.

**Procedure 3 — `sp_monthly_summary`**
- trả summary theo user/tháng/năm.

### 8.3. Functions gợi ý
**Function 1 — `fn_budget_usage_percent(budget_id)`**
- Trả về phần trăm ngân sách đã dùng.

**Function 2 — `fn_remaining_budget(budget_id)`**
- Trả về hạn mức còn lại.

**Function 3 — `fn_debt_remaining(debt_id)`**
- Trả về số nợ còn lại.

### 8.4. Triggers gợi ý
**Trigger 1 — `before insert/update on categories`**
- kiểm tra quan hệ giữa `is_default`, `user_id`, `category_type`.

**Trigger 2 — `after insert on incomes`**
- tăng `current_balance` của `bank_accounts`.

**Trigger 3 — `after insert on expenses`**
- giảm `current_balance` của `bank_accounts`.

**Trigger 4 — `before insert/update on budgets`**
- kiểm tra logic `budget_scope` và `category_id`.

**Trigger 5 — `before insert/update on shared_transactions`**
- kiểm tra đúng một trong hai `expense_id` hoặc `income_id`.

**Trigger 6 — `after insert/update on debt_payments`**
- cập nhật `remaining_amount` và `status` của `debts`.

---

## 9. Ghi chú thiết kế với Django

### 9.1. Với bảng `users`
Khuyến nghị thực tế khi code Django:
- dùng custom user model hoặc Django auth mặc định,
- sau đó map logic tài liệu vào model implementation.

### 9.2. Với soft delete
Có thể dùng:
- `status = 'deleted'`
- hoặc `is_active = false`

### 9.3. Với `categories`
- Có thể tạo sẵn category hệ thống bằng seed data.
- Có thể kiểm tra `category_type` ở serializer/service layer trước khi ghi DB.

### 9.4. Với `shared_transactions`
- Nếu phase đầu muốn đơn giản hơn, có thể chỉ hỗ trợ chia sẻ `expenses`.
- Khi đó `income_id` có thể để mở rộng ở phase sau.

---

## 10. Kết luận
Lược đồ quan hệ này đáp ứng tốt các mục tiêu của project vì đã bao phủ:
- người dùng,
- giao dịch thu,
- giao dịch chi,
- danh mục dùng chung cho income/expense,
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

# Business Modules Specification

## 1. Mục đích tài liệu
Tài liệu này chia hệ thống thành các module nghiệp vụ cụ thể để:
- dễ phân công công việc,
- dễ thiết kế schema và API,
- dễ code theo app trong Django,
- dễ xác định đâu là phần làm trước, đâu là phần mở rộng làm sau.

Các module đã chốt:
- accounts
- income
- expenses
- categories
- bank_accounts
- budgets
- alerts
- debts
- sharing
- reports
- exports
- dashboard

---

## 2. Nguyên tắc chia module
Mỗi module cần xác định rõ:
1. **Mục đích module**
2. **Chức năng chính**
3. **Dữ liệu mà module quản lý**
4. **Module nào phụ thuộc module nào**
5. **Có thuộc MVP hay phase sau không**

---

# 3. Mô tả chi tiết từng module

# 3.1. accounts

## Mục đích
Quản lý người dùng, xác thực và hồ sơ cá nhân.

## Chức năng chính
- Đăng ký.
- Đăng nhập.
- Đăng xuất.
- Xem hồ sơ cá nhân.
- Cập nhật hồ sơ.
- Đổi mật khẩu.
- Quản lý trạng thái tài khoản.
- Mở rộng: Google login.

## Dữ liệu chính
- Users
- UserProfile (nếu tách riêng)
- Login logs (nếu có)

## Đầu vào điển hình
- email/username
- password
- profile fields

## Đầu ra điển hình
- session/token
- profile summary
- trạng thái xác thực

## Phụ thuộc
- Không phụ thuộc module nghiệp vụ khác.
- Là module nền tảng cho toàn hệ thống.

## Mức ưu tiên
**Bắt buộc làm trong bản 1.**

---

# 3.2. income

## Mục đích
Quản lý các khoản thu nhập của người dùng.

## Chức năng chính
- Tạo khoản income.
- Sửa income.
- Xóa income.
- Xem danh sách income.
- Lọc theo thời gian.
- Lọc theo nguồn thu.
- Lọc theo bank account.

## Dữ liệu chính
- Income
- Có liên quan đến Users
- Có thể liên quan BankAccounts

## Thuộc tính chính của income
- user_id
- title
- amount
- income_date
- source_type
- bank_account_id
- description
- note
- created_at
- updated_at

## Luồng nghiệp vụ chính
1. User tạo income.
2. Hệ thống validate dữ liệu.
3. Ghi bản ghi vào bảng income.
4. Nếu income gắn với bank account thì tăng balance.
5. Giao dịch xuất hiện trong dashboard/reports.

## Phụ thuộc
- accounts
- bank_accounts (nếu gắn tài khoản)
- reports

## Mức ưu tiên
**Bắt buộc làm trong bản 1.**

---

# 3.3. expenses

## Mục đích
Quản lý các khoản chi tiêu của người dùng.

## Chức năng chính
- Tạo expense.
- Sửa expense.
- Xóa expense.
- Xem danh sách expense.
- Lọc theo category.
- Lọc theo thời gian.
- Lọc theo bank account.
- Theo dõi transaction history.

## Dữ liệu chính
- Expenses
- Users
- ExpenseCategories
- BankAccounts

## Thuộc tính chính của expense
- user_id
- category_id
- amount
- expense_date
- description
- bank_account_id
- payment_method
- note
- created_at
- updated_at

## Luồng nghiệp vụ chính
1. User nhập expense.
2. Hệ thống validate amount/category/user ownership.
3. Nếu có bank account, hệ thống trừ balance.
4. Hệ thống kiểm tra budget.
5. Nếu vượt ngưỡng, sinh alert.
6. Expense xuất hiện trong dashboard/reports.

## Phụ thuộc
- accounts
- categories
- bank_accounts
- budgets
- alerts
- reports

## Mức ưu tiên
**Bắt buộc làm trong bản 1.**

---

# 3.4. categories

## Mục đích
Quản lý danh mục phân loại chi tiêu.

## Chức năng chính
- Tạo category cá nhân.
- Sửa category.
- Vô hiệu hóa category.
- Xem danh sách category.
- Hỗ trợ category hệ thống mặc định.

## Dữ liệu chính
- ExpenseCategories

## Thuộc tính chính
- user_id (nullable nếu là default/system category)
- category_name
- description
- color
- icon
- is_default
- is_active
- created_at
- updated_at

## Vai trò trong hệ thống
- Giúp chuẩn hóa phân loại chi tiêu.
- Là đầu vào cho reports.
- Là nền cho category budget.

## Phụ thuộc
- accounts
- expenses
- budgets
- reports

## Mức ưu tiên
**Bắt buộc làm trong bản 1.**

---

# 3.5. bank_accounts

## Mục đích
Theo dõi nơi giữ tiền của người dùng: tài khoản ngân hàng, ví điện tử, tiền mặt.

## Chức năng chính
- Tạo bank account.
- Sửa bank account.
- Xem balance.
- Xem transaction liên quan.
- Kích hoạt/vô hiệu hóa tài khoản.

## Dữ liệu chính
- BankAccounts

## Thuộc tính chính
- user_id
- account_name
- account_type
- provider_name
- account_number_masked
- currency
- opening_balance
- current_balance
- is_active
- created_at
- updated_at

## Luồng nghiệp vụ chính
1. User tạo account.
2. Income/expense có thể tham chiếu account này.
3. Balance được tăng/giảm theo giao dịch.
4. Dashboard lấy dữ liệu tổng balance từ module này.

## Phụ thuộc
- accounts
- income
- expenses
- reports

## Mức ưu tiên
**Bắt buộc làm trong bản 1.**

---

# 3.6. budgets

## Mục đích
Quản lý kế hoạch chi tiêu và hạn mức ngân sách.

## Chức năng chính
- Tạo monthly budget.
- Tạo category budget.
- Chỉnh sửa budget.
- Đóng budget.
- Theo dõi amount used / remaining / usage %.
- Gọi logic alert khi vượt ngưỡng.

## Dữ liệu chính
- Budgets

## Thuộc tính chính
- user_id
- budget_name
- budget_scope (monthly/category)
- category_id (nullable)
- period_month
- period_year
- spending_limit
- warning_percent
- status
- created_at
- updated_at

## Luồng nghiệp vụ chính
1. User tạo budget tháng hoặc budget theo category.
2. Mỗi expense mới phát sinh sẽ được so với budget liên quan.
3. Nếu usage >= warning threshold thì sinh alert cảnh báo.
4. Nếu usage > limit thì sinh alert vượt ngân sách.

## Phụ thuộc
- accounts
- expenses
- categories
- alerts
- reports

## Mức ưu tiên
**Bắt buộc làm trong bản 1.**

---

# 3.7. alerts

## Mục đích
Thông báo cho người dùng khi có sự kiện cần chú ý.

## Chức năng chính
- Tạo alert khi vượt budget.
- Tạo alert khi gần chạm budget.
- Tạo alert nợ quá hạn (phase sau).
- Đánh dấu đã đọc.
- Xem danh sách alert.

## Dữ liệu chính
- Alerts

## Thuộc tính chính
- user_id
- alert_type
- title
- message
- related_budget_id
- related_expense_id
- related_debt_id
- is_read
- severity
- created_at

## Nguồn sinh alert
- budget checks khi thêm/sửa expense
- job định kỳ từ Airflow
- debt overdue checker

## Phụ thuộc
- accounts
- budgets
- expenses
- debts

## Mức ưu tiên
**Bắt buộc tối thiểu trong bản 1.**

---

# 3.8. debts

## Mục đích
Quản lý các khoản nợ và lịch sử thanh toán.

## Chức năng chính
- Tạo debt.
- Cập nhật debt.
- Ghi payment cho debt.
- Theo dõi due date.
- Tính số còn nợ.
- Xác định overdue.

## Dữ liệu chính
- Debts
- DebtPayments

## Thuộc tính chính của debt
- user_id
- debt_type
- counterparty_name
- original_amount
- remaining_amount
- due_date
- status
- description
- created_at
- updated_at

## Thuộc tính chính của debt payment
- debt_id
- payment_date
- amount
- bank_account_id
- note

## Phụ thuộc
- accounts
- bank_accounts
- alerts
- reports

## Mức ưu tiên
**Làm sau khi lõi ổn định.**

---

# 3.9. sharing

## Mục đích
Cho phép một nhóm người dùng chia sẻ một phần dữ liệu tài chính chung.

## Chức năng chính
- Tạo group.
- Mời thành viên.
- Quản lý thành viên.
- Gắn shared transaction vào nhóm.
- Xem giao dịch được chia sẻ trong nhóm.

## Dữ liệu chính
- Groups
- GroupMembers
- SharedTransactions

## Ý nghĩa
Phù hợp các tình huống:
- nhóm bạn ở chung,
- nhóm đi du lịch,
- gia đình chia sẻ chi tiêu,
- nhóm làm dự án cần theo dõi quỹ chung.

## Phụ thuộc
- accounts
- expenses/income (nếu cho chia sẻ)
- reports

## Mức ưu tiên
**Làm sau khi bản lõi xong.**

---

# 3.10. reports

## Mục đích
Sinh các báo cáo phục vụ theo dõi và phân tích.

## Chức năng chính
- Báo cáo theo ngày.
- Báo cáo theo tháng.
- Báo cáo theo năm.
- Báo cáo theo category.
- Báo cáo theo bank account.
- Báo cáo bảng.
- Báo cáo biểu đồ.

## Dữ liệu lấy từ
- income
- expenses
- categories
- bank_accounts
- budgets
- debts (nếu mở rộng)

## Output điển hình
- tổng thu
- tổng chi
- chênh lệch thu chi
- top category chi tiêu
- xu hướng chi tiêu theo thời gian

## Phụ thuộc
- gần như phụ thuộc toàn bộ module lõi.

## Mức ưu tiên
**Bắt buộc làm trong bản 1.**

---

# 3.11. exports

## Mục đích
Xuất dữ liệu và báo cáo ra file để lưu trữ hoặc chia sẻ.

## Chức năng chính
- Export Excel.
- Export PDF.
- Xuất báo cáo tháng/năm.
- Xuất danh sách transaction.

## Dữ liệu lấy từ
- reports
- income
- expenses
- budgets

## Phụ thuộc
- reports
- dashboard

## Mức ưu tiên
**Làm sau phần lõi hoặc làm tối thiểu nếu còn thời gian.**

---

# 3.12. dashboard

## Mục đích
Cung cấp cái nhìn tổng quan nhanh nhất về tình hình tài chính hiện tại.

## Chức năng chính
- Hiển thị tổng balance.
- Hiển thị income tháng này.
- Hiển thị expense tháng này.
- Hiển thị recent transactions.
- Hiển thị budget progress.
- Hiển thị unread alerts.
- Hiển thị chart nhanh.

## Dữ liệu lấy từ
- bank_accounts
- income
- expenses
- budgets
- alerts

## Vai trò
- Là màn hình người dùng xem thường xuyên nhất sau khi đăng nhập.
- Là nơi kết nối trực quan giữa các module.

## Mức ưu tiên
**Bắt buộc làm trong bản 1.**

---

## 4. Quan hệ phụ thuộc giữa các module

### Module nền tảng
- accounts
- categories
- bank_accounts

### Module giao dịch lõi
- income
- expenses

### Module kiểm soát tài chính
- budgets
- alerts

### Module hiển thị và đầu ra
- dashboard
- reports
- exports

### Module mở rộng
- debts
- sharing

---

## 5. Chốt module làm bản 1 trước
Các module bắt buộc làm trước:
1. accounts / profile
2. income
3. expenses
4. categories
5. bank_accounts
6. budgets
7. reports
8. dashboard
9. alerts (ít nhất bản cơ bản)

### Lý do chọn các module này cho bản 1
- Đủ để chứng minh nghiệp vụ chính của project.
- Đủ để thiết kế schema core.
- Đủ để demo CRUD + dashboard + report.
- Đủ để sinh use case và ERD mạnh.

---

## 6. Chốt module làm sau
Các module để giai đoạn 2 hoặc làm nếu còn thời gian:
1. debts
2. sharing
3. exports nâng cao
4. Google login
5. cloud sync nâng cao

### Lý do để làm sau
- Phức tạp hơn về rule và UI.
- Không nhất thiết phải có để hệ thống lõi hoạt động.
- Nên triển khai sau khi schema và luồng chính đã ổn định.

---

## 7. Gợi ý mapping module sang Django apps

| Module nghiệp vụ | Django app gợi ý |
|---|---|
| accounts | accounts |
| income | income |
| expenses | expenses |
| categories | categories |
| bank_accounts | bank_accounts |
| budgets | budgets |
| alerts | alerts |
| debts | debts |
| sharing | sharing |
| reports | reports |
| exports | exports |
| dashboard | dashboard |
| admin/logging | core hoặc adminpanel |

---

## 8. Kết luận
Việc chia module như trên giúp project không bị rối khi bắt đầu code. Thay vì nhìn bài toán như một khối lớn, nhóm có thể triển khai theo từng lớp:
- lớp xác thực,
- lớp dữ liệu lõi,
- lớp kiểm soát,
- lớp hiển thị,
- lớp mở rộng.

Đây là bước quan trọng trước khi viết business rules và schema logic, vì nếu module chưa rõ thì database rất dễ bị chồng chéo hoặc trùng chức năng.

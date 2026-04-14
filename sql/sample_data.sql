USE pfms;
SET NAMES utf8mb4;

INSERT INTO users
(user_id, username, email, password_hash, full_name, phone_number, avatar_url, default_currency, timezone, role, is_active, last_login_at, created_at, updated_at)
VALUES
(1, 'admin01', 'admin@gmail.com', '$2b$12$dummy_admin_hash', 'Quản trị hệ thống', '0901000001', NULL, 'VND', 'Asia/Ha_Noi', 'admin', 1, '2026-04-12 08:00:00', '2026-03-01 08:00:00', '2026-04-12 08:00:00'),
(2, 'moe_nu', 'moe@gmail.com', '$2b$12$dummy_hash_2', 'Moè Nu', '0902000002', NULL, 'VND', 'Asia/Ha_Noi', 'user', 1, '2026-04-12 20:30:00', '2026-03-05 10:00:00', '2026-04-12 20:30:00'),
(3, 'lam_nguyen', 'lamngthanh@gmail.com', '$2b$12$dummy_hash_3', 'Lâm Nguyễn', '0903000003', NULL, 'VND', 'Asia/Ha_Noi', 'user', 1, '2026-04-12 18:20:00', '2026-03-06 11:00:00', '2026-04-12 18:20:00'),
(4, 'trang.thuyle', 'an@gmail.com', '$2b$12$dummy_hash_4', 'Thuỳ Trang Lê', '0904000004', NULL, 'VND', 'Asia/Ha_Noi', 'user', 1, '2026-04-11 15:45:00', '2026-03-08 09:30:00', '2026-04-11 15:45:00'),
(5, 'khoa_le', 'khoa@gmail.com', '$2b$12$dummy_hash_5', 'Khoa Lê', '0905000005', NULL, 'VND', 'Asia/Ho_Chi_Minh', 'user', 1, '2026-04-10 08:10:00', '2026-03-10 14:00:00', '2026-04-10 08:10:00');

INSERT INTO categories
(category_id, user_id, category_name, category_type, description, color_code, icon_name, is_default, is_active, created_at, updated_at)
VALUES
(1, NULL, 'Ăn uống', 'expense', 'Chi phí ăn sáng, ăn trưa, ăn tối, siêu thị', '#FF6B6B', 'utensils', 1, 1, '2026-03-01 08:00:00', '2026-03-01 08:00:00'),
(2, NULL, 'Di chuyển', 'expense', 'Taxi, xăng xe, gửi xe, xe buýt', '#4ECDC4', 'car', 1, 1, '2026-03-01 08:00:00', '2026-03-01 08:00:00'),
(3, NULL, 'Hóa đơn', 'expense', 'Điện, nước, internet, điện thoại', '#5D5FEF', 'receipt', 1, 1, '2026-03-01 08:00:00', '2026-03-01 08:00:00'),
(4, NULL, 'Mua sắm', 'expense', 'Mua đồ cá nhân, thiết bị, quần áo', '#F7B801', 'shopping-bag', 1, 1, '2026-03-01 08:00:00', '2026-03-01 08:00:00'),
(5, NULL, 'Sức khỏe', 'expense', 'Khám bệnh, thuốc men, kiểm tra sức khỏe', '#2ECC71', 'heart-pulse', 1, 1, '2026-03-01 08:00:00', '2026-03-01 08:00:00'),
(6, NULL, 'Giáo dục', 'expense', 'Học phí, sách vở, khóa học', '#8E44AD', 'book-open', 1, 1, '2026-03-01 08:00:00', '2026-03-01 08:00:00'),
(7, NULL, 'Giải trí', 'expense', 'Xem phim, cà phê, đi chơi', '#00B894', 'film', 1, 1, '2026-03-01 08:00:00', '2026-03-01 08:00:00'),
(8, NULL, 'Thuê nhà', 'expense', 'Tiền trọ, tiền thuê căn hộ', '#E17055', 'home', 1, 1, '2026-03-01 08:00:00', '2026-03-01 08:00:00'),
(9, NULL, 'Lương', 'income', 'Thu nhập lương hằng tháng', '#0984E3', 'wallet', 1, 1, '2026-03-01 08:00:00', '2026-03-01 08:00:00'),
(10, NULL, 'Thưởng', 'income', 'Tiền thưởng và phụ cấp', '#00CEC9', 'gift', 1, 1, '2026-03-01 08:00:00', '2026-03-01 08:00:00'),
(11, NULL, 'Thu nhập thêm', 'income', 'Freelance, dạy thêm, bán hàng', '#6C5CE7', 'briefcase', 1, 1, '2026-03-01 08:00:00', '2026-03-01 08:00:00'),
(12, NULL, 'Quà tặng', 'income', 'Tiền mừng, hỗ trợ từ gia đình', '#FD79A8', 'heart', 1, 1, '2026-03-01 08:00:00', '2026-03-01 08:00:00'),
(13, NULL, 'Hoàn tiền', 'income', 'Hoàn tiền mua hàng hoặc khuyến mãi', '#FDCB6E', 'rotate-ccw', 1, 1, '2026-03-01 08:00:00', '2026-03-01 08:00:00');

INSERT INTO bank_accounts
(bank_account_id, user_id, account_name, account_type, provider_name, account_number_masked, currency, opening_balance, current_balance, note, is_active, created_at, updated_at)
VALUES
(1, 2, 'Techcombank chính', 'bank', 'Techcombank', '***1234', 'VND', 12000000.00, 12000000.00, 'Tài khoản nhận lương chính', 1, '2026-03-05 10:10:00', '2026-03-05 10:10:00'),
(2, 2, 'Ví MoMo', 'e_wallet', 'MoMo', '***8899', 'VND', 1500000.00, 1500000.00, 'Chi tiêu hằng ngày', 1, '2026-03-05 10:20:00', '2026-03-05 10:20:00'),
(3, 2, 'Tiền mặt', 'cash', 'Cash', NULL, 'VND', 800000.00, 800000.00, 'Tiền mặt mang theo', 1, '2026-03-05 10:30:00', '2026-03-05 10:30:00'),
(4, 3, 'VPBank lương', 'bank', 'VPBank', '***5678', 'VND', 9000000.00, 9000000.00, 'Tài khoản chính của Linh', 1, '2026-03-06 11:15:00', '2026-03-06 11:15:00'),
(5, 3, 'Ví ZaloPay', 'e_wallet', 'ZaloPay', '***2211', 'VND', 700000.00, 700000.00, 'Chi phí nhỏ lẻ', 1, '2026-03-06 11:20:00', '2026-03-06 11:20:00'),
(6, 4, 'MB Bank', 'bank', 'MB Bank', '***3344', 'VND', 6000000.00, 6000000.00, 'Tài khoản ngân hàng của An', 1, '2026-03-08 09:45:00', '2026-03-08 09:45:00'),
(7, 4, 'Ví tiền mặt', 'cash', 'Cash', NULL, 'VND', 500000.00, 500000.00, 'Tiền mặt cá nhân', 1, '2026-03-08 09:50:00', '2026-03-08 09:50:00'),
(8, 5, 'Vietcombank', 'bank', 'Vietcombank', '***2468', 'VND', 10000000.00, 10000000.00, 'Tài khoản chính của Khoa', 1, '2026-03-10 14:10:00', '2026-03-10 14:10:00');

INSERT INTO incomes
(income_id, user_id, category_id, bank_account_id, title, amount, income_date, description, note, status, created_at, updated_at)
VALUES
(1, 2, 9, 1, 'Lương tháng 4', 15000000.00, '2026-04-01', 'Nhận lương tháng 4 từ công ty', 'Chuyển khoản đầu tháng', 'active', '2026-04-01 08:05:00', '2026-04-01 08:05:00'),
(2, 2, 10, 1, 'Thưởng hoàn thành dự án', 3000000.00, '2026-04-09', 'Thưởng do hoàn thành dự án đúng hạn', NULL, 'active', '2026-04-09 17:20:00', '2026-04-09 17:20:00'),
(3, 2, 11, 2, 'Thiết kế freelance', 2200000.00, '2026-04-12', 'Thu nhập từ dự án thiết kế bên ngoài', 'Khách chuyển qua ví', 'active', '2026-04-12 19:00:00', '2026-04-12 19:00:00'),
(4, 2, 13, 2, 'Hoàn tiền mua hàng', 350000.00, '2026-04-15', 'Hoàn tiền do đổi sản phẩm lỗi', NULL, 'active', '2026-04-15 14:10:00', '2026-04-15 14:10:00'),
(5, 3, 9, 4, 'Lương tháng 4', 12000000.00, '2026-04-01', 'Lương chính thức tháng 4', NULL, 'active', '2026-04-01 08:15:00', '2026-04-01 08:15:00'),
(6, 3, 11, 4, 'Dạy kèm cuối tuần', 1800000.00, '2026-04-07', 'Thu nhập từ lớp dạy kèm', NULL, 'active', '2026-04-07 20:10:00', '2026-04-07 20:10:00'),
(7, 3, 12, 5, 'Quà sinh nhật', 1000000.00, '2026-04-11', 'Tiền mừng sinh nhật từ gia đình', NULL, 'active', '2026-04-11 10:30:00', '2026-04-11 10:30:00'),
(8, 4, 9, 6, 'Lương part-time', 7000000.00, '2026-04-01', 'Lương công việc bán thời gian', NULL, 'active', '2026-04-01 08:30:00', '2026-04-01 08:30:00'),
(9, 4, 12, 7, 'Gia đình hỗ trợ', 2000000.00, '2026-04-05', 'Ba mẹ hỗ trợ chi phí sinh hoạt', NULL, 'active', '2026-04-05 09:00:00', '2026-04-05 09:00:00'),
(10, 5, 9, 8, 'Lương tháng 4', 11000000.00, '2026-04-01', 'Nhận lương tháng 4', NULL, 'active', '2026-04-01 08:40:00', '2026-04-01 08:40:00'),
(11, 5, 11, 8, 'Bán đồ cũ', 900000.00, '2026-04-10', 'Bán bàn học cũ', NULL, 'active', '2026-04-10 16:00:00', '2026-04-10 16:00:00'),
(12, 5, 13, 8, 'Hoàn tiền khuyến mãi', 250000.00, '2026-04-18', 'Hoàn tiền từ chương trình khuyến mãi', NULL, 'active', '2026-04-18 11:00:00', '2026-04-18 11:00:00');

INSERT INTO expenses
(expense_id, user_id, category_id, bank_account_id, amount, expense_date, payment_method, description, note, status, created_at, updated_at)
VALUES
(1, 2, 1, 3, 45000.00, '2026-04-02', 'cash', 'Ăn sáng bánh mì và cà phê', NULL, 'active', '2026-04-02 07:30:00', '2026-04-02 07:30:00'),
(2, 2, 1, 2, 75000.00, '2026-04-02', 'e_wallet', 'Ăn trưa văn phòng', NULL, 'active', '2026-04-02 12:20:00', '2026-04-02 12:20:00'),
(3, 2, 2, 2, 120000.00, '2026-04-03', 'e_wallet', 'Đi Grab đến công ty', NULL, 'active', '2026-04-03 08:00:00', '2026-04-03 08:00:00'),
(4, 2, 3, 1, 350000.00, '2026-04-04', 'bank', 'Thanh toán tiền điện tháng 4', NULL, 'active', '2026-04-04 19:10:00', '2026-04-04 19:10:00'),
(5, 2, 3, 1, 220000.00, '2026-04-04', 'bank', 'Thanh toán tiền internet tháng 4', NULL, 'active', '2026-04-04 19:20:00', '2026-04-04 19:20:00'),
(6, 2, 4, 1, 650000.00, '2026-04-05', 'bank', 'Mua tai nghe làm việc', 'Phục vụ làm việc online', 'active', '2026-04-05 14:00:00', '2026-04-05 14:00:00'),
(7, 2, 8, 1, 3000000.00, '2026-04-06', 'bank', 'Thanh toán tiền thuê nhà tháng 4', 'Tiền thuê căn hộ', 'active', '2026-04-06 09:00:00', '2026-04-06 09:00:00'),
(8, 2, 7, 2, 180000.00, '2026-04-08', 'e_wallet', 'Xem phim cuối tuần', NULL, 'active', '2026-04-08 21:00:00', '2026-04-08 21:00:00'),
(9, 2, 1, 1, 420000.00, '2026-04-09', 'bank', 'Mua thực phẩm ở siêu thị', 'Mua đồ ăn cho một tuần', 'active', '2026-04-09 18:00:00', '2026-04-09 18:00:00'),
(10, 2, 1, 2, 95000.00, '2026-04-10', 'e_wallet', 'Cà phê với bạn', NULL, 'active', '2026-04-10 16:20:00', '2026-04-10 16:20:00'),
(11, 2, 2, 3, 150000.00, '2026-04-11', 'cash', 'Gửi xe và đổ xăng', NULL, 'active', '2026-04-11 18:30:00', '2026-04-11 18:30:00'),
(12, 2, 4, 1, 400000.00, '2026-04-12', 'bank', 'Mua áo sơ mi đi làm', NULL, 'active', '2026-04-12 17:00:00', '2026-04-12 17:00:00'),

(13, 3, 1, 4, 250000.00, '2026-04-02', 'bank', 'Ăn tối cùng gia đình', NULL, 'active', '2026-04-02 20:00:00', '2026-04-02 20:00:00'),
(14, 3, 4, 5, 480000.00, '2026-04-03', 'e_wallet', 'Mua mỹ phẩm chăm sóc da', NULL, 'active', '2026-04-03 21:10:00', '2026-04-03 21:10:00'),
(15, 3, 5, 4, 600000.00, '2026-04-04', 'bank', 'Khám da liễu định kỳ', NULL, 'active', '2026-04-04 10:40:00', '2026-04-04 10:40:00'),
(16, 3, 6, 4, 1500000.00, '2026-04-05', 'bank', 'Đóng học phí khóa học tiếng Anh', NULL, 'active', '2026-04-05 15:10:00', '2026-04-05 15:10:00'),
(17, 3, 2, 5, 160000.00, '2026-04-06', 'e_wallet', 'Taxi đi làm', NULL, 'active', '2026-04-06 08:15:00', '2026-04-06 08:15:00'),
(18, 3, 3, 5, 120000.00, '2026-04-07', 'e_wallet', 'Nạp tiền điện thoại', NULL, 'active', '2026-04-07 09:10:00', '2026-04-07 09:10:00'),
(19, 3, 7, 4, 450000.00, '2026-04-08', 'bank', 'Xem hòa nhạc cuối tuần', NULL, 'active', '2026-04-08 22:00:00', '2026-04-08 22:00:00'),
(20, 3, 6, 4, 320000.00, '2026-04-09', 'bank', 'Mua sách chuyên ngành', NULL, 'active', '2026-04-09 17:00:00', '2026-04-09 17:00:00'),

(21, 4, 1, 7, 40000.00, '2026-04-02', 'cash', 'Ăn sáng bánh cuốn', NULL, 'active', '2026-04-02 07:10:00', '2026-04-02 07:10:00'),
(22, 4, 8, 6, 2200000.00, '2026-04-03', 'bank', 'Trả tiền trọ tháng 4', NULL, 'active', '2026-04-03 19:30:00', '2026-04-03 19:30:00'),
(23, 4, 6, 6, 650000.00, '2026-04-05', 'bank', 'Mua giáo trình học', NULL, 'active', '2026-04-05 11:20:00', '2026-04-05 11:20:00'),
(24, 4, 2, 7, 180000.00, '2026-04-06', 'cash', 'Nạp xăng xe', NULL, 'active', '2026-04-06 18:00:00', '2026-04-06 18:00:00'),
(25, 4, 5, 6, 900000.00, '2026-04-10', 'bank', 'Khám răng và lấy thuốc', NULL, 'active', '2026-04-10 09:30:00', '2026-04-10 09:30:00'),
(26, 4, 7, 7, 130000.00, '2026-04-11', 'cash', 'Đi cà phê với bạn', NULL, 'active', '2026-04-11 20:00:00', '2026-04-11 20:00:00'),

(27, 5, 1, 8, 550000.00, '2026-04-02', 'bank', 'Mua thực phẩm cho gia đình', NULL, 'active', '2026-04-02 18:00:00', '2026-04-02 18:00:00'),
(28, 5, 3, 8, 600000.00, '2026-04-04', 'bank', 'Thanh toán điện nước', NULL, 'active', '2026-04-04 20:00:00', '2026-04-04 20:00:00'),
(29, 5, 4, 8, 430000.00, '2026-04-07', 'bank', 'Mua áo sơ mi', NULL, 'active', '2026-04-07 17:30:00', '2026-04-07 17:30:00'),
(30, 5, 7, 8, 160000.00, '2026-04-08', 'bank', 'Xem phim với bạn bè', NULL, 'active', '2026-04-08 21:30:00', '2026-04-08 21:30:00');

INSERT INTO budgets
(budget_id, user_id, budget_name, budget_scope, category_id, period_month, period_year, spending_limit, warning_percent, status, created_at, updated_at)
VALUES
(1, 2, 'Ngân sách tổng tháng 4', 'overall', NULL, 4, 2026, 6000000.00, 80.00, 'active', '2026-04-01 07:30:00', '2026-04-01 07:30:00'),
(2, 2, 'Ngân sách ăn uống tháng 4', 'category', 1, 4, 2026, 1200000.00, 80.00, 'active', '2026-04-01 07:40:00', '2026-04-01 07:40:00'),
(3, 2, 'Ngân sách di chuyển tháng 4', 'category', 2, 4, 2026, 500000.00, 80.00, 'active', '2026-04-01 07:45:00', '2026-04-01 07:45:00'),
(4, 3, 'Ngân sách tổng tháng 4', 'overall', NULL, 4, 2026, 5000000.00, 80.00, 'active', '2026-04-01 07:50:00', '2026-04-01 07:50:00'),
(5, 3, 'Ngân sách sức khỏe tháng 4', 'category', 5, 4, 2026, 700000.00, 75.00, 'active', '2026-04-01 07:55:00', '2026-04-01 07:55:00'),
(6, 4, 'Ngân sách học tập tháng 4', 'category', 6, 4, 2026, 1000000.00, 80.00, 'active', '2026-04-01 08:00:00', '2026-04-01 08:00:00'),
(7, 4, 'Ngân sách tổng tháng 4', 'overall', NULL, 4, 2026, 4500000.00, 80.00, 'active', '2026-04-01 08:05:00', '2026-04-01 08:05:00'),
(8, 5, 'Ngân sách tổng tháng 4', 'overall', NULL, 4, 2026, 3500000.00, 80.00, 'active', '2026-04-01 08:10:00', '2026-04-01 08:10:00');

INSERT INTO debts
(debt_id, user_id, debt_type, counterparty_name, original_amount, remaining_amount, due_date, status, description, note, created_at, updated_at, is_active)
VALUES
(1, 2, 'i_owe', 'Nguyễn Nam', 5000000.00, 5000000.00, '2026-05-10', 'pending', 'Mượn tiền mua laptop', 'Trả góp theo tháng', '2026-04-01 09:00:00', '2026-04-01 09:00:00', 1),
(2, 3, 'owed_to_me', 'Mai Anh', 2000000.00, 2000000.00, '2026-04-25', 'pending', 'Cho bạn mượn tiền ngắn hạn', NULL, '2026-04-03 11:00:00', '2026-04-03 11:00:00', 1),
(3, 2, 'i_owe', 'Lan Hương', 1200000.00, 1200000.00, '2026-04-15', 'overdue', 'Mượn tiền chi phí đột xuất', 'Quá hạn thanh toán', '2026-04-05 14:20:00', '2026-04-16 09:00:00', 1),
(4, 4, 'i_owe', 'Hoàng Minh', 3000000.00, 3000000.00, '2026-05-20', 'pending', 'Mượn tiền để đóng học phí', NULL, '2026-04-06 12:00:00', '2026-04-06 12:00:00', 1);

INSERT INTO debt_payments
(debt_payment_id, debt_id, bank_account_id, payment_date, amount, note, created_at)
VALUES
(1, 1, 1, '2026-04-18', 1500000.00, 'Đợt trả đầu cho Nguyễn Nam', '2026-04-18 18:10:00'),
(2, 2, 4, '2026-04-12', 500000.00, 'Mai Anh chuyển khoản lần 1', '2026-04-12 10:05:00'),
(3, 2, 4, '2026-04-20', 300000.00, 'Mai Anh chuyển khoản lần 2', '2026-04-20 10:10:00'),
(4, 4, 6, '2026-04-18', 500000.00, 'Thanh toán một phần cho Hoàng Minh', '2026-04-18 17:05:00');

INSERT INTO alerts
(alert_id, user_id, alert_type, severity, title, message, related_budget_id, related_expense_id, related_debt_id, is_read, created_at)
VALUES
(1, 2, 'budget_warning', 'warning', 'Cảnh báo ngân sách ăn uống', 'Chi tiêu ăn uống của bạn đã vượt 80% ngân sách tháng 4.', 2, NULL, NULL, 0, '2026-04-09 18:05:00'),
(2, 2, 'budget_exceeded', 'critical', 'Vượt ngân sách di chuyển', 'Bạn đã vượt ngân sách di chuyển sau giao dịch gần nhất.', 3, NULL, NULL, 0, '2026-04-11 18:35:00'),
(3, 3, 'budget_warning', 'warning', 'Cảnh báo ngân sách sức khỏe', 'Ngân sách sức khỏe tháng 4 đã gần chạm giới hạn.', 5, NULL, NULL, 1, '2026-04-04 10:45:00'),
(4, 4, 'budget_warning', 'warning', 'Cảnh báo ngân sách học tập', 'Chi tiêu học tập của bạn đã vượt 80% hạn mức.', 6, NULL, NULL, 0, '2026-04-05 11:25:00'),
(5, 4, 'budget_exceeded', 'critical', 'Vượt ngân sách tổng', 'Tổng chi tiêu tháng 4 của bạn đã vượt ngân sách tổng.', 7, NULL, NULL, 0, '2026-04-10 09:35:00'),
(6, 2, 'debt_overdue', 'critical', 'Khoản nợ quá hạn', 'Khoản nợ với Lan Hương đã quá hạn thanh toán.', NULL, NULL, 3, 0, '2026-04-16 09:10:00'),
(7, 5, 'system_info', 'info', 'Báo cáo tháng đã sẵn sàng', 'Bạn có thể xem và xuất báo cáo tài chính tháng 4.', NULL, NULL, NULL, 1, '2026-04-21 08:00:00');

INSERT INTO `groups`
(group_id, owner_user_id, group_name, description, status, created_at, updated_at)
VALUES
(1, 2, 'Chi tiêu căn hộ', 'Nhóm chia sẻ các khoản chi trong căn hộ', 'active', '2026-04-01 20:00:00', '2026-04-10 20:00:00'),
(2, 3, 'Nhóm học tiếng Anh', 'Nhóm chia sẻ chi phí học tập và tài liệu', 'active', '2026-04-03 21:00:00', '2026-04-12 21:00:00');

INSERT INTO group_members
(group_member_id, group_id, user_id, member_role, joined_at, status)
VALUES
(1, 1, 2, 'owner', '2026-04-01 20:00:00', 'active'),
(2, 1, 3, 'member', '2026-04-02 09:00:00', 'active'),
(3, 2, 3, 'owner', '2026-04-03 21:00:00', 'active'),
(4, 2, 4, 'member', '2026-04-04 10:30:00', 'active');

INSERT INTO shared_transactions
(shared_transaction_id, group_id, shared_by_user_id, expense_id, income_id, visibility_status, note, created_at)
VALUES
(1, 1, 2, 7, NULL, 'visible', 'Chia sẻ tiền thuê nhà tháng 4', '2026-04-06 09:10:00'),
(2, 1, 2, 4, NULL, 'visible', 'Chia sẻ tiền điện tháng 4', '2026-04-04 19:15:00'),
(3, 2, 3, 16, NULL, 'visible', 'Chia sẻ học phí khóa học tiếng Anh', '2026-04-05 15:20:00'),
(4, 2, 3, NULL, 6, 'visible', 'Chia sẻ thu nhập dạy kèm cho quỹ nhóm học', '2026-04-07 20:15:00');

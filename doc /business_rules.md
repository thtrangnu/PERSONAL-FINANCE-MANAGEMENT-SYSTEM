# Business Rules Specification

## 1. Mục đích tài liệu
Tài liệu này định nghĩa các **luật nghiệp vụ** mà hệ thống phải tuân theo. Đây là cầu nối giữa:
- requirement,
- use case,
- database schema,
- backend logic,
- trigger/procedure/function.

Nếu không chốt business rules ngay từ đầu, hệ thống sẽ rất dễ bị:
- lệch nghiệp vụ,
- cập nhật balance sai,
- báo cáo sai,
- phân quyền sai,
- dữ liệu bị mâu thuẫn.

---

## 2. Nguyên tắc chung
1. Mỗi dữ liệu tài chính phải có chủ sở hữu rõ ràng.
2. Mỗi giao dịch phải có giá trị hợp lệ.
3. Mọi thay đổi liên quan đến tiền phải phản ánh nhất quán lên số dư, budget và report.
4. Những dữ liệu đã phát sinh nghiệp vụ nên hạn chế xóa cứng nếu có nguy cơ làm sai lịch sử.
5. Shared data phải được kiểm soát theo nhóm thành viên.

---

# 3. Luật nghiệp vụ chi tiết

# 3.1. Rules về user ownership

### BR-01 — Mỗi income thuộc về đúng một user
- Một bản ghi income phải có `user_id`.
- Không tồn tại income “vô chủ”.
- Chỉ user sở hữu mới được xem/sửa/xóa income đó.

### BR-02 — Mỗi expense thuộc về đúng một user
- Một bản ghi expense phải có `user_id`.
- Chỉ user sở hữu mới được thao tác trên expense đó.

### BR-03 — Mỗi budget thuộc về đúng một user
- Budget không được dùng chung giữa nhiều user ở bản lõi.
- User này không được xem budget của user khác.

### BR-04 — Mỗi bank account thuộc về đúng một user
- Tài khoản ngân hàng hoặc ví tiền là tài sản tài chính cá nhân.
- Chỉ user đó mới được xem và chỉnh sửa.

### BR-05 — Mỗi alert phải gắn với một user nhận cảnh báo
- Alert luôn có đối tượng nhận rõ ràng.
- Không có alert “mồ côi” không biết thuộc ai.

---

# 3.2. Rules về category

### BR-06 — Mỗi income/expense phải thuộc một category hợp lệ
- Income và expense đều phải có `category_id` hợp lệ.
- Điều này giúp tổng hợp báo cáo nhất quán theo category.

### BR-07 — Category chỉ được dùng nếu đang active
- Nếu category bị vô hiệu hóa, user không được dùng nó cho income/expense mới.
- Tuy nhiên lịch sử cũ vẫn giữ nguyên.

### BR-08 — Category có thể là category cá nhân hoặc category hệ thống
- Category hệ thống có thể dùng chung.
- Category cá nhân chỉ thuộc một user.
- Category còn phải có `category_type` phù hợp với giao dịch:
  - income chỉ dùng category type `income` hoặc `both`,
  - expense chỉ dùng category type `expense` hoặc `both`.

### BR-09 — Không xóa cứng category nếu đang được income/expense/budget tham chiếu
- Nên dùng `is_active = false` thay vì xóa.
- Mục tiêu là bảo toàn lịch sử dữ liệu.

---

# 3.3. Rules về income/expense và bank account

### BR-10 — Mỗi income/expense có thể gắn một bank account hoặc không
- Giao dịch có thể thuộc tài khoản ngân hàng/ ví/ tiền mặt cụ thể.
- Nếu không gắn bank account, giao dịch vẫn hợp lệ nhưng không ảnh hưởng balance của account cụ thể.

### BR-11 — Khi thêm income thì balance tăng
- Nếu income có `bank_account_id`, số dư account phải tăng đúng bằng `amount`.
- Quy tắc này phải được áp dụng nhất quán khi tạo mới.

### BR-12 — Khi thêm expense thì balance giảm
- Nếu expense có `bank_account_id`, số dư account phải giảm đúng bằng `amount`.

### BR-13 — Khi sửa income thì balance phải được điều chỉnh chênh lệch
Ví dụ:
- income cũ = 1,000,000
- income mới = 1,500,000
- balance phải tăng thêm 500,000

Nếu đổi bank account:
- account cũ bị trừ rollback số cũ,
- account mới được cộng số mới.

### BR-14 — Khi sửa expense thì balance phải được điều chỉnh chênh lệch
Ví dụ:
- expense cũ = 300,000
- expense mới = 250,000
- balance phải cộng trả lại 50,000

Nếu đổi bank account:
- rollback account cũ,
- áp dụng lại cho account mới.

### BR-15 — Khi xóa income/expense đã gắn bank account, phải rollback balance
- Xóa income => trừ lại balance.
- Xóa expense => cộng lại balance.

### BR-16 — Amount của income/expense phải lớn hơn 0
- Không cho phép amount bằng 0 hoặc âm ở bản ghi chuẩn.
- Nếu cần điều chỉnh âm thì nên dùng loại nghiệp vụ riêng, không dùng sai expense/income thường.

### BR-17 — Expense date và income date không được null
- Mỗi giao dịch phải có ngày phát sinh.
- Đây là dữ liệu bắt buộc để tổng hợp theo ngày/tháng/năm.

---

# 3.4. Rules về bank accounts

### BR-18 — Mỗi bank account có trạng thái active/inactive
- Account inactive vẫn giữ lịch sử cũ.
- Account inactive không nên nhận giao dịch mới.

### BR-19 — Số dư account phải phản ánh trạng thái hiện tại theo rule hệ thống
Có hai cách thường gặp:
1. lưu current_balance và update theo trigger/business logic,
2. hoặc tính động từ opening_balance + transactions.

Trong project này có thể ưu tiên:
- lưu `opening_balance`,
- lưu `current_balance`,
- đồng thời đảm bảo current_balance được cập nhật nhất quán bởi backend/trigger.

### BR-20 — Account number nếu lưu thì chỉ nên lưu dạng masked
- Không nên lưu đầy đủ số tài khoản thật nếu không cần.
- Ví dụ: `****1234`.

---

# 3.5. Rules về budget

### BR-21 — Budget có thể là budget tổng hoặc budget theo category
- `budget_scope = overall` nghĩa là hạn mức cho toàn bộ chi tiêu tháng.
- `budget_scope = category` nghĩa là hạn mức chỉ áp dụng cho một category cụ thể.

### BR-22 — Budget phải gắn với chu kỳ thời gian rõ ràng
- Ít nhất phải có `period_month` và `period_year`.
- Không được tạo budget mà không biết áp dụng cho thời gian nào.

### BR-23 — Budget category bắt buộc phải có category_id
- Nếu scope là category mà không có category_id thì budget không hợp lệ.

### BR-24 — Budget overall không bắt buộc category_id
- Vì nó quản lý tổng chi tiêu toàn tháng.

### BR-25 — Spending limit phải lớn hơn 0
- Không cho phép budget bằng 0 hoặc âm.

### BR-26 — Warning percent phải nằm trong khoảng hợp lệ
Khuyến nghị:
- từ 1 đến 100.
- Thường dùng 70, 80, 90.

### BR-27 — Chi tiêu dùng để tính budget là expense trong đúng kỳ
- Chỉ expense có ngày nằm trong tháng/năm của budget mới được cộng vào usage.

### BR-28 — Budget usage phải được cập nhật khi expense thay đổi
Các thao tác ảnh hưởng usage:
- thêm expense,
- sửa expense,
- xóa expense,
- đổi category,
- đổi date sang tháng khác.

### BR-29 — Một user không nên có 2 budget active trùng logic trong cùng kỳ
Ví dụ không nên có:
- hai overall budget cùng tháng 05/2026 cùng active,
- hoặc hai category budget cùng category ăn uống cho cùng tháng 05/2026 cùng active.

Có thể enforce bằng unique rule nghiệp vụ.

---

# 3.6. Rules về alerts

### BR-30 — Khi chi tiêu vượt ngưỡng budget thì phải tạo alert
- Nếu usage >= warning threshold, tạo alert cảnh báo.
- Nếu usage > limit, tạo alert vượt mức.

### BR-31 — Không tạo alert trùng vô hạn cho cùng một trạng thái
Ví dụ:
- Nếu đã có alert “budget vượt 100%” cho budget tháng này rồi, không nên mỗi lần refresh lại sinh thêm hàng loạt bản sao.

Cần cơ chế chống trùng:
- theo `budget_id + alert_type + period + severity`.

### BR-32 — Alert phải phân loại mức độ
Gợi ý:
- info
- warning
- critical

### BR-33 — Alert có thể ở trạng thái read/unread
- Mặc định alert mới là unread.
- User có thể đánh dấu đã đọc.

### BR-33A — Mỗi alert chỉ nên tham chiếu một đối tượng liên quan
- Alert loại budget chỉ nên dùng `related_budget_id`.
- Alert loại debt chỉ nên dùng `related_debt_id`.
- Một alert không nên đồng thời tham chiếu nhiều đối tượng.

---

# 3.7. Rules về debts

### BR-34 — Debt có trạng thái đang nợ / đã trả / quá hạn
Các trạng thái cơ bản:
- pending
- partially_paid
- paid
- overdue

### BR-35 — Debt phải có original_amount > 0
- Khoản nợ phải có số tiền gốc hợp lệ.

### BR-36 — Remaining amount không được âm
- Sau khi cộng tất cả payment, số còn nợ không được nhỏ hơn 0.
- Nếu user thanh toán vượt, hệ thống phải chặn hoặc yêu cầu điều chỉnh.

### BR-37 — Debt payment phải thuộc một debt cụ thể
- Không có payment độc lập không biết trả cho khoản nợ nào.

### BR-38 — Nếu remaining_amount = 0 thì debt chuyển sang paid
- Quy tắc cập nhật trạng thái phải tự động hoặc bán tự động.

### BR-39 — Nếu quá due_date mà remaining_amount > 0 thì debt có thể chuyển overdue
- Rule này có thể do background job kiểm tra hằng ngày.

---

# 3.8. Rules về sharing groups

### BR-40 — Shared transactions chỉ hiện cho thành viên nhóm
- Đây là rule quan trọng nhất của module sharing.

### BR-41 — Mỗi shared transaction phải thuộc một group cụ thể
- Không có shared transaction “tự do”.

### BR-42 — Chỉ member hợp lệ mới được xem transaction của group
- Nếu user không nằm trong `GroupMembers`, phải bị từ chối truy cập.

### BR-43 — Chỉ owner/admin nhóm mới được quản lý thành viên
- Thêm/xóa thành viên phải có quyền rõ.

### BR-44 — Giao dịch cá nhân không tự động trở thành giao dịch chia sẻ
- User phải chủ động đánh dấu giao dịch là shared hoặc tạo bản ghi liên kết chia sẻ.

### BR-44A — Shared transaction chỉ được tham chiếu một loại giao dịch gốc
- Chỉ một trong hai `expense_id` hoặc `income_id` được phép có giá trị.
- Không được để cả hai cùng có giá trị.
- Không được để cả hai cùng null.

---

# 3.9. Rules về xóa dữ liệu

### BR-45 — Hạn chế xóa cứng dữ liệu tài chính quan trọng
Khuyến nghị soft delete cho:
- categories,
- bank accounts,
- budgets,
- alerts,
- debts.

### BR-46 — Nếu xóa cứng income/expense phải đảm bảo rollback nghiệp vụ
- Điều chỉnh balance.
- Điều chỉnh budget usage.
- Cập nhật report cache nếu có.

### BR-47 — Không được xóa user nếu còn dữ liệu tài chính mà không có chính sách rõ ràng
- Có thể khóa tài khoản thay vì xóa vật lý.

---

# 3.10. Rules về báo cáo

### BR-48 — Daily/Monthly/Yearly summary chỉ tính dữ liệu của chính user hiện tại
- Không gộp nhầm dữ liệu nhiều user.

### BR-49 — Báo cáo phải dựa trên transaction hợp lệ, active
- Không tính những record đã bị invalid/inactive nếu hệ thống có trạng thái này.

### BR-50 — Báo cáo category chỉ tính các expense có category hợp lệ
- Nếu category bị vô hiệu hóa sau này thì lịch sử cũ vẫn có thể được tính, tùy rule báo cáo đã chốt.

### BR-51 — Dashboard là dữ liệu tổng hợp gần thời gian thực
- Dashboard cần cập nhật khi transaction thay đổi.

---

# 3.11. Rules về bảo mật và truy cập dữ liệu

### BR-52 — User không được chỉ định `user_id` của người khác để thao tác dữ liệu
- Backend phải lấy user từ session/token, không tin payload client.

### BR-53 — API/query phải luôn lọc theo owner
- Đây là rule kỹ thuật bắt buộc phát sinh từ rule nghiệp vụ.

### BR-54 — Export chỉ được xuất dữ liệu được phép truy cập
- File export không được chứa dữ liệu người khác.

---

# 3.12. Rules về audit/logging

### BR-55 — Các hành động quan trọng nên được log
Bao gồm:
- login thất bại/thành công,
- tạo/sửa/xóa transaction,
- thay đổi budget,
- chạy backup,
- recovery,
- lỗi hệ thống nghiêm trọng.

### BR-56 — Các tác vụ nền tạo alert/backup nên có dấu vết thực thi
- Có log thời gian chạy,
- kết quả thành công/thất bại,
- thông điệp lỗi nếu có.

---

## 4. Ví dụ minh họa nghiệp vụ

### Ví dụ 1 — Thêm expense có bank account và budget
- User A có bank account với balance = 5,000,000.
- User A có budget ăn uống tháng 4 là 2,000,000.
- Đã chi ăn uống trong tháng 4 là 1,700,000.
- User A thêm expense ăn uống = 400,000 vào ngày 2026-04-10.

**Kết quả đúng phải là:**
- expense được lưu,
- balance account còn 4,600,000,
- budget usage thành 2,100,000,
- hệ thống tạo alert vượt ngân sách.

### Ví dụ 2 — Sửa expense đổi account
- Expense cũ = 300,000 gắn account A.
- User sửa thành 300,000 gắn account B.

**Kết quả đúng:**
- account A được cộng trả lại 300,000,
- account B bị trừ 300,000.

### Ví dụ 3 — Debt quá hạn
- Khoản nợ còn 2,000,000.
- due_date là 2026-04-01.
- Hôm nay là 2026-04-04.
- chưa có payment mới.

**Kết quả đúng:**
- debt status có thể chuyển sang overdue,
- hệ thống tạo alert overdue nếu module này bật.

---

## 5. Kết luận
Business rules là phần chốt để đảm bảo từ thiết kế database đến code Django đều đi cùng một hướng. Với project này, có 4 rule quan trọng nhất cần luôn nhớ:

1. **Mỗi dữ liệu tài chính phải có chủ sở hữu rõ ràng.**
2. **Income làm tăng balance, expense làm giảm balance.**
3. **Budget phải được kiểm tra ngay khi expense thay đổi.**
4. **Shared transaction chỉ hiển thị cho đúng thành viên nhóm.**

Sau khi chốt được tài liệu này, bước tiếp theo là vẽ use case, ERD và thiết kế schema logic chi tiết.

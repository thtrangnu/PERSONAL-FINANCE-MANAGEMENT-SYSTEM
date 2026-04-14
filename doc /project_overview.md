# Project Overview — Personal Finance Management System

## 1. Tên đề tài
**Project 13 — Personal Finance Management System**

Tên gợi ý cho sản phẩm:
- **Smart Finance Hub**
- **MyBudget Manager**
- **Personal Finance Tracker**

Trong tài liệu này, hệ thống sẽ được gọi thống nhất là:
**NUFI**.

---

## 2. Bối cảnh bài toán
Trong thực tế, rất nhiều người dùng cá nhân gặp khó khăn khi quản lý tài chính hằng ngày vì các lý do sau:
- Không ghi lại đầy đủ các khoản thu và chi.
- Không biết tiền đang nằm ở tài khoản ngân hàng nào.
- Không nắm được tổng chi tiêu theo ngày, tháng, năm.
- Không có kế hoạch ngân sách rõ ràng cho từng nhóm chi tiêu.
- Chỉ phát hiện chi tiêu vượt mức khi đã hết tiền.
- Không có báo cáo trực quan để đánh giá thói quen tài chính.
- Việc tổng hợp dữ liệu thủ công bằng Excel dễ sai sót, mất thời gian và khó mở rộng.

Từ bài toán đó, hệ thống NUFI được xây dựng nhằm cung cấp một nền tảng giúp người dùng:
- quản lý hồ sơ cá nhân,
- ghi nhận thu nhập và chi tiêu,
- theo dõi số dư tài khoản,
- lập ngân sách,
- nhận cảnh báo vượt ngưỡng,
- xem báo cáo dưới dạng bảng và biểu đồ,
- mở rộng sang quản lý nợ, nhóm chia sẻ tài chính, xuất báo cáo và đồng bộ đám mây.

---

## 3. Mục tiêu tổng quát của dự án
Hệ thống cần giải quyết được các nhu cầu cốt lõi sau:

1. **Quản lý người dùng**
   - Người dùng có thể đăng ký, đăng nhập, cập nhật hồ sơ.
   - Hệ thống phải đảm bảo dữ liệu tài chính của mỗi người là riêng biệt.

2. **Quản lý thu nhập và chi tiêu**
   - Người dùng có thể thêm, sửa, xóa, xem các khoản income/expense.
   - Có thể phân loại cả thu nhập và chi tiêu theo category.
   - Có thể gắn khoản thu/chi với bank account cụ thể.

3. **Theo dõi tài khoản ngân hàng / ví**
   - Người dùng có thể quản lý nhiều tài khoản.
   - Hệ thống cần phản ánh biến động số dư khi phát sinh giao dịch.

4. **Lập kế hoạch ngân sách**
   - Người dùng đặt ngân sách theo tháng hoặc theo category.
   - Hệ thống theo dõi mức sử dụng ngân sách và cảnh báo khi gần hoặc vượt hạn mức.

5. **Báo cáo và thống kê**
   - Cung cấp tổng hợp theo ngày/tháng/năm.
   - Hiển thị biểu đồ trực quan và bảng chi tiết.

6. **Yêu cầu cơ sở dữ liệu nâng cao**
   - Có sử dụng **indexes, views, procedures, functions, triggers**.
   - Có cơ chế về **security, backup, recovery**.

7. **Khả năng mở rộng**
   - Hỗ trợ quản lý nợ.
   - Hỗ trợ nhóm chia sẻ tài chính.
   - Hỗ trợ xuất Excel/PDF.
   - Hỗ trợ đồng bộ cloud.

---

## 4. Phạm vi dự án

### 4.1. In-scope (nằm trong phạm vi làm)
Các chức năng thuộc phạm vi chính thức của dự án gồm:

#### A. Tài khoản và hồ sơ người dùng
- Đăng ký tài khoản.
- Đăng nhập / đăng xuất.
- Quản lý hồ sơ cá nhân.
- Đổi mật khẩu.
- Khóa / mở tài khoản ở mức quản trị.

#### B. Quản lý thu nhập
- Thêm khoản thu nhập.
- Sửa khoản thu nhập.
- Xóa khoản thu nhập.
- Xem danh sách khoản thu nhập.
- Lọc theo thời gian, loại, tài khoản.

#### C. Quản lý chi tiêu
- Thêm khoản chi tiêu.
- Sửa khoản chi tiêu.
- Xóa khoản chi tiêu.
- Xem danh sách khoản chi.
- Gắn category cho expense.
- Lọc theo category, thời gian, bank account.

#### D. Quản lý danh mục thu nhập và chi tiêu
- Tạo category cá nhân.
- Sửa category.
- Kích hoạt/vô hiệu hóa category.
- Chọn loại category cho income / expense / both.
- Gắn màu, biểu tượng, mô tả.

#### E. Quản lý tài khoản ngân hàng / ví tiền
- Tạo bank account.
- Chỉnh sửa thông tin tài khoản.
- Theo dõi số dư hiện tại.
- Theo dõi lịch sử giao dịch liên quan.

#### F. Quản lý ngân sách
- Tạo ngân sách tổng theo tháng.
- Tạo ngân sách theo category.
- Theo dõi mức đã dùng, còn lại, % sử dụng.
- Sinh cảnh báo khi sắp/vượt ngưỡng.

#### G. Báo cáo
- Tổng hợp theo ngày.
- Tổng hợp theo tháng.
- Tổng hợp theo năm.
- Báo cáo dạng bảng.
- Báo cáo dạng biểu đồ.

#### H. Chức năng mở rộng ưu tiên sau lõi
- Quản lý nợ.
- Nhóm chia sẻ tài chính.
- Xuất báo cáo.
- Đồng bộ cloud.

#### I. Hạ tầng và triển khai
- Backend: Django.
- Database: MySQL.
- Container hóa bằng Docker.
- Airflow cho các tác vụ nền / đồng bộ / backup / tổng hợp định kỳ.
- AWS cho triển khai cloud.

---

### 4.2. Out-of-scope (chưa làm trong giai đoạn đầu)
Những nội dung dưới đây **không ưu tiên ở bản đầu tiên** hoặc chỉ để dự phòng mở rộng:
- Tích hợp thanh toán điện tử trực tiếp với ngân hàng.
- Đồng bộ số dư ngân hàng theo API real-time.
- OCR hóa đơn tự động bằng AI.
- Dự báo tài chính nâng cao bằng Machine Learning.
- Chatbot tư vấn tài chính.
- Hỗ trợ đa tiền tệ với tỷ giá real-time.
- Mobile app native riêng cho iOS/Android.
- Phân tích đầu tư, cổ phiếu, crypto.

---

## 5. Các nhóm người dùng chính
Hệ thống có 3 actor chính:

### 5.1. Guest
Người chưa đăng nhập vào hệ thống.
Quyền chính:
- Xem landing page.
- Đăng ký.
- Đăng nhập.
- Xem một số thông tin giới thiệu hệ thống.

### 5.2. User
Người dùng đã đăng nhập.
Quyền chính:
- Quản lý dữ liệu tài chính của **chính mình**.
- Tạo/sửa/xóa income, expense, category, bank account, budget.
- Xem cảnh báo, báo cáo, dashboard.
- Theo dõi nợ cá nhân.
- Tham gia nhóm chia sẻ nếu có.

### 5.3. Admin
Người quản trị hệ thống.
Quyền chính:
- Quản lý người dùng.
- Quản lý category hệ thống mặc định.
- Xem log hoạt động.
- Theo dõi lỗi hệ thống.
- Kiểm tra backup, phục hồi, vận hành dữ liệu.

---

## 6. Giá trị mà hệ thống mang lại

### 6.1. Đối với người dùng cá nhân
- Biết tiền đi đâu về đâu mỗi ngày.
- Kiểm soát tốt thói quen chi tiêu.
- Có cảnh báo trước khi vượt ngân sách.
- Dễ đưa ra quyết định tài chính hơn.

### 6.2. Đối với việc học và làm project
- Bao quát đầy đủ các thành phần của một hệ thống quản lý dữ liệu thực tế.
- Có cơ hội áp dụng cả backend, database, cloud, container, workflow scheduling.
- Dễ trình bày vì có quy trình nghiệp vụ rõ, dữ liệu rõ, báo cáo trực quan.
- Phù hợp để chứng minh năng lực thiết kế database, xây dựng API, bảo mật và triển khai.

---

## 7. Stack công nghệ được chốt

### 7.1. Django
Lý do chọn:
- Phát triển web nhanh.
- Có sẵn authentication, admin site, ORM.
- Phù hợp với mô hình CRUD nhiều module.
- Dễ tổ chức project theo app/module.

Vai trò trong dự án:
- Xử lý business logic.
- Xử lý xác thực người dùng.
- Tạo API hoặc render web UI.
- Kết nối với MySQL.

### 7.2. MySQL
Lý do chọn:
- Quan hệ rõ ràng, phù hợp bài toán tài chính.
- Dễ thiết kế khóa chính/khóa ngoại/index.
- Hỗ trợ view, procedure, function, trigger.
- Phù hợp yêu cầu môn học về CSDL.

Vai trò trong dự án:
- Lưu dữ liệu người dùng, giao dịch, ngân sách, cảnh báo, nhóm chia sẻ.
- Hỗ trợ truy vấn tổng hợp và báo cáo.

### 7.3. Docker
Lý do chọn:
- Môi trường chạy đồng nhất cho cả nhóm.
- Giảm lỗi “chạy được trên máy này nhưng không chạy trên máy kia”.
- Dễ đóng gói Django + MySQL + Airflow.

Vai trò trong dự án:
- Container hóa backend.
- Container hóa database.
- Container hóa Airflow nếu cần.

### 7.4. Airflow
Lý do chọn:
- Phù hợp các tác vụ định kỳ và workflow tự động.
- Có thể dùng cho backup, tổng hợp báo cáo định kỳ, sync cloud, gửi alert nền.

Vai trò trong dự án:
- Chạy job hằng ngày/hằng tháng.
- Tạo snapshot, backup dữ liệu.
- Tổng hợp báo cáo định kỳ.
- Kiểm tra budget threshold và sinh alert tự động.

### 7.5. AWS
Lý do chọn:
- Có thể triển khai thật trên cloud.
- Phù hợp nếu muốn demo production-like.
- Có thể kết hợp EC2, RDS, S3.

Vai trò trong dự án:
- EC2: host ứng dụng Django/Airflow.
- RDS hoặc MySQL tự host: lưu trữ DB.
- S3: lưu backup, file export.

---

## 8. Tính năng mở rộng đã chốt

### 8.1. Debt Tracking
Cho phép người dùng:
- ghi lại khoản mình đang nợ,
- khoản người khác nợ mình,
- kỳ hạn thanh toán,
- lịch sử trả nợ,
- trạng thái đã trả / còn nợ / quá hạn.

### 8.2. Sharing Groups
Cho phép nhóm người dùng:
- tạo group,
- mời thành viên,
- chia sẻ một số giao dịch,
- cùng theo dõi chi tiêu nhóm.

### 8.3. Export Excel/PDF
Cho phép xuất:
- báo cáo tháng,
- chi tiết income/expense,
- ngân sách,
- tổng hợp biểu đồ và bảng.

### 8.4. Cloud Sync
Cho phép:
- đồng bộ dữ liệu lên cloud,
- backup định kỳ,
- hỗ trợ phục hồi khi có sự cố.

---

## 9. Kiến trúc tổng quan mức cao
Kiến trúc đề xuất:

**Frontend/UI**
- Django templates hoặc Django + REST API + frontend tách rời.

**Backend**
- Django apps theo module:
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

**Database**
- MySQL relational database.
- Chuẩn hóa bảng, PK/FK rõ ràng.
- Có view/procedure/function/trigger.

**Scheduler / background jobs**
- Airflow.
- Chạy backup, sync, alert checks, monthly summary jobs.

**Infrastructure**
- Docker Compose cho local.
- AWS cho triển khai cloud.

---

## 10. Luồng nghiệp vụ tổng quát của hệ thống

### 10.1. Luồng cơ bản của người dùng
1. Người dùng đăng ký hoặc đăng nhập.
2. Người dùng cập nhật hồ sơ và tạo bank account.
3. Người dùng tạo category nếu cần.
4. Người dùng nhập income và expense.
5. Hệ thống cập nhật số dư tài khoản tương ứng.
6. Người dùng tạo budget cho tháng hoặc category.
7. Khi phát sinh chi tiêu, hệ thống so sánh với budget.
8. Nếu gần hoặc vượt ngưỡng, hệ thống sinh alert.
9. Người dùng xem dashboard, bảng thống kê, biểu đồ.
10. Người dùng có thể xuất báo cáo hoặc theo dõi nợ / nhóm chia sẻ.

### 10.2. Luồng quản trị
1. Admin đăng nhập vào vùng quản trị.
2. Kiểm tra user, log, category mặc định.
3. Kiểm tra backup và tác vụ nền.
4. Theo dõi lỗi hệ thống và bảo mật.

---

## 11. Yêu cầu phi chức năng tổng quát
Hệ thống không chỉ cần chạy đúng chức năng mà còn phải đảm bảo các tiêu chí sau:

### 11.1. Bảo mật
- Mỗi user chỉ xem được dữ liệu của mình.
- Không lộ thông tin tài chính giữa các tài khoản khác nhau.
- Mật khẩu phải được băm an toàn.
- API và form phải chống truy cập trái phép.

### 11.2. Toàn vẹn dữ liệu
- Mọi transaction phải gắn đúng user.
- Khóa ngoại và ràng buộc phải được thiết kế chặt chẽ.
- Trigger/procedure không được làm sai số dư.

### 11.3. Hiệu năng
- Có index cho các cột tìm kiếm nhiều.
- Báo cáo tháng/năm phải trả kết quả hợp lý với dữ liệu tăng dần.

### 11.4. Khả năng phục hồi
- Có backup định kỳ.
- Có tài liệu recovery.
- Có thể khôi phục dữ liệu khi hệ thống lỗi.

### 11.5. Khả năng mở rộng
- Có thể thêm module mới mà không phá cấu trúc cũ.
- Có thể triển khai cloud và scale trong tương lai.

---

## 12. Kết quả kỳ vọng của bản đầu tiên (MVP)
Bản đầu tiên nên tập trung làm tốt các phần sau:
- Đăng ký / đăng nhập / hồ sơ người dùng.
- Quản lý income.
- Quản lý expenses.
- Quản lý categories.
- Quản lý bank accounts.
- Quản lý budgets.
- Dashboard cơ bản.
- Báo cáo ngày/tháng/năm.
- Alert cơ bản khi vượt budget.

Đây là phần đủ mạnh để:
- demo nghiệp vụ,
- chứng minh schema database,
- trình bày use case,
- trình diễn CRUD + báo cáo,
- mở rộng thêm module sau.

---

## 13. Tiêu chí đánh giá thành công của project
Dự án được xem là thành công khi đạt các tiêu chí sau:

### 13.1. Về chức năng
- User có thể quản lý dữ liệu tài chính cá nhân trọn vẹn.
- Hệ thống tạo được báo cáo và alert có ý nghĩa.
- Quyền truy cập giữa các actor là chính xác.

### 13.2. Về dữ liệu
- Schema hợp lý, chuẩn hóa, có PK/FK/index.
- View/procedure/function/trigger được dùng đúng mục đích.
- Không có lỗi dữ liệu xuyên user.

### 13.3. Về kỹ thuật
- Chạy được bằng Docker.
- Có thể kết nối MySQL ổn định.
- Có Airflow cho ít nhất một số job nền.
- Có hướng triển khai lên AWS.

### 13.4. Về trình bày đồ án
- Tài liệu rõ ràng.
- Có use case, ERD, schema.
- Có minh họa giao diện và luồng chạy.
- Có demo dữ liệu thực tế mô phỏng đủ thuyết phục.

---

## 14. Kết luận
NUFI là một đề tài có phạm vi rõ, gần với bài toán thực tế, và phù hợp để triển khai thành một hệ thống web quản lý tài chính cá nhân hoàn chỉnh. Với stack đã chốt gồm **Django + MySQL + Docker + Airflow + AWS**, nhóm có thể xây dựng một sản phẩm vừa đáp ứng yêu cầu môn học về cơ sở dữ liệu, vừa thể hiện năng lực thiết kế hệ thống phần mềm hiện đại.

Trong giai đoạn đầu, dự án sẽ tập trung vào các chức năng lõi như profile, income, expenses, categories, bank accounts, budgets và reports. Sau khi lõi đã ổn định, nhóm sẽ mở rộng sang debt tracking, sharing groups, export và cloud sync.

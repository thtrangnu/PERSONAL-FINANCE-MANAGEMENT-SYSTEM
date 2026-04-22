# NUFI

NUFI là hệ thống quản lý tài chính cá nhân chạy bằng Django và MySQL. Repo đã được chuẩn bị để chạy local bằng Docker Compose, dùng chung MySQL local trên máy Mac, và có CI/CD bằng GitHub Actions.

## Trọng Tâm Database Của Dự Án

Đây là project môn **Hệ quản trị cơ sở dữ liệu**, nên database không chỉ là nơi lưu dữ liệu cho web mà là phần cốt lõi của toàn bộ hệ thống.

Trong dự án này:

- Hệ quản trị CSDL chính là **MySQL 8**.
- Cơ sở dữ liệu quản lý các thực thể chính như:
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
- Thiết kế dữ liệu có sử dụng:
  - **Primary Key**
  - **Foreign Key**
  - **CHECK**
  - **UNIQUE**
  - **NOT NULL**
  - **INDEX**
  - **VIEW**
  - **FUNCTION**
  - **PROCEDURE**
  - **TRIGGER**
- Hệ thống còn mở rộng sang các nội dung gần với vận hành thực tế như:
  - backup / restore
  - scheduled jobs
  - monitoring
  - alerting

Nếu nhìn theo đúng tinh thần môn DBMS, repo này có 3 lớp chính:

1. **Thiết kế dữ liệu**
   - ERD
   - lược đồ quan hệ
   - business rules
   - phân quyền dữ liệu

2. **Cài đặt SQL**
   - schema
   - views
   - functions
   - procedures
   - triggers
   - indexes
   - sample data

3. **Tích hợp và khai thác dữ liệu**
   - Django đọc/ghi dữ liệu từ MySQL
   - dashboard, reports, alerts
   - CronJob, backup, monitoring

Các tài liệu database quan trọng nhất:

- [project-overview.md](/Users/thuytrangneee/DBMS/PERSONAL-FINANCE-MANAGEMENT-SYSTEM/docs/specifications/project-overview.md)
- [business-rules.md](/Users/thuytrangneee/DBMS/PERSONAL-FINANCE-MANAGEMENT-SYSTEM/docs/specifications/business-rules.md)
- [relational-schema.md](/Users/thuytrangneee/DBMS/PERSONAL-FINANCE-MANAGEMENT-SYSTEM/docs/specifications/relational-schema.md)
- [system-requirements.md](/Users/thuytrangneee/DBMS/PERSONAL-FINANCE-MANAGEMENT-SYSTEM/docs/specifications/system-requirements.md)

## Hướng Dẫn Chạy Nhanh

Nếu muốn chạy nhanh dự án bằng Docker Compose, làm theo thứ tự này:

1. Lấy source code về máy:

```bash
git clone https://github.com/thtrangnu/PERSONAL-FINANCE-MANAGEMENT-SYSTEM.git
cd PERSONAL-FINANCE-MANAGEMENT-SYSTEM
```

2. Tạo file cấu hình môi trường cho Docker:

```bash
cp .env.docker.example .env.docker
```

3. Chạy Docker Compose:

```bash
docker compose --env-file .env.docker up --build -d
```

4. Mở web:

```text
http://127.0.0.1:8001/
```

## Chạy Local Bằng Django Trên Cổng 8000

Nếu muốn chạy trực tiếp bằng Django thay vì Docker, có thể dùng một trong hai cách dưới đây.

### Cách 1. Chạy local nhanh nhất bằng SQLite

1. Tạo môi trường ảo và cài thư viện:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Chạy migrate với SQLite:

```bash
DB_ENGINE=sqlite python manage.py migrate
```

3. Mở web local ở cổng `8000`:

```bash
DB_ENGINE=sqlite python manage.py runserver 127.0.0.1:8000
```

4. Truy cập:

```text
http://127.0.0.1:8000/
```

### Cách 2. Chạy local với MySQL

1. Tạo file môi trường:

```bash
cp .env.example .env
```

2. Chỉnh `.env` cho đúng MySQL local của bạn, ví dụ:

```env
DB_ENGINE=mysql
DB_NAME=pfms
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=127.0.0.1
DB_PORT=3306
```

3. Chạy migrate:

```bash
python manage.py migrate
```

4. Mở web local ở cổng `8000`:

```bash
python manage.py runserver 127.0.0.1:8000
```

5. Truy cập:

```text
http://127.0.0.1:8000/
```

## Cấu Trúc Thư Mục Dự Án

Các thư mục chính trong repo:

```text
PERSONAL-FINANCE-MANAGEMENT-SYSTEM/
├── apps/                  # Các app nghiệp vụ: accounts, income, expenses, budgets, debts...
├── config/                # Cấu hình Django, urls, wsgi/asgi, settings
├── templates/             # Giao diện HTML dùng cho toàn hệ thống
├── sql/                   # Schema, view, function, procedure, trigger, sample data cho MySQL
├── docker/                # Script khởi động container
├── deploy/                # Helm chart, monitoring, version config
├── docs/
│   ├── architecture/      # Sơ đồ và mô tả luồng chạy hệ thống
│   ├── deployment/        # Hướng dẫn triển khai Docker/Kubernetes/Cloudflare
│   ├── operations/        # Backup/restore, checklist demo, tài liệu vận hành
│   └── specifications/    # Overview, business rules, schema, module, phân quyền
├── scripts/               # Smoke test, alert watcher và script hỗ trợ vận hành
├── image/                 # Hình ERD, schema minh họa
├── media/                 # Avatar/file upload local
├── generated_reports/     # Output report, backup/export sinh ra khi chạy job
├── .github/workflows/     # CI/CD bằng GitHub Actions
├── Dockerfile             # Docker image cho Django + Gunicorn
├── docker-compose.yml     # Chạy local bằng Docker Compose
├── requirements.txt       # Python dependencies
└── manage.py              # Entrypoint chính của Django
```

## Chạy Local Bằng Docker

Project có file `.env.docker` riêng cho container, không ghi đè `.env` local. Mặc định `docker-compose.yml` chạy đủ `web + db`.

```bash
docker compose --env-file .env.docker up --build -d
```

Nếu muốn Docker web dùng chung MySQL local trên máy Mac thay vì DB container, chỉnh `.env.docker`:

```env
DB_HOST=host.docker.internal
DB_USER=root
DB_PASSWORD=your_local_mysql_password
DB_PORT=3306
DB_NAME=pfms
```

Sau khi container chạy xong:

- Web Django: http://127.0.0.1:8001
- Django admin: http://127.0.0.1:8001/admin/

Tài khoản admin demo được tạo tự động khi chạy Docker nếu `.env.docker` giữ nguyên:

- Username: `admin`
- Password: `admin12345`

Nếu muốn quay lại DB container cho demo độc lập, dùng:

```bash
DB_HOST=db
DB_USER=nufi
DB_PASSWORD=nufi_password
```

## Biến Môi Trường

Tạo file `.env` khi chạy local không dùng Docker, hoặc `.env.docker` khi chạy bằng Docker Compose. Các biến chính:

- `SECRET_KEY`: khóa bí mật của Django.
- `DEBUG`: `True` khi dev, `False` khi deploy.
- `ALLOWED_HOSTS`: danh sách host được phép truy cập, cách nhau bằng dấu phẩy.
- `DB_ENGINE`: `mysql` hoặc `sqlite`.
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`: thông tin kết nối database.
- `DB_UNIX_SOCKET`: dùng khi cần kết nối MySQL qua Unix socket.
- `GS_BUCKET_NAME`: để trống nếu không dùng upload report ra storage ngoài.
- `REPORT_OUTPUT_DIR`: thư mục lưu report/job output local, mặc định `generated_reports`.
- `GOOGLE_OAUTH_CLIENT_ID`, `GOOGLE_OAUTH_CLIENT_SECRET`: dùng cho đăng nhập Google.

## Đăng Nhập Google Khi Chạy Local/Docker/Kubernetes

Google OAuth kiểm tra callback URL rất chặt. Port nào đang mở web thì phải thêm đúng callback URL đó trong Google Cloud Console.

Authorized JavaScript origins nên thêm:

```text
http://127.0.0.1:8000
http://127.0.0.1:8001
http://127.0.0.1:8002
```

Authorized redirect URIs nên thêm:

```text
http://127.0.0.1:8000/accounts/google/login/callback/
http://127.0.0.1:8001/accounts/google/login/callback/
http://127.0.0.1:8002/accounts/google/login/callback/
```

Nếu Docker đang chạy bằng cấu hình mặc định trong repo thì callback thực tế là:

```text
http://127.0.0.1:8001/accounts/google/login/callback/
```

Nếu Kubernetes đang mở bằng port-forward `8002:80` thì callback thực tế là:

```text
http://127.0.0.1:8002/accounts/google/login/callback/
```

Lệnh cố định nên dùng để mở web trên Kubernetes:

```bash
kubectl -n nufi port-forward svc/nufi 8002:80
```

Nên mở web bằng `127.0.0.1` thay vì `localhost` khi test Google:

```text
http://127.0.0.1:8001/login/
http://127.0.0.1:8002/login/
```

Nếu lỡ mở bằng `localhost`, nút Google trong NUFI sẽ tự chuyển sang `127.0.0.1` để tránh lỗi `redirect_uri_mismatch`.

## Lệnh Django Hay Dùng

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Trong Docker:

```bash
docker compose --env-file .env.docker exec web python manage.py migrate
docker compose --env-file .env.docker exec web python manage.py createsuperuser
```

## Chạy SQL Thủ Công

Repo có sẵn bộ script MySQL trong thư mục [sql/](/Users/thuytrangneee/DBMS/PERSONAL-FINANCE-MANAGEMENT-SYSTEM/sql) để phục vụ học phần CSDL, minh họa schema, view, procedure, function, trigger và sample data.

Lưu ý quan trọng:

- File [schema.sql](/Users/thuytrangneee/DBMS/PERSONAL-FINANCE-MANAGEMENT-SYSTEM/sql/schema.sql) có `DROP DATABASE IF EXISTS pfms;`, nên sẽ xóa và tạo lại database `pfms`.
- Chỉ chạy bộ script này khi bạn muốn dựng lại database từ đầu.
- Ứng dụng Django hằng ngày vẫn ưu tiên chạy bằng `python manage.py migrate`.

Thứ tự chạy SQL khuyến nghị:

1. [schema.sql](/Users/thuytrangneee/DBMS/PERSONAL-FINANCE-MANAGEMENT-SYSTEM/sql/schema.sql)
2. [functions.sql](/Users/thuytrangneee/DBMS/PERSONAL-FINANCE-MANAGEMENT-SYSTEM/sql/functions.sql)
3. [triggers.sql](/Users/thuytrangneee/DBMS/PERSONAL-FINANCE-MANAGEMENT-SYSTEM/sql/triggers.sql)
4. [views.sql](/Users/thuytrangneee/DBMS/PERSONAL-FINANCE-MANAGEMENT-SYSTEM/sql/views.sql)
5. [procedures.sql](/Users/thuytrangneee/DBMS/PERSONAL-FINANCE-MANAGEMENT-SYSTEM/sql/procedures.sql)
6. [indexes.sql](/Users/thuytrangneee/DBMS/PERSONAL-FINANCE-MANAGEMENT-SYSTEM/sql/indexes.sql)
7. [sample_data.sql](/Users/thuytrangneee/DBMS/PERSONAL-FINANCE-MANAGEMENT-SYSTEM/sql/sample_data.sql)

Ví dụ chạy bằng MySQL local:

```bash
mysql -u root -p < sql/schema.sql
mysql -u root -p < sql/functions.sql
mysql -u root -p < sql/triggers.sql
mysql -u root -p < sql/views.sql
mysql -u root -p < sql/procedures.sql
mysql -u root -p < sql/indexes.sql
mysql -u root -p < sql/sample_data.sql
```

Nếu đang dùng MySQL container trong Docker Compose:

```bash
docker compose --env-file .env.docker exec -T db mysql -unufi -pnufi_password < sql/schema.sql
docker compose --env-file .env.docker exec -T db mysql -unufi -pnufi_password < sql/functions.sql
docker compose --env-file .env.docker exec -T db mysql -unufi -pnufi_password < sql/triggers.sql
docker compose --env-file .env.docker exec -T db mysql -unufi -pnufi_password < sql/views.sql
docker compose --env-file .env.docker exec -T db mysql -unufi -pnufi_password < sql/procedures.sql
docker compose --env-file .env.docker exec -T db mysql -unufi -pnufi_password < sql/indexes.sql
docker compose --env-file .env.docker exec -T db mysql -unufi -pnufi_password < sql/sample_data.sql
```

Nếu bạn chỉ muốn dựng web để chạy ứng dụng Django, không cần chạy toàn bộ script SQL ở trên. Chỉ cần:

```bash
python manage.py migrate
```

## Tài Liệu Database

Nếu bạn đọc repo theo hướng học phần DBMS, nên đi theo thứ tự này:

1. Xem tổng quan bài toán và phạm vi dữ liệu:

```text
docs/specifications/project-overview.md
```

2. Xem các luật nghiệp vụ chi phối dữ liệu:

```text
docs/specifications/business-rules.md
```

3. Xem module nghiệp vụ để hiểu dữ liệu được dùng ở đâu:

```text
docs/specifications/modules.md
```

4. Xem lược đồ quan hệ, chuẩn hóa, ERD rút gọn, PK/FK và các SQL object:

```text
docs/specifications/relational-schema.md
```

5. Xem yêu cầu chức năng và phi chức năng gắn với dữ liệu:

```text
docs/specifications/system-requirements.md
```

6. Sau đó mới đi vào phần script SQL thực thi:

```text
sql/schema.sql
sql/functions.sql
sql/triggers.sql
sql/views.sql
sql/procedures.sql
sql/indexes.sql
sql/sample_data.sql
```

Nếu cần viết bài luận hoặc báo cáo môn DBMS, 2 tài liệu quan trọng nhất để bắt đầu là:

- [relational-schema.md](/Users/thuytrangneee/DBMS/PERSONAL-FINANCE-MANAGEMENT-SYSTEM/docs/specifications/relational-schema.md)
- [system-requirements.md](/Users/thuytrangneee/DBMS/PERSONAL-FINANCE-MANAGEMENT-SYSTEM/docs/specifications/system-requirements.md)

## Kiểm Tra Luồng Chính

Sau khi web lên, kiểm tra nhanh:

1. Đăng nhập hoặc tạo tài khoản mới.
2. Tạo tài khoản tiền ở trang Tài khoản.
3. Thêm khoản thu ở trang Thu nhập.
4. Thêm khoản chi ở trang Chi tiêu.
5. Tạo ngân sách và nhập chi tiêu vượt ngưỡng để kiểm tra cảnh báo.
6. Vào Báo cáo để xem và xuất Excel/PDF.

## Tác Vụ Định Kỳ

Project không dùng Airflow. Các tác vụ định kỳ được tách thành Django management commands để chạy local hoặc trong Docker:

```bash
python manage.py daily_summary
python manage.py budget_alert_check
python manage.py backup_and_export
```

Trong Docker:

```bash
docker compose --env-file .env.docker exec web python manage.py daily_summary
docker compose --env-file .env.docker exec web python manage.py budget_alert_check
docker compose --env-file .env.docker exec web python manage.py backup_and_export
```

Output mặc định được lưu ở `generated_reports/` và không commit lên Git.

## CI/CD Không Dùng Cloud

Repo có sẵn:

- `.github/workflows/ci.yml`: chạy trên GitHub runner, bật MySQL service, cài dependencies, chạy `check`, `migrate`, 3 job định kỳ và build Docker image.
- `.github/workflows/cd.yml`: build image, push lên GitHub Container Registry; nếu bật biến repo `ENABLE_K8S_DEPLOY=true` thì deploy tiếp bằng Helm trên self-hosted runner.
- `.github/workflows/cd-local.yml`: chạy trên self-hosted runner, dùng Docker Compose để deploy lại web trên máy local/VPS.
- `.github/workflows/cd-kubernetes.yml`: chạy trên self-hosted runner có `kubectl` và `helm`, build image rồi deploy NUFI lên Kubernetes bằng Helm chart.
- `.github/workflows/daily-smoke.yml`: kiểm tra health/route hằng ngày khi có secret `SMOKE_BASE_URL`.

Luồng đề xuất nếu chỉ dùng branch `main`:

1. Push code lên `main` để chạy CI.
2. Nếu CI thành công, chạy workflow `CD Local` bằng nút `Run workflow`, hoặc để workflow tự chạy khi push lên `main`.
3. CD local cần GitHub self-hosted runner đang chạy trên máy muốn deploy.
4. Thêm GitHub Secrets cho CD local: `SECRET_KEY`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `GOOGLE_OAUTH_CLIENT_ID`, `GOOGLE_OAUTH_CLIENT_SECRET`.

Nếu chưa cài self-hosted runner, vào GitHub repo:

```text
Settings -> Actions -> Runners -> New self-hosted runner
```

Sau đó làm theo hướng dẫn GitHub đưa ra cho macOS.

## Kubernetes Và Monitoring

Repo có Helm chart tại:

```text
deploy/helm/nufi
```

Chart này gồm:

- `Deployment` cho Django + Gunicorn.
- `Service` và `Ingress` tùy chọn.
- `Job` chạy migration.
- `CronJob` cho `daily_summary`, `budget_alert_check`, `backup_and_export`.
- `CronJob` tùy chọn để dump MySQL ra file `.sql.gz`.
- `ServiceMonitor`, `PrometheusRule`, Grafana dashboard cho monitoring.
- PVC lưu `media/` và `generated_reports/`.

Khi chạy Kubernetes bằng Docker Desktop và muốn avatar dùng chung với local/Docker Compose, deploy thêm file local:

```bash
helm upgrade --install nufi deploy/helm/nufi \
  --namespace nufi \
  --reuse-values \
  -f deploy/helm/nufi/values-local.yaml
```

Để tránh mỗi lần đổi sang cổng khác, giữ cố định lệnh mở web Kubernetes:

```bash
kubectl -n nufi port-forward svc/nufi 8002:80
```

Sau đó luôn truy cập:

```text
http://127.0.0.1:8002/
```

Nếu báo cổng đang bận thì tắt terminal đang chạy port-forward cũ bằng `Ctrl + C`, rồi chạy lại đúng lệnh trên.

Tài liệu triển khai chi tiết nằm ở:

```text
docs/deployment/kubernetes.md
```

### Cách Mở Monitoring

Sau khi stack `monitoring` đã được cài trên Kubernetes, có thể mở các dịch vụ giám sát như sau:

1. Mở Grafana:

```bash
kubectl -n monitoring port-forward svc/monitoring-grafana 3000:80
```

Truy cập:

```text
http://127.0.0.1:3000/
```

2. Mở Prometheus:

```bash
kubectl -n monitoring port-forward svc/monitoring-kube-prometheus-prometheus 9090:9090
```

Truy cập:

```text
http://127.0.0.1:9090/
```

3. Mở Alertmanager:

```bash
kubectl -n monitoring port-forward svc/monitoring-kube-prometheus-alertmanager 9093:9093
```

Truy cập:

```text
http://127.0.0.1:9093/
```

4. Kiểm tra target của ứng dụng NUFI trong Prometheus:

```promql
up{job="nufi"}
```

Nếu target hoạt động đúng, giá trị sẽ là `1`.

5. Kiểm tra nhanh các metric của ứng dụng:

```promql
nufi_active_income_total
```

```promql
nufi_active_expenses_total
```

```promql
nufi_unread_alerts_total
```

6. Nếu muốn máy local nhận thông báo khi có alert mới:

```bash
.venv/bin/python scripts/alert_watcher.py
```

Hoặc chỉ kiểm tra một lần:

```bash
.venv/bin/python scripts/alert_watcher.py --once
```

### Dashboard Monitoring Của NUFI

Sau khi Grafana mở ở `3000`, bạn có thể:

- vào `Dashboards`
- tìm dashboard `NUFI Monitoring` hoặc `NUFI Monitoring Tổng Quan`

Dashboard này lấy dữ liệu trực tiếp từ Prometheus thông qua `ServiceMonitor` và `PrometheusRule` đã cấu hình trong Helm chart của dự án.

### Vai Trò Của Từng Thành Phần Monitoring

#### Prometheus

Prometheus là thành phần thu thập và lưu trữ metrics của hệ thống.

Trong dự án này, Prometheus có nhiệm vụ:

- scrape metrics từ ứng dụng NUFI qua endpoint `/metrics`
- lưu dữ liệu chuỗi thời gian để phục vụ query và biểu đồ
- đánh giá các `PrometheusRule`
- phát hiện các tình huống như:
  - app `DOWN`
  - scrape lỗi
  - chỉ số nghiệp vụ vượt ngưỡng
  - CPU hoặc RAM cao

Prometheus phù hợp nhất khi bạn cần:

- kiểm tra target có đang `UP` không
- query nhanh bằng `PromQL`
- xác minh dữ liệu monitoring của ứng dụng

#### Grafana

Grafana là thành phần hiển thị dữ liệu monitoring theo dạng trực quan.

Trong dự án này, Grafana có nhiệm vụ:

- kết nối Prometheus làm data source
- hiển thị dashboard cho NUFI
- trực quan hóa các metric như:
  - trạng thái ứng dụng
  - số lượng thu nhập / chi tiêu / ngân sách / cảnh báo
  - CPU / RAM
  - các biểu đồ xu hướng theo thời gian

Grafana phù hợp nhất khi bạn cần:

- xem nhanh tình trạng hệ thống
- trình bày dashboard khi demo
- theo dõi biến động dữ liệu mà không cần viết query nhiều

#### Alertmanager

Alertmanager là thành phần tiếp nhận và điều phối cảnh báo từ Prometheus.

Trong dự án này, Alertmanager có nhiệm vụ:

- nhận các alert đang firing từ Prometheus
- group alert lại để giảm spam
- deduplicate các alert trùng nhau
- áp dụng rule inhibit giữa `warning` và `critical`
- cung cấp API để `scripts/alert_watcher.py` đọc và bật thông báo trên máy local

Alertmanager phù hợp nhất khi bạn cần:

- kiểm tra hệ thống đang có alert nào
- xem luồng cảnh báo vận hành
- nối alert từ cluster về máy local để demo

#### Luồng hoạt động chung

Ba thành phần trên phối hợp với nhau theo luồng:

1. Ứng dụng NUFI expose `/metrics`
2. Prometheus scrape metrics từ ứng dụng
3. Prometheus đánh giá rule và phát hiện bất thường
4. Alertmanager nhận và quản lý cảnh báo
5. Grafana đọc dữ liệu từ Prometheus để hiển thị dashboard

Nói ngắn gọn:

- `Prometheus`: thu thập và phân tích số liệu
- `Grafana`: hiển thị số liệu cho người dùng
- `Alertmanager`: quản lý và điều phối cảnh báo

## Public Demo Bằng Cloudflare Tunnel

Khi cần chia sẻ nhanh web ra Internet để demo, có thể dùng `Cloudflare Tunnel`. Trong dự án này, Cloudflare chỉ đóng vai trò mở đường public tạm thời cho bản đang chạy trên máy local hoặc Kubernetes, không phải nền tảng deploy chính.

Nếu muốn mở `port-forward` và Cloudflare cùng lúc bằng một lệnh:

```bash
chmod +x scripts/run_public_demo.sh
./scripts/run_public_demo.sh
```

Script này sẽ:

- giữ cổng `8002` bằng `kubectl port-forward`
- tự đợi web phản hồi rồi mới mở Cloudflare
- dừng cả `port-forward` và `cloudflared` khi bạn nhấn `Ctrl + C`

Luồng chạy:

1. Mở web Kubernetes bằng cổng cố định:

```bash
kubectl -n nufi port-forward svc/nufi 8002:80
```

2. Ở terminal khác, chạy tunnel:

```bash
cloudflared tunnel --url http://127.0.0.1:8002
```

3. Cloudflare sẽ trả về một link dạng:

```text
https://random-name.trycloudflare.com
```

Lưu ý:

- Link `trycloudflare.com` là link tạm, có thể thay đổi mỗi lần chạy lại.
- Terminal `cloudflared` và terminal `port-forward` phải cùng còn chạy thì link public mới hoạt động.
- Nếu cần URL cố định cho demo hoặc OAuth, nên dùng `named tunnel` với domain riêng trên Cloudflare.
- Google OAuth không phù hợp với `Quick Tunnel` nếu callback URL thay đổi liên tục.

Nếu terminal báo `helm: command not found`, cài Helm trên macOS:

```bash
brew install helm
```

## Cổng Mặc Định

Các cổng thường dùng trong repo:

- `8000`: Django local chạy trực tiếp bằng `runserver`
- `8001`: Docker Compose
- `8002`: Kubernetes qua `kubectl port-forward svc/nufi 8002:80`
- `3000`: Grafana
- `9090`: Prometheus
- `9093`: Alertmanager

Nên giữ đúng các cổng trên khi demo để:

- Google OAuth callback không bị lệch
- smoke test và checklist demo không phải sửa lại
- Cloudflare Tunnel luôn trỏ đúng vào bản Kubernetes ở `8002`

## Troubleshooting

### Web không lên ở `8000`

- Kiểm tra môi trường ảo đã activate chưa.
- Nếu dùng SQLite, chạy lại:

```bash
DB_ENGINE=sqlite python manage.py migrate
DB_ENGINE=sqlite python manage.py runserver 127.0.0.1:8000
```

### Web không lên ở `8001`

- Kiểm tra container:

```bash
docker compose --env-file .env.docker ps
```

- Xem log web:

```bash
docker compose --env-file .env.docker logs -f web
```

### Web không lên ở `8002`

- Chạy lại port-forward:

```bash
kubectl -n nufi port-forward svc/nufi 8002:80
```

- Nếu cổng đang bận, dừng terminal `port-forward` cũ hoặc kill tiến trình cũ.

### Prometheus target `nufi` bị `DOWN`

- Mở Prometheus ở `9090`.
- Kiểm tra query:

```promql
up{job="nufi"}
```

- Nếu bằng `0`, kiểm tra:
  - pod `nufi` còn chạy không
  - `ServiceMonitor` đã apply chưa
  - `ALLOWED_HOSTS` có chặn pod IP hoặc tunnel host không

### Alertmanager / watcher không báo

- Kiểm tra Alertmanager đang mở ở `9093`.
- Chạy thử một lần:

```bash
.venv/bin/python scripts/alert_watcher.py --once
```

- Nếu cổng `9093` đang bận, đổi sang cổng khác:

```bash
kubectl -n monitoring port-forward svc/monitoring-kube-prometheus-alertmanager 9094:9093
.venv/bin/python scripts/alert_watcher.py --url http://127.0.0.1:9094/api/v2/alerts
```

### Cloudflare trả `502` hoặc `Bad Request`

- Kiểm tra terminal `cloudflared` còn chạy không.
- Kiểm tra terminal `kubectl -n nufi port-forward svc/nufi 8002:80` còn chạy không.
- Refresh lại link sau khi `8002` hoạt động lại.

## Tài Liệu Quan Trọng

File quản lý version app, data model và pipeline:

```text
deploy/versions/pipeline.yaml
```

Tài liệu backup/restore:

```text
docs/operations/backup-restore.md
```

Sơ đồ luồng chạy hệ thống:

```text
docs/architecture/system-flow.md
```

Checklist ảnh chụp/video để demo:

```text
docs/operations/demo-evidence-checklist.md
```

Tài liệu phân tích và thiết kế:

```text
docs/specifications/project-overview.md
docs/specifications/business-rules.md
docs/specifications/modules.md
docs/specifications/relational-schema.md
docs/specifications/roles-permissions.md
docs/specifications/system-requirements.md
```

## Lệnh Hữu Ích

```bash
docker compose --env-file .env.docker ps
docker compose --env-file .env.docker logs -f web
docker compose --env-file .env.docker down
docker compose --env-file .env.docker down -v
```

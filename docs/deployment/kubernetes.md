# NUFI Kubernetes Deployment

Thư mục này chứa cấu hình triển khai NUFI lên Kubernetes bằng Helm, kèm monitoring và backup định kỳ.

## Thành Phần

- `helm/nufi`: Helm chart cho Django web, migration job, scheduled jobs, backup jobs, ServiceMonitor và Grafana dashboard.
- `monitoring/kube-prometheus-stack-values.yaml`: cấu hình mẫu để cài Prometheus + Grafana bằng kube-prometheus-stack.
- `versions/pipeline.yaml`: nơi quản lý version app, data model và pipeline dữ liệu.

## Build Image

```bash
docker build -t nufi-web:0.1.0 .
```

Nếu máy báo `helm: command not found`, cài Helm trước:

```bash
brew install helm
```

Kiểm tra:

```bash
helm version
```

Nếu dùng Minikube:

```bash
minikube image load nufi-web:0.1.0
```

Nếu dùng Kind:

```bash
kind load docker-image nufi-web:0.1.0
```

## Cài Monitoring

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm upgrade --install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  -f deploy/monitoring/kube-prometheus-stack-values.yaml
```

## Triển Khai NUFI

Tạo namespace:

```bash
kubectl create namespace nufi
```

Deploy với Helm:

```bash
helm upgrade --install nufi deploy/helm/nufi \
  --namespace nufi \
  --reuse-values \
  -f deploy/helm/nufi/values-local.yaml \
  --set image.repository=nufi-web \
  --set image.tag=0.1.0 \
  --set externalDatabase.host=host.docker.internal \
  --set externalDatabase.name=pfms \
  --set externalDatabase.user=root \
  --set secret.dbPassword='YOUR_DB_PASSWORD' \
  --set secret.secretKey='YOUR_DJANGO_SECRET_KEY'
```

Nếu đã cài kube-prometheus-stack và muốn Prometheus scrape metrics:

```bash
helm upgrade --install nufi deploy/helm/nufi \
  --namespace nufi \
  --set monitoring.serviceMonitor.enabled=true \
  --set monitoring.prometheusRule.enabled=true
```

## Mở Web

```bash
kubectl -n nufi port-forward svc/nufi 8002:80
```

Mở:

```text
http://127.0.0.1:8002/
```

Nên giữ nguyên đúng lệnh trên mỗi lần chạy để Google callback và đường dẫn test không bị đổi cổng. Nếu cổng `8002` đang bận, dừng phiên port-forward cũ bằng `Ctrl + C` rồi chạy lại.

## Public Web Ra Internet Bằng Cloudflare

Nếu cần chia sẻ bản demo cho người khác truy cập từ Internet, có thể mở tunnel từ máy đang chạy Kubernetes:

1. Giữ terminal `port-forward`:

```bash
kubectl -n nufi port-forward svc/nufi 8002:80
```

2. Ở terminal khác, chạy:

```bash
cloudflared tunnel --url http://127.0.0.1:8002
```

3. Cloudflare sẽ in ra một URL public dạng:

```text
https://random-name.trycloudflare.com
```

Ghi chú:

- Đây là cách public nhanh để demo, không phải môi trường production chính thức.
- Nếu `port-forward` bị rớt thì link Cloudflare sẽ lỗi ngay, dù tunnel vẫn còn chạy.
- Nếu cần domain cố định cho Google OAuth hoặc demo lâu dài, nên dùng `named tunnel` và domain riêng trên Cloudflare.

## Kiểm Tra Monitoring

```bash
kubectl -n monitoring port-forward svc/monitoring-grafana 3000:80
```

Mở:

```text
http://127.0.0.1:3000
```

Tài khoản mặc định theo file mẫu:

```text
admin / admin
```

Dashboard NUFI sẽ được Grafana sidecar tự nhận nếu `monitoring.grafanaDashboard.enabled=true`.

Dashboard tổng quan dễ nhìn hơn cho NUFI:

```text
http://127.0.0.1:3000/d/nufi-monitoring
```

Dashboard này hiển thị nhanh:

- trạng thái ứng dụng có đang `up` hay không
- số alert đang kích hoạt
- số cảnh báo chưa đọc trong app
- số tài khoản, khoản thu, khoản chi, ngân sách đang theo dõi
- CPU, bộ nhớ và xu hướng alert theo thời gian

Muốn kiểm tra Prometheus scrape đúng app NUFI:

```bash
kubectl -n monitoring port-forward svc/monitoring-kube-prometheus-prometheus 9090:9090
```

Mở:

```text
http://127.0.0.1:9090/targets
```

Khi đúng, target `serviceMonitor/nufi/nufi/0` phải ở trạng thái `UP`.

## Bộ Alert Chuyên Nghiệp Hơn

NUFI hiện có 4 nhóm alert chính:

- `availability`: ứng dụng mất scrape hoặc endpoint metrics phản hồi chậm
- `stability`: pod restart lặp lại hoặc bị `OOMKilled`
- `resource`: CPU và bộ nhớ tăng cao theo 2 mức `warning` và `critical`
- `business`: số cảnh báo chưa đọc bị tồn đọng quá nhiều

Các alert mới đều có:

- `severity`: `warning` hoặc `critical`
- `category`: loại sự cố để dễ lọc trong Alertmanager
- `impact`: tác động dự kiến lên người dùng hoặc vận hành
- `action`: gợi ý xử lý ngắn gọn, đọc phát là làm được
- `dashboard_url`: trỏ về dashboard tổng quan của NUFI

Alertmanager cũng đã được chỉnh để:

- gom alert theo `namespace`, `alertname`, `severity`
- giảm spam bằng `group_wait`, `group_interval`, `repeat_interval`
- tự ẩn alert `warning` khi đã có alert `critical` cùng loại

Muốn xem các alert đang bắn:

```bash
kubectl -n monitoring port-forward svc/monitoring-kube-prometheus-alertmanager 9093:9093
```

Mở:

```text
http://127.0.0.1:9093/
```

## Cảnh Báo Về Máy

Nếu muốn máy của bạn bật thông báo khi NUFI có alert mới, mở Alertmanager:

```bash
kubectl -n monitoring port-forward svc/monitoring-kube-prometheus-alertmanager 9093:9093
```

Sau đó chạy watcher cục bộ:

```bash
.venv/bin/python scripts/alert_watcher.py
```

Tùy chọn hữu ích:

```bash
.venv/bin/python scripts/alert_watcher.py --once
.venv/bin/python scripts/alert_watcher.py --interval 10
.venv/bin/python scripts/alert_watcher.py --name-prefix Nufi
```

Trên macOS, script sẽ dùng Notification Center qua `osascript`. Trên Linux, script sẽ thử `notify-send`. Nếu không có cơ chế thông báo desktop, script vẫn in alert ra terminal để bạn theo dõi.

## Backup Dữ Liệu

Chart có 2 lớp backup:

- `backup-and-export`: chạy `python manage.py backup_and_export`, xuất CSV/manifest vào PVC `generated_reports`.
- `mysql-dump`: tùy chọn, chạy `mysqldump` ra file `.sql.gz`.

Bật SQL dump:

```bash
helm upgrade --install nufi deploy/helm/nufi \
  --namespace nufi \
  --set pipelines.mysqlDump.enabled=true
```

Chạy backup thủ công:

```bash
kubectl -n nufi create job --from=cronjob/nufi-backup-and-export nufi-backup-manual
```

Quy trình restore chi tiết:

```text
docs/operations/backup-restore.md
```

## Kiểm Thử Hằng Ngày

Chart có CronJob smoke test:

```bash
kubectl -n nufi get cronjob nufi-smoke-test
kubectl -n nufi create job --from=cronjob/nufi-smoke-test nufi-smoke-test-manual
kubectl -n nufi logs job/nufi-smoke-test-manual
```

## Quản Lý Version Và Cấu Hình Pipeline

File version chính nằm ở:

```text
deploy/versions/pipeline.yaml
```

Trong Helm, cùng thông tin này được đưa vào ConfigMap và mount vào pod tại:

```text
/app/config/runtime/pipeline-version.yaml
```

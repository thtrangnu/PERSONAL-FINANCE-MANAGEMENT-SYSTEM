# NUFI System Flow

Tài liệu này dùng để giải thích luồng chạy tổng thể khi demo hoặc viết báo cáo.

## Luồng Ứng Dụng

```mermaid
flowchart LR
    User["Người dùng"] --> Browser["Trình duyệt"]
    Browser --> Web["NUFI Django Web"]
    Web --> Auth["Đăng nhập / Đăng ký"]
    Web --> Finance["Thu nhập, chi tiêu, ngân sách, nợ, nhóm"]
    Finance --> DB["MySQL"]
    Web --> Reports["Excel / PDF / báo cáo"]
    Reports --> Files["generated_reports / PVC"]
    Web --> Metrics["/healthz và /metrics"]
```

## Luồng Docker Local

```mermaid
flowchart LR
    Dev["Developer"] --> Compose["docker compose up --build"]
    Compose --> Web["web container: Django + Gunicorn"]
    Compose --> DB["db container: MySQL 8"]
    Web --> Migrate["entrypoint migrate --fake-initial"]
    Web --> Static["collectstatic"]
    Web --> App["http://127.0.0.1:8001"]
    App --> Smoke["scripts/smoke_test.py"]
```

## Luồng CI/CD Trên Main

```mermaid
flowchart TD
    Push["Push code lên main"] --> CI["GitHub Actions CI"]
    CI --> Check["Django check"]
    CI --> Migrate["Migrate trên MySQL service"]
    CI --> Jobs["daily_summary / budget_alert_check / backup_and_export"]
    CI --> Build["Docker build"]
    Build --> GHCR["Push image lên GHCR"]
    GHCR --> CD{"ENABLE_K8S_DEPLOY=true?"}
    CD -- "Có" --> Helm["helm upgrade --install"]
    CD -- "Không" --> Done["Dừng ở build image"]
    Helm --> K8s["Kubernetes Deployment"]
```

## Luồng Kubernetes Và Monitoring

```mermaid
flowchart LR
    Helm["Helm Release"] --> Deploy["Deployment web"]
    Helm --> Service["Service"]
    Helm --> Ingress["Ingress nếu bật"]
    Helm --> Cron["CronJob pipeline và backup"]
    Helm --> Monitor["ServiceMonitor"]
    Deploy --> Metrics["/metrics"]
    Monitor --> Prometheus["Prometheus"]
    Prometheus --> Grafana["Grafana dashboard"]
    Prometheus --> Alerts["PrometheusRule alerts"]
```

## Luồng Backup Và Restore

```mermaid
flowchart TD
    Cron["CronJob backup"] --> Export["backup_and_export"]
    Cron --> Dump["mysqldump nếu bật"]
    Export --> ReportsPVC["PVC generated_reports"]
    Dump --> ReportsPVC
    ReportsPVC --> BackupFile["File backup có timestamp"]
    BackupFile --> Restore["Restore theo docs/operations/backup-restore.md"]
```


# NUFI System Flow

This document explains the overall system flow for demos and reports.

## Application Flow

```mermaid
flowchart LR
    User["User"] --> Browser["Browser"]
    Browser --> Web["NUFI Django Web"]
    Web --> Auth["Login / Register"]
    Web --> Finance["Income, Expenses, Budgets, Debts, Groups"]
    Finance --> DB["MySQL"]
    Web --> Reports["Excel / PDF / Reports"]
    Reports --> Files["generated_reports / PVC"]
    Web --> Metrics["/healthz and /metrics"]
```

## Local Docker Flow

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

## CI/CD Flow on Main

```mermaid
flowchart TD
    Push["Push code to main"] --> CI["GitHub Actions CI"]
    CI --> Check["Django check"]
    CI --> Migrate["Migrate on MySQL service"]
    CI --> Jobs["daily_summary / budget_alert_check / backup_and_export"]
    CI --> Build["Docker build"]
    Build --> GHCR["Push image to GHCR"]
    GHCR --> CD{"ENABLE_K8S_DEPLOY=true?"}
    CD -- "Yes" --> Helm["helm upgrade --install"]
    CD -- "No" --> Done["Stop at image build"]
    Helm --> K8s["Kubernetes Deployment"]
```

## Kubernetes and Monitoring Flow

```mermaid
flowchart LR
    Helm["Helm Release"] --> Deploy["web Deployment"]
    Helm --> Service["Service"]
    Helm --> Ingress["Ingress if enabled"]
    Helm --> Cron["CronJob pipeline and backup"]
    Helm --> Monitor["ServiceMonitor"]
    Deploy --> Metrics["/metrics"]
    Monitor --> Prometheus["Prometheus"]
    Prometheus --> Grafana["Grafana dashboard"]
    Prometheus --> Alerts["PrometheusRule alerts"]
```

## Backup and Restore Flow

```mermaid
flowchart TD
    Cron["CronJob backup"] --> Export["backup_and_export"]
    Cron --> Dump["mysqldump if enabled"]
    Export --> ReportsPVC["PVC generated_reports"]
    Dump --> ReportsPVC
    ReportsPVC --> BackupFile["Timestamped backup file"]
    BackupFile --> Restore["Restore via docs/operations/backup-restore.md"]
```

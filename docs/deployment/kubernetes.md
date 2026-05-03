# NUFI Kubernetes Deployment

This directory contains the configuration for deploying NUFI to Kubernetes via Helm, along with monitoring and scheduled backup.

## Components

- `helm/nufi`: Helm chart for the Django web app, migration job, scheduled jobs, backup jobs, ServiceMonitor, and Grafana dashboard.
- `monitoring/kube-prometheus-stack-values.yaml`: sample configuration for installing Prometheus + Grafana via kube-prometheus-stack.
- `versions/pipeline.yaml`: manages app version, data model, and data pipeline.

## Build Image

```bash
docker build -t nufi-web:0.1.0 .
```

If the terminal reports `helm: command not found`, install Helm first:

```bash
brew install helm
```

Verify:

```bash
helm version
```

If using Minikube:

```bash
minikube image load nufi-web:0.1.0
```

If using Kind:

```bash
kind load docker-image nufi-web:0.1.0
```

## Install Monitoring

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm upgrade --install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  -f deploy/monitoring/kube-prometheus-stack-values.yaml
```

## Deploy NUFI

Create namespace:

```bash
kubectl create namespace nufi
```

Deploy with Helm:

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

If kube-prometheus-stack is already installed and you want Prometheus to scrape metrics:

```bash
helm upgrade --install nufi deploy/helm/nufi \
  --namespace nufi \
  --set monitoring.serviceMonitor.enabled=true \
  --set monitoring.prometheusRule.enabled=true
```

## Open the Web App

```bash
kubectl -n nufi port-forward svc/nufi 8002:80
```

Open:

```text
http://127.0.0.1:8002/
```

Keep this exact command every time to avoid Google callback and test path port mismatches. If port `8002` is busy, stop the old port-forward session with `Ctrl + C` and re-run.

## Expose the Web Publicly via Cloudflare

To share the demo with external users over the Internet:

1. Keep the `port-forward` terminal open:

```bash
kubectl -n nufi port-forward svc/nufi 8002:80
```

2. In another terminal, start the tunnel:

```bash
cloudflared tunnel --url http://127.0.0.1:8002
```

3. Cloudflare will print a public URL like:

```text
https://random-name.trycloudflare.com
```

Notes:

- This is a quick public method for demos, not the primary production environment.
- If `port-forward` drops, the Cloudflare link will fail even if the tunnel is still running.
- For a stable domain for Google OAuth or long-running demos, use a `named tunnel` with a custom Cloudflare domain.

## Check Monitoring

```bash
kubectl -n monitoring port-forward svc/monitoring-grafana 3000:80
```

Open:

```text
http://127.0.0.1:3000
```

Default credentials from the sample file:

```text
admin / admin
```

The NUFI dashboard is auto-imported by Grafana sidecar if `monitoring.grafanaDashboard.enabled=true`.

Main overview dashboard:

```text
http://127.0.0.1:3000/d/nufi-monitoring
```

This dashboard displays:

- whether the application is `up`
- number of active firing alerts
- number of unread in-app alerts
- counts of accounts, income, expenses, and budgets
- CPU, memory, and alert trends over time

To verify Prometheus is scraping the NUFI app correctly:

```bash
kubectl -n monitoring port-forward svc/monitoring-kube-prometheus-prometheus 9090:9090
```

Open:

```text
http://127.0.0.1:9090/targets
```

When correct, the target `serviceMonitor/nufi/nufi/0` must show `UP` status.

## Alert Groups

NUFI currently has 4 main alert groups:

- `availability`: application loses scrape or metrics endpoint responds slowly
- `stability`: pod restarts repeatedly or is `OOMKilled`
- `resource`: CPU and memory rise to high levels at two thresholds — `warning` and `critical`
- `business`: too many unread in-app alerts are accumulating

All alerts include:

- `severity`: `warning` or `critical`
- `category`: incident type for easy filtering in Alertmanager
- `impact`: expected impact on users or operations
- `action`: short remediation suggestion — read and act immediately
- `dashboard_url`: link to the NUFI overview dashboard

Alertmanager is also configured to:

- group alerts by `namespace`, `alertname`, `severity`
- reduce spam via `group_wait`, `group_interval`, `repeat_interval`
- auto-suppress `warning` alerts when a `critical` alert of the same type is firing

To view currently firing alerts:

```bash
kubectl -n monitoring port-forward svc/monitoring-kube-prometheus-alertmanager 9093:9093
```

Open:

```text
http://127.0.0.1:9093/
```

## Desktop Alert Notifications

To receive desktop notifications when NUFI has new alerts, open Alertmanager:

```bash
kubectl -n monitoring port-forward svc/monitoring-kube-prometheus-alertmanager 9093:9093
```

Then run the local watcher:

```bash
.venv/bin/python scripts/alert_watcher.py
```

Useful options:

```bash
.venv/bin/python scripts/alert_watcher.py --once
.venv/bin/python scripts/alert_watcher.py --interval 10
.venv/bin/python scripts/alert_watcher.py --name-prefix Nufi
```

On macOS, the script uses Notification Center via `osascript`. On Linux, it tries `notify-send`. If no desktop notification mechanism is available, the script still prints alerts to the terminal.

## Data Backup

The chart has 2 backup layers:

- `backup-and-export`: runs `python manage.py backup_and_export`, exports CSV/manifest into the `generated_reports` PVC.
- `mysql-dump`: optional, runs `mysqldump` to a `.sql.gz` file.

Enable SQL dump:

```bash
helm upgrade --install nufi deploy/helm/nufi \
  --namespace nufi \
  --set pipelines.mysqlDump.enabled=true
```

Run a manual backup:

```bash
kubectl -n nufi create job --from=cronjob/nufi-backup-and-export nufi-backup-manual
```

Detailed restore procedure:

```text
docs/operations/backup-restore.md
```

## Daily Smoke Testing

The chart includes a smoke test CronJob:

```bash
kubectl -n nufi get cronjob nufi-smoke-test
kubectl -n nufi create job --from=cronjob/nufi-smoke-test nufi-smoke-test-manual
kubectl -n nufi logs job/nufi-smoke-test-manual
```

## Version and Pipeline Configuration Management

The main version file:

```text
deploy/versions/pipeline.yaml
```

In Helm, the same information is placed into a ConfigMap and mounted into the pod at:

```text
/app/config/runtime/pipeline-version.yaml
```

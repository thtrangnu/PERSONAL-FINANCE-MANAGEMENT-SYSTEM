# Demo Evidence Checklist

Use this checklist to capture screenshots or short video clips when demoing.

## Day 25: Docker and CI

- Docker image builds successfully: `docker build -t nufi-web:test .`
- Docker Compose is running: `docker compose --env-file .env.docker ps`
- Web is accessible: `http://127.0.0.1:8001`
- Smoke test passes: `SMOKE_BASE_URL=http://127.0.0.1:8001 python scripts/smoke_test.py`
- GitHub Actions CI passes after pushing to `main`.

## Day 26: Kubernetes, Helm, Monitoring

- Helm chart lint passes: `helm lint deploy/helm/nufi`
- Helm template renders: `helm template nufi deploy/helm/nufi --namespace nufi`
- Helm release deploys successfully: `helm list -n nufi`
- Pod/Service/Ingress running: `kubectl -n nufi get pods,svc,ingress`
- Prometheus scrapes `/metrics` successfully.
- Grafana dashboard shows panels for Web Up, CPU, Memory, and business record counts.

## Day 27: Version, Backup, Daily Testing

- Version/config file exists: `deploy/versions/pipeline.yaml`
- Pipeline CronJob exists: `kubectl -n nufi get cronjob`
- Backup job runs successfully: `kubectl -n nufi logs job/<backup-job-name>`
- Backup files with timestamps are present in PVC or the `generated_reports` directory.
- Daily smoke test passes via GitHub Actions or Kubernetes CronJob.
- Restore documentation is available: `docs/operations/backup-restore.md`.

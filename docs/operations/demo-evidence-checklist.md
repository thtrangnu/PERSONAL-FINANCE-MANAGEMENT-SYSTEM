# Demo Evidence Checklist

Dùng checklist này để chụp ảnh màn hình hoặc quay video ngắn khi demo.

## Ngày 25: Docker Và CI

- Docker image build thành công: `docker build -t nufi-web:test .`
- Docker Compose đang chạy: `docker compose --env-file .env.docker ps`
- Web mở được: `http://127.0.0.1:8001`
- Smoke test pass: `SMOKE_BASE_URL=http://127.0.0.1:8001 python scripts/smoke_test.py`
- GitHub Actions CI pass sau khi push `main`.

## Ngày 26: Kubernetes, Helm, Monitoring

- Helm chart lint pass: `helm lint deploy/helm/nufi`
- Helm template render được: `helm template nufi deploy/helm/nufi --namespace nufi`
- Helm release deploy thành công: `helm list -n nufi`
- Pod/Service/Ingress: `kubectl -n nufi get pods,svc,ingress`
- Prometheus scrape được `/metrics`.
- Grafana dashboard có panel Web Up, CPU, Memory, business records.

## Ngày 27: Version, Backup, Daily Test

- File version/config: `deploy/versions/pipeline.yaml`
- CronJob pipeline: `kubectl -n nufi get cronjob`
- Backup job chạy thành công: `kubectl -n nufi logs job/<backup-job-name>`
- File backup có timestamp trong PVC hoặc thư mục `generated_reports`.
- Daily smoke test chạy thành công qua GitHub Actions hoặc Kubernetes CronJob.
- Tài liệu restore: `docs/operations/backup-restore.md`.


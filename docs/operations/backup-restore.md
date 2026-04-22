# Backup and Restore

Tài liệu này mô tả luồng backup/restore cho NUFI khi chạy bằng Docker hoặc Kubernetes.

## Loại Dữ Liệu Cần Backup

- Database MySQL: dữ liệu người dùng, giao dịch, ngân sách, cảnh báo, nợ, nhóm.
- File report/export: thư mục `generated_reports/`.
- File media: avatar hoặc file upload trong `media/`.
- Cấu hình triển khai: Helm values, ConfigMap, Secret template, version registry.

## Backup Trong Kubernetes

Chart có 2 CronJob:

- `nufi-backup-and-export`: chạy `python manage.py backup_and_export`, xuất CSV và manifest.
- `nufi-mysql-dump`: tùy chọn, chạy `mysqldump`, tạo file `.sql.gz`.

Bật SQL dump:

```bash
helm upgrade --install nufi deploy/helm/nufi \
  --namespace nufi \
  --set pipelines.mysqlDump.enabled=true
```

Chạy backup thủ công:

```bash
kubectl -n nufi create job --from=cronjob/nufi-backup-and-export nufi-backup-manual
kubectl -n nufi logs job/nufi-backup-manual
```

Kiểm tra file backup:

```bash
kubectl -n nufi get pvc
kubectl -n nufi exec deploy/nufi -- ls -lah /app/generated_reports
```

## Backup Bằng Docker Local

Export dữ liệu ứng dụng:

```bash
docker compose --env-file .env.docker exec web python manage.py backup_and_export
```

Dump MySQL container:

```bash
docker compose --env-file .env.docker exec db sh -c \
  'mysqldump -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE" | gzip > /var/lib/mysql/pfms-$(date +%Y%m%d-%H%M%S).sql.gz'
```

## Restore MySQL

Giải nén và import:

```bash
gunzip -c pfms-YYYYMMDD-HHMMSS.sql.gz | mysql -h 127.0.0.1 -P 3306 -u root -p pfms
```

Nếu restore vào MySQL container:

```bash
gunzip -c pfms-YYYYMMDD-HHMMSS.sql.gz | docker compose --env-file .env.docker exec -T db mysql -unufi -pnufi_password pfms
```

Sau khi restore:

```bash
python manage.py migrate --noinput --fake-initial
python manage.py check
python scripts/smoke_test.py
```

## Backup Cấu Hình

Các file cấu hình quan trọng cần nằm trong Git:

- `deploy/helm/nufi/values.yaml`
- `deploy/helm/nufi/values-local.yaml`
- `deploy/versions/pipeline.yaml`
- `.github/workflows/*.yml`
- `.env.example`
- `.env.docker.example`

Secret thật không commit lên Git. Secret được lưu ở GitHub Secrets hoặc Kubernetes Secret.

## Minh Chứng Demo

Khi demo, nên chụp:

- CronJob backup đã tạo Job thành công.
- Log backup có dòng `Backup/export ready`.
- Thư mục backup có file `.csv`, `manifest.json` hoặc `.sql.gz`.
- Restore command hoặc tài liệu restore này.

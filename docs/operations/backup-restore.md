# Backup and Restore

This document describes the backup/restore flow for NUFI when running with Docker or Kubernetes.

## Data to Back Up

- MySQL database: users, transactions, budgets, alerts, debts, sharing groups.
- Report/export files: the `generated_reports/` directory.
- Media files: avatars or uploaded files in `media/`.
- Deployment configuration: Helm values, ConfigMap, Secret templates, version registry.

## Backup in Kubernetes

The chart includes 2 CronJobs:

- `nufi-backup-and-export`: runs `python manage.py backup_and_export`, exports CSV and manifest files.
- `nufi-mysql-dump`: optional, runs `mysqldump` to create a `.sql.gz` file.

Enable SQL dump:

```bash
helm upgrade --install nufi deploy/helm/nufi \
  --namespace nufi \
  --set pipelines.mysqlDump.enabled=true
```

Run a manual backup:

```bash
kubectl -n nufi create job --from=cronjob/nufi-backup-and-export nufi-backup-manual
kubectl -n nufi logs job/nufi-backup-manual
```

Check backup files:

```bash
kubectl -n nufi get pvc
kubectl -n nufi exec deploy/nufi -- ls -lah /app/generated_reports
```

## Backup with Local Docker

Export application data:

```bash
docker compose --env-file .env.docker exec web python manage.py backup_and_export
```

Dump the MySQL container:

```bash
docker compose --env-file .env.docker exec db sh -c \
  'mysqldump -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE" | gzip > /var/lib/mysql/pfms-$(date +%Y%m%d-%H%M%S).sql.gz'
```

## Restore MySQL

Decompress and import:

```bash
gunzip -c pfms-YYYYMMDD-HHMMSS.sql.gz | mysql -h 127.0.0.1 -P 3306 -u root -p pfms
```

If restoring into the MySQL container:

```bash
gunzip -c pfms-YYYYMMDD-HHMMSS.sql.gz | docker compose --env-file .env.docker exec -T db mysql -unufi -pnufi_password pfms
```

After restore:

```bash
python manage.py migrate --noinput --fake-initial
python manage.py check
python scripts/smoke_test.py
```

## Configuration Backup

Key configuration files that should be in Git:

- `deploy/helm/nufi/values.yaml`
- `deploy/helm/nufi/values-local.yaml`
- `deploy/versions/pipeline.yaml`
- `.github/workflows/*.yml`
- `.env.example`
- `.env.docker.example`

Real secrets must not be committed to Git. Secrets are stored in GitHub Secrets or Kubernetes Secrets.

## Demo Evidence

When demoing, capture:

- CronJob backup successfully created a Job.
- Backup log contains the line `Backup/export ready`.
- Backup directory contains `.csv`, `manifest.json`, or `.sql.gz` files with timestamps.
- Restore command or this restore documentation.

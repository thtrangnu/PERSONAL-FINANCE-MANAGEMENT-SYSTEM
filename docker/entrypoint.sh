#!/usr/bin/env sh
set -e

if [ "${DB_ENGINE:-mysql}" != "sqlite" ]; then
  python - <<'PY'
import os
import time

import mysql.connector

db_unix_socket = os.getenv("DB_UNIX_SOCKET", "")
config = {
    "user": os.getenv("DB_USER", "nufi"),
    "password": os.getenv("DB_PASSWORD", "nufi_password"),
    "database": os.getenv("DB_NAME", "pfms"),
}
if db_unix_socket:
    config["unix_socket"] = db_unix_socket
else:
    config["host"] = os.getenv("DB_HOST", "db")
    config["port"] = int(os.getenv("DB_PORT", "3306"))

for attempt in range(1, 61):
    try:
        connection = mysql.connector.connect(**config)
        connection.close()
        print("MySQL is ready.")
        break
    except mysql.connector.Error as exc:
        print(f"Waiting for MySQL ({attempt}/60): {exc}")
        time.sleep(2)
else:
    raise SystemExit("MySQL was not ready after 120 seconds.")
PY
fi

if [ "$(printf '%s' "${RUN_MIGRATIONS:-true}" | tr '[:upper:]' '[:lower:]')" != "false" ]; then
  python manage.py migrate --noinput --fake-initial
fi

if [ "$(printf '%s' "${RUN_COLLECTSTATIC:-true}" | tr '[:upper:]' '[:lower:]')" != "false" ]; then
  python manage.py collectstatic --noinput
fi

if [ -n "${DJANGO_SUPERUSER_USERNAME:-}" ] && [ -n "${DJANGO_SUPERUSER_PASSWORD:-}" ]; then
  python manage.py shell -c "
import os
from django.contrib.auth import get_user_model

User = get_user_model()
username = os.environ['DJANGO_SUPERUSER_USERNAME']
email = os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@nufi.local')
password = os.environ['DJANGO_SUPERUSER_PASSWORD']
reset_password = os.getenv('DJANGO_SUPERUSER_RESET_PASSWORD', '').lower() in {'1', 'true', 'yes', 'on'}

user, created = User.objects.get_or_create(username=username, defaults={'email': email})
user.email = email
user.is_staff = True
user.is_superuser = True
if created or reset_password:
    user.set_password(password)
user.save()
print(f'Superuser {username} is ready.')
"
fi

exec "$@"

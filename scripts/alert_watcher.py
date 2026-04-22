#!/usr/bin/env python3
"""Watch Alertmanager and show local desktop notifications."""

from __future__ import annotations

import argparse
import json
import platform
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Dict
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


DEFAULT_URL = "http://127.0.0.1:9093/api/v2/alerts"


@dataclass
class AlertInfo:
    fingerprint: str
    name: str
    severity: str
    status: str
    summary: str
    description: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Theo dõi Alertmanager và hiện thông báo lên máy tính."
    )
    parser.add_argument(
        "--url",
        default=DEFAULT_URL,
        help=f"URL API Alertmanager (mặc định: {DEFAULT_URL})",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=15,
        help="Số giây giữa mỗi lần kiểm tra.",
    )
    parser.add_argument(
        "--name-prefix",
        default="Nufi",
        help="Chỉ theo dõi alert có tên bắt đầu bằng prefix này. Để trống để theo dõi tất cả.",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Chỉ in nhanh trạng thái hiện tại một lần rồi thoát.",
    )
    return parser.parse_args()


def fetch_alerts(url: str, timeout: int = 10) -> list[dict]:
    request = Request(url, headers={"Accept": "application/json"})
    with urlopen(request, timeout=timeout) as response:
        return json.load(response)


def normalize_alert(raw_alert: dict) -> AlertInfo:
    labels = raw_alert.get("labels", {})
    annotations = raw_alert.get("annotations", {})
    status = raw_alert.get("status", {})
    fingerprint = raw_alert.get("fingerprint") or labels.get("alertname", "unknown")

    return AlertInfo(
        fingerprint=fingerprint,
        name=labels.get("alertname", "UnknownAlert"),
        severity=labels.get("severity", "info"),
        status=status.get("state", "unknown"),
        summary=annotations.get("summary", labels.get("alertname", "Cảnh báo mới")),
        description=annotations.get(
            "description",
            "Không có mô tả chi tiết. Hãy mở Grafana hoặc Prometheus để xem thêm.",
        ),
    )


def should_keep(alert: AlertInfo, prefix: str) -> bool:
    if alert.status != "active":
        return False
    if not prefix:
        return True
    return alert.name.startswith(prefix)


def escape_applescript(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def send_desktop_notification(title: str, message: str) -> None:
    system = platform.system()

    if system == "Darwin":
        script = (
            f'display notification "{escape_applescript(message)}" '
            f'with title "{escape_applescript(title)}"'
        )
        subprocess.run(
            ["osascript", "-e", script],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return

    if system == "Linux" and shutil.which("notify-send"):
        subprocess.run(
            ["notify-send", title, message],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return

    print(f"[notification] {title}: {message}")


def print_status(message: str) -> None:
    now = datetime.now().strftime("%H:%M:%S")
    print(f"[{now}] {message}")


def notify_new_alert(alert: AlertInfo) -> None:
    title = f"NUFI alert: {alert.summary}"
    body = f"Mức độ: {alert.severity}. {alert.description}"
    print_status(f"ALERT MỚI -> {alert.name} ({alert.severity})")
    send_desktop_notification(title, body)


def notify_resolved_alert(alert: AlertInfo) -> None:
    title = f"NUFI đã ổn định lại: {alert.summary}"
    body = f"Alert {alert.name} đã không còn kích hoạt."
    print_status(f"ALERT HẾT -> {alert.name}")
    send_desktop_notification(title, body)


def run_once(url: str, prefix: str) -> int:
    try:
        alerts = [
            normalize_alert(item)
            for item in fetch_alerts(url)
            if should_keep(normalize_alert(item), prefix)
        ]
    except (HTTPError, URLError, TimeoutError) as exc:
        print_status(f"Không đọc được Alertmanager: {exc}")
        return 1

    if not alerts:
        print_status("Không có alert đang kích hoạt.")
        return 0

    print_status(f"Có {len(alerts)} alert đang kích hoạt:")
    for alert in alerts:
        print(f"- {alert.name} [{alert.severity}] :: {alert.summary}")
    return 0


def watch_forever(url: str, interval: int, prefix: str) -> int:
    known_alerts: Dict[str, AlertInfo] = {}
    print_status(f"Đang theo dõi Alertmanager tại {url}")
    if prefix:
        print_status(f"Chỉ lấy alert bắt đầu bằng: {prefix}")

    while True:
        try:
            current_alerts = {
                alert.fingerprint: alert
                for alert in (normalize_alert(item) for item in fetch_alerts(url))
                if should_keep(alert, prefix)
            }
        except (HTTPError, URLError, TimeoutError) as exc:
            print_status(f"Không đọc được Alertmanager: {exc}")
            time.sleep(interval)
            continue

        for fingerprint, alert in current_alerts.items():
            if fingerprint not in known_alerts:
                notify_new_alert(alert)

        for fingerprint, alert in known_alerts.items():
            if fingerprint not in current_alerts:
                notify_resolved_alert(alert)

        known_alerts = current_alerts
        time.sleep(interval)


def main() -> int:
    args = parse_args()
    if args.once:
        return run_once(args.url, args.name_prefix)
    return watch_forever(args.url, args.interval, args.name_prefix)


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env bash

set -euo pipefail

NAMESPACE="${NUFI_NAMESPACE:-nufi}"
SERVICE_NAME="${NUFI_SERVICE:-nufi}"
LOCAL_PORT="${NUFI_LOCAL_PORT:-8002}"
REMOTE_PORT="${NUFI_REMOTE_PORT:-80}"
BASE_URL="http://127.0.0.1:${LOCAL_PORT}"
HEALTH_PATH="${NUFI_HEALTH_PATH:-/healthz/}"
PORT_FORWARD_LOG="${TMPDIR:-/tmp}/nufi-port-forward-${LOCAL_PORT}.log"

show_help() {
  cat <<EOF
Giữ kubectl port-forward và mở Cloudflare Quick Tunnel cho NUFI.

Biến môi trường hỗ trợ:
  NUFI_NAMESPACE    Mặc định: nufi
  NUFI_SERVICE      Mặc định: nufi
  NUFI_LOCAL_PORT   Mặc định: 8002
  NUFI_REMOTE_PORT  Mặc định: 80
  NUFI_HEALTH_PATH  Mặc định: /healthz/

Ví dụ:
  ./scripts/run_public_demo.sh
  NUFI_LOCAL_PORT=8000 ./scripts/run_public_demo.sh
EOF
}

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  show_help
  exit 0
fi

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Thiếu lệnh '$1'. Hãy cài trước rồi chạy lại." >&2
    exit 1
  fi
}

require_command kubectl
require_command cloudflared
require_command curl

if command -v lsof >/dev/null 2>&1; then
  existing_pid="$(lsof -tiTCP:"${LOCAL_PORT}" -sTCP:LISTEN 2>/dev/null | head -n 1 || true)"
  if [[ -n "${existing_pid}" ]]; then
    existing_cmd="$(ps -p "${existing_pid}" -o command= 2>/dev/null || true)"
    if [[ "${existing_cmd}" != *"kubectl -n ${NAMESPACE} port-forward svc/${SERVICE_NAME} ${LOCAL_PORT}:${REMOTE_PORT}"* ]]; then
      echo "Cổng ${LOCAL_PORT} đang được dùng bởi tiến trình khác:" >&2
      echo "${existing_cmd:-PID ${existing_pid}}" >&2
      echo "Hãy giải phóng cổng này hoặc đổi NUFI_LOCAL_PORT rồi chạy lại." >&2
      exit 1
    fi
    pkill -f "kubectl -n ${NAMESPACE} port-forward svc/${SERVICE_NAME} ${LOCAL_PORT}:${REMOTE_PORT}" >/dev/null 2>&1 || true
    sleep 1
  fi
fi

PORT_FORWARD_LOOP_PID=""

cleanup() {
  if [[ -n "${PORT_FORWARD_LOOP_PID}" ]] && kill -0 "${PORT_FORWARD_LOOP_PID}" 2>/dev/null; then
    kill "${PORT_FORWARD_LOOP_PID}" 2>/dev/null || true
    wait "${PORT_FORWARD_LOOP_PID}" 2>/dev/null || true
  fi
}

trap cleanup EXIT INT TERM

start_port_forward_loop() {
  while true; do
    echo "[$(date '+%H:%M:%S')] Mở port-forward ${LOCAL_PORT}:${REMOTE_PORT} cho svc/${SERVICE_NAME}..." >>"${PORT_FORWARD_LOG}"
    kubectl -n "${NAMESPACE}" port-forward "svc/${SERVICE_NAME}" "${LOCAL_PORT}:${REMOTE_PORT}" >>"${PORT_FORWARD_LOG}" 2>&1 || true
    echo "[$(date '+%H:%M:%S')] Port-forward bị ngắt, thử lại sau 2 giây..." >>"${PORT_FORWARD_LOG}"
    sleep 2
  done
}

: >"${PORT_FORWARD_LOG}"
start_port_forward_loop &
PORT_FORWARD_LOOP_PID=$!

echo "Đang giữ cổng ${LOCAL_PORT} cho http://127.0.0.1:${LOCAL_PORT}"
echo "Log port-forward: ${PORT_FORWARD_LOG}"

ready=false
for _ in $(seq 1 30); do
  if curl -fsS "${BASE_URL}${HEALTH_PATH}" >/dev/null 2>&1 || curl -fsS "${BASE_URL}/" >/dev/null 2>&1; then
    ready=true
    break
  fi
  sleep 1
done

if [[ "${ready}" != true ]]; then
  echo "Web chưa phản hồi trên ${BASE_URL}. Kiểm tra log port-forward ở ${PORT_FORWARD_LOG}." >&2
  exit 1
fi

cat <<EOF
Port-forward đã sẵn sàng.

Web nội bộ:
  ${BASE_URL}

Sắp mở Cloudflare Quick Tunnel.
Nhấn Ctrl + C để dừng cả Cloudflare và port-forward.
EOF

exec cloudflared tunnel --url "${BASE_URL}"

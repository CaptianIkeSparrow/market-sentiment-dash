#!/usr/bin/env bash
set -euo pipefail

# Installs a cron entry to run tracker_update.py on weekdays after market close.
# America/Denver market close is 2:00 PM MT (4:00 PM ET). This schedules 2:05 PM MT.

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="${PROJECT_DIR}/venv/bin/python"
LOG_FILE="${PROJECT_DIR}/data/tracker_update.log"
CRON_LINE="5 14 * * 1-5 cd ${PROJECT_DIR} && ${PYTHON_BIN} tracker_update.py >> ${LOG_FILE} 2>&1"

if [[ ! -x "${PYTHON_BIN}" ]]; then
  echo "Expected venv python at: ${PYTHON_BIN}"
  echo "Create it with: python3 -m venv venv && ./venv/bin/pip install -r requirements.txt"
  exit 2
fi

mkdir -p "${PROJECT_DIR}/data"

EXISTING="$(crontab -l 2>/dev/null || true)"
if echo "${EXISTING}" | grep -Fq "${CRON_LINE}"; then
  echo "Cron entry already installed."
  exit 0
fi

{
  echo "${EXISTING}"
  echo "${CRON_LINE}"
} | crontab -

echo "Installed cron entry:"
echo "${CRON_LINE}"
echo "Logs will be written to: ${LOG_FILE}"


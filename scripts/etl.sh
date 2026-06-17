#!/bin/bash
set -euo pipefail

REPO_ROOT=$(cd "$(dirname "$0")/.." && pwd)

python "${REPO_ROOT}/services/etl/etl.py" \
  --tx-log-path "${REPO_ROOT}/data/tx_log.csv" \
  --accounts-path "${REPO_ROOT}/data/accounts.csv" \
  --sar-accounts-path "${REPO_ROOT}/data/sar_accounts.csv" \
  --out-path "${REPO_ROOT}/data/clean.parquet" \
  "$@"

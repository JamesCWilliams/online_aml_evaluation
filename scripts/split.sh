#!/bin/bash
set -euo pipefail

REPO_ROOT=$(cd "$(dirname "$0")/.." && pwd)

python "${REPO_ROOT}/services/train_val_test_split/temporal.py" \
  --clean-df-path "${REPO_ROOT}/data/clean.parquet" \
  --out-dir "${REPO_ROOT}/data/split/temporal" \
  "$@"

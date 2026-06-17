#!/bin/bash
PARAM_SET=${1^^}
PARAM_SET=${PARAM_SET:-1K}
SEED=${2:-$RANDOM}

REPO_ROOT=$(cd "$(dirname "$0")/.." && pwd)
DATA_DIR="${REPO_ROOT}/data"
mkdir -p "${DATA_DIR}"

echo "Generating dataset: size=${PARAM_SET}, seed=${SEED}"

docker run --rm \
  --user "$(id -u):0" \
  -v "${DATA_DIR}:/amlsim/outputs" \
  -v "${REPO_ROOT}/services/amlsim/vendor/paramFiles:/amlsim/paramFiles" \
  amlsim "${PARAM_SET}" "${SEED}"

echo "Done. Output in data/"

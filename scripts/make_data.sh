#!/bin/bash
PARAM_SET=${1:-1K}
SEED=${2:-$RANDOM}

echo "Generating dataset: size=${PARAM_SET}, seed=${SEED}"

docker run --rm \
  -v $(pwd)/services/amlsim/vendor/outputs:/amlsim/outputs \
  amlsim "${PARAM_SET}" "${SEED}"

echo "Done. Output in services/amlsim/vendor/outputs/"

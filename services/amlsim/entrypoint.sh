#!/bin/bash
PARAM_SET=${1:-1K}
SEED=${2:-0}
sed -i "s|\"directory\":.*|\"directory\": \"paramFiles/${PARAM_SET}\",|" conf.json
sed -i "s|\"random_seed\":.*|\"random_seed\": ${SEED},|" conf.json
python3 scripts/transaction_graph_generator.py conf.json
bash scripts/run_AMLSim.sh conf.json

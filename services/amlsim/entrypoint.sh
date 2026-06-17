#!/bin/bash
PARAM_SET=${1:-1K}
SEED=${2:-0}
sed -i "s|\"directory\": \"paramFiles/.*\"|\"directory\": \"paramFiles/${PARAM_SET}\"|" conf.json
sed -i "s|\"random_seed\":.*|\"random_seed\": ${SEED},|" conf.json
python3 scripts/transaction_graph_generator.py conf.json
bash scripts/run_AMLSim.sh conf.json
python3 scripts/convert_logs.py conf.json

mkdir -p outputs/aux
mv outputs/sample/transactions.csv \
   outputs/sample/cash_tx.csv \
   outputs/sample/alert_accounts.csv \
   outputs/sample/alert_transactions.csv \
   outputs/sample/accountMapping.csv \
   outputs/sample/individuals-bulkload.csv \
   outputs/sample/organizations-bulkload.csv \
   outputs/sample/resolvedentities.csv \
   outputs/aux/
mv outputs/sample/* outputs/
rmdir outputs/sample

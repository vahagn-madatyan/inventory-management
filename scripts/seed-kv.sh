#!/bin/bash
# Seed KV namespace with JSON data files.
# Usage: ./scripts/seed-kv.sh [NAMESPACE_ID]
#
# If NAMESPACE_ID is not provided, uses the default from wrangler.jsonc.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATA_DIR="${SCRIPT_DIR}/../server/data"

NAMESPACE_ID="${1:-686f63570a3241798376f261c68a564f}"

declare -A FILES=(
  ["data:inventory"]="inventory.json"
  ["data:orders"]="orders.json"
  ["data:demand_forecasts"]="demand_forecasts.json"
  ["data:backlog_items"]="backlog_items.json"
  ["data:spending"]="spending.json"
  ["data:transactions"]="transactions.json"
  ["data:purchase_orders"]="purchase_orders.json"
  ["data:restocking_orders"]="restocking_orders.json"
)

for key in "${!FILES[@]}"; do
  file="${DATA_DIR}/${FILES[$key]}"
  if [ ! -f "$file" ]; then
    echo "ERROR: Required file $file not found. Aborting." >&2
    exit 1
  fi
  echo "Uploading ${FILES[$key]} as '$key'..."
  npx wrangler kv key put "$key" --path="$file" --namespace-id="$NAMESPACE_ID"
done

echo "KV seeding complete."

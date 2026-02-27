#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ ! -x "./venv/bin/python" ]]; then
  echo "[plot-style] failed: ./venv/bin/python not found or not executable"
  exit 1
fi

PYTHON="./venv/bin/python"

export MPLCONFIGDIR="${MPLCONFIGDIR:-/tmp/mplconfig}"
mkdir -p "$MPLCONFIGDIR"

echo "[plot-style] running static style contract check"
scripts/check_plot_style_contract.sh

echo "[plot-style] running unittest style contract"
"$PYTHON" -m unittest tests.test_characterization.test_plot_style_contract

echo "[plot-style] all checks passed"


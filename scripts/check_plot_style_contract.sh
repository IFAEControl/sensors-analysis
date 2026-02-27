#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PLOTS_DIR="$ROOT_DIR/characterization/elements/plots"

echo "[style-check] checking hardcoded hex colors outside style_spec.py"
if rg -n '#[0-9A-Fa-f]{6}' "$PLOTS_DIR" --glob '*.py' --glob '!style_spec.py'; then
  echo "[style-check] failed: found hardcoded hex colors outside style_spec.py"
  exit 1
fi

echo "[style-check] checking alpha usage outside plot_base.py"
if rg -n 'alpha\s*=' "$PLOTS_DIR" --glob '*.py' --glob '!plot_base.py'; then
  echo "[style-check] failed: found alpha usage outside plot_base.py"
  exit 1
fi

echo "[style-check] checking for hardcoded fmt markers in plot modules"
if rg -n "fmt\s*=\s*['\"][^'\"]+['\"]" "$PLOTS_DIR" --glob '*.py' --glob '!plot_base.py' --glob '!style_spec.py'; then
  echo "[style-check] failed: found hardcoded fmt marker"
  exit 1
fi

echo "[style-check] passed"


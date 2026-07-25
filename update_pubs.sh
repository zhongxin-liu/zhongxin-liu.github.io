#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python_bin="${PYTHON:-$script_dir/venv/bin/python}"

if [[ ! -x "$python_bin" ]]; then
  python_bin="python3"
fi

cd "$script_dir"
"$python_bin" scripts/convert_bib.py metadata/pub2.bib metadata/pub2.json
"$python_bin" scripts/update_pubs.py index.html metadata/pub2.json

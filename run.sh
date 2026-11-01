#!/usr/bin/env bash
# One command: fetch all public data and rebuild metrics + dashboard. Python 3.9+, stdlib only.
set -euo pipefail; cd "$(dirname "$0")"
python3 pipeline/fetch.py && python3 pipeline/build.py
echo "Open docs/index.html  |  scores in data/metrics.json"

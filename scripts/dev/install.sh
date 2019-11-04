#!/usr/bin/env bash
set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && cd ../.. && pwd)"
cd "${PROJECT_ROOT}"

install() {
  poetry install

  echo ""
  echo "Virtual environment interpreter installed at:"
  poetry run python -c "import sys; print(sys.executable)"
}

install

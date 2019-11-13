#! /usr/bin/env bash

set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && cd ../.. && pwd)"
cd "${DIR}"

export PYTHONPATH="test_client"
pytest tests


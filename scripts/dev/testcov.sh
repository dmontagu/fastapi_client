#! /usr/bin/env bash

set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && cd ../.. && pwd)"
cd "${DIR}"

export PYTHONPATH="example"

python tests/auth_app.py &
auth_app_pid=$!
trap 'kill -KILL $auth_app_pid; echo "Killed auth app process"' EXIT
sleep 1

pytest tests --cov=example

kill -KILL $auth_app_pid
echo "Killed auth app process"
trap - EXIT

echo "building coverage html"
coverage html

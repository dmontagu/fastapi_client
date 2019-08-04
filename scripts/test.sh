#! /usr/bin/env bash

set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )"
cd "${DIR}"

export PYTHONPATH="example"

python tests/auth_app.py &
auth_app_pid=$!
sleep 1
pytest .
kill -KILL $auth_app_pid
echo "Killed auth app process"

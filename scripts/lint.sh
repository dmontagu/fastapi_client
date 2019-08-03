#! /bin/bash

set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )"
cd "${DIR}"

mypy example
echo "No mypy problems"
flake8 --max-line-length 120 example
echo "No flake8 problems"
echo "Success!"
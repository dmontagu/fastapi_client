#! /usr/bin/env bash

set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )"
cd "${DIR}"

[ -z "$1" ] && echo "Did not pass PACKAGE_NAME as first arg to _postprocess.sh" && exit 1
PACKAGE_NAME=$1

docker build -t fastapi-client-generator:latest .
docker run --rm -v "$(pwd)":/local fastapi-client-generator:latest "${PACKAGE_NAME}"

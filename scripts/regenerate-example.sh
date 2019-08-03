#! /bin/bash

set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )"
cd "${DIR}"

# Generate
./scripts/generate.sh fastapi_client -i https://petstore.swagger.io/v2/swagger.json

# Replace example
rm -r example/fastapi_client > /dev/null 2>&1 || true
cp -r generated/fastapi_client example

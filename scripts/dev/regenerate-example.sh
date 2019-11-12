#! /usr/bin/env bash
set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && cd ../.. && pwd)"
cd "${PROJECT_ROOT}"

# Generate
rm -r generated >/dev/null 2>&1 || true
./scripts/generate.sh -p client -n example.client -o generated --include-auth -i https://petstore.swagger.io/v2/swagger.json

# Replace example
rm -r example/client >/dev/null 2>&1 || true
cp -r generated/client example

#! /usr/bin/env bash

set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )"
cd "${DIR}"

[ -z "$1" ] && echo "Did not pass PACKAGE_NAME as first arg to generate.sh" && exit 1
PACKAGE_NAME=$1

# Delete existing files; important if you remove models/apis
rm -r generated > /dev/null 2>&1 || true

# Replace the ignore file
mkdir generated
cp other-templates/.openapi-generator-ignore generated

# Replace PACKAGE_NAME in the ignore with the appropriate value
sed -i.bak "s/PACKAGE_NAME/${PACKAGE_NAME}/" generated/.openapi-generator-ignore
rm generated/.openapi-generator-ignore.bak

./scripts/_openapi-generate.sh "${PACKAGE_NAME}" "${@:2}"

# Add extra files (not openapi templates)
cp other-templates/password_flow_client.template generated/"${PACKAGE_NAME}"/password_flow_client.py
cp other-templates/auth.template generated/"${PACKAGE_NAME}"/auth.py
sed -i.bak "s/PACKAGE_NAME/${PACKAGE_NAME}/" generated/"${PACKAGE_NAME}"/password_flow_client.py
sed -i.bak "s/PACKAGE_NAME/${PACKAGE_NAME}/" generated/"${PACKAGE_NAME}"/auth.py
rm generated/"${PACKAGE_NAME}"/password_flow_client.py.bak
rm generated/"${PACKAGE_NAME}"/auth.py.bak

./scripts/_postprocess.sh "${PACKAGE_NAME}"

# Remove traces of OpenAPI generation
rm -r generated/.openapi-generator
rm generated/.openapi-generator-ignore

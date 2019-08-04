#! /usr/bin/env bash

set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )"
cd "${DIR}"

[ -z "$1" ] && echo "Did not pass PACKAGE_NAME as first arg to generate.sh" && exit 1
PACKAGE_NAME=$1

docker run --rm -v ${PWD}:/local openapitools/openapi-generator-cli generate \
    -g python \
    -o /local/generated \
    --package-name="${PACKAGE_NAME}" \
    --additional-properties=generateSourceCodeOnly=true,packageName="${PACKAGE_NAME}" \
    -t /local/openapi-python-templates \
    --type-mappings array=List,uuid=UUID,file=IO \
    "${@:2}"

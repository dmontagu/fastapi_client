#! /usr/bin/env bash -x

set -e
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && cd ../.. && pwd)"

CMDNAME=${0##*/}

PACKAGE_NAME=""
INPUT=""
WORK_DIR=""
SOURCE_CODE_ONLY="true"

OPENAPI_IMAGE="openapitools/openapi-generator-cli:v5.3.0"

usage() {
  exitcode="$1"
  cat <<USAGE >&2

Use openapi-generator to generate an unprocessed version of the client

Usage:
  $CMDNAME -p PACKAGE_NAME -w WORK_DIR -- [*openapi-generator-cli args]

Options:
  -p, --package-name       The name to use for the generated package
  -w, --work-dir           The working directory to use for generator output
  -i, --input              The location of the OpenAPI spec, as URL or file
  -m, --with-meta          Generate meta-data (setup.py, docs, tests)
  -h, --help               Show this message
USAGE
  exit "$exitcode"
}

main() {
  validate_inputs
  if [ -z "$IS_HTTP" ]; then
    generate_in_docker_file "$@"
  else
    generate_in_docker_http "$@"
  fi
}

validate_inputs() {
  if [ -z "$PACKAGE_NAME" ]; then
    echo "Error: you need to provide --package-name argument"
    usage 2
  fi
  if [ -z "$INPUT" ]; then
    echo "Error: you need to provide --input argument"
    usage 2
  fi
  if [ -z "$WORK_DIR" ]; then
    echo "Error: you need to provide --work-dir argument"
    usage 2
  fi

  IS_HTTP="$(echo "$INPUT" | grep '^https\{0,1\}://' || true)"
}

generate_in_docker_http() {
  docker run --user $(id -u):$(id -g) --rm -v "$WORK_DIR":/generator-output -v "$PROJECT_ROOT":/local $OPENAPI_IMAGE generate \
    -g python \
    -o /generator-output \
    --package-name="${PACKAGE_NAME}" \
    --additional-properties=generateSourceCodeOnly="${SOURCE_CODE_ONLY}" \
    -t /local/openapi-python-templates \
    --type-mappings array=List,uuid=UUID,file=IO,object=Any \
    -i "${INPUT}" \
    "$@"
}

generate_in_docker_file() {
  INPUT_FILE="$(cd "$(dirname "$INPUT")" && pwd )"/"$(basename "$INPUT")"

  docker run --user $(id -u):$(id -g) --rm -v "$WORK_DIR":/generator-output -v "$PROJECT_ROOT":/local -v "${INPUT_FILE}":/openapi.json \
    $OPENAPI_IMAGE generate \
    -g python \
    -o /generator-output \
    --package-name="${PACKAGE_NAME}" \
    --additional-properties=generateSourceCodeOnly="${SOURCE_CODE_ONLY}" \
    -t /local/openapi-python-templates \
    --type-mappings array=List,uuid=UUID,file=IO,object=Any \
    -i /openapi.json \
    "$@"
}

while [ $# -gt 0 ]; do
  case "$1" in
  -p | --package-name)
    PACKAGE_NAME=$2
    shift 2
    ;;
  -i | --input)
    INPUT=$2
    shift 2
    ;;
  -w | --work-dir)
    WORK_DIR=$2
    shift 2
    ;;
  -m | --with-meta)
    SOURCE_CODE_ONLY="false"
    shift 1
    ;;
  -h | --help)
    usage 0
    ;;
  --)
    shift 1
    break
    ;;
  *)
    echo "Unknown argument: $1"
    usage 1
    ;;
  esac
done

main "$@"

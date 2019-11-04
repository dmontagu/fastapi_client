#! /usr/bin/env bash

set -e
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && cd .. && pwd)"
cd "${PROJECT_ROOT}"

CMDNAME=${0##*/}

INCLUDE_AUTH=""
OUTPUT_PATH=""
PACKAGE_NAME=""
WORK_DIR=""

usage() {
  exitcode="$1"
  cat <<USAGE >&2

Usage:
  $CMDNAME -p PACKAGE_NAME -o OUTPUT_PATH [--include-auth] -- [*openapi-generator-cli args]

Options:
  -p, --package-name       The name to use for the generated package
  -o, --output-path        The parent folder to use for the generated package
  -h, --help               Show this message
USAGE
  exit "$exitcode"
}

main() {
  validate_inputs

  WORK_DIR=$(mktemp -d "$(pwd)/tmp.XXXXXXXXX")
  echo "Storing intermediate outputs in ${WORK_DIR}; it will be removed if generation is successful"
  setup_openapi_generation "$WORK_DIR"
  ./scripts/util/openapi-generate.sh -p "$PACKAGE_NAME" -w "$WORK_DIR" -- "$@"

  if [ -n "$INCLUDE_AUTH" ]; then
    add_auth_files "$WORK_DIR"
  fi

  ./scripts/util/postprocess.sh -p "${PACKAGE_NAME}" -w "$WORK_DIR"
  clean_openapi_generator_output "$WORK_DIR"
  move_generated_output "$WORK_DIR"
  echo "Generation succeeded 🚀"
}

validate_inputs() {
  if [ -z "$PACKAGE_NAME" ]; then
    echo "Error: you need to provide --package-name argument"
    usage 2
  fi
  if [ -z "$OUTPUT_PATH" ]; then
    echo "Error: you need to provide --output-path argument"
    usage 2
  fi
  if [ -d "${OUTPUT_PATH}/${PACKAGE_NAME}" ]; then
    echo "A folder already exists at ${OUTPUT_PATH}/${PACKAGE_NAME}; it must be removed first"
    usage 2
  fi
}

setup_openapi_generation() {
  WORK_DIR=$1
  cp other-templates/.openapi-generator-ignore "$WORK_DIR"

  # Replace PACKAGE_NAME in the ignore with the appropriate value
  sed -i.bak "s/PACKAGE_NAME/${PACKAGE_NAME}/" "$WORK_DIR"/.openapi-generator-ignore
  rm "$WORK_DIR"/.openapi-generator-ignore.bak
}

add_auth_files() {
  WORK_DIR=$1
  add_extra_python_template "$WORK_DIR" auth
  add_extra_python_template "$WORK_DIR" password_flow_client
}

clean_openapi_generator_output() {
  WORK_DIR=$1
  rm -r "$WORK_DIR"/.openapi-generator
  rm "$WORK_DIR"/.openapi-generator-ignore
}

move_generated_output() {
  WORK_DIR=$1
  mkdir -p "$OUTPUT_PATH"
  mv "$WORK_DIR"/"$PACKAGE_NAME" "$OUTPUT_PATH"
  rm -r "$WORK_DIR"
}

add_extra_python_template() {
  WORK_DIR=$1
  TEMPLATE_NAME=$2

  PACKAGE_DIR="$WORK_DIR"/"$PACKAGE_NAME"
  cp other-templates/"$TEMPLATE_NAME".template "$PACKAGE_DIR"/"$TEMPLATE_NAME".py
  sed -i.bak "s/PACKAGE_NAME/${PACKAGE_NAME}/" "$PACKAGE_DIR"/"$TEMPLATE_NAME".py
  rm "$PACKAGE_DIR"/"$TEMPLATE_NAME".py.bak
}

while [ $# -gt 0 ]; do
  case "$1" in
  -p | --package-name)
    PACKAGE_NAME=$2
    shift 2
    ;;
  -o | --output-path)
    OUTPUT_PATH=$2
    shift 2
    ;;
  -h | --help)
    usage 0
    ;;
  --include-auth)
    INCLUDE_AUTH="yes"
    shift 1
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

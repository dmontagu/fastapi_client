#! /usr/bin/env bash

set -e
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && cd .. && pwd)"
cd "${PROJECT_ROOT}"

CMDNAME=${0##*/}

usage() {
  exitcode="$1"
  cat <<USAGE >&2
Usage:
  $CMDNAME -p PACKAGE_NAME -- [*openapi-generator-cli args]

Options:
  -p, --package-name       The name to use for the generated package
  -h, --help               Show this message
USAGE
  exit "$exitcode"
}

main() {
  validate_inputs
  clean_existing
  setup_openapi_generation
  ./scripts/util/openapi-generate.sh -p "${PACKAGE_NAME}" -- "$@"
  add_extra_files
  ./scripts/_postprocess.sh "${PACKAGE_NAME}"
  clean_openapi_generator_output
}

validate_inputs() {
  if [ -z "$PACKAGE_NAME" ]; then
    echo "Error: you need to provide --package-name argument"
    usage 2
  fi
}

clean_existing() {
  # Delete existing files; important if you remove models/apis
  rm -r generated >/dev/null 2>&1 || true
}


setup_openapi_generation() {
  # Replace the ignore file
  mkdir generated
  cp other-templates/.openapi-generator-ignore generated

  # Replace PACKAGE_NAME in the ignore with the appropriate value
  sed -i.bak "s/PACKAGE_NAME/${PACKAGE_NAME}/" generated/.openapi-generator-ignore
  rm generated/.openapi-generator-ignore.bak
}

add_extra_files() {
  cp other-templates/password_flow_client.template generated/"${PACKAGE_NAME}"/password_flow_client.py
  cp other-templates/auth.template generated/"${PACKAGE_NAME}"/auth.py

  sed -i.bak "s/PACKAGE_NAME/${PACKAGE_NAME}/" generated/"${PACKAGE_NAME}"/password_flow_client.py
  sed -i.bak "s/PACKAGE_NAME/${PACKAGE_NAME}/" generated/"${PACKAGE_NAME}"/auth.py

  rm generated/"${PACKAGE_NAME}"/password_flow_client.py.bak
  rm generated/"${PACKAGE_NAME}"/auth.py.bak
}


clean_openapi_generator_output() {
  # Remove traces of OpenAPI generation
  rm -r generated/.openapi-generator
  rm generated/.openapi-generator-ignore
}


while [ $# -gt 0 ]; do
  case "$1" in
  -p | --package-name)
    PACKAGE_NAME=$2
    shift 2
    ;;
  -h | --help)
    usage 0
    ;;
  --)
    break
    ;;
  *)
    echo "Unknown argument: $1"
    usage 1
    ;;
  esac
done

main "$@"

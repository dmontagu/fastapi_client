#! /usr/bin/env bash

set -e
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && cd ../.. && pwd)"
cd "${PROJECT_ROOT}"

CMDNAME=${0##*/}

usage() {
  exitcode="$1"
  cat <<USAGE >&2

Use docker to postprocess the output of openapi-generator

Usage:
  $CMDNAME -p PACKAGE_NAME

Options:
  -p, --package-name       The name to use for the generated package
  -h, --help               Show this message
USAGE
  exit "$exitcode"
}

main() {
  validate_inputs
  docker build -t fastapi-client-generator:latest .
  docker run --rm -v "$(pwd)":/local fastapi-client-generator:latest "${PACKAGE_NAME}"
}

validate_inputs() {
  if [ -z "$PACKAGE_NAME" ]; then
    echo "Error: you need to provide --package-name argument"
    usage 2
  fi
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
  *)
    echo "Unknown argument: $1"
    usage 1
    ;;
  esac
done

main

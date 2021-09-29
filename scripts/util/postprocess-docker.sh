#! /usr/bin/env bash

set -e
cd /generator-output

CMDNAME=${0##*/}

usage() {
  exitcode="$1"
  cat <<USAGE >&2

Postprocess the output of openapi-generator

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
  merge_generated_models
  delete_unused
  fix_any_of
  fix_docs_path
  apply_formatters
}

validate_inputs() {
  if [ -z "$PACKAGE_NAME" ]; then
    echo "Error: you need to provide --package-name argument"
    usage 2
  fi
}

merge_generated_models() {
  # Need to merge the generated models into a single file to prevent circular imports
  # shellcheck disable=SC2046
  # shellcheck disable=SC2010
  cat $(ls "${PACKAGE_NAME}"/models/*.py | grep -v __init__) >"${PACKAGE_NAME}"/models.py
  rm -r "${PACKAGE_NAME}"/models >/dev/null 2>&1 || true

  echo "
import inspect
import sys
import io
import pydantic

IO = io.IOBase

current_module = sys.modules[__name__]

for model in inspect.getmembers(current_module, inspect.isclass):
    model_class = model[1]
    if isinstance(model_class, pydantic.BaseModel) or hasattr(model_class, \"update_forward_refs\"):
        model_class.update_forward_refs()
" >> "${PACKAGE_NAME}"/models.py
}

delete_unused() {
  # Delete empty folder
  rm -r "${PACKAGE_NAME}"/test >/dev/null 2>&1 || true

  rm "${PACKAGE_NAME}"/rest.py >/dev/null 2>&1 || true
  rm "${PACKAGE_NAME}"/configuration.py >/dev/null 2>&1 || true
}

fix_any_of() {
  find . -name "*.py" -exec sed -i.bak "s/AnyOf[a-zA-Z0-9]*/Any/" {} \;
  find . -name "*.md" -exec sed -i.bak "s/AnyOf[a-zA-Z0-9]*/Any/" {} \;
  find . -name "*.bak" -exec rm {} \;
}

fix_docs_path() {
  sed -i -e "s="${PACKAGE_NAME}"/docs=docs=" "${PACKAGE_NAME}"_README.md
}

apply_formatters() {
  autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place "${PACKAGE_NAME}" --exclude=__init__.py
  isort --float-to-top -w 120 -m 3 --trailing-comma --force-grid-wrap 0 --combine-as -p "${PACKAGE_NAME}" "${PACKAGE_NAME}"
  black --fast -l 120 --target-version py36 "${PACKAGE_NAME}"
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

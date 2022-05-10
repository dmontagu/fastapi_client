#! /usr/bin/env bash -x

set -e

# Prevent automatic path conversions by MSYS-based bash. 
# It's revelant only for Windows
export MSYS_NO_PATHCONV=1 

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && cd .. && pwd)"

CMDNAME=${0##*/}

INCLUDE_AUTH=""
OUTPUT_PATH=""
INPUT=""
PACKAGE_NAME=""
IMPORT_NAME=""
WORK_DIR=""
TEMP_DIR=""
WITH_META=""
MAP_LOCALHOST=""

usage() {
  exitcode="$1"
  cat <<USAGE >&2

Usage:
  $CMDNAME -i INPUT -p PACKAGE_NAME -o OUTPUT_PATH [-n IMPORT_NAME] [--include-auth] -- [*openapi-generator-cli args]

Options:
  -i, --input              The location of the OpenAPI spec, as URL or file
  -p, --package-name       The name to use for the generated package
  -n, --import-name        The name to use for imports of the package (defaults to PACKAGE_NAME)
  -o, --output-path        The parent folder to use for the generated package
  -t, --temp-dir           The location for temporary files
  -m, --map-localhost      (OSX): Map localhost / 127.0.0.1 to host.docker.internal
  --with-meta              Generate meta-data (setup.py, docs, tests)
  -h, --help               Show this message
USAGE
  exit "$exitcode"
}

main() {
  validate_inputs

  WORK_DIR=$(mktemp -d "$TEMP_DIR/tmp.XXXXXXXXX")
  echo "Storing intermediate outputs in ${WORK_DIR}; it will be removed if generation is successful"
  setup_openapi_generation "$WORK_DIR"
  "${PROJECT_ROOT}/scripts/util/openapi-generate.sh" -p "$PACKAGE_NAME" -w "$WORK_DIR" -i "$INPUT" ${WITH_META:+ --with-meta} -- "$@"

  cd "${PROJECT_ROOT}"

  if [ -n "$INCLUDE_AUTH" ]; then
    add_auth_files "$WORK_DIR"
  fi
  fill_import_name_templates "$WORK_DIR"

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
  mkdir -p "$OUTPUT_PATH"
  OUTPUT_PATH="$(cd "$OUTPUT_PATH" && pwd)"
  if [ -d "${OUTPUT_PATH}/${PACKAGE_NAME}" ]; then
    echo "A folder already exists at ${OUTPUT_PATH}/${PACKAGE_NAME}; it must be removed first"
    usage 2
  fi
  if [ -z "$INPUT" ]; then
    echo "Error: you need to provide --input argument"
    usage 2
  fi

  if [ -z "$TEMP_DIR" ]; then
    TEMP_DIR="$PROJECT_ROOT"
  fi
  if [ -z "$IMPORT_NAME" ]; then
    IMPORT_NAME="$PACKAGE_NAME"
  fi

  if [ ! -z "$MAP_LOCALHOST" ] && [ "$(uname -s)" == "Darwin" ]; then
    INPUT=$(echo "$INPUT" | sed -E 's%^(https?://)(localhost|127\.0\.0\.1)([:/])%\1host.docker.internal\3%')
  fi
}

setup_openapi_generation() {
  WORK_DIR=$1
  cp "${PROJECT_ROOT}/other-templates/.openapi-generator-ignore" "$WORK_DIR"

  # Replace @PACKAGE_NAME@ in the ignore with the appropriate value
  sed -i.bak "s/@PACKAGE_NAME@/${PACKAGE_NAME}/" "$WORK_DIR"/.openapi-generator-ignore
  rm "$WORK_DIR"/.openapi-generator-ignore.bak
}

add_auth_files() {
  WORK_DIR=$1
  add_extra_python_template "$WORK_DIR" auth
  add_extra_python_template "$WORK_DIR" password_flow_client
}

fill_import_name_templates() {
  WORK_DIR=$1
  PACKAGE_DIR="$WORK_DIR"/"$PACKAGE_NAME"
  fill_import_name_template "$PACKAGE_DIR"/api_client.py
  fill_import_name_template "$PACKAGE_DIR"/__init__.py

  pushd "${PACKAGE_DIR}/api"
  find . -name "*.py" | while read -r filename; do
    fill_import_name_template "$filename"
  done
  popd

}

clean_openapi_generator_output() {
  WORK_DIR=$1
  rm -r "$WORK_DIR"/.openapi-generator
  rm "$WORK_DIR"/.openapi-generator-ignore
}

move_generated_output() {
  WORK_DIR=$1
  mkdir -p "$OUTPUT_PATH"
  if [ -n "$WITH_META" ]; then
    # TODO: add valid generation for docs
    rm -r "$WORK_DIR"/docs
    # TODO: add valid generation for tests
    rm -r "$WORK_DIR"/test
    mv "$WORK_DIR" "$OUTPUT_PATH"/"$PACKAGE_NAME"
  else
     mv "$WORK_DIR"/"$PACKAGE_NAME" "$OUTPUT_PATH"
  fi
  rm -r "$WORK_DIR"
}

add_extra_python_template() {
  WORK_DIR=$1
  TEMPLATE_NAME=$2

  PACKAGE_DIR="$WORK_DIR"/"$PACKAGE_NAME"
  cp other-templates/"$TEMPLATE_NAME".template "$PACKAGE_DIR"/"$TEMPLATE_NAME".py
  fill_import_name_template "$PACKAGE_DIR"/"$TEMPLATE_NAME".py
}

fill_import_name_template() {
  python_filename="$1"
  sed -i.bak "s/@IMPORT_NAME@/${IMPORT_NAME}/" "$python_filename"
  rm "$python_filename".bak
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
  -i | --input)
    INPUT=$2
    shift 2
    ;;
  -n | --import-name)
    IMPORT_NAME=$2
    shift 2
    ;;
  -h | --help)
    usage 0
    ;;
  -t | --temp-dir)
    TEMP_DIR=$2
    shift 2
    ;;
  -m | --map-localhost)
    MAP_LOCALHOST="yes"
    shift 1
    ;;
  --include-auth)
    INCLUDE_AUTH="yes"
    shift 1
    ;;
  --with-meta)
    WITH_META="yes"
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

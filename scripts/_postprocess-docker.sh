#! /bin/bash
set -e

[ -z "$1" ] && echo "Did not pass PACKAGE_NAME as first arg to _postprocess-docker.sh" && exit 1
PACKAGE_NAME=$1
cd /local/generated

# Need to merge the generated models into a single file to prevent circular imports
cat $(ls "${PACKAGE_NAME}"/models/*.py | grep -v __init__) > ${PACKAGE_NAME}/models.py
rm -r "${PACKAGE_NAME}"/models > /dev/null 2>&1 || true

# The following lines have been useful for me to remove some auto-generated cruft models; they may not be necessary
#find python/scan_client -type f -name '*.py' -exec grep -l "DefaultApi" {} + | xargs -I '{}' sh -c $'echo \'{}\' && awk \'!/import DefaultApi/\' \'{}\' > temp && mv temp \'{}\''
#find python/scan_client -type f -name '*.py' -exec grep -l "from scan_client.models import Body" {} + | xargs -I '{}' sh -c $'echo \'{}\' && awk \'!/from scan_client.models import Body/\' \'{}\' > temp && mv temp \'{}\''

# Delete empty folder
rm -r "${PACKAGE_NAME}"/test > /dev/null 2>&1 || true

# Clean up the generated code where possible
autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place "${PACKAGE_NAME}" --exclude=__init__.py
isort -w 120 -m 3 -tc -fgw 0 -ca -p fastapi_client -rc fastapi_client
black -l 120 --target-version py36 "${PACKAGE_NAME}"
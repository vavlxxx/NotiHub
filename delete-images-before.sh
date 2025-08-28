#!/bin/sh

usage(){
# ============================================================
echo "This script removes all images of the same repository and"
echo "older than the provided image from the docker instance."
echo
echo "This cleans up older images, but retains layers from the"
echo "provided image, which makes them available for caching."
echo
echo "Usage:"
echo
echo '$ ./delete-images-before.sh <image-name>:<tag>'
exit 1
# ============================================================
}

# Проверка аргументов (sh синтаксис)
if [ $# -ne 1 ]; then
    usage
fi

IMAGE=$(echo $1 | awk -F: '{ print $1 }')
TAG=$(echo $1 | awk -F: '{ print $2 }')

FOUND=$(docker images --format '{{.Repository}}:{{.Tag}}' | grep ${IMAGE}:${TAG})

if [ -z "${FOUND}" ]; then
    echo "The image ${IMAGE}:${TAG} does not exist"
    exit 2
fi

docker images --filter before=${IMAGE}:${TAG} \
    | grep ${IMAGE} \
    | awk '{ print $3 }' \
    | xargs --no-run-if-empty \
    docker --log-level=warn rmi --force || true

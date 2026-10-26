#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"

# Build the image if it doesn't exist
if ! docker image inspect mkdocs-site >/dev/null 2>&1; then
    echo "Building Docker image..."
    docker build -t mkdocs-site .
fi

echo "Starting MkDocs server..."
docker run --rm -it \
    -p 127.0.0.1:8000:8000 \
    -v "$PWD:/docs" \
    mkdocs-site

#!/bin/bash
echo "--- Attempting to build the Docker image ---"
docker build -t nutriede-test-build ./nutriede-app
if [ $? -eq 0 ]; then
    echo "--- Docker image built successfully! ---"
    exit 0
else
    echo "--- Docker image build failed as expected. ---"
    exit 1
fi
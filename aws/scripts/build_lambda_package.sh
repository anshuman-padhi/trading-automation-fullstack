#!/bin/bash
# Build Lambda deployment package with uv

set -e

FUNCTION_NAME=$1
OUTPUT_DIR="aws/lambda/packages"

PROJECT_ROOT=$(pwd)

if [ -z "$FUNCTION_NAME" ]; then
    echo "Usage: ./build_lambda_package.sh <function_name>"
    exit 1
fi

echo "Building Lambda package for: $FUNCTION_NAME"

# Create temp directory
rm -rf /tmp/lambda-build
mkdir -p /tmp/lambda-build

# Install dependencies with uv (FAST!)
# Install dependencies with uv (FAST!)
# Install dependencies with pip (cross-platform support)
echo "Installing dependencies with pip..."
pip install \
    --target /tmp/lambda-build \
    --platform manylinux2014_x86_64 \
    --implementation cp \
    --python-version 3.11 \
    --only-binary=:all: \
    --upgrade \
    requests python-dotenv alpaca-py

# Prune heavy libraries provided by Lambda Layers (pandas, numpy) to save space and avoid conflicts
echo "Pruning pandas and numpy (provided by Layer)..."
rm -rf /tmp/lambda-build/pandas*
rm -rf /tmp/lambda-build/numpy*
rm -rf /tmp/lambda-build/docutils* # Cleanup typical bloat if present

# Copy source code
echo "Copying source code..."
cp -r src /tmp/lambda-build/
cp aws/lambda/${FUNCTION_NAME}_handler.py /tmp/lambda-build/

# Create ZIP
echo "Creating deployment package..."
mkdir -p ${PROJECT_ROOT}/${OUTPUT_DIR}
rm -f ${PROJECT_ROOT}/${OUTPUT_DIR}/${FUNCTION_NAME}.zip
cd /tmp/lambda-build
zip -r ${PROJECT_ROOT}/${OUTPUT_DIR}/${FUNCTION_NAME}.zip . -x "*.pyc" -x "*__pycache__*" -x ".env" -x "*.DS_Store" -x "*.git*"

echo "✅ Package created: ${OUTPUT_DIR}/${FUNCTION_NAME}.zip"
ls -lh ${PROJECT_ROOT}/${OUTPUT_DIR}/${FUNCTION_NAME}.zip

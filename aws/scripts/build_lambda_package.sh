#!/bin/bash
# Build Lambda deployment package with uv

set -e

FUNCTION_NAME=$1
OUTPUT_DIR="aws/lambda/packages"

if [ -z "$FUNCTION_NAME" ]; then
    echo "Usage: ./build_lambda_package.sh <function_name>"
    exit 1
fi

echo "Building Lambda package for: $FUNCTION_NAME"

# Create temp directory
rm -rf /tmp/lambda-build
mkdir -p /tmp/lambda-build

# Install dependencies with uv (FAST!)
echo "Installing dependencies with uv..."
uv pip install \
    --target /tmp/lambda-build \
    --python-version 3.11 \
    boto3 requests python-dotenv

# Copy source code
echo "Copying source code..."
cp -r src/modules /tmp/lambda-build/
cp -r src/utils /tmp/lambda-build/
cp -r src/config /tmp/lambda-build/
cp aws/lambda/${FUNCTION_NAME}_handler.py /tmp/lambda-build/

# Create ZIP
echo "Creating deployment package..."
mkdir -p $OUTPUT_DIR
cd /tmp/lambda-build
zip -r ../../${OUTPUT_DIR}/${FUNCTION_NAME}.zip . -x "*.pyc" -x "*__pycache__*"

echo "✅ Package created: ${OUTPUT_DIR}/${FUNCTION_NAME}.zip"
ls -lh ../../${OUTPUT_DIR}/${FUNCTION_NAME}.zip

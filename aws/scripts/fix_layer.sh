#!/bin/bash
# Rebuild Lambda layer with Linux-compatible binaries

set -e

# Configuration
LAYER_NAME="trading-automation-deps"
REGION="us-east-1"
PYTHON_VERSION="3.11"
PLATFORM="manylinux2014_x86_64"

# Navigate to layer directory
cd "$(dirname "$0")/../layers"

# Clean previous build
rm -rf python

# Copy entire src directory recursively to ensure config and utils are included
mkdir -p python/src
cp -R ../../src/* python/src/

# Clean up any copied pycache
find python/src -name "__pycache__" -type d -exec rm -rf {} +

echo "📥 Installing Linux binaries..."
# Install dependencies with platform flags using standard pip
# --target installs to the specified directory
# --platform manylinux2014_x86_64 fetches compatible binaries for Lambda
# --python-version 3.11 ensures compatibility with Lambda runtime
# --only-binary=:all: disables source builds (which require gcc etc)
# --upgrade ensures all packages are upgraded to their latest compatible versions
# --implementation cp specifies CPython implementation
# 1. Install Linux binaries and strict dependencies
# Note: Reverted to pip because 'uv pip install' does not yet support --platform overrides 
# for cross-platform target installation on macOS as robustly as pip.
python3 -m pip install \
    --target python \
    --platform ${PLATFORM} \
    --implementation cp \
    --python-version 3.11 \
    --only-binary=:all: \
    --upgrade \
    "python-dotenv>=1.0.0" \
    "multitasking>=0.0.7" \
    "platformdirs>=2.0.0" \
    "frozendict>=2.3.4" \
    "protobuf>=4.21.0" \
    "beautifulsoup4>=4.11.0"

# 2. Install Peewee
python3 -m pip install \
    --target python \
    --upgrade \
    "peewee>=3.16.2"

# 3. Install YFinance
python3 -m pip install \
    --target python \
    --platform ${PLATFORM} \
    --implementation cp \
    --python-version 3.11 \
    --only-binary=:all: \
    --upgrade \
    --no-deps \
    "yfinance==0.2.40"

# Remove __pycache__ and other unnecessary files to save space
find python -type d -name "__pycache__" -exec rm -rf {} +
find python -type d -name "tests" -exec rm -rf {} +
find python -type d -name "test" -exec rm -rf {} +
find python -type d -name "sample_data" -exec rm -rf {} +
find python -type d -name "examples" -exec rm -rf {} +
find python -name "*.dist-info" -type d -exec rm -rf {} +
find python -name "*.egg-info" -type d -exec rm -rf {} +
find python -name "*.pyc" -delete
find python -name "*.pyo" -delete
# Remove unused pandas components
rm -rf python/pandas/tests
rm -rf python/pandas/io/sas
rm -rf python/pandas/io/spss
# Remove heavy scipy components if possible (risky but trying to valid ML only)
# Keep scipy for sklearn, but remove doc
rm -rf python/scipy/doc
rm -rf python/numpy/doc

echo "📦 Zipping layer..."
rm -f trading-automation-layer.zip
zip -r -q trading-automation-layer.zip python/

SIZE=$(du -h trading-automation-layer.zip | cut -f1)
echo "   Layer size: ${SIZE}"

# Upload to S3 to avoid request size limits (Base64 encoding expands >50MB zip beyond 70MB limit)
S3_BUCKET="trading-automation-data-904583676284"
S3_KEY="layers/layer.zip"

echo "☁️ Uploading layer to s3://${S3_BUCKKET}/${S3_KEY}..."
aws s3 cp "trading-automation-layer.zip" "s3://${S3_BUCKET}/${S3_KEY}"

echo "Kc Publishing layer from S3..."
LAYER_VERSION_ARN=$(aws lambda publish-layer-version \
    --layer-name ${LAYER_NAME} \
    --description "Dependencies including yfinance 1.0, curl_cffi, websockets" \
    --content S3Bucket=${S3_BUCKET},S3Key=${S3_KEY} \
    --compatible-runtimes python3.11 python3.12 \
    --region ${REGION} \
    --query 'LayerVersionArn' \
    --output text)

echo "✅ Layer published: ${LAYER_VERSION_ARN}"

# Update deploy_functions.sh with new ARN
DEPLOY_SCRIPT="../scripts/deploy_functions.sh"
if [ -f "${DEPLOY_SCRIPT}" ]; then
    echo "📝 Updating deployment script..."
    # Escape / in ARN for sed
    ESCAPED_ARN=$(echo ${LAYER_VERSION_ARN} | sed 's/\//\\\//g')
    
    # Replace the LAYER_ARN line
    sed -i '' "s/LAYER_ARN=\".*\"/LAYER_ARN=\"${ESCAPED_ARN}\"/" ${DEPLOY_SCRIPT}
    
    echo "✅ deploy_functions.sh updated"
else
    echo "⚠️  deploy_functions.sh not found at ${DEPLOY_SCRIPT}"
fi

echo "🎉 Fix complete! You can now run ./deploy_functions.sh"

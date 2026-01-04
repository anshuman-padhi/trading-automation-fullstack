#!/bin/bash
set -e

REGION="us-east-1"
ACCOUNT_ID="904583676284"
REPO_NAME="stock-screener"
ECR_URI="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${REPO_NAME}"

echo "🔒 Authenticating with ECR..."
aws ecr get-login-password --region ${REGION} | podman login --username AWS --password-stdin ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com

echo "🐳 Building Docker Image (x86_64 on ARM64)..."
# Running from Project Root, pointing to Dockerfile in aws/lambda
podman build --platform linux/amd64 -t ${REPO_NAME}:latest -f aws/lambda/Dockerfile .

echo "🏷️ Tagging Image..."
podman tag ${REPO_NAME}:latest ${ECR_URI}:latest

echo "☁️ Pushing Image to ECR..."
podman push ${ECR_URI}:latest

echo "✅ Podman build and push complete!"

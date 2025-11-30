#!/bin/bash
set -e

echo "Building frontend..."
cd frontend
npm install
npm run build
cd ..

echo "Installing Python dependencies (prebuilt wheels only)..."
cd backend
pip install --only-binary :all: -r requirements.txt
cd ..

echo "Build complete!"

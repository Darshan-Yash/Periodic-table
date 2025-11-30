#!/bin/bash
set -e

echo "Building frontend..."
cd frontend
npm install
npm run build
echo "Frontend build complete. Dist location: $(pwd)/dist"
cd ..

echo "Verifying frontend dist exists..."
if [ -d "frontend/dist" ]; then
  echo "✓ Frontend dist found at frontend/dist"
  echo "Contents: $(ls -la frontend/dist/)"
else
  echo "✗ ERROR: Frontend dist not found!"
  exit 1
fi

echo "Installing Python dependencies (prebuilt wheels only)..."
cd backend
pip install --only-binary :all: -r requirements.txt
cd ..

echo "Build complete!"

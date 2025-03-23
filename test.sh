#!/bin/bash
# Test script for Bunkr Scraper application

# Create test directories if they don't exist
mkdir -p test_downloads
mkdir -p test_uploads

# Start the backend server in the background
cd backend
source venv/bin/activate
# Make sure all dependencies are installed
pip install -q requests beautifulsoup4 aiohttp tqdm fastapi uvicorn
echo "Starting backend server for testing..."
python -m uvicorn api:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for backend to start
echo "Waiting for backend to start..."
sleep 5

# Run tests
echo "Running tests..."

# Test 1: Get configuration
echo "Test 1: Get configuration"
curl -s http://localhost:8000/config | python3 -m json.tool

# Test 2: Update configuration
echo -e "\nTest 2: Update configuration"
curl -s -X POST http://localhost:8000/config \
  -H "Content-Type: application/json" \
  -d '{"min_size": 5, "max_size": 500, "daily_download_limit": 1000, "time_period": "24h"}' | python3 -m json.tool

# Test 3: Scrape content
echo -e "\nTest 3: Scrape content"
curl -s http://localhost:8000/scrape | python3 -m json.tool

# Test 4: Get usage stats
echo -e "\nTest 4: Get usage stats"
curl -s http://localhost:8000/usage | python3 -m json.tool

# Test 5: List downloads
echo -e "\nTest 5: List downloads"
curl -s http://localhost:8000/downloads | python3 -m json.tool

# Test 6: List uploads
echo -e "\nTest 6: List uploads"
curl -s http://localhost:8000/uploads | python3 -m json.tool

# Kill the backend server
echo -e "\nTests completed. Stopping backend server..."
kill $BACKEND_PID

echo "Testing completed!"

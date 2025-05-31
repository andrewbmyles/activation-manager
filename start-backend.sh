#!/bin/bash
# Start the backend server for Variable Picker

echo "🚀 Starting Activation Manager Backend..."
echo "================================"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed!"
    exit 1
fi

# Navigate to project directory
cd "$(dirname "$0")"

# Check if main.py exists
if [ ! -f "main.py" ]; then
    echo "❌ main.py not found!"
    exit 1
fi

# Start the backend
echo "📦 Starting backend server on port 8080..."
echo "🌐 API will be available at: http://localhost:8080"
echo ""
echo "Press Ctrl+C to stop the server"
echo "================================"
echo ""

# Run the backend
python3 main.py
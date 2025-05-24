#!/bin/bash

export PYTHONPATH=$(pwd)

echo "🔧 Setting up virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "📦 Installing dependencies from requirements.txt..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt

echo "🧪 Running all unit tests..."
echo "=============================="

if [ ! -d "tests" ]; then
  echo "❌ 'tests' directory not found!"
  exit 1
fi

for test_file in tests/test_automation_thread.py; do
  echo "📄 Running: $test_file"
  python "$test_file"
  echo "------------------------------"
done

echo "✅ All tests completed."
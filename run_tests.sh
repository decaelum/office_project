cd ~/Desktop/office_project
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export PYTHONPATH=$(pwd)
python3 tests/test_fetch_urls_with_driver_mac_optimized.py
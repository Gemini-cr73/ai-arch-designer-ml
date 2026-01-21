# run_api.ps1
# Usage: .\scripts\run_api.ps1

.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

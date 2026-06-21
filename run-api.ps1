# Starts the GCC-SWSS FastAPI engine API at http://localhost:8078
# Default CORS already allows http://localhost:3000 (the web dev port).
Set-Location "$PSScriptRoot\api"
$env:PYTHONPATH = "."
& "$PSScriptRoot\engine\.venv\Scripts\python.exe" -m uvicorn app.main:app --port 8078 --reload

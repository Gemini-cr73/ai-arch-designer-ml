# bootstrap_venv.ps1
# Usage: .\scripts\bootstrap_venv.ps1

$ErrorActionPreference = "Stop"

$PROJECT_NAME = "ai-arch-designer-ml"
$VENV_PATH = ".\.venv"
$PY = "python"

Write-Host "==> Creating .venv (if missing)..."
if (-Not (Test-Path $VENV_PATH)) {
  & $PY -m venv .venv
}

Write-Host "==> Activating .venv..."
& .\.venv\Scripts\Activate.ps1

Write-Host "==> Upgrading pip..."
& $PY -m pip install --upgrade pip

# Prefer pyproject.toml editable install; fallback to requirements.txt if you use one
if (Test-Path ".\pyproject.toml") {
  Write-Host "==> Installing project dependencies from pyproject.toml (editable + dev)..."
  pip install -e ".[dev]"
}
elseif (Test-Path ".\requirements.txt") {
  Write-Host "==> Installing dependencies from requirements.txt..."
  pip install -r .\requirements.txt
}
else {
  Write-Host "!! No pyproject.toml or requirements.txt found. Skipping dependency install."
}

Write-Host "==> Installing ipykernel (optional but recommended for notebooks)..."
pip install ipykernel

Write-Host "==> Registering Jupyter kernel for this project..."
& $PY -m ipykernel install --user --name $PROJECT_NAME --display-name "Python (.venv) $PROJECT_NAME"

Write-Host "✅ Done."
Write-Host "👉 Next:"
Write-Host "   - Run API: .\scripts\run_api.ps1"
Write-Host "   - Run tests: .\scripts\run_tests.ps1"

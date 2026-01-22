# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found Python: $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Error "Python is not installed or not in PATH. Please install Python 3.10+."
    exit 1
}

# Define venv path
$venvPath = Join-Path $PSScriptRoot ".venv"

# Create venv if it doesn't exist
if (-not (Test-Path $venvPath)) {
    Write-Host "Creating virtual environment at $venvPath..." -ForegroundColor Cyan
    python -m venv $venvPath
} else {
    Write-Host "Virtual environment already exists at $venvPath." -ForegroundColor Yellow
}

# Activate venv
$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
if (Test-Path $activateScript) {
    Write-Host "Activating virtual environment..." -ForegroundColor Cyan
    . $activateScript
} else {
    Write-Error "Activation script not found at $activateScript"
    exit 1
}

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Cyan
python -m pip install --upgrade pip

# Install requirements
$reqFile = Join-Path $PSScriptRoot "requirements.txt"
if (Test-Path $reqFile) {
    Write-Host "Installing dependencies from requirements.txt..." -ForegroundColor Cyan
    pip install -r $reqFile
} else {
    Write-Warning "requirements.txt not found. Skipping dependency installation."
}

Write-Host "Setup complete! To activate the environment manually, run:" -ForegroundColor Green
Write-Host ". .venv\Scripts\Activate.ps1" -ForegroundColor Gray

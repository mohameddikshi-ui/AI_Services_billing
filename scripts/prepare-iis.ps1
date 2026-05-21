param(
    [string]$Python = "python",
    [string]$VenvPath = ".\.venv",
    [switch]$RecreateVenv
)

$ErrorActionPreference = "Stop"

Set-Location (Split-Path -Parent $PSScriptRoot)

function Test-VenvPython {
    param([string]$Path)

    if (-not (Test-Path $Path)) {
        return $false
    }

    try {
        & $Path --version *> $null
        return $LASTEXITCODE -eq 0
    }
    catch {
        return $false
    }
}

$pythonCommand = Get-Command $Python -ErrorAction SilentlyContinue
if (-not $pythonCommand) {
    throw "Python command '$Python' was not found. Install Python or pass -Python C:\Path\To\python.exe."
}

$VenvPath = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($VenvPath)
$venvPython = Join-Path $VenvPath "Scripts\python.exe"

if ((Test-Path $VenvPath) -and -not (Test-VenvPython $venvPython)) {
    if (-not $RecreateVenv) {
        throw "Existing virtual environment '$VenvPath' is broken or points to a missing Python install. Run .\scripts\prepare-iis.ps1 -RecreateVenv to rebuild it."
    }

    Write-Host "Removing broken virtual environment at $VenvPath..."
    Remove-Item -LiteralPath $VenvPath -Recurse -Force
}

if (-not (Test-Path $VenvPath)) {
    Write-Host "Creating virtual environment at $VenvPath using $($pythonCommand.Source)..."
    & $Python -m venv $VenvPath
}

if (-not (Test-VenvPython $venvPython)) {
    throw "Virtual environment was created, but '$venvPython' could not run."
}

& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -r requirements.txt

if (-not (Test-Path ".\logs")) {
    New-Item -ItemType Directory -Path ".\logs" | Out-Null
}

if (-not (Test-Path ".\.env")) {
    Copy-Item ".\.env.example" ".\.env"
    Write-Host "Created .env from .env.example. Update DB_URL before starting the IIS site."
}

Write-Host "IIS preparation complete."
Write-Host "Verify the server has IIS HttpPlatformHandler and Microsoft ODBC Driver 18 for SQL Server installed."

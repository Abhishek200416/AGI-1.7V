# Run IVA PowerShell wrapper for Windows
if (Get-Command py -ErrorAction SilentlyContinue) {
    & py -3 "$PSScriptRoot\run_iva.py" @args
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    & python "$PSScriptRoot\run_iva.py" @args
} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
    & python3 "$PSScriptRoot\run_iva.py" @args
} else {
    Write-Host "❌ Error: Python 3.10+ was not found on your system." -ForegroundColor Red
    Write-Host "   Please install official Python from https://www.python.org/downloads/" -ForegroundColor Yellow
}

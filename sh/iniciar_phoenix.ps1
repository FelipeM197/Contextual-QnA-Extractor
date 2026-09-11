$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = (Resolve-Path "$ScriptDir\..").Path
$PythonCmd = Join-Path $ProjectRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $PythonCmd)) {
    $PythonCmd = "python"
}

Write-Host "Iniciando Servidor Arize Phoenix en http://127.0.0.1:6006 ..." -ForegroundColor Cyan
& $PythonCmd -m phoenix.server.main serve

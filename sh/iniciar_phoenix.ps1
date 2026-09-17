# ==============================================================================
# Inicio del Servidor Arize Phoenix (PowerShell nativo para Windows)
# ==============================================================================

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = (Resolve-Path "$ScriptDir\..").Path
$PythonCmd = Join-Path $ProjectRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $PythonCmd)) {
    $PythonCmd = "python"
}

# Directorio y archivo de log para esta ejecucion, para poder diagnosticar
# fallos de arranque aunque la ventana se cierre sola.
$LogDir = Join-Path $ProjectRoot "outputs\phoenix-logs"
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$LogFile = Join-Path $LogDir "phoenix_$Timestamp.log"

Write-Host "============================================="
Write-Host " Iniciando Servidor Arize Phoenix"
Write-Host " URL      : http://127.0.0.1:6006"
Write-Host " Python   : $PythonCmd"
Write-Host " Log      : $LogFile"
Write-Host "============================================="

$exitCode = 0
try {
    # 2>&1 combina stdout y stderr; Tee-Object los muestra en pantalla
    # y ademas los guarda en el log para revision posterior.
    & $PythonCmd -m phoenix.server.main serve 2>&1 | Tee-Object -FilePath $LogFile
    $exitCode = $LASTEXITCODE
} catch {
    $_ | Out-String | Tee-Object -FilePath $LogFile -Append
    $exitCode = 1
}

if ($exitCode -ne 0) {
    Write-Host ""
    Write-Host "=============================================" -ForegroundColor Red
    Write-Host " Phoenix termino con codigo de error: $exitCode" -ForegroundColor Red
    Write-Host " Revisa el log completo en:" -ForegroundColor Yellow
    Write-Host " $LogFile" -ForegroundColor Yellow
    Write-Host "=============================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Presiona cualquier tecla para cerrar esta ventana..." -ForegroundColor Yellow
    [void][System.Console]::ReadKey($true)
}

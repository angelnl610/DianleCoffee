$ErrorActionPreference = 'Stop'
$Raiz = Split-Path -Parent $PSScriptRoot
$PythonProyecto = Join-Path $Raiz '.venv\Scripts\python.exe'

function Invoke-PythonProyecto {
    if (-not (Test-Path $PythonProyecto)) {
        throw 'Primero ejecutá preparar_entorno.ps1.'
    }
    Push-Location $Raiz
    try {
        & $PythonProyecto @args
        if ($LASTEXITCODE -ne 0) { throw "Python devolvió código $LASTEXITCODE." }
    } finally {
        Pop-Location
    }
}

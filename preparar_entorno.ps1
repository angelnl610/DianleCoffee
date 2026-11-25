. "$PSScriptRoot\scripts\entorno.ps1"
if (-not (Test-Path $PythonProyecto)) {
    & py -3.13 -m venv (Join-Path $Raiz '.venv')
    if ($LASTEXITCODE -ne 0) { throw 'Instalá Python 3.13 x64 y el lanzador py.' }
}
Invoke-PythonProyecto -m pip install -r requirements.txt

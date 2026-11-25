param([switch]$Descargar)
. "$PSScriptRoot\scripts\entorno.ps1"
$Crudo = Test-Path (Join-Path $Raiz 'data\raw\cafe_raw.csv')
$Manifest = Test-Path (Join-Path $Raiz 'data\raw\manifest.json')
if ($Descargar -or (-not $Crudo -and -not $Manifest)) {
    Invoke-PythonProyecto -m scripts.acquire --limite 2000 --shards 32
}
Invoke-PythonProyecto -m scripts.run_analytics
Invoke-PythonProyecto -m scripts.train

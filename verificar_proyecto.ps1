param([switch]$Sdk)
. "$PSScriptRoot\scripts\entorno.ps1"
if ($Sdk) {
    Invoke-PythonProyecto -m scripts.verify_local --sdk
} else {
    Invoke-PythonProyecto -m scripts.verify_local
}

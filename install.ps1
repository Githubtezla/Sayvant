# Richtet Sayvant ein: virtuelle Umgebung und Pakete.
#   .\install.ps1              CPU (Standard)
#   .\install.ps1 -DirectML    Erkennung zusätzlich auf der Grafikkarte (AMD, Intel, NVIDIA)
param([switch]$DirectML)

$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
$venv = Join-Path $root '.venv'
$py = Join-Path $venv 'Scripts\python.exe'

if (-not (Test-Path $py)) {
    Write-Host 'Lege virtuelle Umgebung an ...'
    python -m venv $venv
}
& $py -m pip install --upgrade pip -q
# constraints.txt hält auch die indirekten Pakete auf dem getesteten Stand
& $py -m pip install -r (Join-Path $root 'requirements.txt') -c (Join-Path $root 'constraints.txt')

if ($DirectML) {
    Write-Host 'Tausche onnxruntime gegen onnxruntime-directml ...'
    & $py -m pip uninstall -y onnxruntime
    & $py -m pip install onnxruntime-directml
}

Write-Host ''
Write-Host 'Fertig. Start mit "Sayvant starten.cmd" (ohne Konsole) oder "Sayvant debug.cmd" (mit Konsole).'

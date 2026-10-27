# Baut dist\Sayvant\Sayvant.exe und, falls Inno Setup installiert ist, den Installer.
#   .\packaging\build.ps1              exe und Installer
#   .\packaging\build.ps1 -SkipInstaller
param([switch]$SkipInstaller, [string]$Python = "")

$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
if (-not $Python) {
    $venv = Join-Path $root '.venv\Scripts\python.exe'
    $Python = if (Test-Path $venv) { $venv } else { 'python' }
}
Push-Location $root
try {
    & $Python -m pip install -q pyinstaller -c constraints.txt
    $version = (& $Python packaging\prepare.py).Trim()
    Write-Host "Sayvant $version"
    & $Python -m PyInstaller packaging\sayvant.spec --noconfirm --clean --distpath dist --workpath build\pyinstaller
    if ($LASTEXITCODE -ne 0) { throw "PyInstaller fehlgeschlagen" }

    if (-not $SkipInstaller) {
        $iscc = @(
            "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
            "$env:ProgramFiles\Inno Setup 6\ISCC.exe",
            "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe"
        ) | Where-Object { Test-Path $_ } | Select-Object -First 1
        if (-not $iscc) { Write-Warning "Inno Setup nicht gefunden, Installer übersprungen."; return }
        & $iscc "/DAppVersion=$version" packaging\sayvant.iss
        if ($LASTEXITCODE -ne 0) { throw "Inno Setup fehlgeschlagen" }
    }
} finally {
    Pop-Location
}

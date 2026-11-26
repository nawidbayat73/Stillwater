@echo off
setlocal
set "STILLWATER_INSTALLER=%~f0"
powershell.exe -NoProfile -Command "$lines=[IO.File]::ReadAllLines($env:STILLWATER_INSTALLER); $start=[Array]::IndexOf($lines,'# Download')+1; try { & ([scriptblock]::Create([string]::Join([Environment]::NewLine,$lines,$start,$lines.Length-$start))) } catch { Write-Host $_.Exception.Message; exit 1 }"
set "STILLWATER_EXIT=%ERRORLEVEL%"
pause
exit /b %STILLWATER_EXIT%
# Download
$ErrorActionPreference='Stop'
$root=Split-Path -Parent $env:STILLWATER_INSTALLER
$url='https://raw.githubusercontent.com/nawidbayat73/Stillwater/downloads-uferstrasse/Stillwater-Uferstrasse-Windows.zip'
$archive=Join-Path $root 'Stillwater-Uferstrasse-Windows.zip'
$partial="$archive.download"
$expected='b59f1ea8b64ce2abd2ea5c5d277e92ee7d4836fe329327b2471d011533b4cbd0'
if (!(Test-Path -LiteralPath $archive)) {
    Write-Host 'Stillwater wird heruntergeladen.'
    & curl.exe --fail --location --retry 3 --connect-timeout 25 --continue-at - --output $partial $url
    if ($LASTEXITCODE -eq 33) {
        & curl.exe --fail --location --retry 3 --connect-timeout 25 --output $partial $url
    }
    if ($LASTEXITCODE -ne 0) { throw 'Download unterbrochen. Starte die BAT erneut, um ihn fortzusetzen.' }
    if ((Get-FileHash -LiteralPath $partial -Algorithm SHA256).Hash -ne $expected) {
        throw 'Download fehlerhaft. Benenne die .download-Datei um und starte die BAT erneut.'
    }
    Move-Item -LiteralPath $partial -Destination $archive
}
if ((Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash -ne $expected) {
    throw 'Die vorhandene ZIP-Datei gehoert nicht zu dieser Version.'
}
$target=Join-Path $root 'Stillwater-Uferstrasse'
Expand-Archive -LiteralPath $archive -DestinationPath $target -Force
Write-Host "Fertig. Starte Stillwater-The-Last-Tide.exe im Ordner $target."

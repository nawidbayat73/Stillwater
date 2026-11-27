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
$exe='Stillwater-The-Last-Tide.exe'
if (Test-Path -LiteralPath (Join-Path $root $exe)) {
    Write-Host "Das Spiel ist in diesem Ordner. Starte $exe oder Stillwater-Starten.bat."
    return
}
$name='Stillwater-Materialien-Windows.zip'
$source='https://media.githubusercontent.com/media/nawidbayat73/Stillwater/downloads-materialien'
$checksums=Invoke-RestMethod -Uri 'https://raw.githubusercontent.com/nawidbayat73/Stillwater/downloads-materialien/SHA256SUMS.txt'
$pattern='(?m)^([a-fA-F0-9]{64}) +'+[regex]::Escape($name)+'\r?$'
$match=[regex]::Match([string]$checksums,$pattern)
if (!$match.Success) { throw 'Die Pruefsumme ist zurzeit nicht erreichbar.' }
$expected=$match.Groups[1].Value
$archive=Join-Path $root $name
$partial="$archive.download"
if (!(Test-Path -LiteralPath $archive)) {
    Write-Host 'Stillwater wird heruntergeladen.'
    & curl.exe --fail --location --retry 3 --connect-timeout 25 --continue-at - --output $partial "$source/$name"
    if ($LASTEXITCODE -eq 33) {
        & curl.exe --fail --location --retry 3 --connect-timeout 25 --output $partial "$source/$name"
    }
    if ($LASTEXITCODE -ne 0) { throw 'Download unterbrochen. Starte die BAT erneut, um ihn fortzusetzen.' }
    if ((Get-FileHash -LiteralPath $partial -Algorithm SHA256).Hash -ne $expected) {
        throw 'Der Download ist beschaedigt. Benenne die .download-Datei um und starte die BAT erneut.'
    }
    Move-Item -LiteralPath $partial -Destination $archive
}
if ((Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash -ne $expected) {
    throw 'Die vorhandene ZIP-Datei passt nicht. Benenne sie um und starte die BAT erneut.'
}
$target=Join-Path $root 'Stillwater-Materialien'
Expand-Archive -LiteralPath $archive -DestinationPath $target -Force
Write-Host "Fertig. Starte $exe im Ordner $target."

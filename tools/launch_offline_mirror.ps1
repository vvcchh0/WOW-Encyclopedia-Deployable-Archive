param([int]$Port = 8765)
$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $ProjectRoot
if (-not (Test-Path -LiteralPath (Join-Path $ProjectRoot 'offline/build-manifest.json'))) {
    throw 'Missing offline/build-manifest.json. Extract the complete offline package first.'
}
$PythonLauncher = Get-Command py -ErrorAction SilentlyContinue
if ($PythonLauncher) {
    $PythonExe = $PythonLauncher.Source
    $PythonArgs = @('-3')
} else {
    $Candidates = @(
        (Join-Path $env:ProgramFiles 'Python311/python.exe'),
        (Join-Path $env:USERPROFILE '.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe')
    )
    $PythonExe = $Candidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
    if (-not $PythonExe) {
        $PythonCommand = Get-Command python -ErrorAction SilentlyContinue
        if ($PythonCommand) { $PythonExe = $PythonCommand.Source }
    }
    if (-not $PythonExe) { throw 'Python 3 is required. Install Python 3 or run offline_mirror.py with your Python interpreter.' }
    $PythonArgs = @()
}
Write-Host "Open http://127.0.0.1:$Port/ for the 2008 official homepage."
Write-Host "Encyclopedia: http://127.0.0.1:$Port/info/encyclopedia/index.xml"
Write-Host 'Keep this window open while browsing; press Ctrl+C to stop.'
& $PythonExe @PythonArgs (Join-Path $PSScriptRoot 'offline_mirror.py') serve --host 127.0.0.1 --port $Port
exit $LASTEXITCODE

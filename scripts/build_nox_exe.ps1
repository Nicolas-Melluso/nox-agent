param(
    [switch]$Clean
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$UvCandidates = @(
    "uv",
    (Join-Path $env:USERPROFILE ".local\bin\uv.exe")
)

$Uv = $null
foreach ($Candidate in $UvCandidates) {
    $Command = Get-Command $Candidate -ErrorAction SilentlyContinue
    if ($Command) {
        $Uv = $Command.Source
        break
    }
    if (Test-Path -LiteralPath $Candidate) {
        $Uv = $Candidate
        break
    }
}

if (-not $Uv) {
    throw "uv was not found. Install uv first: https://docs.astral.sh/uv/getting-started/installation/"
}

Push-Location $RepoRoot
try {
    if ($Clean) {
        Remove-Item -LiteralPath (Join-Path $RepoRoot "build") -Recurse -Force -ErrorAction SilentlyContinue
        Remove-Item -LiteralPath (Join-Path $RepoRoot "dist\nox") -Recurse -Force -ErrorAction SilentlyContinue
    }

    & $Uv sync --extra dev --extra installer
    & $Uv run --extra installer pyinstaller `
        --name nox `
        --onedir `
        --console `
        --clean `
        --noconfirm `
        --paths src `
        packaging/windows/nox_pyinstaller_entry.py

    $ExePath = Join-Path $RepoRoot "dist\nox\nox.exe"
    if (-not (Test-Path -LiteralPath $ExePath)) {
        throw "Expected executable was not created: $ExePath"
    }

    Write-Host "Built: $ExePath"
}
finally {
    Pop-Location
}

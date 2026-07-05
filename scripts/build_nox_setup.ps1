param(
    [switch]$Clean
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$BuildExeScript = Join-Path $RepoRoot "scripts\build_nox_exe.ps1"
$PyprojectPath = Join-Path $RepoRoot "pyproject.toml"

$ProjectVersion = $null
foreach ($Line in Get-Content -LiteralPath $PyprojectPath) {
    if ($Line -match '^version\s*=\s*"([^"]+)"') {
        $ProjectVersion = $Matches[1]
        break
    }
}

if (-not $ProjectVersion) {
    throw "Could not read project version from $PyprojectPath"
}

if ($Clean) {
    & $BuildExeScript -Clean
} else {
    & $BuildExeScript
}

$IsccCandidates = @(
    "ISCC.exe",
    "$env:ProgramFiles\Inno Setup 7\ISCC.exe",
    "${env:ProgramFiles(x86)}\Inno Setup 7\ISCC.exe",
    "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
    "$env:ProgramFiles\Inno Setup 6\ISCC.exe"
)

$Iscc = $null
foreach ($Candidate in $IsccCandidates) {
    $Command = Get-Command $Candidate -ErrorAction SilentlyContinue
    if ($Command) {
        $Iscc = $Command.Source
        break
    }
    if (Test-Path -LiteralPath $Candidate) {
        $Iscc = $Candidate
        break
    }
}

if (-not $Iscc) {
    Write-Warning "Inno Setup compiler was not found. Install Inno Setup to build NoxSetup.exe: https://jrsoftware.org/isdl.php"
    Write-Host "nox.exe is ready at: $(Join-Path $RepoRoot 'dist\nox\nox.exe')"
    exit 2
}

Push-Location $RepoRoot
try {
    & $Iscc "/DMyAppVersion=$ProjectVersion" "packaging\windows\NoxSetup.iss"
    $SetupPath = Join-Path $RepoRoot "dist\installer\NoxSetup.exe"
    if (-not (Test-Path -LiteralPath $SetupPath)) {
        throw "Expected installer was not created: $SetupPath"
    }

    Write-Host "Built: $SetupPath"
}
finally {
    Pop-Location
}

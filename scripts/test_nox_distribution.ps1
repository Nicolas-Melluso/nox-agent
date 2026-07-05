param(
    [Parameter(Mandatory = $true)]
    [string]$ExePath
)

$ErrorActionPreference = "Stop"
$ResolvedExePath = (Resolve-Path -LiteralPath $ExePath).Path
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$ProjectVersion = $null

foreach ($Line in Get-Content -LiteralPath (Join-Path $RepoRoot "pyproject.toml")) {
    if ($Line -match '^version\s*=\s*"([^"]+)"') {
        $ProjectVersion = $Matches[1]
        break
    }
}

if (-not $ProjectVersion) {
    throw "Could not read project version from pyproject.toml"
}

function Invoke-NoxSmoke {
    param(
        [string[]]$Arguments,
        [string]$ExpectedText
    )

    $Output = & $ResolvedExePath @Arguments 2>&1
    $ExitCode = $LASTEXITCODE
    $Text = ($Output | Out-String)

    if ($ExitCode -ne 0) {
        throw "nox $($Arguments -join ' ') failed with exit code $ExitCode.`n$Text"
    }

    if ($ExpectedText -and ($Text -notlike "*$ExpectedText*")) {
        throw "nox $($Arguments -join ' ') did not output expected text '$ExpectedText'.`n$Text"
    }

    return $Text
}

Invoke-NoxSmoke -Arguments @("version") -ExpectedText "nox $ProjectVersion" | Out-Null
Invoke-NoxSmoke -Arguments @("--help") -ExpectedText "api" | Out-Null
Invoke-NoxSmoke -Arguments @("api", "serve", "--help") -ExpectedText "Serve the local HTTP API" | Out-Null

$Workspace = Join-Path ([System.IO.Path]::GetTempPath()) ("nox-dist-smoke-" + [guid]::NewGuid().ToString())
$OutFile = Join-Path $Workspace "api.stdout.log"
$ErrFile = Join-Path $Workspace "api.stderr.log"
New-Item -ItemType Directory -Path $Workspace -Force | Out-Null

try {
    Invoke-NoxSmoke -Arguments @("init", $Workspace) -ExpectedText "Initialized Nox workspace" | Out-Null

    $Listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, 0)
    $Listener.Start()
    $Port = $Listener.LocalEndpoint.Port
    $Listener.Stop()

    $Process = Start-Process `
        -FilePath $ResolvedExePath `
        -ArgumentList @("api", "serve", "--host", "127.0.0.1", "--port", "$Port", "--path", $Workspace) `
        -PassThru `
        -WindowStyle Hidden `
        -RedirectStandardOutput $OutFile `
        -RedirectStandardError $ErrFile

    $HealthUri = "http://127.0.0.1:$Port/health"
    $Started = $false

    for ($Attempt = 0; $Attempt -lt 30; $Attempt++) {
        Start-Sleep -Milliseconds 250
        if ($Process.HasExited) {
            $StdOut = if (Test-Path -LiteralPath $OutFile) { Get-Content -LiteralPath $OutFile -Raw } else { "" }
            $StdErr = if (Test-Path -LiteralPath $ErrFile) { Get-Content -LiteralPath $ErrFile -Raw } else { "" }
            throw "nox api serve exited early with code $($Process.ExitCode).`nSTDOUT:`n$StdOut`nSTDERR:`n$StdErr"
        }

        try {
            $Health = Invoke-RestMethod -Uri $HealthUri -TimeoutSec 2
            if ($Health.status -eq "ok") {
                $Started = $true
                break
            }
        }
        catch {
            # Server may still be starting.
        }
    }

    if (-not $Started) {
        throw "nox api serve did not respond at $HealthUri"
    }
}
finally {
    if ($Process -and -not $Process.HasExited) {
        Stop-Process -Id $Process.Id -Force
        $Process.WaitForExit()
    }
    Remove-Item -LiteralPath $Workspace -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host "Distribution smoke tests passed: $ResolvedExePath"

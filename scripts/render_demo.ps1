$ErrorActionPreference = "Stop"

$repoRoot = Join-Path $PSScriptRoot ".."

if (Get-Command vhs -ErrorAction SilentlyContinue) {
    Push-Location $repoRoot
    try {
        vhs demos/demo.tape
        Write-Host "Demo rendered to demos/demo.gif"
    }
    finally {
        Pop-Location
    }
} else {
    Write-Host "vhs not found in PATH — falling back to Python (Pillow) renderer."
    $python = Join-Path $repoRoot ".venv\Scripts\python.exe"
    if (-not (Test-Path $python)) {
        $python = "python"
    }
    & $python (Join-Path $repoRoot "scripts\make_demo_gif.py")
}

# Install PromptPropulserClaude skill to all coding agent directories
param()

$skillDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$skillName = "promptpropulser"

$targets = @(
    "$env:USERPROFILE\.claude\skills\$skillName",
    "$env:USERPROFILE\.cursor\skills\$skillName",
    "$env:USERPROFILE\.config\opencode\skills\$skillName",
    "$env:USERPROFILE\.codex\skills\$skillName"
)

Write-Host "Installing PromptPropulserClaude skill..." -ForegroundColor Green

$installed = 0
foreach ($target in $targets) {
    New-Item -ItemType Directory -Force -Path $target | Out-Null
    Copy-Item "$skillDir\SKILL.md" -Destination $target -Force
    if (Test-Path "$skillDir\prompts") {
        Copy-Item "$skillDir\prompts" -Destination $target -Recurse -Force -ErrorAction SilentlyContinue
    }
    Write-Host "  → $target"
    $installed++
}

if ($installed -eq 0) {
    $fallback = "$env:USERPROFILE\.claude\skills\$skillName"
    New-Item -ItemType Directory -Force -Path $fallback | Out-Null
    Copy-Item "$skillDir\SKILL.md" -Destination $fallback -Force
    Write-Host "  → $fallback (fallback)"
}

Write-Host ""
Write-Host "PromptPropulserClaude installed." -ForegroundColor Green
Write-Host "Your coding agents will auto-load the skill on next session."

#!/usr/bin/env pwsh
# ============================================================================
# MW-Vision Auto-Backup Script
# 
# This script automatically backs up your changes to GitHub.
# Run it manually or schedule with Windows Task Scheduler.
# 
# Schedule with: schtasks /create /tn "MW-Vision Backup" /tr "powershell.exe -File C:\path\to\auto-git-backup.ps1" /sc HOURLY
# ============================================================================

$ErrorActionPreference = "Stop"

# Configuration
$repoPath = "L:\nicedev-Project\MW-Vision"
$branch = "main"
$commitMsg = "chore: auto-backup $(Get-Date -Format 'yyyy-MM-dd HH:mm')"

# Colors for output
$Green = "#00FF00"
$Cyan = "#00FFFF"
$Yellow = "#FFFF00"
$Red = "#FF0000"

function Write-Status {
    param([string]$Message, [string]$Color = $Cyan)
    Write-Host "[$((Get-Date).ToString('HH:mm:ss'))]" -ForegroundColor Gray -NoNewline
    Write-Host " $Message" -ForegroundColor $Color
}

function Test-GitRepository {
    try {
        $result = git -C $repoPath rev-parse --git-dir 2>$null
        return $null -ne $result
    } catch {
        return $false
    }
}

function Test-GitHubRemote {
    try {
        $remotes = git -C $repoPath remote -v
        return $remotes -match "github"
    } catch {
        return $false
    }
}

function Get-UncommittedChanges {
    $status = git -C $repoPath status --porcelain
    return $status.Count
}

function Push-ToGitHub {
    Write-Status "Pushing to GitHub..." $Yellow
    
    try {
        git -C $repoPath push origin $branch
        Write-Status "✅ Successfully pushed to GitHub!" $Green
        return $true
    } catch {
        Write-Status "❌ Failed to push: $_" $Red
        return $false
    }
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════╗" -ForegroundColor $Cyan
Write-Host "║         MW-VISION AUTO-BACKUP SCRIPT                ║" -ForegroundColor $Cyan
Write-Host "╚══════════════════════════════════════════════════════╝" -ForegroundColor $Cyan
Write-Host ""

# Check if Git repository exists
if (-not (Test-GitRepository)) {
    Write-Status "❌ Not a Git repository: $repoPath" $Red
    exit 1
}
Write-Status "✅ Git repository found"

# Check GitHub remote
if (-not (Test-GitHubRemote)) {
    Write-Status "⚠️  No GitHub remote configured" $Yellow
} else {
    Write-Status "✅ GitHub remote configured"
}

# Check for uncommitted changes
$changes = Get-UncommittedChanges
if ($changes -eq 0) {
    Write-Status "No changes to commit" $Green
} else {
    Write-Status "Found $changes uncommitted change(s)" $Yellow
    
    # Stage all changes
    Write-Status "Staging changes..." $Yellow
    git -C $repoPath add -A
    
    # Create commit
    Write-Status "Creating commit..." $Yellow
    git -C $repoPath commit -m $commitMsg
    
    # Push to GitHub
    Push-ToGitHub
}

Write-Host ""
Write-Status "Backup complete!" $Green
Write-Host ""

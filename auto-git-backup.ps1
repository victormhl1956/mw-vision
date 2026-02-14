# MW-Vision Auto-Commit Script
# Automatic version control system for MW-Vision project
# Runs every 30 minutes and commits changes to GitHub

$repoPath = "L:\nicedev-Project\MW-Vision"
$interval = 1800 # 30 minutes in seconds
$logFile = "$repoPath\auto-backup.log"

function Write-Log {
    param($Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] $Message"
    Write-Host $logEntry
    Add-Content -Path $logFile -Value $logEntry
}

Write-Log "=== MW-Vision Auto-Backup System Started ==="
Write-Log "Repository: $repoPath"
Write-Log "Interval: $interval seconds (30 minutes)"
Write-Log "Press Ctrl+C to stop"

while ($true) {
    try {
        Set-Location $repoPath
        
        # Check for changes
        $status = git status --porcelain
        
        if ($status) {
            $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
            $changedFiles = ($status -split "`n").Count
            
            Write-Log "Changes detected: $changedFiles file(s)"
            
            # Add all changes
            git add . 2>&1 | Out-Null
            
            # Commit with timestamp
            $commitMessage = "chore: auto-save checkpoint - $timestamp"
            git commit -m $commitMessage 2>&1 | Out-Null
            
            # Push to GitHub
            $pushResult = git push origin main 2>&1
            
            if ($LASTEXITCODE -eq 0) {
                Write-Log "✅ AUTO-BACKUP SUCCESS - Changes committed and pushed to GitHub"
                Write-Log "   Files changed: $changedFiles"
                Write-Log "   Commit: $commitMessage"
            } else {
                Write-Log "⚠️ AUTO-BACKUP WARNING - Commit successful, but push failed"
                Write-Log "   Error: $pushResult"
            }
        } else {
            Write-Log "No changes detected - skipping backup"
        }
    }
    catch {
        Write-Log "❌ ERROR: $($_.Exception.Message)"
    }
    
    # Wait 30 minutes
    Write-Log "Next backup check in 30 minutes..."
    Start-Sleep -Seconds $interval
}
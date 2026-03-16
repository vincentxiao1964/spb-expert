$ErrorActionPreference = "Stop"

# Configuration
$ServerUser = "root"
$ServerIP = "101.35.139.208"
$RemotePath = "/root/spb-expert9"
$LocalScript = "diagnose.py"

Write-Host "=== SPB-Expert9 Diagnosis Tool ===" -ForegroundColor Cyan
Write-Host "Uploading diagnosis script..."

# Upload script
scp $LocalScript ${ServerUser}@${ServerIP}:${RemotePath}/

Write-Host "Running diagnosis on server..."
Write-Host "Please enter server password if prompted." -ForegroundColor Yellow

# Run script
ssh ${ServerUser}@${ServerIP} "cd ${RemotePath} && source venv/bin/activate && python diagnose.py"

Write-Host "`n=== Done ===" -ForegroundColor Cyan

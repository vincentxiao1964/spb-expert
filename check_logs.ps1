$ErrorActionPreference = "Stop"

# Configuration
$ServerUser = "root"
$ServerIP = "101.35.139.208"

Write-Host "=== SPB-Expert9 Log Checker ===" -ForegroundColor Cyan
Write-Host "This script will fetch the latest server logs to diagnose the 'Unknown Error'."
Write-Host "Target: $ServerUser@$ServerIP"
Write-Host "Note: Please enter your server password when prompted." -ForegroundColor Yellow

# SSH and tail the log file
ssh ${ServerUser}@${ServerIP} "tail -n 50 /root/spb-expert9/nohup.out"

Write-Host "`n=== End of Logs ===" -ForegroundColor Cyan

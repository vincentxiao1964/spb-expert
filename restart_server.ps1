$ErrorActionPreference = "Stop"

# Configuration
$ServerUser = "root"
$ServerIP = "101.35.139.208"
$RemotePath = "/root/spb-expert9"

Write-Host "=== Restarting SPB-Expert9 Server ===" -ForegroundColor Cyan
Write-Host "Connecting to server..."
Write-Host "Please enter server password if prompted." -ForegroundColor Yellow

$RemoteScript = @"
cd $RemotePath
source venv/bin/activate

echo "--- Killing old process ---"
fuser -k 8000/tcp || true

echo "--- Starting new server ---"
nohup python manage.py runserver 0.0.0.0:8000 > nohup.out 2>&1 &

echo "--- Checking logs ---"
sleep 2
tail -n 10 nohup.out
"@

# Execute remote script
ssh ${ServerUser}@${ServerIP} $RemoteScript

Write-Host "`n=== Server Restarted ===" -ForegroundColor Cyan

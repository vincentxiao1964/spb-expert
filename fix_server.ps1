$ErrorActionPreference = "Stop"

# Configuration
$ServerUser = "root"
$ServerIP = "101.35.139.208"
$RemotePath = "/root/spb-expert9"

Write-Host "=== SPB-Expert9 Server Fix Script (Round 2) ===" -ForegroundColor Cyan
Write-Host "This script will FORCE DOWNGRADE dependencies to Python 3.6 compatible versions."
Write-Host "Target: $ServerUser@$ServerIP"

Write-Host "Note: You may be asked to enter your server password multiple times." -ForegroundColor Yellow

# 1. Upload new requirements.txt
Write-Host "1/3 Uploading Python 3.6 compatible requirements.txt..." -ForegroundColor Green
scp .\requirements.txt ${ServerUser}@${ServerIP}:${RemotePath}/requirements.txt

# 2. Upload a helper shell script to run on server
$RemoteScript = @"
cd $RemotePath
source venv/bin/activate

echo "Cleaning up conflicting packages..."
# Force uninstall problematic packages to avoid dependency resolution conflicts
pip uninstall -y djangorestframework-simplejwt PyJWT djangorestframework django-cors-headers Werkzeug

echo "Installing Python 3.6 compatible dependencies..."
pip install -r requirements.txt

echo "Restarting service..."
# Find and kill existing runserver (port 8000)
fuser -k 8000/tcp || true
# Start new server
nohup python manage.py runserver 0.0.0.0:8000 > nohup.out 2>&1 &
echo "Server restarted. Logs:"
tail -n 5 nohup.out
"@

# Save remote script locally temporarily
Set-Content -Path ".\remote_fix.sh" -Value $RemoteScript -Encoding ASCII

# Upload the remote script
Write-Host "2/3 Uploading fix script..." -ForegroundColor Green
scp .\remote_fix.sh ${ServerUser}@${ServerIP}:${RemotePath}/remote_fix.sh

# 3. Execute the remote script
Write-Host "3/3 Executing fix on server..." -ForegroundColor Green
ssh ${ServerUser}@${ServerIP} "bash ${RemotePath}/remote_fix.sh"

# Cleanup
Remove-Item ".\remote_fix.sh"

Write-Host "=== Fix Complete! ===" -ForegroundColor Cyan
Write-Host "The 'decode' error should be gone. Please try WeChat login again."

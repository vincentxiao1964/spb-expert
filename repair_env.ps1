$ErrorActionPreference = "Stop"

# Configuration
$ServerUser = "root"
$ServerIP = "101.35.139.208"
$RemotePath = "/root/spb-expert9"

Write-Host "=== SPB-Expert9 Environment Repair Tool ===" -ForegroundColor Cyan
Write-Host "Connecting to server to repair Python environment..."
Write-Host "Please enter server password if prompted." -ForegroundColor Yellow

$RemoteScript = @"
cd $RemotePath
source venv/bin/activate

echo "--- Verifying pip ---"
pip --version

echo "--- Re-installing missing core dependencies ---"
# Install simplejwt 4.4.0 which is available in the mirror
pip install "djangorestframework-simplejwt==4.4.0"

echo "--- Checking installation status ---"
python -c "import rest_framework; print('DRF version: ' + rest_framework.VERSION)"
python -c "import jwt; print('PyJWT version: ' + jwt.__version__)"
python -c "import rest_framework_simplejwt; print('SimpleJWT version: ' + rest_framework_simplejwt.__version__)"

echo "--- Restarting service ---"
fuser -k 8000/tcp || true
nohup python manage.py runserver 0.0.0.0:8000 > nohup.out 2>&1 &
echo "Server restarted. Logs:"
tail -n 10 nohup.out
"@

# Execute remote script
ssh ${ServerUser}@${ServerIP} $RemoteScript

Write-Host "`n=== Repair Complete ===" -ForegroundColor Cyan

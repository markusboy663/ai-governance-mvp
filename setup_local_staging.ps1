# Local Staging Environment Setup
# This script prepares the local environment for testing

Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║      🚀 LOCAL STAGING ENVIRONMENT SETUP                      ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Step 1: Backend Setup
Write-Host "Step 1️⃣  Backend Setup" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

cd backend

# Check if venv exists
if (-Not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Gray
    python -m venv venv
}

# Activate venv
Write-Host "Activating virtual environment..." -ForegroundColor Gray
.\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Gray
pip install -r requirements.txt -q

Write-Host "✅ Backend setup complete" -ForegroundColor Green
Write-Host ""

# Step 2: Environment Configuration
Write-Host "Step 2️⃣  Environment Configuration" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

# Check DATABASE_URL
$env_file = ".env"
if (Test-Path $env_file) {
    $database_url = (Select-String -Path $env_file -Pattern "DATABASE_URL" | Select-Object -First 1).Line
    Write-Host "Found: $database_url" -ForegroundColor Gray
} else {
    Write-Host "✅ .env file exists" -ForegroundColor Green
}

Write-Host "Set env: DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/ai_governance" -ForegroundColor Gray
$env:DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/ai_governance"

Write-Host "✅ Environment configured" -ForegroundColor Green
Write-Host ""

# Step 3: Database Migrations
Write-Host "Step 3️⃣  Database Migrations" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "⚠️  PostgreSQL required: docker-compose up -d  (or local PostgreSQL)" -ForegroundColor Yellow
Write-Host "To run migrations when DB is ready:" -ForegroundColor Gray
Write-Host "  alembic upgrade head" -ForegroundColor Cyan
Write-Host "  python scripts/seed_policies.py" -ForegroundColor Cyan
Write-Host ""

# Step 4: Test API Key
Write-Host "Step 4️⃣  Generate Test API Key" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

$test_key = "test_key_staging_12345678901234"
Write-Host "Test API Key: $test_key" -ForegroundColor Green
Write-Host "Copy this for: Authorization: Bearer [KEY]" -ForegroundColor Gray
Write-Host ""

# Step 5: Backend Server
Write-Host "Step 5️⃣  Start Backend Server" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "Ready to start! Run in a new terminal:" -ForegroundColor Gray
Write-Host "  cd backend" -ForegroundColor Cyan
Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor Cyan
Write-Host "  python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000" -ForegroundColor Cyan
Write-Host ""

# Step 6: Frontend
Write-Host "Step 6️⃣  Start Frontend" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "In another terminal:" -ForegroundColor Gray
Write-Host "  cd frontend" -ForegroundColor Cyan
Write-Host "  npm install" -ForegroundColor Cyan
Write-Host "  npm run dev" -ForegroundColor Cyan
Write-Host ""

# Step 7: Testing
Write-Host "Step 7️⃣  Test the Stack" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "In a third terminal, test endpoints:" -ForegroundColor Gray
Write-Host ""
Write-Host "1. Health Check:" -ForegroundColor Cyan
Write-Host "   curl http://127.0.0.1:8000/health" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Protected Endpoint (requires API key):" -ForegroundColor Cyan
Write-Host "   curl -X POST http://127.0.0.1:8000/v1/check \" -ForegroundColor Gray
Write-Host "     -H `"Authorization: Bearer $test_key`" \" -ForegroundColor Gray
Write-Host "     -H `"Content-Type: application/json`" \" -ForegroundColor Gray
Write-Host "     -d '{`"model`":`"gpt-4`",`"operation`":`"classify`",`"metadata`":{}}'" -ForegroundColor Gray
Write-Host ""

Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  ✅ SETUP COMPLETE - Ready for local testing                 ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "📚 Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Start PostgreSQL: docker-compose up -d" -ForegroundColor Gray
Write-Host "  2. Run migrations: alembic upgrade head" -ForegroundColor Gray
Write-Host "  3. Start services in 3 terminals (see above)" -ForegroundColor Gray
Write-Host "  4. Test endpoints with curl commands" -ForegroundColor Gray
Write-Host ""

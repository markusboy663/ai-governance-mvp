# Test Script for AI Governance MVP
# Usage: .\test_api.ps1

param(
    [string]$ApiKey = "api_test_key",
    [string]$BaseUrl = "http://localhost:8000"
)

Write-Host "🧪 AI Governance MVP - API Test Script" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Test 1: Health Check
Write-Host "Test 1: Health Endpoint" -ForegroundColor Yellow
Write-Host "GET $BaseUrl/health"
try {
    $response = Invoke-WebRequest -Uri "$BaseUrl/health" -Method Get -ErrorAction Stop
    Write-Host "✅ Status: $($response.StatusCode)" -ForegroundColor Green
    Write-Host $response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 2
} catch {
    Write-Host "❌ Failed: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 2: Check endpoint - Valid Request
Write-Host "Test 2: /v1/check - Valid Request" -ForegroundColor Yellow
Write-Host "POST $BaseUrl/v1/check (Valid governance request)" -ForegroundColor Gray

$body = @{
    model = "gpt-4"
    operation = "classify"
    metadata = @{
        intent = "spam_detection"
    }
} | ConvertTo-Json

Write-Host "Body: $body"
try {
    $response = Invoke-WebRequest -Uri "$BaseUrl/v1/check" `
        -Method Post `
        -Headers @{
            "Authorization" = "Bearer $ApiKey"
            "Content-Type" = "application/json"
        } `
        -Body $body `
        -ErrorAction Stop
    Write-Host "✅ Status: $($response.StatusCode)" -ForegroundColor Green
    $response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 2
} catch {
    if ($_.Exception.Response.StatusCode -eq 401) {
        Write-Host "⚠️  Unauthorized (401) - API key invalid or missing" -ForegroundColor Yellow
        Write-Host "Note: This is expected if DATABASE_URL not configured" -ForegroundColor Gray
    } else {
        Write-Host "❌ Failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}
Write-Host ""

# Test 3: Check endpoint - Blocked (Personal Data)
Write-Host "Test 3: /v1/check - Blocked Request (Personal Data)" -ForegroundColor Yellow
Write-Host "POST $BaseUrl/v1/check (Should be blocked)" -ForegroundColor Gray

$body = @{
    model = "gpt-4"
    operation = "analyze"
    metadata = @{
        contains_personal_data = $true
    }
} | ConvertTo-Json

Write-Host "Body: $body"
try {
    $response = Invoke-WebRequest -Uri "$BaseUrl/v1/check" `
        -Method Post `
        -Headers @{
            "Authorization" = "Bearer $ApiKey"
            "Content-Type" = "application/json"
        } `
        -Body $body `
        -ErrorAction Stop
    Write-Host "✅ Status: $($response.StatusCode)" -ForegroundColor Green
    $json = $response.Content | ConvertFrom-Json
    Write-Host ($json | ConvertTo-Json -Depth 2)
    
    if ($json.allowed -eq $false) {
        Write-Host "✅ Correctly blocked (risk_score: $($json.risk_score), reason: $($json.reason))" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Failed: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 4: Check endpoint - External Model
Write-Host "Test 4: /v1/check - External Model Detected" -ForegroundColor Yellow
Write-Host "POST $BaseUrl/v1/check (External model flag)" -ForegroundColor Gray

$body = @{
    model = "claude-3"
    operation = "generate"
    metadata = @{
        is_external_model = $true
    }
} | ConvertTo-Json

Write-Host "Body: $body"
try {
    $response = Invoke-WebRequest -Uri "$BaseUrl/v1/check" `
        -Method Post `
        -Headers @{
            "Authorization" = "Bearer $ApiKey"
            "Content-Type" = "application/json"
        } `
        -Body $body `
        -ErrorAction Stop
    Write-Host "✅ Status: $($response.StatusCode)" -ForegroundColor Green
    $json = $response.Content | ConvertFrom-Json
    Write-Host ($json | ConvertTo-Json -Depth 2)
    
    if ($json.allowed -eq $false) {
        Write-Host "✅ Correctly blocked (risk_score: $($json.risk_score), reason: $($json.reason))" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Failed: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 5: Invalid API Key
Write-Host "Test 5: Invalid API Key (Should return 401)" -ForegroundColor Yellow
Write-Host "POST $BaseUrl/v1/check (Invalid authorization)" -ForegroundColor Gray

$body = @{
    model = "gpt-4"
    operation = "test"
    metadata = @{}
} | ConvertTo-Json

try {
    $response = Invoke-WebRequest -Uri "$BaseUrl/v1/check" `
        -Method Post `
        -Headers @{
            "Authorization" = "Bearer invalid_key_12345"
            "Content-Type" = "application/json"
        } `
        -Body $body `
        -ErrorAction Stop
    Write-Host "❌ Should have been rejected" -ForegroundColor Red
} catch {
    if ($_.Exception.Response.StatusCode -eq 401 -or $_.Exception.Response.StatusCode -eq 403) {
        Write-Host "✅ Correctly rejected with status: $($_.Exception.Response.StatusCode)" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Unexpected error: $($_.Exception.Message)" -ForegroundColor Yellow
    }
}
Write-Host ""

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "✅ Test script completed!" -ForegroundColor Cyan
Write-Host ""
Write-Host "Note: Some tests may fail if:" -ForegroundColor Gray
Write-Host "  - Backend not running (start with: uvicorn main:app --reload)" -ForegroundColor Gray
Write-Host "  - DATABASE_URL not configured in .env" -ForegroundColor Gray
Write-Host "  - API key not generated (run: python scripts/generate_api_key.py test@example.com)" -ForegroundColor Gray

# Postman Collection Runner - PowerShell Version
# Runs AI Governance MVP Postman collection tests
# 
# Usage:
#   .\run_postman_tests.ps1
#   .\run_postman_tests.ps1 -BaseUrl "http://staging.example.com"
#   .\run_postman_tests.ps1 -ApiKey "your_custom_key"
#   .\run_postman_tests.ps1 -GenerateReport

param(
    [string]$BaseUrl = "http://localhost:8000",
    [string]$ApiKey = "test_key_staging_12345678901234",
    [switch]$GenerateReport = $false,
    [string]$CollectionPath = "docs/postman_collection.json"
)

# Color constants
$Colors = @{
    Green = @{ ForegroundColor = 'Green' }
    Red = @{ ForegroundColor = 'Red' }
    Yellow = @{ ForegroundColor = 'Yellow' }
    Blue = @{ ForegroundColor = 'Cyan' }
    Bold = @{ ForegroundColor = 'White'; Intensity = 'Bold' }
}

function Write-Header {
    param([string]$Text)
    Write-Host ""
    Write-Host "$(([char]0xF0A9) * 60)" @($Colors.Blue)
    Write-Host "$Text" @($Colors.Bold)
    Write-Host "$(([char]0xF0A9) * 60)" @($Colors.Blue)
    Write-Host ""
}

function Write-Success {
    param([string]$Text)
    Write-Host "✅ $Text" @($Colors.Green)
}

function Write-Error-Custom {
    param([string]$Text)
    Write-Host "❌ $Text" @($Colors.Red)
}

function Write-Warning-Custom {
    param([string]$Text)
    Write-Host "⚠️  $Text" @($Colors.Yellow)
}

function Write-Info {
    param([string]$Text)
    Write-Host "ℹ️  $Text" @($Colors.Blue)
}

# Check if collection exists
if (-not (Test-Path $CollectionPath)) {
    Write-Error-Custom "Collection not found: $CollectionPath"
    exit 1
}

# Check if Newman is installed
Write-Info "Checking for Newman (Postman CLI)..."
$NewmanVersion = npm list -g newman 2>$null | Select-String "newman@"

if ($NewmanVersion) {
    Write-Success "Newman is installed: $NewmanVersion"
} else {
    Write-Warning-Custom "Newman not found globally. Installing..."
    npm install -g newman | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Newman installed successfully"
    } else {
        Write-Error-Custom "Failed to install Newman"
        Write-Host "Install manually with: npm install -g newman"
        exit 1
    }
}

# Create temporary environment file
$TempEnvFile = "temp_postman_env.json"
$EnvData = @{
    id = "ai-governance-test-env"
    name = "AI Governance MVP - Test"
    values = @(
        @{ key = "BASE_URL"; value = $BaseUrl; enabled = $true; type = "string" },
        @{ key = "API_KEY"; value = $ApiKey; enabled = $true; type = "string" },
        @{ key = "request_count"; value = "0"; enabled = $true; type = "string" }
    )
    _postman_variable_scope = "environment"
    _postman_exported_at = (Get-Date -Format "o")
} | ConvertTo-Json

$EnvData | Out-File -Encoding UTF8 -FilePath $TempEnvFile

Write-Success "Test environment created"

# Build Newman command
Write-Header "🚀 Running Postman Collection Tests"
Write-Info "Collection: $CollectionPath"
Write-Info "Base URL: $BaseUrl"
Write-Info "Environment: $TempEnvFile"
Write-Host ""

$NewmanArgs = @(
    "run"
    $CollectionPath
    "--environment", $TempEnvFile
    "--reporters", "cli,json"
    "--reporter-json-export", "postman_results.json"
)

if ($GenerateReport) {
    $NewmanArgs += @("--reporter-html-export", "postman_report.html")
}

# Run Newman
npx newman @NewmanArgs
$ExitCode = $LASTEXITCODE

# Parse results if available
if (Test-Path "postman_results.json") {
    $Results = Get-Content "postman_results.json" | ConvertFrom-Json
    
    Write-Header "📊 Test Execution Summary"
    
    $Stats = $Results.run.stats
    $Total = $Stats.requests.total
    $Failed = $Stats.requests.failed
    $Passed = $Total - $Failed
    
    Write-Host "Total Requests: $Total"
    Write-Success "Passed: $Passed"
    if ($Failed -gt 0) {
        Write-Error-Custom "Failed: $Failed"
    }
    
    $AssertStats = $Stats.assertions
    $TotalAssertions = $AssertStats.total
    $FailedAssertions = $AssertStats.failed
    $PassedAssertions = $TotalAssertions - $FailedAssertions
    
    Write-Host ""
    Write-Host "Total Assertions: $TotalAssertions"
    Write-Success "Passed: $PassedAssertions"
    if ($FailedAssertions -gt 0) {
        Write-Error-Custom "Failed: $FailedAssertions"
    }
    
    $Duration = $Results.run.timings.total
    Write-Host ""
    Write-Host "Total Duration: $($Duration)ms"
}

# Report info
if ($GenerateReport -and (Test-Path "postman_report.html")) {
    Write-Success "HTML report generated: postman_report.html"
}

# Cleanup
Remove-Item -Path $TempEnvFile -Force -ErrorAction SilentlyContinue

Write-Host ""
if ($ExitCode -eq 0) {
    Write-Success "All tests passed! ✅"
} else {
    Write-Warning-Custom "Some tests failed (exit code: $ExitCode)"
}

exit $ExitCode

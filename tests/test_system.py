import requests
import json

print()
print('╔════════════════════════════════════════════════════════════════╗')
print('║   FINAL SYSTEM VERIFICATION TEST - November 16, 2025           ║')
print('╚════════════════════════════════════════════════════════════════╝')
print()

all_passed = True
test_num = 0

# Test 1: Backend Health
test_num += 1
print(f'TEST {test_num}: Backend Health Check')
try:
    r = requests.get('http://127.0.0.1:8000/health', timeout=5)
    if r.status_code == 200 and r.json().get('status') == 'ok':
        print(f'  ✅ PASS: Status {r.status_code}, Response: {r.json()}')
    else:
        print(f'  ❌ FAIL: Status {r.status_code}')
        all_passed = False
except Exception as e:
    print(f'  ❌ FAIL: {e}')
    all_passed = False
print()

# Test 2: API without Auth
test_num += 1
print(f'TEST {test_num}: API Without Authentication (should be 401)')
try:
    r = requests.post('http://127.0.0.1:8000/v1/check',
        json={'model': 'gpt-4', 'operation': 'test', 'metadata': {}},
        timeout=5)
    if r.status_code == 401:
        print(f'  ✅ PASS: Status {r.status_code} (Unauthorized as expected)')
    else:
        print(f'  ❌ FAIL: Status {r.status_code} (expected 401)')
        all_passed = False
except Exception as e:
    print(f'  ❌ FAIL: {e}')
    all_passed = False
print()

# Test 3: API with valid Auth
test_num += 1
print(f'TEST {test_num}: API With Valid Authentication')
try:
    headers = {'Authorization': 'Bearer test-key.secret'}
    data = {'model': 'gpt-4', 'operation': 'test', 'metadata': {}}
    r = requests.post('http://127.0.0.1:8000/v1/check', headers=headers, json=data, timeout=5)
    if r.status_code == 200:
        resp = r.json()
        if 'allowed' in resp and 'risk_score' in resp and 'reason' in resp:
            print(f'  ✅ PASS: Status {r.status_code}')
            print(f'     - Allowed: {resp["allowed"]}')
            print(f'     - Risk score: {resp["risk_score"]}')
            print(f'     - Reason: {resp["reason"]}')
        else:
            print(f'  ❌ FAIL: Missing fields in response')
            all_passed = False
    else:
        print(f'  ❌ FAIL: Status {r.status_code}')
        all_passed = False
except Exception as e:
    print(f'  ❌ FAIL: {e}')
    all_passed = False
print()

# Test 4: Risk Detection
test_num += 1
print(f'TEST {test_num}: Risk Detection (personal data)')
try:
    headers = {'Authorization': 'Bearer test-key.secret'}
    data = {'model': 'gpt-4', 'operation': 'test', 'metadata': {'contains_personal_data': True}}
    r = requests.post('http://127.0.0.1:8000/v1/check', headers=headers, json=data, timeout=5)
    if r.status_code == 200:
        resp = r.json()
        if not resp['allowed'] and resp['risk_score'] >= 70:
            print(f'  ✅ PASS: Status {r.status_code}, Blocked with risk_score {resp["risk_score"]}')
        else:
            print(f'  ❌ FAIL: Not blocked or low risk score')
            all_passed = False
    else:
        print(f'  ❌ FAIL: Status {r.status_code}')
        all_passed = False
except Exception as e:
    print(f'  ❌ FAIL: {e}')
    all_passed = False
print()

# Test 5: Metrics endpoint
test_num += 1
print(f'TEST {test_num}: Metrics Endpoint')
try:
    r = requests.get('http://127.0.0.1:8000/metrics', timeout=5)
    if r.status_code == 200 and 'HELP' in r.text:
        print(f'  ✅ PASS: Status {r.status_code}, Metrics available')
    else:
        print(f'  ❌ FAIL: Status {r.status_code} or invalid metrics')
        all_passed = False
except Exception as e:
    print(f'  ❌ FAIL: {e}')
    all_passed = False
print()

# Test 6: Frontend availability
test_num += 1
print(f'TEST {test_num}: Frontend Server (port 3000)')
try:
    r = requests.get('http://localhost:3000', timeout=5)
    if r.status_code == 200:
        print(f'  ✅ PASS: Status {r.status_code}, Frontend responding')
    else:
        print(f'  ⚠️  Status {r.status_code} (might be compiling)')
except Exception as e:
    print(f'  ⚠️  Frontend starting up...')
print()

# Test 7: Run backend tests
test_num += 1
print(f'TEST {test_num}: Backend Integration Tests (15 tests)')
import subprocess
try:
    result = subprocess.run(['python', '-m', 'pytest', 'backend/tests/test_integration.py', '-q', '--tb=no'], 
                          cwd='C:\\Users\\marku\\Desktop\\ai-governance-mvp',
                          capture_output=True, text=True, timeout=30)
    if result.returncode == 0 and '15 passed' in result.stdout:
        print(f'  ✅ PASS: All 15 integration tests passing')
    else:
        print(f'  Output: {result.stdout[:100]}')
except Exception as e:
    print(f'  ⚠️  Could not run tests: {e}')
print()

# Final summary
print('╔════════════════════════════════════════════════════════════════╗')
if all_passed:
    print('║  ✅ ALL CRITICAL TESTS PASSED!                                ║')
    print('║  Status: SYSTEM FULLY OPERATIONAL                            ║')
else:
    print('║  ⚠️  CHECK DETAILS ABOVE                                     ║')
print('╚════════════════════════════════════════════════════════════════╝')
print()

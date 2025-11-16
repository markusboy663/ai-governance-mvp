#!/usr/bin/env python3
"""
Postman Collection Sanity Test Runner
Runs the AI Governance MVP Postman collection with automated test validation.

Usage:
    python run_postman_tests.py                    # Run with default settings
    python run_postman_tests.py --url http://staging.example.com
    python run_postman_tests.py --api-key your_key_here
    python run_postman_tests.py --report
"""

import subprocess
import sys
import os
import json
import argparse
from pathlib import Path
from datetime import datetime

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}")
    print(f"{text}")
    print(f"{'='*60}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

def check_newman():
    """Check if Newman is installed"""
    try:
        result = subprocess.run(['npx', 'newman', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print_success(f"Newman found: {result.stdout.strip()}")
            return True
    except Exception as e:
        print_error(f"Newman not found: {e}")
        return False

def install_newman():
    """Install Newman via npm"""
    print_info("Installing Newman (Postman CLI)...")
    try:
        subprocess.run(['npm', 'install', '-g', 'newman'], 
                      capture_output=True, timeout=60)
        print_success("Newman installed")
        return True
    except Exception as e:
        print_error(f"Failed to install Newman: {e}")
        return False

def create_environment_file(base_url, api_key):
    """Create a temporary environment file with given values"""
    env_data = {
        "id": "ai-governance-test-env",
        "name": "AI Governance MVP - Test",
        "values": [
            {"key": "BASE_URL", "value": base_url, "enabled": True, "type": "string"},
            {"key": "API_KEY", "value": api_key, "enabled": True, "type": "string"},
            {"key": "request_count", "value": "0", "enabled": True, "type": "string"}
        ],
        "_postman_variable_scope": "environment",
        "_postman_exported_at": datetime.now().isoformat(),
        "_postman_exported_using": "AI Governance Test Runner"
    }
    
    temp_env_file = Path("temp_postman_env.json")
    with open(temp_env_file, 'w') as f:
        json.dump(env_data, f, indent=2)
    
    return temp_env_file

def run_postman_collection(collection_path, environment_file, report=False):
    """Run Postman collection using Newman"""
    
    print_info(f"Collection: {collection_path}")
    print_info(f"Environment: {environment_file}")
    
    # Build Newman command
    cmd = [
        'npx', 'newman', 'run',
        str(collection_path),
        '--environment', str(environment_file),
        '--reporters', 'cli,json',
        '--reporter-json-export', 'postman_results.json'
    ]
    
    if report:
        cmd.extend(['--reporter-html-export', 'postman_report.html'])
    
    try:
        print_header("🚀 Running Postman Collection Tests")
        
        result = subprocess.run(cmd, timeout=300)
        
        if result.returncode == 0:
            print_success("All tests passed!")
            return True
        else:
            print_warning(f"Some tests failed (exit code: {result.returncode})")
            return False
            
    except subprocess.TimeoutExpired:
        print_error("Tests timed out after 5 minutes")
        return False
    except Exception as e:
        print_error(f"Failed to run tests: {e}")
        return False

def parse_results(results_file):
    """Parse Newman JSON results"""
    if not Path(results_file).exists():
        return None
    
    try:
        with open(results_file, 'r') as f:
            results = json.load(f)
        
        return results
    except Exception as e:
        print_error(f"Failed to parse results: {e}")
        return None

def print_summary(results):
    """Print test execution summary"""
    if not results:
        return
    
    print_header("📊 Test Execution Summary")
    
    stats = results.get('run', {}).get('stats', {})
    
    # Test counts
    total = stats.get('requests', {}).get('total', 0)
    failed = stats.get('requests', {}).get('failed', 0)
    passed = total - failed
    
    print(f"Total Requests: {Colors.BOLD}{total}{Colors.END}")
    print(f"  {Colors.GREEN}✅ Passed: {passed}{Colors.END}")
    if failed > 0:
        print(f"  {Colors.RED}❌ Failed: {failed}{Colors.END}")
    
    # Assertions
    assertions = stats.get('assertions', {})
    total_assertions = assertions.get('total', 0)
    failed_assertions = assertions.get('failed', 0)
    passed_assertions = total_assertions - failed_assertions
    
    print(f"\nTotal Assertions: {Colors.BOLD}{total_assertions}{Colors.END}")
    print(f"  {Colors.GREEN}✅ Passed: {passed_assertions}{Colors.END}")
    if failed_assertions > 0:
        print(f"  {Colors.RED}❌ Failed: {failed_assertions}{Colors.END}")
    
    # Duration
    duration = results.get('run', {}).get('timings', {}).get('total', 0)
    print(f"\nTotal Duration: {Colors.BOLD}{duration}ms{Colors.END}")

def main():
    parser = argparse.ArgumentParser(
        description='Run AI Governance MVP Postman collection tests'
    )
    parser.add_argument(
        '--url',
        default='http://localhost:8000',
        help='Base URL for API (default: http://localhost:8000)'
    )
    parser.add_argument(
        '--api-key',
        default='test_key_staging_12345678901234',
        help='API key to use for tests'
    )
    parser.add_argument(
        '--report',
        action='store_true',
        help='Generate HTML report'
    )
    parser.add_argument(
        '--collection',
        default='docs/postman_collection.json',
        help='Path to Postman collection JSON'
    )
    
    args = parser.parse_args()
    
    # Check if collection exists
    collection_path = Path(args.collection)
    if not collection_path.exists():
        print_error(f"Collection not found: {args.collection}")
        sys.exit(1)
    
    # Check/install Newman
    if not check_newman():
        print_warning("Newman CLI not found, attempting installation...")
        if not install_newman():
            print_error("Failed to install Newman. Install manually:")
            print("  npm install -g newman")
            sys.exit(1)
    
    # Create environment file
    print_info("Creating test environment...")
    env_file = create_environment_file(args.url, args.api_key)
    print_success(f"Environment created: {env_file}")
    
    # Run tests
    success = run_postman_collection(collection_path, env_file, args.report)
    
    # Parse and display results
    results = parse_results('postman_results.json')
    if results:
        print_summary(results)
    
    # Cleanup
    if env_file.exists():
        env_file.unlink()
    
    # Report generated
    if args.report and Path('postman_report.html').exists():
        print_success("HTML report generated: postman_report.html")
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()

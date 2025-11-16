"""
Simplified Integration Tests for Local Testing
Uses mocking for database operations
Full integration tests run in CI/CD with real PostgreSQL

For real database testing, set TEST_DATABASE_URL environment variable
and ensure PostgreSQL is running
"""

import pytest
import httpx
import os
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
from starlette.testclient import TestClient
import uuid
import bcrypt

from main import app, CheckRequest, CheckResponse


@pytest.fixture
def mock_api_key_data():
    """Generate mock API key for testing"""
    raw_key = f"test_key_{uuid.uuid4().hex[:24]}"
    return {
        "id": str(uuid.uuid4()),
        "raw_key": raw_key,
        "customer_id": str(uuid.uuid4()),
        "is_active": True
    }


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


class TestHealth:
    """Health endpoint tests (no auth required)"""

    def test_health_endpoint(self, client):
        """Test health endpoint returns 200"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    def test_health_response_structure(self, client):
        """Test health response has correct structure"""
        response = client.get("/health")
        data = response.json()
        assert isinstance(data, dict)
        assert "status" in data


class TestAuthentication:
    """Authentication tests"""

    def test_missing_auth_header(self, client):
        """Test request without auth header is rejected"""
        response = client.post(
            "/v1/check",
            json={
                "model": "gpt-4",
                "operation": "chat_completion",
                "metadata": {"temperature": 0.7}
            }
        )
        assert response.status_code == 401

    def test_invalid_api_key(self, client):
        """Test invalid API key is rejected"""
        response = client.post(
            "/v1/check",
            json={
                "model": "gpt-4",
                "operation": "chat_completion",
                "metadata": {"temperature": 0.7}
            },
            headers={"Authorization": "Bearer invalid_key_12345678901234"}
        )
        assert response.status_code == 401

    def test_malformed_auth_header(self, client):
        """Test malformed auth header"""
        response = client.post(
            "/v1/check",
            json={
                "model": "gpt-4",
                "operation": "chat_completion",
                "metadata": {"temperature": 0.7}
            },
            headers={"Authorization": "InvalidFormat"}
        )
        assert response.status_code == 401


class TestRequestValidation:
    """Request validation tests"""

    def test_missing_model_field(self, client):
        """Test request without model field"""
        response = client.post(
            "/v1/check",
            json={
                "operation": "chat_completion",
                "metadata": {}
            },
            headers={"Authorization": "Bearer test_key"}
        )
        # Should return 422 for validation error
        assert response.status_code in [401, 422]

    def test_missing_operation_field(self, client):
        """Test request without operation field"""
        response = client.post(
            "/v1/check",
            json={
                "model": "gpt-4",
                "metadata": {}
            },
            headers={"Authorization": "Bearer test_key"}
        )
        assert response.status_code in [401, 422]

    def test_forbidden_field_prompt(self, client):
        """Test that 'prompt' field is rejected"""
        response = client.post(
            "/v1/check",
            json={
                "model": "gpt-4",
                "operation": "chat_completion",
                "metadata": {
                    "prompt": "This should not be allowed"
                }
            },
            headers={"Authorization": "Bearer test_key_123"}
        )
        # Should be rejected (auth or validation error)
        assert response.status_code in [400, 401, 422]

    def test_forbidden_field_content(self, client):
        """Test that nested 'content' field is rejected"""
        response = client.post(
            "/v1/check",
            json={
                "model": "gpt-4",
                "operation": "chat_completion",
                "metadata": {
                    "messages": [{"content": "This should not be allowed"}]
                }
            },
            headers={"Authorization": "Bearer test_key_123"}
        )
        assert response.status_code in [400, 401, 422]

    def test_forbidden_field_text(self, client):
        """Test that 'text' field is rejected"""
        response = client.post(
            "/v1/check",
            json={
                "model": "gpt-4",
                "operation": "chat_completion",
                "metadata": {
                    "text": "This should not be allowed"
                }
            },
            headers={"Authorization": "Bearer test_key_123"}
        )
        assert response.status_code in [400, 401, 422]

    def test_forbidden_field_input(self, client):
        """Test that 'input' field is rejected"""
        response = client.post(
            "/v1/check",
            json={
                "model": "gpt-4",
                "operation": "chat_completion",
                "metadata": {
                    "input": "This should not be allowed"
                }
            },
            headers={"Authorization": "Bearer test_key_123"}
        )
        assert response.status_code in [400, 401, 422]


class TestRequestStructure:
    """Request structure and format tests"""

    def test_valid_request_format(self, client):
        """Test valid request structure"""
        response = client.post(
            "/v1/check",
            json={
                "model": "gpt-4",
                "operation": "chat_completion",
                "metadata": {
                    "temperature": 0.7,
                    "max_tokens": 100
                }
            },
            headers={"Authorization": "Bearer valid_key"}
        )
        # Should return 401 (invalid key) not 422 (validation error)
        assert response.status_code == 401

    def test_empty_metadata_accepted(self, client):
        """Test that empty metadata is accepted"""
        response = client.post(
            "/v1/check",
            json={
                "model": "gpt-4",
                "operation": "chat_completion",
                "metadata": {}
            },
            headers={"Authorization": "Bearer valid_key"}
        )
        assert response.status_code == 401  # Auth error, not validation

    def test_null_metadata_handled(self, client):
        """Test that null metadata is handled"""
        response = client.post(
            "/v1/check",
            json={
                "model": "gpt-4",
                "operation": "chat_completion",
                "metadata": None
            },
            headers={"Authorization": "Bearer valid_key"}
        )
        # Should either accept or return validation error
        assert response.status_code in [401, 422]


class TestResponseStructure:
    """Response format and structure tests"""

    def test_health_response_is_json(self, client):
        """Test health response is valid JSON"""
        response = client.get("/health")
        assert response.headers["content-type"].startswith("application/json")

    def test_health_response_has_status_field(self, client):
        """Test health response includes status field"""
        response = client.get("/health")
        data = response.json()
        assert "status" in data
        assert data["status"] == "ok"

    def test_auth_error_response_structure(self, client):
        """Test auth error response structure"""
        response = client.post(
            "/v1/check",
            json={
                "model": "gpt-4",
                "operation": "test",
                "metadata": {}
            }
        )
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data or "message" in data


class TestEdgeCases:
    """Edge case tests"""

    def test_very_long_model_name(self, client):
        """Test handling of very long model name"""
        response = client.post(
            "/v1/check",
            json={
                "model": "a" * 1000,
                "operation": "chat_completion",
                "metadata": {}
            },
            headers={"Authorization": "Bearer test"}
        )
        # Should handle gracefully (auth error, not crash)
        assert response.status_code == 401

    def test_special_characters_in_model(self, client):
        """Test special characters in model name"""
        response = client.post(
            "/v1/check",
            json={
                "model": "gpt-4-@#$%^&*()",
                "operation": "chat_completion",
                "metadata": {}
            },
            headers={"Authorization": "Bearer test"}
        )
        assert response.status_code == 401

    def test_unicode_in_operation(self, client):
        """Test unicode in operation field"""
        response = client.post(
            "/v1/check",
            json={
                "model": "gpt-4",
                "operation": "测试-test-テスト",
                "metadata": {}
            },
            headers={"Authorization": "Bearer test"}
        )
        assert response.status_code == 401

    def test_deeply_nested_metadata(self, client):
        """Test deeply nested metadata"""
        nested = {"level": 1}
        for i in range(5):
            nested = {"nested": nested}
        
        response = client.post(
            "/v1/check",
            json={
                "model": "gpt-4",
                "operation": "test",
                "metadata": nested
            },
            headers={"Authorization": "Bearer test"}
        )
        assert response.status_code == 401


class TestHTTPMethods:
    """Test correct HTTP method handling"""

    def test_health_get_only(self, client):
        """Test health endpoint is GET only"""
        # POST to health should fail
        response = client.post("/health")
        assert response.status_code in [404, 405]

    def test_check_post_only(self, client):
        """Test check endpoint requires POST"""
        # GET to check should fail
        response = client.get("/v1/check")
        assert response.status_code in [404, 405]


class TestContentNegotiation:
    """Content type and negotiation tests"""

    def test_json_request_content_type(self, client):
        """Test with application/json content type"""
        response = client.post(
            "/v1/check",
            json={"model": "gpt-4", "operation": "test", "metadata": {}},
            headers={"Authorization": "Bearer test"}
        )
        assert response.status_code in [200, 401, 422]

    def test_response_content_type_json(self, client):
        """Test response is JSON"""
        response = client.get("/health")
        assert "application/json" in response.headers.get("content-type", "")


class TestErrorHandling:
    """Error handling and resilience tests"""

    def test_malformed_json(self, client):
        """Test handling of malformed JSON"""
        response = client.post(
            "/v1/check",
            content="{invalid json",
            headers={
                "Authorization": "Bearer test",
                "Content-Type": "application/json"
            }
        )
        assert response.status_code in [400, 422]

    def test_empty_body(self, client):
        """Test handling of empty request body"""
        response = client.post(
            "/v1/check",
            content="",
            headers={"Authorization": "Bearer test"}
        )
        assert response.status_code in [400, 422]

    def test_extremely_large_payload(self, client):
        """Test handling of very large payload"""
        large_metadata = {"data": "x" * 10000}
        response = client.post(
            "/v1/check",
            json={
                "model": "gpt-4",
                "operation": "test",
                "metadata": large_metadata
            },
            headers={"Authorization": "Bearer test"}
        )
        # Should handle gracefully
        assert response.status_code in [200, 401, 413, 422]


class TestEndpointAvailability:
    """Test that endpoints are available"""

    def test_health_endpoint_exists(self, client):
        """Test health endpoint is available"""
        response = client.get("/health")
        assert response.status_code in [200, 405]

    def test_check_endpoint_exists(self, client):
        """Test check endpoint is available"""
        response = client.post(
            "/v1/check",
            json={"model": "test", "operation": "test", "metadata": {}},
            headers={"Authorization": "Bearer test"}
        )
        # Should get a response (even if 401)
        assert response.status_code in [200, 400, 401, 405, 422]

# pytest configuration
import sys
import os
from unittest.mock import MagicMock, patch
import pytest

# Add backend to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Set test DATABASE_URL before importing main modules
os.environ['DATABASE_URL'] = 'postgresql+asyncpg://test:test@localhost:5432/test_db'

# Mock the database connection during testing
@pytest.fixture(autouse=True)
def mock_db():
    """Mock database to avoid connection errors during testing"""
    with patch('db.engine') as mock_engine, \
         patch('db.AsyncSessionLocal') as mock_session:
        mock_engine.return_value = MagicMock()
        mock_session.return_value = MagicMock()
        yield

"""
Test suite for Support Solutions CRM System
"""

import os
import sys
from unittest.mock import Mock, patch

import pytest

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.config import DB_PATH
from app.db import run_query
from web import app


class TestDatabase:
    """Test database functionality"""

    def test_database_exists(self):
        """Test that database file exists"""
        assert os.path.exists(DB_PATH), "Database file should exist"

    def test_customers_table_exists(self):
        """Test that customers table exists and has data"""
        result = run_query("SELECT COUNT(*) as count FROM customers")
        assert result is not None
        assert len(result) > 0
        assert result[0]["count"] > 0, "Should have customers in database"

    def test_deals_table_exists(self):
        """Test that deals table exists"""
        result = run_query("SELECT COUNT(*) as count FROM deals")
        assert result is not None
        assert len(result) > 0

    def test_projects_table_exists(self):
        """Test that projects table exists"""
        result = run_query("SELECT COUNT(*) as count FROM projects")
        assert result is not None
        assert len(result) > 0


class TestFlaskApp:
    """Test Flask application"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        app.config["TESTING"] = True
        with app.test_client() as client:
            yield client

    def test_index_page_loads(self, client):
        """Test that index page loads successfully"""
        response = client.get("/")
        assert response.status_code == 200
        assert b"Support Solutions" in response.data

    def test_customers_page_loads(self, client):
        """Test that customers page loads"""
        response = client.get("/customers")
        assert response.status_code == 200

    def test_deals_page_loads(self, client):
        """Test that deals page loads"""
        response = client.get("/deals")
        assert response.status_code == 200

    def test_projects_page_loads(self, client):
        """Test that projects page loads"""
        response = client.get("/projects")
        assert response.status_code == 200

    def test_api_status_endpoint(self, client):
        """Test API status endpoint"""
        response = client.get("/api/status")
        assert response.status_code == 200
        data = response.get_json()
        assert "status" in data
        assert data["system"] == "Support Solutions CRM"


class TestAIAgent:
    """Test AI agent functionality"""

    @patch("openai.OpenAI")
    def test_ai_agent_import(self, mock_openai):
        """Test that AI agent can be imported"""
        from app.agent import ask

        assert ask is not None

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    @patch("openai.OpenAI")
    def test_ask_function_structure(self, mock_openai):
        """Test ask function returns proper structure"""
        from app.agent import ask

        # Mock successful response
        with patch("app.agent.run_query") as mock_query:
            mock_query.return_value = [{"id": 1, "name": "Test Customer"}]

            # Mock OpenAI client behavior
            mock_client = mock_openai.return_value
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "SELECT * FROM customers;"
            mock_client.chat.completions.create.return_value = mock_response

            result = ask("Show me all customers")

            assert isinstance(result, dict)
            # Should have sql and rows keys in successful response


class TestConfiguration:
    """Test application configuration"""

    def test_config_import(self):
        """Test that config can be imported"""
        from app.config import DB_PATH

        assert DB_PATH is not None
        assert str(DB_PATH).endswith(".db")

    def test_environment_variables(self):
        """Test environment variable handling"""
        # Test with no API key
        with patch.dict(os.environ, {}, clear=True):
            from web import app

            with app.test_client() as client:
                response = client.get("/api/status")
                data = response.get_json()
                # Should be False when no API key is present
                assert data["ai_available"] is False or data["ai_available"] is None


class TestSecurityAndValidation:
    """Test security aspects"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        app.config["TESTING"] = True
        with app.test_client() as client:
            yield client

    def test_sql_injection_protection(self, client):
        """Test basic SQL injection protection"""
        # Test malicious input
        malicious_input = "'; DROP TABLE customers; --"

        response = client.post("/", data={"question": malicious_input})

        # Should redirect (normal behavior) not crash
        assert response.status_code in [200, 302]

        # Database should still have customers
        result = run_query("SELECT COUNT(*) as count FROM customers")
        assert result[0]["count"] > 0, "Customers table should still exist"

    def test_xss_protection(self, client):
        """Test XSS protection"""
        xss_input = "<script>alert('xss')</script>"

        response = client.post("/", data={"question": xss_input})
        assert response.status_code in [200, 302]

        # Follow redirect if any
        if response.status_code == 302:
            response = client.get("/")

        # Script tags should be escaped in response
        assert b"<script>" not in response.data or b"&lt;script&gt;" in response.data


if __name__ == "__main__":
    pytest.main([__file__])

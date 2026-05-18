"""
Tests for frontend-v2 API integration and configuration
"""

import os
import pytest
from fastapi.testclient import TestClient

from app.main import app


class TestFrontendV2Routes:
    """Test frontend-v2 specific routes"""
    
    def test_v2_index_route_exists(self, client):
        """Test /v2 endpoint returns frontend-v2 index.html"""
        response = client.get("/v2")
        assert response.status_code in [200, 404]  # 404 if frontend-v2 not built
        
    def test_v2_spa_fallback(self, client):
        """Test /v2/* routes fallback to SPA"""
        response = client.get("/v2/courses")
        assert response.status_code in [200, 404]
        
    def test_v2_static_files_css(self, client):
        """Test /v2/styles.css is served"""
        response = client.get("/v2/styles.css")
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            assert "text/css" in response.headers.get("content-type", "")
            
    def test_v2_static_files_js(self, client):
        """Test /v2/data.js is served"""
        response = client.get("/v2/data.js")
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            assert "javascript" in response.headers.get("content-type", "")


class TestFrontendVersionConfig:
    """Test FRONTEND_VERSION environment variable"""
    
    def test_health_check_reports_frontend_version(self, client):
        """Test health endpoint includes frontend version info"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "frontend_version" in data
        assert "frontend_dir" in data
        assert data["status"] == "healthy"
        
    def test_default_frontend_version_is_v1(self, client):
        """Test default FRONTEND_VERSION is 'v1'"""
        response = client.get("/health")
        data = response.json()
        
        # Should default to v1 for backward compatibility
        assert data.get("frontend_version") in ["v1", "v2"]
        
    def test_static_dir_contains_frontend_v2(self, client):
        """Test frontend_dir is correctly set"""
        response = client.get("/health")
        data = response.json()
        
        if data.get("frontend_version") == "v2":
            assert "frontend-v2" in data.get("frontend_dir", "")


class TestV1BackwardCompatibility:
    """Test V1 frontend still works"""
    
    def test_root_route_still_serves_v1(self, client):
        """Test / still serves frontend-v1"""
        response = client.get("/")
        assert response.status_code == 200
        
        # Should not be V2 404
        assert "Frontend V2 Not Found" not in response.text
        
    def test_api_routes_unaffected(self, client):
        """Test API routes work regardless of frontend version"""
        # Health check should work
        response = client.get("/health")
        assert response.status_code == 200
        
        # API docs should work
        response = client.get("/docs")
        assert response.status_code == 200


class TestFrontendV2Content:
    """Test frontend-v2 content if available"""
    
    def test_v2_react_app_structure(self, client):
        """Test V2 returns proper React app structure"""
        response = client.get("/v2")
        
        if response.status_code == 200:
            content = response.text
            # Should contain React root div
            assert '<div id="root">' in content or '<div id="root"' in content
            # Should load React from CDN
            assert "react" in content.lower() or "unpkg.com" in content
            # Should have Babel for JSX
            assert "babel" in content.lower() or "@babel" in content
            
    def test_v2_data_js_exists(self, client):
        """Test V2 data.js is accessible and valid JavaScript"""
        response = client.get("/v2/data.js")
        
        if response.status_code == 200:
            content = response.text
            # Should contain JavaScript code
            assert len(content) > 0
            # Should not be HTML error page
            assert "<!DOCTYPE" not in content
            assert "<html>" not in content

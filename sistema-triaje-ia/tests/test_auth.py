"""Tests de autenticación — /api/auth/*"""
import pytest
from fastapi import status


class TestAuth:
    """Pruebas del flujo de autenticación."""

    def test_login_success_admin(self, client):
        """Login con credenciales válidas de admin."""
        res = client.post("/api/auth/login", json={
            "username": "admin", "password": "admin123",
        })
        assert res.status_code == status.HTTP_200_OK
        data = res.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["rol"] == "Administrador"
        assert len(data["permissions"]) > 0

    def test_login_invalid_credentials(self, client):
        """Login con credenciales inválidas."""
        res = client.post("/api/auth/login", json={
            "username": "admin", "password": "wrongpassword",
        })
        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_empty_body(self, client):
        """Login sin body → 422."""
        res = client.post("/api/auth/login", json={})
        assert res.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_protected_endpoint_without_token(self, client):
        """Endpoint protegido sin token → 403."""
        res = client.get("/api/auth/permissions")
        assert res.status_code in (401, 403)

    def test_protected_endpoint_with_token(self, client, auth_headers):
        """Endpoint protegido con token válido."""
        res = client.get("/api/auth/permissions", headers=auth_headers)
        assert res.status_code == status.HTTP_200_OK
        data = res.json()
        assert "pages" in data["data"]

    def test_logout(self, client, auth_headers):
        """Logout con token válido."""
        res = client.post("/api/auth/logout", headers=auth_headers)
        assert res.status_code == status.HTTP_200_OK

    def test_health_check(self, client):
        """Health check público."""
        res = client.get("/health")
        assert res.status_code == status.HTTP_200_OK
        assert res.json()["status"] == "ok"

"""Tests de pacientes — /api/patients/*"""
from fastapi import status


class TestPatients:
    """Pruebas del CRUD de pacientes."""

    PATIENT_DATA = {
        "tipo_documento": "CC",
        "numero_documento": "1234567890",
        "nombre": "Test",
        "apellido": "Paciente",
        "fecha_nacimiento": "1990-01-01",
        "sexo": "M",
        "grupo_sanguineo": "O+",
        "eps": "Nueva EPS",
        "alergias": "Ninguna",
        "via_llegada": "Particular",
        "departamento": "",
        "municipio": "",
        "telefono": "3001234567",
        "correo": "test@example.com",
    }

    def test_create_patient(self, client, auth_headers):
        """Crear paciente exitosamente → 201."""
        res = client.post("/api/patients", json=self.PATIENT_DATA, headers=auth_headers)
        assert res.status_code == status.HTTP_201_CREATED
        data = res.json()
        assert data["success"] is True
        assert data["data"]["numero_documento"] == "1234567890"

    def test_create_duplicate_patient(self, client, auth_headers):
        """Crear paciente duplicado → 409."""
        client.post("/api/patients", json=self.PATIENT_DATA, headers=auth_headers)
        res = client.post("/api/patients", json=self.PATIENT_DATA, headers=auth_headers)
        assert res.status_code == status.HTTP_409_CONFLICT

    def test_get_patient_by_document(self, client, auth_headers):
        """Buscar paciente por documento."""
        client.post("/api/patients", json=self.PATIENT_DATA, headers=auth_headers)
        res = client.get("/api/patients/1234567890", headers=auth_headers)
        assert res.status_code == status.HTTP_200_OK
        assert res.json()["data"]["nombres"] == "Test"

    def test_get_patient_not_found(self, client, auth_headers):
        """Buscar paciente inexistente → 404."""
        res = client.get("/api/patients/9999999999", headers=auth_headers)
        assert res.status_code == status.HTTP_404_NOT_FOUND

    def test_search_patients(self, client, auth_headers):
        """Búsqueda textual de pacientes."""
        client.post("/api/patients", json=self.PATIENT_DATA, headers=auth_headers)
        res = client.get("/api/patients?q=Test", headers=auth_headers)
        assert res.status_code == status.HTTP_200_OK
        assert len(res.json()["data"]) >= 1

    def test_invalid_patient_data(self, client, auth_headers):
        """Paciente sin campos obligatorios → 422."""
        res = client.post("/api/patients", json={"nombre": "Incompleto"}, headers=auth_headers)
        assert res.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

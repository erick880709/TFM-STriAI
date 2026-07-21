"""Tests de triajes — /api/triages/*"""
from fastapi import status


class TestTriages:
    """Pruebas del flujo de triaje."""

    PATIENT = {
        "tipo_documento": "CC", "numero_documento": "5550001111",
        "nombre": "Triage", "apellido": "Test", "fecha_nacimiento": "1985-05-15",
        "sexo": "F", "grupo_sanguineo": "A+", "eps": "Nueva EPS",
        "via_llegada": "Particular",
    }

    VITAL_SIGNS = {
        "frecuencia_cardiaca": 80, "frecuencia_respiratoria": 16,
        "presion_sistolica": 120, "presion_diastolica": 80,
        "temperatura": 36.5, "saturacion_oxigeno": 98,
    }

    CLINICAL_EVAL = {
        "motivo_consulta": "Dolor torácico agudo",
        "categoria_motivo": "Dolor torácico",
        "glasgow_ocular": 4, "glasgow_verbal": 5, "glasgow_motora": 6,
        "escala_dolor": 5, "nivel_conciencia": "Alerta", "comorbilidades": [],
    }

    def test_full_triage_flow(self, client, auth_headers):
        """Flujo completo: crear paciente → ver triajes → validar endpoints."""
        # 1. Crear paciente
        p = client.post("/api/patients", json=self.PATIENT, headers=auth_headers)
        assert p.status_code == status.HTTP_201_CREATED
        id_paciente = p.json()["data"]["id_paciente"]

        # 2. Verificar que los endpoints de triaje responden
        # GET triajes del paciente (esperado vacío para paciente nuevo)
        tr = client.get(f"/api/patients/{id_paciente}/triages", headers=auth_headers)
        assert tr.status_code == status.HTTP_200_OK

        # GET triaje activo
        at = client.get(f"/api/patients/{id_paciente}/active-triage", headers=auth_headers)
        assert at.status_code == status.HTTP_200_OK

    def test_get_triage_not_found(self, client, auth_headers):
        """Triaje inexistente → 404."""
        res = client.get("/api/triages/noexiste-123", headers=auth_headers)
        assert res.status_code == status.HTTP_404_NOT_FOUND

    def test_invalid_vital_signs(self, client, auth_headers):
        """Signos vitales fuera de rango → 422."""
        res = client.put(
            "/api/triages/test-id/vital-signs",
            json={
                "frecuencia_cardiaca": 999, "frecuencia_respiratoria": 16,
                "presion_sistolica": 120, "presion_diastolica": 80,
                "temperatura": 36.5, "saturacion_oxigeno": 98,
            }, headers=auth_headers,
        )
        assert res.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

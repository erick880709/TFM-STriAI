"""
Servicios cacheados con @st.cache_resource.
Cada servicio se crea UNA sola vez por sesión de Streamlit,
eliminando la recreación en cada rerun y entre páginas.

IMPORTANTE: Los imports pesados (inference_service → torch, transformers, shap,
sentence-transformers) son LAZY — solo se importan cuando una página
que realmente necesita inferencia llama a get_cached_inference_service().
Esto evita que páginas ligeras (login, registro, dashboard) paguen el costo
de cargar ~2 GB de dependencias ML.

Uso en páginas UI:
    from app.services.cached import get_triage_service, get_patient_service
    triage_svc = get_triage_service(db_path)
    patient_svc = get_patient_service(db_path)
"""
import streamlit as st

# Servicios ligeros — import directo (no tienen dependencias pesadas)
from app.services.triage_service import TriageService
from app.services.patient_service import PatientService
from app.services.dashboard_service import DashboardService
from app.services.audit_service import AuditService
from app.services.model_management_service import ModelManagementService


@st.cache_resource
def get_triage_service(db_path: str) -> TriageService:
    """TriageService cacheado — se crea una sola vez."""
    return TriageService(db_path)


@st.cache_resource
def get_patient_service(db_path: str) -> PatientService:
    """PatientService cacheado — se crea una sola vez."""
    return PatientService(db_path)


@st.cache_resource
def get_dashboard_service(db_path: str) -> DashboardService:
    """DashboardService cacheado — se crea una sola vez."""
    return DashboardService(db_path)


@st.cache_resource
def get_audit_service(db_path: str) -> AuditService:
    """AuditService cacheado — se crea una sola vez."""
    return AuditService(db_path)


@st.cache_resource
def get_model_management_service(db_path: str) -> ModelManagementService:
    """ModelManagementService cacheado — se crea una sola vez."""
    return ModelManagementService(db_path)


@st.cache_resource
def get_cached_inference_service() -> object:
    """
    InferenceService cacheado — se crea una sola vez (incluye carga de modelo).
    ¡IMPORTANTE! El import de inference_service es LAZY (dentro de la función)
    para evitar que páginas sin IA carguen torch/transformers/shap (~2 GB).
    """
    from app.services.inference_service import get_inference_service
    return get_inference_service(None)

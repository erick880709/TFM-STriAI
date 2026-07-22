"""Verify API-only FastAPI setup."""
import requests

# Test 1: Health check
r = requests.get("http://localhost:8000/health")
print(f"Health: {r.status_code} - {r.json()}")

# Test 2: Root should redirect to Streamlit
r = requests.get("http://localhost:8000/", allow_redirects=False)
print(f"Root: {r.status_code} - Location: {r.headers.get('location', 'N/A')}")

# Test 3: Swagger
r = requests.get("http://localhost:8000/docs")
print(f"Swagger: {r.status_code}")

# Test 4: API login
r = requests.post("http://localhost:8000/api/auth/login", json={"username":"admin","password":"admin123"})
print(f"Login API: {r.status_code} - OK: {r.ok}")

# Test 5: Old React routes should 404
r = requests.get("http://localhost:8000/pacientes")
print(f"Old React route: {r.status_code}")

# Test 6: Inference API
token = requests.post("http://localhost:8000/api/auth/login", json={"username":"admin","password":"admin123"}).json()["access_token"]
body = {"frecuencia_cardiaca":110,"frecuencia_respiratoria":24,"presion_sistolica":130,"presion_diastolica":85,"temperatura":38.5,"saturacion_oxigeno":93,"edad":45,"sexo":"Femenino","motivo_texto":"Dolor toracico agudo"}
r = requests.post("http://localhost:8000/api/inference/predict", json=body, headers={"Authorization": f"Bearer {token}"})
print(f"Inference API: {r.status_code} - Nivel: {r.json().get('nivel_predicho')}")

print("\n=== All tests passed! ===")

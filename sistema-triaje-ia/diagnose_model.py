"""Diagnóstico de modelo Early Fusion — ¿por qué siempre predice Nivel III?"""
import joblib, json, numpy as np, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

MODEL_DIR = "../models/early_fusion_v20260720_224350"

# 1. Cargar artefactos
model = joblib.load(f"{MODEL_DIR}/model.joblib")
scaler = joblib.load(f"{MODEL_DIR}/scaler.joblib")
encoder = joblib.load(f"{MODEL_DIR}/encoder.joblib")

print("=== 1. SHAPE DEL MODELO ===")
print(f"Tipo: {type(model).__name__}")
if hasattr(model, 'n_features_in_'):
    print(f"n_features_in_: {model.n_features_in_}")
if hasattr(model, 'feature_importances_'):
    fi = model.feature_importances_
    print(f"Feature importances shape: {fi.shape}")
    print(f"Top 10 FI: {sorted(fi, reverse=True)[:10]}")
    nonzero = (fi > 0).sum()
    print(f"Features con FI > 0: {nonzero}/{len(fi)}")
if hasattr(model, 'n_classes_'):
    print(f"n_classes_: {model.n_classes_}")

print("\n=== 2. PREDICCIÓN CON 3 FEATURES (sin NLP) ===")
# Simular: edad=45, sexo=F, regimen=Contributivo
edad_arr = np.array([[45]])
edad_s = scaler.transform(edad_arr)[0, 0]
cat_arr = np.array([["F", "Contributivo"]])
cat_enc = encoder.transform(cat_arr)[0]
X3 = np.array([[edad_s, float(cat_enc[0]), float(cat_enc[1])]])
print(f"X3 shape: {X3.shape}, values: {X3[0]}")

try:
    p = model.predict_proba(X3)[0]
    print(f"Probas 3d: {[f'{x:.4f}' for x in p]}")
except Exception as e:
    print(f"ERROR con 3d: {e}")

print("\n=== 3. PREDICCIÓN CON 387 FEATURES (3 struct + 384 NLP zeros) ===")
X387 = np.hstack([X3, np.zeros((1, 384))])
print(f"X387 shape: {X387.shape}")
try:
    p387 = model.predict_proba(X387)[0]
    labels = ["I", "II", "III", "IV", "V"]
    for i, lb in enumerate(labels):
        print(f"  Nivel {lb}: {p387[i]:.4f}")
    print(f"  Argmax: Nivel {labels[int(np.argmax(p387))]}")
except Exception as e:
    print(f"ERROR con 387d: {e}")

print("\n=== 4. PREDICCIÓN CON DATOS CLÍNICOS VARIADOS (387d, NLP=zeros) ===")
tests = [
    ("Crítico: edad 85, sexo M", 85, "M", "Subsidiado"),
    ("Crítico: edad 90, sexo F", 90, "F", "Contributivo"),
    ("Leve: edad 18, sexo M", 18, "M", "Contributivo"),
    ("Leve: edad 22, sexo F", 22, "F", "Subsidiado"),
    ("Moderado: edad 55, sexo M", 55, "M", "Contributivo"),
    ("Niño: edad 3, sexo M", 3, "M", "Subsidiado"),
]
for label, edad, sexo, regimen in tests:
    e_s = scaler.transform(np.array([[edad]]))[0, 0]
    c_enc = encoder.transform(np.array([[sexo, regimen]]))[0]
    x3 = np.array([[e_s, float(c_enc[0]), float(c_enc[1])]])
    x387 = np.hstack([x3, np.zeros((1, 384))])
    proba = model.predict_proba(x387)[0]
    pred = labels[int(np.argmax(proba))]
    print(f"  {label}: Nivel={pred} | probas={[f'{p:.3f}' for p in proba]}")

print("\n=== 5. PREDICCIÓN CON NLP RANDOM (simulando embeddings reales) ===")
rng = np.random.RandomState(42)
for label, edad, sexo, regimen in tests[:3]:
    e_s = scaler.transform(np.array([[edad]]))[0, 0]
    c_enc = encoder.transform(np.array([[sexo, regimen]]))[0]
    x3 = np.array([[e_s, float(c_enc[0]), float(c_enc[1])]])
    nlp_random = rng.randn(1, 384) * 0.1
    x387 = np.hstack([x3, nlp_random])
    proba = model.predict_proba(x387)[0]
    pred = labels[int(np.argmax(proba))]
    print(f"  {label}: Nivel={pred} | probas={[f'{p:.3f}' for p in proba]}")

print("\n=== 6. MÉTRICAS DEL ENTRENAMIENTO ===")
with open(f"{MODEL_DIR}/metadata.json") as f:
    meta = json.load(f)
for k, v in meta["metrics"].items():
    print(f"  {k}: {v:.4f}")
print(f"  thresholds: {meta['thresholds']}")
print(f"  n_features (metadata): {meta['n_features']}")

print("\n=== 7. DISTRIBUCIÓN DE PROBAS PROMEDIO (100 muestras aleatorias) ===")
all_probas = []
for _ in range(100):
    edad_r = rng.randint(1, 100)
    sexo_r = rng.choice(["M", "F"])
    regimen_r = rng.choice(["Contributivo", "Subsidiado", "Especial", "No afiliado"])
    e_s = scaler.transform(np.array([[edad_r]]))[0, 0]
    try:
        c_enc = encoder.transform(np.array([[sexo_r, regimen_r]]))[0]
    except:
        c_enc = np.zeros(2)
    x3 = np.array([[e_s, float(c_enc[0]), float(c_enc[1])]])
    x387 = np.hstack([x3, np.zeros((1, 384))])
    proba = model.predict_proba(x387)[0]
    all_probas.append(proba)

avg = np.mean(all_probas, axis=0)
print(f"Probas promedio: {[f'{p:.4f}' for p in avg]}")
print(f"Nivel más probable en promedio: {labels[int(np.argmax(avg))]}")

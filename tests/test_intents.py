from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200

def test_intent_general_minimal():
    r = client.post("/intent/classify", json={"text":"", "language":"ru"})
    assert r.status_code == 200
    data = r.json()
    assert "intent" in data and "confidence" in data

# Интеграционный тест ниже потребует реальный API KEY в окружении:
# можно временно пометить как e2e или пропускать, если нет ключа.
def test_llm_or_fallback():
    r = client.post("/intent/classify", json={"text":"Хочу открыть вклад и карту"})
    assert r.status_code == 200
    data = r.json()
    assert data["intent"] in {"product_recommendation","general_knowledge","analytics","goal_planning","wellness"}

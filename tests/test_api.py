import pytest

# Guard against missing dependencies
try:
    from fastapi.testclient import TestClient
    from api import main
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False


class DummyModel:
    def predict(self, X):
        # return X doubled
        return [[x[0] * 2] for x in X]


@pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI unavailable")
def test_predict_success(monkeypatch):
    # replace global model with dummy
    monkeypatch.setattr(main, "model", DummyModel())
    
    client = TestClient(main.app)
    response = client.post("/predict", json={"revenue": 10})
    assert response.status_code == 200
    assert response.json()["prediction"] == 20


@pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI unavailable")
def test_predict_no_model(monkeypatch):
    monkeypatch.setattr(main, "model", None)
    
    client = TestClient(main.app)
    response = client.post("/predict", json={"revenue": 10})
    assert response.status_code == 503

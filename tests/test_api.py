import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from fastapi.testclient import TestClient
    from api import main
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False


class DummyModel:
    def predict(self, X):
        return [[x[0] * 2] for x in X]


@pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI unavailable")
def test_predict_success():
    # Override the dependency
    def override_model():
        return DummyModel()

    main.app.dependency_overrides[main.get_model] = override_model

    client = TestClient(main.app, lifespan=None)
    response = client.post("/predict", json={"revenue": 10})

    assert response.status_code == 200
    assert response.json()["prediction"] == 20

    # Clean up overrides
    main.app.dependency_overrides.clear()


@pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI unavailable")
def test_predict_no_model():
    # Override the dependency to raise 503
    def override_model():
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail="Model not available")

    main.app.dependency_overrides[main.get_model] = override_model

    client = TestClient(main.app, lifespan=None)
    response = client.post("/predict", json={"revenue": 10})

    assert response.status_code == 503
    assert response.json()["detail"] == "Model not available"

    main.app.dependency_overrides.clear()


@pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI unavailable")
def test_status_endpoint():
    client = TestClient(main.app, lifespan=None)
    response = client.get("/status")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

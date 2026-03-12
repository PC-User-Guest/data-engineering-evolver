import os
import sys
import pytest

# Add parent directory to path for module imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from fastapi.testclient import TestClient
    from api import main
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False


class DummyModel:
    """Simple dummy model for testing /predict."""
    def predict(self, X):
        return [[x[0] * 2] for x in X]


@pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI unavailable")
def test_predict_success():
    """Test /predict endpoint with a valid model."""
    # Override the dependency to use DummyModel
    main.app.dependency_overrides[main.get_model] = lambda: DummyModel()

    client = TestClient(main.app)
    response = client.post("/predict", json={"revenue": 10})

    assert response.status_code == 200
    assert response.json()["prediction"] == 20

    # Clear overrides to avoid side effects
    main.app.dependency_overrides.clear()


@pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI unavailable")
def test_predict_no_model():
    """Test /predict endpoint when model is not available."""
    # Override the dependency to simulate no model
    def raise_no_model():
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail="Model not available")

    main.app.dependency_overrides[main.get_model] = raise_no_model

    client = TestClient(main.app)
    response = client.post("/predict", json={"revenue": 10})

    assert response.status_code == 503
    assert response.json()["detail"] == "Model not available"

    main.app.dependency_overrides.clear()


@pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI unavailable")
def test_status_endpoint():
    """Test /status endpoint."""
    client = TestClient(main.app)
    response = client.get("/status")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

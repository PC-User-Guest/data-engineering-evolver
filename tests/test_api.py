import os
import sys
import pytest

# Add parent directory to path for module imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
def test_predict_success():
    # Create a fresh app instance with the test model
    original_model = main.model
    try:
        main.model = DummyModel()
        client = TestClient(main.app)
        response = client.post("/predict", json={"revenue": 10})
        assert response.status_code == 200
        assert response.json()["prediction"] == 20
    finally:
        main.model = original_model


@pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI unavailable")
def test_predict_no_model():
    original_model = main.model
    try:
        main.model = None
        client = TestClient(main.app)
        response = client.post("/predict", json={"revenue": 10})
        assert response.status_code == 503
    finally:
        main.model = original_model


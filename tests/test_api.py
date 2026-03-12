import pytest
from fastapi.testclient import TestClient

from api import main


class DummyModel:
    def predict(self, X):
        # return X doubled
        return [[x[0] * 2] for x in X]


@pytest.fixture(autouse=True)
def setup_model(monkeypatch):
    # replace global model with dummy
    monkeypatch.setattr(main, "model", DummyModel())


client = TestClient(main.app)


def test_predict_success():
    response = client.post("/predict", json={"revenue": 10})
    assert response.status_code == 200
    assert response.json()["prediction"] == 20


def test_predict_no_model(monkeypatch):
    monkeypatch.setattr(main, "model", None)
    response = client.post("/predict", json={"revenue": 10})
    assert response.status_code == 503

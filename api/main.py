import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mlflow

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Global model variable (initially None, loaded at startup)
model = None


async def load_model_on_startup():
    """Load MLflow model at startup."""
    global model
    model_path = os.environ.get("MLFLOW_MODEL_PATH", "mlruns/0/abcdef123456/model")
    try:
        model = mlflow.sklearn.load_model(model_path)
        logger.info(f"Loaded model from {model_path}")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        model = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown."""
    # Startup
    await load_model_on_startup()
    yield
    # Shutdown
    logger.info("Shutting down")


app = FastAPI(title="Sales Prediction API", lifespan=lifespan)


class PredictRequest(BaseModel):
    revenue: float


@app.post("/predict")
def predict(req: PredictRequest):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not available")
    try:
        pred = model.predict([[req.revenue]])
        return {"prediction": float(pred[0][0])}
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail="Prediction failed")


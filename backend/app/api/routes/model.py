"""Model status endpoint."""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from app.ml.model import model_predictor

router = APIRouter()


class ModelLoadRequest(BaseModel):
    model_path: str


@router.get("/model/status")
async def model_status():
    """
    Get the status of the ML model.

    Returns whether the model is loaded and ready for predictions.
    """
    is_loaded = model_predictor.is_loaded()

    return {
        "model_loaded": is_loaded,
        "message": "Model is ready" if is_loaded else "Model is not loaded"
    }


@router.post("/model/load")
async def load_model_endpoint(request: ModelLoadRequest):
    """
    Load the ML model from a specified path.

    This endpoint allows loading a trained model for use in predictions.
    In a production environment, this would likely be restricted to admin users.
    """
    try:
        model_predictor.load_model(request.model_path)
        return {
            "message": f"Model loaded successfully from {request.model_path}",
            "model_loaded": True
        }
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model file not found: {request.model_path}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load model: {str(e)}"
        )
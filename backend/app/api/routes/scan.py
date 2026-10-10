"""Scan endpoint for URL phishing detection."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from app.core.security import get_current_user
from app.ml.model import predict_url, ModelPredictor
from slowapi import Limiter
from slowapi.util import get_remote_address
import os

router = APIRouter()

# Rate limiter for scan endpoint
limiter = Limiter(key_func=get_remote_address)
# Default rate limit from environment or 60 requests/minute
RATE_LIMIT = os.getenv("RATE_LIMIT_REQUESTS_PER_MINUTE", "60")

class ScanRequest(BaseModel):
    url: str


class ScanResponse(BaseModel):
    url: str
    is_phishing: bool
    probability: float | None = None
    features: dict


@router.post("/scan", response_model=ScanResponse)
@limiter.limit(f"{RATE_LIMIT}/minute")
async def scan_url(
    request: ScanRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Scan a URL for phishing attempts.

    Requires authentication. Returns whether the URL is predicted to be phishing,
    along with the probability and extracted features.
    """
    # Check if model is loaded
    if not ModelPredictor.model_predictor.is_loaded():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ML model not loaded. Please train and provide a model.",
        )

    try:
        result = predict_url(request.url)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

    return ScanResponse(
        url=request.url,
        is_phishing=result["is_phishing"],
        probability=result["probability"],
        features=result["features"],
    )
from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.model import WinrateModelService

router = APIRouter(
    prefix="/api/v1",
    tags=["predictions"],
)

model_service = WinrateModelService()


class TeamSelection(BaseModel):
    """Payload de entrada: IDs de campeones de ambos equipos."""

    team_champions: List[int] = Field(..., min_items=1, max_items=5)
    enemy_champions: List[int] = Field(..., min_items=1, max_items=5)


class PredictionResponse(BaseModel):
    """Respuesta: probabilidad de victoria del equipo (0-1)."""

    winrate: float


@router.post("/predict", response_model=PredictionResponse)
def predict(selection: TeamSelection) -> PredictionResponse:
    try:
        winrate = model_service.predict_winrate(
            team_champions=selection.team_champions,
            enemy_champions=selection.enemy_champions,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    return PredictionResponse(winrate=winrate)

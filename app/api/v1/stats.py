from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import pandas as pd
from pathlib import Path

router = APIRouter(
    prefix="/api/v1/stats",
    tags=["stats"],
)


class ChampionStats(BaseModel):
    champion_id: int
    games: int
    wins: int
    winrate: float


@router.get("/champions", response_model=List[ChampionStats])
def get_champion_stats() -> List[ChampionStats]:
    """Devuelve estadísticas de partidas por campeón."""
    stats_path = Path("data/processed/stats_per_champion.csv")
    if not stats_path.exists():
        raise HTTPException(
            status_code=500,
            detail="No se encontraron estadísticas procesadas. "
            "Ejecuta primero: poetry run python -m scripts.process_matches",
        )

    df = pd.read_csv(stats_path)

    # limitamos por si el dataset es grande
    df_sorted = df.sort_values("games", ascending=False).head(30)

    result = [
        ChampionStats(
            champion_id=int(row["champion_id"]),
            games=int(row["games"]),
            wins=int(row["wins"]),
            winrate=float(row["winrate"]),
        )
        for _, row in df_sorted.iterrows()
    ]

    return result

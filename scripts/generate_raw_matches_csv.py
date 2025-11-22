"""Genera un CSV crudo de partidas simuladas usando IDs REALES de campeones.

- Obtiene la lista de campeones desde Riot Data Dragon.
- Usa sus IDs numéricos oficiales (champ.key) para armar los equipos.
- Resultado: data/raw/matches_raw.csv
"""

from pathlib import Path

import numpy as np
import pandas as pd
import requests


def fetch_champion_ids() -> list[int]:
    """Devuelve una lista de IDs numéricos de campeones desde Data Dragon."""
    # Última versión disponible
    versions_resp = requests.get(
        "https://ddragon.leagueoflegends.com/api/versions.json",
        timeout=10,
    )
    versions_resp.raise_for_status()
    versions = versions_resp.json()
    latest = versions[0]

    champs_resp = requests.get(
        f"https://ddragon.leagueoflegends.com/cdn/{latest}/data/en_US/champion.json",
        timeout=10,
    )
    champs_resp.raise_for_status()
    data = champs_resp.json()

    champ_ids: list[int] = [
        int(champ["key"]) for champ in data["data"].values()
    ]

    return champ_ids


def main() -> None:
    raw_dir = Path("data/raw")
    raw_dir.mkdir(parents=True, exist_ok=True)

    output_path = raw_dir / "matches_raw.csv"

    rng = np.random.default_rng(seed=42)

    # 🔹 Usamos IDs reales de campeones
    champ_ids = fetch_champion_ids()
    n_champions = len(champ_ids)
    print(f"Campeones obtenidos desde Data Dragon: {n_champions}")

    n_matches = 5000

    def random_team() -> np.ndarray:
        # Elegimos 5 campeones distintos por equipo
        return rng.choice(champ_ids, size=5, replace=False)

    team_matrix = np.vstack([random_team() for _ in range(n_matches)])
    enemy_matrix = np.vstack([random_team() for _ in range(n_matches)])

    data = {
        "match_id": np.arange(1, n_matches + 1),
        "team_champ1": team_matrix[:, 0],
        "team_champ2": team_matrix[:, 1],
        "team_champ3": team_matrix[:, 2],
        "team_champ4": team_matrix[:, 3],
        "team_champ5": team_matrix[:, 4],
        "enemy_champ1": enemy_matrix[:, 0],
        "enemy_champ2": enemy_matrix[:, 1],
        "enemy_champ3": enemy_matrix[:, 2],
        "enemy_champ4": enemy_matrix[:, 3],
        "enemy_champ5": enemy_matrix[:, 4],
        # 1 = tu equipo gana, 0 = pierde
        "team_win": rng.integers(0, 2, size=n_matches),
    }

    df = pd.DataFrame(data)
    df.to_csv(output_path, index=False)
    print(f"CSV crudo generado en: {output_path}")


if __name__ == "__main__":
    main()

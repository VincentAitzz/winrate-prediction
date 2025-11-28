"""Genera un CSV crudo de partidas simuladas usando IDs REALES de campeones y RUNAS.

- Obtiene la lista de campeones desde Riot Data Dragon.
- Obtiene la lista de Runas Clave (Keystones) desde Riot Data Dragon.
- Usa IDs numéricos oficiales para armar los equipos y sus elecciones.
- Resultado: data/raw/matches_raw.csv
"""

from pathlib import Path

import numpy as np
import pandas as pd
import requests


def get_latest_version() -> str:
    """Obtiene la última versión del juego desde Data Dragon."""
    versions_resp = requests.get(
        "https://ddragon.leagueoflegends.com/api/versions.json",
        timeout=10,
    )
    versions_resp.raise_for_status()
    return versions_resp.json()[0]


def fetch_champion_ids(version: str) -> list[int]:
    """Devuelve una lista de IDs numéricos de campeones."""
    print(f"Descargando campeones versión {version}...")
    champs_resp = requests.get(
        f"https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/champion.json",
        timeout=10,
    )
    champs_resp.raise_for_status()
    data = champs_resp.json()

    return [int(champ["key"]) for champ in data["data"].values()]


def fetch_keystone_ids(version: str) -> list[int]:

    print(f"Descargando runas versión {version}...")
    runes_resp = requests.get(
        f"https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/runesReforged.json",
        timeout=10,
    )
    runes_resp.raise_for_status()
    data = runes_resp.json()

    keystones = []
    # Data es una lista de árboles (Precision, Domination, etc.)
    for tree in data:
        # El slot 0 contiene las runas más importantes
        if tree["slots"]:
            for rune in tree["slots"][0]["runes"]:
                keystones.append(rune["id"])

    return keystones


def main() -> None:
    raw_dir = Path("data/raw")
    raw_dir.mkdir(parents=True, exist_ok=True)

    output_path = raw_dir / "matches_raw.csv"

    rng = np.random.default_rng(seed=42)

    # 1. Obtener versión y datos reales
    latest_version = get_latest_version()
    champ_ids = fetch_champion_ids(latest_version)
    rune_ids = fetch_keystone_ids(latest_version)

    n_champions = len(champ_ids)
    n_runes = len(rune_ids)
    print(f"Datos obtenidos: {n_champions} Campeones y {n_runes} Keystones.")

    n_matches = 100000  # De 5k a 100k (lo siento, 5k es muy poquito)

    # 2. Generar Matrices de Campeones (Sin repetir en el mismo equipo)
    def random_team_champs() -> np.ndarray:
        return rng.choice(champ_ids, size=5, replace=False)

    team_champ_matrix = np.vstack([random_team_champs() for i in range(n_matches)])
    enemy_champ_matrix = np.vstack([random_team_champs() for i in range(n_matches)])

    # 3. Generar Matrices de Runas (Se pueden repetir, ej: 2 personas con Conquistador)
    def random_team_runes() -> np.ndarray:
        return rng.choice(rune_ids, size=5, replace=True)

    team_rune_matrix = np.vstack([random_team_runes() for i in range(n_matches)])
    enemy_rune_matrix = np.vstack([random_team_runes() for i in range(n_matches)])

    # 4. Construir el DataFrame
    data = {
        "match_id": np.arange(1, n_matches + 1),
        # Team Stats
        "team_champ1": team_champ_matrix[:, 0],
        "team_rune1": team_rune_matrix[:, 0],
        "team_champ2": team_champ_matrix[:, 1],
        "team_rune2": team_rune_matrix[:, 1],
        "team_champ3": team_champ_matrix[:, 2],
        "team_rune3": team_rune_matrix[:, 2],
        "team_champ4": team_champ_matrix[:, 3],
        "team_rune4": team_rune_matrix[:, 3],
        "team_champ5": team_champ_matrix[:, 4],
        "team_rune5": team_rune_matrix[:, 4],
        # Enemy Stats
        "enemy_champ1": enemy_champ_matrix[:, 0],
        "enemy_rune1": enemy_rune_matrix[:, 0],
        "enemy_champ2": enemy_champ_matrix[:, 1],
        "enemy_rune2": enemy_rune_matrix[:, 1],
        "enemy_champ3": enemy_champ_matrix[:, 2],
        "enemy_rune3": enemy_rune_matrix[:, 2],
        "enemy_champ4": enemy_champ_matrix[:, 3],
        "enemy_rune4": enemy_rune_matrix[:, 3],
        "enemy_champ5": enemy_champ_matrix[:, 4],
        "enemy_rune5": enemy_rune_matrix[:, 4],
        # Target (Win/Loss)
        "team_win": rng.integers(0, 2, size=n_matches),
    }

    df = pd.DataFrame(data)
    df.to_csv(output_path, index=False)
    print(f"CSV generado exitosamente en: {output_path}")
    print("Columnas generadas:", list(df.columns[:4]), "...")


if __name__ == "__main__":
    main()

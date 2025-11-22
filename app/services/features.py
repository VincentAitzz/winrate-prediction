from typing import List

import numpy as np


def selection_to_feature_vector(
    team_champions: List[int],
    enemy_champions: List[int],
) -> np.ndarray:
    """Convierte la selección de campeones en un vector numérico fijo.

    Por ahora:
    - Se consideran hasta 5 campeones por equipo.
    - Se rellenan con 0 si son menos.
    - Devuelve un vector de longitud 10: [team(5), enemy(5)]

    Más adelante aquí puedes meter toda la lógica de encoding
    (one-hot, embeddings, sinergias, etc.).
    """
    max_per_team = 5

    team = (team_champions + [0] * max_per_team)[:max_per_team]
    enemy = (enemy_champions + [0] * max_per_team)[:max_per_team]

    features = np.array(team + enemy, dtype=float)
    return features

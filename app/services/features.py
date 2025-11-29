from typing import List
import numpy as np

# El ID más alto actual en LoL ronda el 950. 
# Ponemos 1000 para tener margen de seguridad.
MAX_CHAMP_ID = 1000 

def selection_to_feature_vector(
    team_champions: List[int],
    enemy_champions: List[int],
) -> np.ndarray:
    """
    Convierte la selección en un vector posicional (One-Hot).
    
    Retorna un array de tamaño 1000 donde:
     +1 = Campeón está en Tu Equipo
     -1 = Campeón está en el Equipo Enemigo
      0 = Campeón no está en la partida
    """
    # 1. Creamos un tablero vacío (todo ceros)
    features = np.zeros(MAX_CHAMP_ID, dtype=np.int8)

    # 2. Marcamos con un 1 los campeones aliados
    for champ_id in team_champions:
        if 0 < champ_id < MAX_CHAMP_ID:
            features[champ_id] = 1

    # 3. Marcamos con un -1 los campeones enemigos
    for champ_id in enemy_champions:
        if 0 < champ_id < MAX_CHAMP_ID:
            features[champ_id] = -1

    return features
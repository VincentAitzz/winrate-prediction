# Pipeline de Datos

## 1. Ingesta de datos (crudos)

- Script: `scripts/generate_raw_matches_csv.py`
- Salida: `data/raw/matches_raw.csv`
- Contenido:
  - `match_id`
  - `team_champ1..5`
  - `enemy_champ1..5`
  - `team_win` (1 = el equipo aliado ganó, 0 = perdió)

En una versión futura, este script se reemplaza por un proceso que obtenga
partidas reales desde la API de RiotGames.

---

## 2. Procesamiento

- Script: `scripts/process_matches.py`
- Entrada: `data/raw/matches_raw.csv`
- Salida: `data/processed/stats_per_champion.csv`

Pasos principales:

1. Se “desapilan” los 5 campeones aliados y los 5 enemigos para obtener
   una tabla con una fila por campeón y partida.
2. Se calcula una columna `champion_win`:
   - Para campeones aliados: igual a `team_win`.
   - Para campeones enemigos: `1 - team_win`.
3. Se agrupa por `champion_id` y se calculan:
   - `games`: número de partidas.
   - `wins`: partidas ganadas por ese campeón.
   - `winrate = wins / games`.

---

## 3. Features para el modelo

Archivo: `app/services/features.py`

- La función `selection_to_feature_vector(team_champions, enemy_champions)`:

  - Rellena con ceros si hay menos de 5 campeones.
  - Asegura que la dimensión siempre sea 10: `[ally1..ally5, enemy1..enemy5]`.

Esta misma función se usa:

- En `scripts/train_model.py` (entrenamiento).
- En `WinrateModelService.predict_winrate` (producción).

---

## 4. Entrenamiento de modelo

- Script: `scripts/train_model.py`
- Entrada:
  - `data/raw/matches_raw.csv`
- Salida:
  - `models/winrate_model.pkl`

El script:

1. Lee el CSV crudo.
2. Genera features usando `selection_to_feature_vector`.
3. Aplica `train_test_split` (80% train, 20% test, estratificado).
4. Entrena `LogisticRegression`.
5. Calcula métricas y las imprime en consola.
6. Guarda el modelo entrenado en la ruta indicada por `MODEL_PATH`.
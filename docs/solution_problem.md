# Problema y Solución Técnica

## 1. El problema

En League of Legends, cada partida se juega con dos equipos de 5 campeones.
La composición de estos equipos (sinergias internas, counters, tipos de daño, etc.)
tiene un impacto directo en la probabilidad de victoria.

Los jugadores típicamente:

- Eligen campeones por costumbre o preferencia personal.
- No consideran datos históricos de winrate de combinaciones de campeones.
- No disponen de una herramienta sencilla para analizar composiciones.

**Problema técnico:** Dado un conjunto de 5 campeones aliados y 5 campeones enemigos,
estimar la probabilidad de que el equipo aliado gane la partida (`team_win`).

---

## 2. La solución propuesta

### 2.1 Arquitectura general

La solución se compone de:

1. **Pipeline de datos**
   - Generación o descarga de partidas y almacenamiento en `data/raw/matches_raw.csv`.
   - Procesamiento de datos y obtención de estadísticas en `data/processed/`.
   - Entrenamiento de un modelo que se guarda en `models/winrate_model.pkl`.

2. **Modelo de Machine Learning**
   - Modelo base: `LogisticRegression` de `scikit-learn`.
   - Entrada: vector de 10 características (IDs de campeones aliados y enemigos).
   - Salida: probabilidad de victoria (`P(team_win=1)`).

3. **API REST**
   - Desarrollada con FastAPI.
   - Endpoint `/api/v1/predict` que recibe dos listas: `team_champions` y `enemy_champions`.
   - Endpoint `/api/v1/stats/champions` que expone estadísticas agregadas por campeón.

4. **Dashboard**
   - Vista `/dashboard` que consume el endpoint de estadísticas.
   - Uso de Chart.js para mostrar winrate por campeón.

---

## 3. Decisiones técnicas

### 3.1 Pipeline de datos

- **Generación cruda:**  
  `scripts/generate_raw_matches_csv.py` genera un CSV simulado con columnas:

  - `team_champ1..5`, `enemy_champ1..5`, `team_win`.

- **Procesamiento:**  
  `scripts/process_matches.py` transforma el CSV crudo en:

  - `data/processed/stats_per_champion.csv`: partidas jugadas y winrate por campeón.

- **Features:**  
  La función `selection_to_feature_vector` en `app/services/features.py` convierte
  la selección de campeones en un vector numérico reutilizable tanto en
  *entrenamiento* como en *producción*.

### 3.2 Modelo de ML

- Se elige `LogisticRegression` porque:
  - Es un modelo lineal adecuado para clasificación binaria.
  - Sus probabilidades de salida son fáciles de interpretar.
  - Es rápido de entrenar y sirve como línea base.

- Se usan métricas de:
  - Accuracy.
  - Precision, recall y F1 (report de clasificación).
  - Matriz de confusión.

### 3.3 Integración modelo – API – dashboard

- El servicio `WinrateModelService` carga el modelo desde disco y
  expone un método `predict_winrate`.
- El endpoint `/predict` delega en ese servicio la creación de features y la predicción.
- El dashboard utiliza el endpoint `/stats/champions` para obtener un JSON con:
  - `champion_id`, `games`, `wins`, `winrate`.
- Chart.js se utiliza para convertir esas estadísticas en gráficos interactivos.

---

## 4. Impacto técnico

Esta solución demuestra:

- Diseño de un pipeline reproducible de datos.
- Separación clara entre:
  - Capa de datos (scripts + `data/`).
  - Capa de modelo (`models/` + `app/services/model.py`).
  - Capa de exposición (`app/api/*` + frontend).
- Uso práctico de FastAPI para desplegar un modelo de ML.
- Capacidad de extender el sistema para usar datos reales de RiotGames.
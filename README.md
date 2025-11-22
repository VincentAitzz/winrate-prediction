# LoL Winrate Predictor 🎮📈

Aplicación completa de **Machine Learning** que predice la probabilidad de victoria
de un equipo en **League of Legends** a partir de la selección de campeones de ambos equipos.

Incluye:

- Modelo de ML entrenado a partir de partidas simuladas (y preparado para datos reales de Riot).
- API REST en **FastAPI** con endpoint `/api/v1/predict`.
- Frontend simple para seleccionar campeones por nombre y ver el winrate.
- Dashboard (ruta `/dashboard`) para visualizar estadísticas de campeones.
- Scripts de generación de datos, procesamiento y entrenamiento.
- Tests unitarios básicos.
- Documentación técnica en `/docs`.

---

## Problema y solución (resumen técnico)

### Problema

En League of Legends, la composición de campeones de cada equipo influye fuertemente
en la probabilidad de victoria. Sin embargo, muchos jugadores toman decisiones
intuitivas, sin apoyo en datos históricos ni en análisis cuantitativo.

**Objetivo:** predecir el `winrate` esperado de un equipo dado un conjunto de
campeones aliados y enemigos.

### Solución propuesta

1. **Pipeline de datos**
   - Generación / descarga de partidas y guardado en `data/raw/matches_raw.csv`.
   - Procesamiento y extracción de features reproducible en scripts de Python.
   - Entrenamiento de un modelo con `scikit-learn` y guardado en `models/winrate_model.pkl`.

2. **Modelo de ML**
   - Se utiliza `LogisticRegression` como modelo base por ser simple,
     interpretable y rápido de entrenar.
   - Las features actuales son los IDs de campeones aliados y enemigos (10 valores enteros).
   - El modelo sigue un esquema clásico de `train_test_split` con métricas de clasificación.

3. **API + Frontend**
   - API FastAPI con endpoint `/api/v1/predict` que recibe listas de IDs de campeones.
   - Frontend en HTML/CSS/JS que permite seleccionar campeones por nombre y mostrar
     la probabilidad de victoria.
   - Dashboard `/dashboard` para visualizar estadísticas agregadas por campeón.

---

## Stack Tecnológico

- **Python** 3.11+
- **Gestor de dependencias**: Poetry
- **Backend**: FastAPI + Uvicorn
- **ML / Datos**: scikit-learn, pandas, numpy
- **Config**: pydantic-settings, python-dotenv
- **Frontend**: HTML, CSS, JavaScript, Chart.js
- **Testing**: pytest

---

## Estructura del proyecto

```text
app/
  main.py
  api/
    v1/
      predictions.py
      stats.py
  core/
    config.py
    riot_client.py
  services/
    features.py
    model.py
  frontend/
    templates/
      index.html
      dashboard.html
    static/
      css/styles.css
      js/app.js
      js/dashboard.js
scripts/
  generate_raw_matches_csv.py
  process_matches.py
  train_model.py
data/
  raw/
    matches_raw.csv
  processed/
    stats_per_champion.csv
models/
  winrate_model.pkl
tests/
  test_api.py
  test_features.py
  test_model_service.py
docs/
  solution_problem.md
  data_pipeline.md
  modelo.md
  pruebas/
    api_prediccion.md
    dashboard.md
.env
pyproject.toml
README.md
```
## Cómo ejecutar el proyecto

1. Instalar dependencias
```bash
poetry install
```
2. Configurar variables de entorno
```bash
cp .env.example .env
```
# editar .env si es necesario
3. Generar datos crudos y procesados
```bash
poetry run python -m scripts.generate_raw_matches_csv
poetry run python -m scripts.process_matches
```
4. Entrenar el modelo
```bash
poetry run python -m scripts.train_model4
```
5. Levantar el servidor
```bash
poetry run uvicorn app.main:app --reload
```

Frontend predicción: http://127.0.0.1:8000/

Dashboard: http://127.0.0.1:8000/dashboard

Docs API: http://127.0.0.1:8000/docs

Tests
```bash
poetry run pytest
```
# Documentación técnica
Ver carpeta docs/:

   - solution_problem.md: explicación técnica detallada del problema y la solución.
   - data_pipeline.md: pipeline de datos y procesamiento.
   - modelo.md: descripción del modelo, hiperparámetros y métricas.
   - docs/pruebas/*: evidencias de pruebas funcionales (API + dashboard).

# Roadmap
   - Reemplazar datos simulados por datos reales de Riot API.
   - Mejorar el encoding de campeones (roles, sinergias, counters).
   - Probar otros modelos (RandomForest, XGBoost).
   - Autenticación y control de versiones de modelos.
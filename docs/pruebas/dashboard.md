# Evidencias de Pruebas Funcionales - Dashboard

## 1. Flujo probado

1. Generar datos y estadísticas:

```bash
   poetry run python -m scripts.generate_raw_matches_csv
   poetry run python -m scripts.process_matches
```
# Levantar el servidor:

```bash
poetry run uvicorn app.main:app --reload
```
Abrir el dashboard en el navegador:

http://127.0.0.1:8000/dashboard

2. Elementos verificados
El gráfico principal se renderiza correctamente usando Chart.js.

Al inspeccionar las llamadas de red del navegador (pestaña Network):
- Se observa una petición GET /api/v1/stats/champions.

El endpoint responde con un arreglo JSON donde cada elemento contiene:
- champion_id
- games
- wins
- winrate

Los ejes del gráfico muestran:
- Eje izquierdo (y): cantidad de partidas (games).
- Eje derecho (y1): winrate del campeón (valores entre 0 y 1, mostrados como porcentaje).
# Evidencias de Pruebas Funcionales - API de Predicción

## 1. Flujo probado

1. Levantar el servidor:
```bash
poetry run uvicorn app.main:app --reload
```
Abrir la documentación interactiva de la API en:

http://127.0.0.1:8000/docs

Probar el endpoint POST /api/v1/predict desde Swagger UI.

## 2. Caso de prueba
**Input**
```json
Copiar código
{
  "team_champions": [266, 103, 84, 12, 32],
  "enemy_champions": [67, 157, 238, 145, 51]
}
```
Resultado esperado
Código HTTP: 200 OK.

La respuesta contiene un campo winrate con un valor numérico en el rango [0, 1].

Resultado obtenido (ejemplo)
```json
{
  "winrate": 0.4733
}
```
(El valor exacto puede variar dependiendo del modelo entrenado.)

# 3. Observaciones
Se verificó que el endpoint valida correctamente:
- Que exista al menos un campeón por equipo.
- Que no se ingresen más de 5 campeones por equipo.

En caso de error de validación, la API responde con:
- Código HTTP 422 Unprocessable Entity.
- Un cuerpo JSON con el campo detail indicando el problema.
En caso de error interno (por ejemplo, problemas al cargar el modelo), la API responde con:
- Código HTTP 500 Internal Server Error.
- Un cuerpo JSON con el campo detail describiendo el error.
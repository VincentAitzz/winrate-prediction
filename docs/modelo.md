# Modelo Predictivo de Winrate

## 1. Algoritmo

Se utiliza **Regresión Logística** (`LogisticRegression`) de scikit-learn:

- Tipo de problema: clasificación binaria (`team_win` ∈ {0, 1}).
- Salida: probabilidad `P(team_win=1 | features)`.

### Justificación técnica

- Modelo lineal simple, rápido de entrenar.
- Probabilidades directamente interpretables.
- Sirve como línea base sobre la cual comparar futuros modelos:
  - RandomForestClassifier
  - GradientBoosting
  - XGBoost, etc.

---

## 2. Features

Entrada al modelo: vector de 10 características numéricas:

- `ally_1 .. ally_5`: IDs de campeones aliados.
- `enemy_1 .. enemy_5`: IDs de campeones enemigos.

La función `selection_to_feature_vector`:

- Rellena con ceros si hay menos de 5 campeones.
- Asegura que la dimensión siempre sea 10.

---

## 3. Entrenamiento

Script: `scripts/train_model.py`

- `train_test_split` con:
  - `test_size = 0.2`
  - `random_state = 42`
  - `stratify = y` para mantener la proporción de clases.

- Hiperparámetros:
  - `max_iter = 1000` (para asegurar convergencia).
  - El resto se mantienen por defecto (`C=1.0`, penalty L2).

---

## 4. Métricas

Para el conjunto de test se calculan:

- Accuracy.
- Precision, Recall y F1 para cada clase.
- Matriz de confusión.

Estas métricas se imprimen en consola al ejecutar `train_model.py`
y se pueden copiar a este documento o a la presentación final.

---

## 5. Interpretación técnica

- Si la accuracy de test es similar a la de entrenamiento, el modelo no está
  sobreajustando fuertemente al dataset simulado.
- La matriz de confusión permite ver si el modelo está sesgado hacia predecir
  siempre victoria o derrota (clase mayoritaria).
- Dado que los datos actuales son sintéticos, el valor absoluto de las métricas
  no es crítico; lo importante es dejar lista la infraestructura para entrenar
  con datos reales de RiotGames.
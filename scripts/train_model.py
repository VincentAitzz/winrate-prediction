"""Entrena un modelo de winrate usando el CSV crudo de partidas."""

from pathlib import Path

import numpy as np
import pandas as pd
from joblib import dump
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

from app.core.config import get_settings
from app.services.features import selection_to_feature_vector


def main() -> None:
    settings = get_settings()

    raw_path = Path("data/raw/matches_raw.csv")
    if not raw_path.exists():
        raise FileNotFoundError(
            f"No se encontró {raw_path}. "
            "Primero ejecuta: poetry run python -m scripts.generate_raw_matches_csv"
        )

    print(f"Leyendo datos crudos desde: {raw_path}")
    df = pd.read_csv(raw_path)

    team_cols = ["team_champ1", "team_champ2", "team_champ3", "team_champ4", "team_champ5"]
    enemy_cols = ["enemy_champ1", "enemy_champ2", "enemy_champ3", "enemy_champ4", "enemy_champ5"]

    features_list: list[np.ndarray] = []
    for _, row in df.iterrows():
        team = [int(row[c]) for c in team_cols]
        enemy = [int(row[c]) for c in enemy_cols]
        feat = selection_to_feature_vector(team, enemy)
        features_list.append(feat)

    X = np.vstack(features_list)
    y = df["team_win"].values

    print(f"Total muestras: {X.shape[0]}, número de features: {X.shape[1]}")

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)

    acc_train = model.score(X_train, y_train)
    acc_test = model.score(X_test, y_test)

    print(f"Accuracy entrenamiento: {acc_train:.3f}")
    print(f"Accuracy test:         {acc_test:.3f}")

    y_pred = model.predict(X_test)
    print("\n=== Classification report ===")
    print(classification_report(y_test, y_pred))

    print("=== Confusion matrix ===")
    print(confusion_matrix(y_test, y_pred))

    model_path = Path(settings.model_path)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    dump(model, model_path)

    print(f"\nModelo entrenado guardado en: {model_path}")


if __name__ == "__main__":
    main()

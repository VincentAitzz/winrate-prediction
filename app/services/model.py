from __future__ import annotations

import os
from typing import List

import numpy as np
from joblib import load
from sklearn.linear_model import LogisticRegression

from app.core.config import get_settings
from app.services.features import selection_to_feature_vector


class WinrateModelService:
    """Servicio que encapsula la carga del modelo y la predicción."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.model = self._load_or_create_dummy_model()

    def _load_or_create_dummy_model(self):
        """Intenta cargar el modelo desde disco, si no existe crea uno dummy.

        El modelo dummy sirve solo para poder probar el flujo completo.
        Más adelante lo sobrescribes con tu modelo real desde scripts/train_model.py.
        """
        model_path = self.settings.model_path

        if os.path.exists(model_path):
            return load(model_path)

        # Modelo dummy: entrena con datos aleatorios solo para tener algo funcional
        rng = np.random.default_rng(seed=42)
        n_samples = 200
        n_features = 10  # 5 champs aliados + 5 enemigos

        X = rng.integers(low=0, high=200, size=(n_samples, n_features))
        y = rng.integers(low=0, high=2, size=n_samples)

        model = LogisticRegression(max_iter=1000)
        model.fit(X, y)

        return model

    def predict_winrate(
        self,
        team_champions: List[int],
        enemy_champions: List[int],
    ) -> float:
        """Devuelve la probabilidad de victoria del equipo (entre 0 y 1)."""
        features = selection_to_feature_vector(team_champions, enemy_champions)
        features = features.reshape(1, -1)

        # Asumimos que el modelo tiene predict_proba
        proba = self.model.predict_proba(features)[0, 1]
        return float(proba)

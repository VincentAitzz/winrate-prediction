from pathlib import Path
import json
import numpy as np
import pandas as pd
from joblib import dump
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from app.core.config import get_settings
from app.services.features import selection_to_feature_vector
from app.services.analyzer import ChampionAnalyzer

def main() -> None:
    settings = get_settings()
    raw_path = Path("data/raw/matches_raw.csv")
    
    if not raw_path.exists():
        print(f"CSV no encontrado en {raw_path}. Ejecuta primero generate_raw_matches_csv.")
        return

    print(f"Leído datos desde: {raw_path}")
    df = pd.read_csv(raw_path)

    # --- PARTE 1: Machine Learning (Random Forest) ---
    print("\n--- Entrenando Random Forest (Esto puede tardar unos segundos) ---")
    
    team_cols = ["team_champ1", "team_champ2", "team_champ3", "team_champ4", "team_champ5"]
    enemy_cols = ["enemy_champ1", "enemy_champ2", "enemy_champ3", "enemy_champ4", "enemy_champ5"]

    # Preparamos los vectores (features)
    # Nota: Para datasets MUY grandes (millones), esto debería optimizarse con numpy puro,
    # pero para <500k funciona bien.
    features_list = []
    for _, row in df.iterrows():
        team = [int(row[c]) for c in team_cols]
        enemy = [int(row[c]) for c in enemy_cols]
        feat = selection_to_feature_vector(team, enemy)
        features_list.append(feat)

    X = np.vstack(features_list)
    y = df["team_win"].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # CONFIGURACIÓN DEL MODELO
    # n_estimators: Número de árboles (más es mejor pero más lento, 100 es estándar)
    # n_jobs=-1: Usa todos los núcleos de tu CPU para ir rápido
    model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    
    model.fit(X_train, y_train)
    
    acc = accuracy_score(y_test, model.predict(X_test))
    print(f"Accuracy test: {acc:.3f}")
    
    model_path = Path(settings.model_path)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    dump(model, model_path)
    print(f"Modelo guardado en {model_path}")

    # --- PARTE 2: Análisis Estadístico ---
    print("\n--- Generando Estadísticas por Campeón ---")
    analyzer = ChampionAnalyzer(df)
    
    matchup_stats = analyzer.process_matchups()
    rune_stats = analyzer.process_runes()
    
    output_dir = Path("data/processed")
    output_dir.mkdir(exist_ok=True)
    
    with open(output_dir / "champion_counters.json", "w") as f:
        json.dump(matchup_stats, f, indent=2)
        
    with open(output_dir / "champion_runes.json", "w") as f:
        json.dump(rune_stats, f, indent=2)

    print(f"Estadísticas JSON actualizadas en {output_dir}")

if __name__ == "__main__":
    main()
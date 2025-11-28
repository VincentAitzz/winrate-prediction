from pathlib import Path
import json
import numpy as np
import pandas as pd
from joblib import dump
from sklearn.ensemble import RandomForestClassifier  # <--- CAMBIO IMPORTANTE
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

# Asumimos que estas importaciones existen en tu proyecto
from app.core.config import get_settings
from app.services.features import selection_to_feature_vector

class ChampionAnalyzer:
    """
    Clase dedicada a extraer estadísticas descriptivas del DataFrame de partidas.
    (Misma lógica que tenías antes, no cambia).
    """
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.team_cols = ["team_champ1", "team_champ2", "team_champ3", "team_champ4", "team_champ5"]
        self.enemy_cols = ["enemy_champ1", "enemy_champ2", "enemy_champ3", "enemy_champ4", "enemy_champ5"]
        self.rune_cols = [c for c in df.columns if "rune" in c and "team" in c]

    def process_matchups(self) -> dict:
        print("Calculando estadísticas de matchups...")
        stats = {}
        
        for i, col in enumerate(self.team_cols):
            temp_df = self.df[[col, "team_win"] + self.enemy_cols].copy()
            temp_df.rename(columns={col: "champion_id"}, inplace=True)
            
            for enemy_col in self.enemy_cols:
                pair_stats = temp_df.groupby(["champion_id", enemy_col])["team_win"].agg(["count", "sum"])
                
                for (my_champ, enemy_champ), row in pair_stats.iterrows():
                    my_champ = int(my_champ)
                    enemy_champ = int(enemy_champ)
                    
                    if my_champ not in stats:
                        stats[my_champ] = {"total_games": 0, "wins": 0, "counters": {}}
                    
                    if enemy_champ not in stats[my_champ]["counters"]:
                        stats[my_champ]["counters"][enemy_champ] = {"games": 0, "wins": 0}
                    
                    stats[my_champ]["counters"][enemy_champ]["games"] += row["count"]
                    stats[my_champ]["counters"][enemy_champ]["wins"] += row["sum"]

        final_stats = {}
        for champ_id, data in stats.items():
            counter_list = []
            for enemy_id, enemy_data in data["counters"].items():
                # FILTRO APLICADO: Mínimo 10 partidas para considerar el matchup
                if enemy_data["games"] >= 10: 
                    wr = (enemy_data["wins"] / enemy_data["games"]) * 100
                    counter_list.append({
                        "enemy_id": enemy_id,
                        "games": int(enemy_data["games"]),
                        "winrate": round(wr, 2)
                    })
            
            counter_list.sort(key=lambda x: x["winrate"])
            final_stats[champ_id] = {
                "counters": counter_list[:10] 
            }
            
        return final_stats

    def process_runes(self) -> dict:
        if not self.rune_cols:
            return {}

        print("Calculando estadísticas de runas...")
        rune_stats = {}
        
        for i in range(1, 6):
            champ_col = f"team_champ{i}"
            rune_col = f"team_rune{i}"
            
            if rune_col not in self.df.columns:
                continue
                
            temp_df = self.df[[champ_col, rune_col, "team_win"]]
            groups = temp_df.groupby([champ_col, rune_col])["team_win"].agg(["count", "sum"])
            
            for (champ, rune), row in groups.iterrows():
                champ = int(champ)
                rune = int(rune)
                
                if champ not in rune_stats:
                    rune_stats[champ] = []
                
                wr = (row["sum"] / row["count"]) * 100
                rune_stats[champ].append({
                    "rune_id": rune,
                    "games": int(row["count"]),
                    "winrate": round(wr, 2)
                })

        for champ in rune_stats:
            rune_stats[champ].sort(key=lambda x: x["games"], reverse=True)
            
        return rune_stats

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
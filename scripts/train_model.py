from pathlib import Path
import json
import numpy as np
import pandas as pd
from joblib import dump
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

# Asumimos que estas importaciones existen en tu proyecto
# Si no, puedes comentar las líneas de 'selection_to_feature_vector' si solo quieres stats
from app.core.config import get_settings
from app.services.features import selection_to_feature_vector

class ChampionAnalyzer:
    """
    Clase dedicada a extraer estadísticas descriptivas del DataFrame de partidas.
    """
    def __init__(self, df: pd.DataFrame):
        self.df = df
        # Definimos las columnas base
        self.team_cols = ["team_champ1", "team_champ2", "team_champ3", "team_champ4", "team_champ5"]
        self.enemy_cols = ["enemy_champ1", "enemy_champ2", "enemy_champ3", "enemy_champ4", "enemy_champ5"]
        
        # Intentamos detectar columnas de runas si existen en el CSV
        # Asume formato: team_rune1_primary, team_rune2_primary, etc.
        self.rune_cols = [c for c in df.columns if "rune" in c and "team" in c]

    def process_matchups(self) -> dict:
        """
        Genera un diccionario con winrates y counters para cada campeón.
        """
        print("Calculando estadísticas de matchups...")
        stats = {}
        
        # Iteramos por las columnas de los 5 jugadores del equipo
        for i, col in enumerate(self.team_cols):
            # Creamos un sub-dataframe temporal para este "slot" (jugador 1, 2, etc)
            # Incluye: Campeón usado, Si ganó, y contra quién jugó (los 5 enemigos)
            temp_df = self.df[[col, "team_win"] + self.enemy_cols].copy()
            temp_df.rename(columns={col: "champion_id"}, inplace=True)
            
            # Iteramos sobre los enemigos para construir pares (Yo vs Enemigo)
            for enemy_col in self.enemy_cols:
                # Agrupamos por (Mi Campeón, Campeón Enemigo)
                # Esto cuenta cuántas veces gané y perdí contra ese enemigo específico
                pair_stats = temp_df.groupby(["champion_id", enemy_col])["team_win"].agg(["count", "sum"])
                
                for (my_champ, enemy_champ), row in pair_stats.iterrows():
                    my_champ = int(my_champ)
                    enemy_champ = int(enemy_champ)
                    
                    if my_champ not in stats:
                        stats[my_champ] = {"total_games": 0, "wins": 0, "counters": {}}
                    
                    # Actualizar stats generales del campeón
                    # Nota: Esto se sumará 5 veces por partida (una por cada enemigo), 
                    # así que lo ajustaremos después o usamos lógica distinta para totales.
                    # Para simplificar counters, nos enfocamos en el diccionario 'counters'.
                    
                    if enemy_champ not in stats[my_champ]["counters"]:
                        stats[my_champ]["counters"][enemy_champ] = {"games": 0, "wins": 0}
                    
                    stats[my_champ]["counters"][enemy_champ]["games"] += row["count"]
                    stats[my_champ]["counters"][enemy_champ]["wins"] += row["sum"]

        # Post-procesamiento para calcular porcentajes
        final_stats = {}
        for champ_id, data in stats.items():
            counter_list = []
            for enemy_id, enemy_data in data["counters"].items():
                if enemy_data["games"] > 0: # Filtro mínimo de partidas si deseas
                    wr = (enemy_data["wins"] / enemy_data["games"]) * 100
                    counter_list.append({
                        "enemy_id": enemy_id,
                        "games": int(enemy_data["games"]),
                        "winrate": round(wr, 2)
                    })
            
            # Ordenar counters: Aquellos contra los que tengo PEOR winrate (mis counters reales)
            counter_list.sort(key=lambda x: x["winrate"])
            
            final_stats[champ_id] = {
                "counters": counter_list[:10] # Top 10 peores matchups
            }
            
        return final_stats

    def process_runes(self) -> dict:
        """
        Calcula las runas más frecuentes y su winrate si las columnas existen.
        """
        if not self.rune_cols:
            return {"error": "No se encontraron columnas de runas en el CSV"}

        print("Calculando estadísticas de runas...")
        rune_stats = {}
        
        # Lógica similar: Pivotear datos para asociar Campeón -> Runa -> Win/Loss
        # Asumiendo que team_champ1 corresponde a team_rune1
        for i in range(1, 6):
            champ_col = f"team_champ{i}"
            rune_col = f"team_rune{i}" # Ajusta este nombre según tu CSV real
            
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

        # Ordenar runas por popularidad (games)
        for champ in rune_stats:
            rune_stats[champ].sort(key=lambda x: x["games"], reverse=True)
            
        return rune_stats

def main() -> None:
    settings = get_settings()
    raw_path = Path("data/raw/matches_raw.csv")
    
    if not raw_path.exists():
        print("CSV no encontrado.")
        return

    print(f"Leyendo datos crudos desde: {raw_path}")
    df = pd.read_csv(raw_path)

    # --- PARTE 1: Machine Learning (Tu código original) ---
    print("\n--- Iniciando Entrenamiento de Modelo ---")
    team_cols = ["team_champ1", "team_champ2", "team_champ3", "team_champ4", "team_champ5"]
    enemy_cols = ["enemy_champ1", "enemy_champ2", "enemy_champ3", "enemy_champ4", "enemy_champ5"]

    features_list: list[np.ndarray] = []
    # Usamos iterrows para ML, aunque vectorize sería más rápido para grandes volúmenes
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

    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)
    
    print(f"Accuracy test: {model.score(X_test, y_test):.3f}")
    
    model_path = Path(settings.model_path)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    dump(model, model_path)

    # --- PARTE 2: Análisis Estadístico (Nueva Funcionalidad) ---
    print("\n--- Generando Estadísticas por Campeón ---")
    analyzer = ChampionAnalyzer(df)
    
    # 1. Obtener Counters
    matchup_stats = analyzer.process_matchups()
    
    # 2. Obtener Runas (Si hay columnas)
    rune_stats = analyzer.process_runes()
    
    # Guardamos los resultados en JSON para ser consumidos por una API o Frontend
    output_dir = Path("data/processed")
    output_dir.mkdir(exist_ok=True)
    
    with open(output_dir / "champion_counters.json", "w") as f:
        json.dump(matchup_stats, f, indent=2)
        
    with open(output_dir / "champion_runes.json", "w") as f:
        json.dump(rune_stats, f, indent=2)

    print(f"Estadísticas guardadas en {output_dir}")
    
    # Ejemplo de impresión para verificar
    example_champ_id = list(matchup_stats.keys())[0]
    print(f"\nEjemplo stats para Champ ID {example_champ_id}:")
    print(f"Peores matchups (Counters): {matchup_stats[example_champ_id]['counters'][:3]}")

if __name__ == "__main__":
    main()
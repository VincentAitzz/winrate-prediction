import pandas as pd

class ChampionAnalyzer:
    """
    Clase dedicada a extraer estadísticas descriptivas del DataFrame de partidas.
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

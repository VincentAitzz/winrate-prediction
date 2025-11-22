"""Procesa el CSV crudo de partidas y genera estadísticas por campeón.

- Lee: data/raw/matches_raw.csv
- Genera: data/processed/stats_per_champion.csv
"""

from pathlib import Path

import pandas as pd


def main() -> None:
    raw_path = Path("data/raw/matches_raw.csv")
    if not raw_path.exists():
        raise FileNotFoundError(
            f"No se encontró {raw_path}. Ejecuta primero "
            "poetry run python -m scripts.generate_raw_matches_csv"
        )

    processed_dir = Path("data/processed")
    processed_dir.mkdir(parents=True, exist_ok=True)
    out_stats = processed_dir / "stats_per_champion.csv"

    df = pd.read_csv(raw_path)

    team_cols = ["team_champ1", "team_champ2", "team_champ3", "team_champ4", "team_champ5"]
    enemy_cols = ["enemy_champ1", "enemy_champ2", "enemy_champ3", "enemy_champ4", "enemy_champ5"]

    # "Desapilar" campeones aliados
    team_df = df[["team_win"] + team_cols].melt(
        id_vars=["team_win"],
        value_vars=team_cols,
        var_name="slot",
        value_name="champion_id",
    )
    team_df["is_ally"] = 1

    # "Desapilar" campeones enemigos
    enemy_df = df[["team_win"] + enemy_cols].melt(
        id_vars=["team_win"],
        value_vars=enemy_cols,
        var_name="slot",
        value_name="champion_id",
    )
    enemy_df["is_ally"] = 0

    all_df = pd.concat([team_df, enemy_df], ignore_index=True)

    # Para enemigos, una victoria del equipo aliado es una derrota del campeón
    all_df["champion_win"] = all_df.apply(
        lambda row: row["team_win"] if row["is_ally"] == 1 else 1 - row["team_win"],
        axis=1,
    )

    grouped = (
        all_df.groupby("champion_id")["champion_win"]
        .agg(["count", "sum"])
        .reset_index()
        .rename(columns={"count": "games", "sum": "wins"})
    )

    grouped["winrate"] = grouped["wins"] / grouped["games"]

    grouped.to_csv(out_stats, index=False)
    print(f"Estadísticas por campeón guardadas en: {out_stats}")


if __name__ == "__main__":
    main()

async function fetchChampionStats() {
    const response = await fetch("/api/v1/stats/champions");
    if (!response.ok) {
        throw new Error("No se pudieron obtener las estadísticas de campeones.");
    }
    return response.json();
}

/**
 * Obtiene un mapa { id_numérico: nombre } desde Data Dragon.
 */
async function fetchChampionNameMap() {
    const versionsRes = await fetch("https://ddragon.leagueoflegends.com/api/versions.json");
    const versions = await versionsRes.json();
    const latest = versions[0];

    // es_ES para nombres en español
    const champsRes = await fetch(
        `https://ddragon.leagueoflegends.com/cdn/${latest}/data/es_ES/champion.json`
    );
    const data = await champsRes.json();

    const map = {};
    Object.values(data.data).forEach((champ) => {
        map[Number(champ.key)] = champ.name;
    });

    return map;
}

function buildChart(ctx, labels, games, winrates) {
    // eslint-disable-next-line no-undef
    new Chart(ctx, {
        type: "bar",
        data: {
            labels,
            datasets: [
                {
                    type: "bar",
                    label: "Partidas jugadas",
                    data: games,
                    yAxisID: "y",
                },
                {
                    type: "line",
                    label: "Winrate",
                    data: winrates,
                    yAxisID: "y1",
                },
            ],
        },
        options: {
            responsive: true,
            interaction: {
                mode: "index",
                intersect: false,
            },
            scales: {
                y: {
                    beginAtZero: true,
                    position: "left",
                    title: {
                        display: true,
                        text: "Partidas",
                    },
                },
                y1: {
                    beginAtZero: true,
                    position: "right",
                    grid: {
                        drawOnChartArea: false,
                    },
                    title: {
                        display: true,
                        text: "Winrate",
                    },
                    ticks: {
                        callback: (value) => `${(value * 100).toFixed(0)}%`,
                    },
                },
            },
        },
    });
}

document.addEventListener("DOMContentLoaded", async () => {
    const canvas = document.getElementById("championWinrateChart");
    if (!canvas) return;
    const ctx = canvas.getContext("2d");

    try {
        const [stats, champNameMap] = await Promise.all([
            fetchChampionStats(),
            fetchChampionNameMap(),
        ]);

        const labels = stats.map(
            (s) => champNameMap[s.champion_id] || `Champ ${s.champion_id}`
        );
        const games = stats.map((s) => s.games);
        const winrates = stats.map((s) => s.winrate);

        buildChart(ctx, labels, games, winrates);
    } catch (err) {
        console.error("Error al construir el dashboard:", err);
        // aquí podrías mostrar un mensaje en pantalla si quieres
    }
});

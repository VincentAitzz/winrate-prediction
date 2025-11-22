let CHAMPIONS = [];

/**
 * Carga la lista de campeones desde Riot Data Dragon (última versión)
 * y los deja en la variable global CHAMPIONS ordenados alfabéticamente.
 */
async function loadChampions() {
    // Usamos es_ES para mostrar los nombres en español
    const versionsRes = await fetch("https://ddragon.leagueoflegends.com/api/versions.json");
    const versions = await versionsRes.json();
    const latest = versions[0];

    const champsRes = await fetch(
        `https://ddragon.leagueoflegends.com/cdn/${latest}/data/es_ES/champion.json`
    );
    const data = await champsRes.json();

    CHAMPIONS = Object.values(data.data)
        .map((champ) => ({
            id: Number(champ.key), // ID numérico usado por Riot
            name: champ.name,      // Nombre en español
        }))
        .sort((a, b) => a.name.localeCompare(b.name));

    // Una vez cargados, construimos los selects y activamos la búsqueda
    createChampionSelects("team-selects", "team");
    createChampionSelects("enemy-selects", "enemy");
    setupSearchInput("team-filter", "team");
    setupSearchInput("enemy-filter", "enemy");
}

/**
 * Crea 5 <select> para el equipo indicado, usando la lista global CHAMPIONS.
 */
function createChampionSelects(containerId, namePrefix) {
    const container = document.getElementById(containerId);
    container.innerHTML = "";

    for (let i = 0; i < 5; i++) {
        const select = document.createElement("select");
        select.name = namePrefix;

        const placeholder = document.createElement("option");
        placeholder.value = "";
        placeholder.textContent = `Campeón ${i + 1} (opcional)`;
        placeholder.selected = true;
        select.appendChild(placeholder);

        CHAMPIONS.forEach((champ) => {
            const option = document.createElement("option");
            option.value = String(champ.id);
            option.textContent = champ.name;
            select.appendChild(option);
        });

        container.appendChild(select);
    }
}

/**
 * Configura el input de búsqueda para filtrar las opciones de todos
 * los <select> de un equipo.
 */
function setupSearchInput(inputId, selectName) {
    const input = document.getElementById(inputId);
    if (!input) return;

    input.addEventListener("input", () => {
        const term = input.value.toLowerCase();

        const options = document.querySelectorAll(`select[name="${selectName}"] option`);
        options.forEach((opt) => {
            if (opt.value === "") {
                // siempre mostramos el placeholder
                opt.hidden = false;
                return;
            }
            const text = opt.textContent.toLowerCase();
            opt.hidden = !text.includes(term);
        });
    });
}

/**
 * Obtiene los IDs de campeones seleccionados desde los <select>.
 */
function parseChampionInputs(name) {
    const selects = Array.from(document.querySelectorAll(`select[name="${name}"]`));
    const values = selects
        .map((sel) => sel.value.trim())
        .filter((v) => v !== "")
        .map((v) => Number(v))
        .filter((v) => Number.isFinite(v) && v >= 0);

    return values;
}

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("prediction-form");
    const resultSection = document.getElementById("result");
    const winrateValue = document.getElementById("winrate-value");
    const errorMessage = document.getElementById("form-error");

    // Cargamos los campeones (async) al iniciar
    loadChampions().catch((err) => {
        console.error("Error al cargar campeones desde Data Dragon:", err);
        errorMessage.textContent =
            "No se pudieron cargar los campeones. Revisa tu conexión a internet e intenta recargar la página.";
        errorMessage.classList.remove("hidden");
    });

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        errorMessage.classList.add("hidden");
        resultSection.classList.add("hidden");

        const teamChampions = parseChampionInputs("team");
        const enemyChampions = parseChampionInputs("enemy");

        if (teamChampions.length === 0 || enemyChampions.length === 0) {
            errorMessage.textContent = "Debes seleccionar al menos 1 campeón por equipo.";
            errorMessage.classList.remove("hidden");
            return;
        }

        if (teamChampions.length > 5 || enemyChampions.length > 5) {
            errorMessage.textContent = "Máximo 5 campeones por equipo.";
            errorMessage.classList.remove("hidden");
            return;
        }

        const payload = {
            team_champions: teamChampions,
            enemy_champions: enemyChampions,
        };

        try {
            const response = await fetch("/api/v1/predict", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(payload),
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || "Error al obtener la predicción.");
            }

            const data = await response.json();
            const winrate = (data.winrate * 100).toFixed(2);

            winrateValue.textContent = `Probabilidad de victoria: ${winrate}%`;
            resultSection.classList.remove("hidden");
        } catch (err) {
            console.error(err);
            errorMessage.textContent = err.message || "Ocurrió un error inesperado.";
            errorMessage.classList.remove("hidden");
        }
    });
});

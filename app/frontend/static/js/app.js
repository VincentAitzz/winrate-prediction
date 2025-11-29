let CHAMPIONS = []; // Array para los selectores (ordenado)
let CHAMPION_MAP = {}; // Objeto para búsqueda rápida por ID { 103: {name: "Ahri", ...} }
let RUNE_MAP = {}; // Objeto para nombres de runas { 8000: "Precision", ... }
let DD_VERSION = "13.24.1"; // Valor por defecto, se actualiza al cargar

/**
 * Carga inicial de datos estáticos (Versión, Campeones, Runas)
 */
async function loadStaticData() {
  try {
    // 1. Obtener última versión
    const versionsRes = await fetch(
      "https://ddragon.leagueoflegends.com/api/versions.json",
    );
    const versions = await versionsRes.json();
    DD_VERSION = versions[0];

    // 2. Cargar Campeones
    const champsRes = await fetch(
      `https://ddragon.leagueoflegends.com/cdn/${DD_VERSION}/data/es_ES/champion.json`,
    );
    const champData = await champsRes.json();

    // Procesamos campeones
    CHAMPIONS = Object.values(champData.data)
      .map((champ) => ({
        id: Number(champ.key), // ID Numérico (para la API de predicción)
        alias: champ.id, // ID Texto (para URLs de imágenes, ej: "LeeSin")
        name: champ.name, // Nombre visual
        tags: champ.tags, // Roles (Mago, Asesino, etc.)
      }))
      .sort((a, b) => a.name.localeCompare(b.name));

    // Llenar el mapa para búsquedas rápidas
    CHAMPIONS.forEach((c) => {
      CHAMPION_MAP[c.id] = c;
    });

    // 3. Cargar Runas (para mostrar nombres en el panel)
    const runesRes = await fetch(
      `https://ddragon.leagueoflegends.com/cdn/${DD_VERSION}/data/es_ES/runesReforged.json`,
    );
    const runesData = await runesRes.json();

    // Aplanamos la estructura de runas para búsqueda fácil
    runesData.forEach((tree) => {
      // Runas clave suelen estar en los slots
      tree.slots.forEach((slot) => {
        slot.runes.forEach((rune) => {
          RUNE_MAP[rune.id] = {
            name: rune.name,
            icon: rune.icon, // Ruta parcial de imagen
          };
        });
      });
    });

    // 4. Inicializar UI
    createChampionSelects("team-selects", "team");
    createChampionSelects("enemy-selects", "enemy");
    setupSearchInput("team-filter", "team");
    setupSearchInput("enemy-filter", "enemy");

    console.log(
      `Datos cargados: ${CHAMPIONS.length} campeones, Versión ${DD_VERSION}`,
    );
  } catch (err) {
    console.error("Error cargando datos estáticos:", err);
    document.getElementById("form-error").textContent =
      "Error cargando datos de Riot. Recarga la página.";
    document.getElementById("form-error").classList.remove("hidden");
  }
}

/**
 * Crea los <select> y les añade el evento para actualizar el panel.
 */
function createChampionSelects(containerId, namePrefix) {
  const container = document.getElementById(containerId);
  container.innerHTML = "";

  for (let i = 0; i < 5; i++) {
    const select = document.createElement("select");
    select.name = namePrefix;
    select.classList.add("champ-select"); // Clase para estilo

    const placeholder = document.createElement("option");
    placeholder.value = "";
    placeholder.textContent = `Campeón ${i + 1} (opcional)`;
    select.appendChild(placeholder);

    CHAMPIONS.forEach((champ) => {
      const option = document.createElement("option");
      option.value = String(champ.id);
      option.textContent = champ.name;
      select.appendChild(option);
    });

    // EVENTOS PARA EL PANEL LATERAL
    // Al cambiar la selección
    select.addEventListener("change", (e) => {
      if (e.target.value) updateInfoPanel(e.target.value);
      updateSelectAvailability(containerId);
    });

    // Al hacer foco (para teclado o click)
    select.addEventListener("focus", (e) => {
      if (e.target.value) updateInfoPanel(e.target.value);
      updateSelectAvailability(containerId);
    });

    container.appendChild(select);
  }
}

/**
 * Lógica principal para actualizar el panel derecho
 */
function updateInfoPanel(championId) {
  const id = Number(championId);
  const champData = CHAMPION_MAP[id];
  const panel = document.getElementById("champion-info-panel");

  if (!champData) return;

  // Mostrar panel
  panel.classList.remove("hidden");

  // 1. Header: Imagen y Nombre
  const imgEl = document.getElementById("info-img");
  imgEl.src = `https://ddragon.leagueoflegends.com/cdn/${DD_VERSION}/img/champion/${champData.alias}.png`;
  imgEl.classList.remove("hidden");

  document.getElementById("info-name").textContent = champData.name;
  document.getElementById("info-role").textContent = champData.tags.join(" • ");

  // 2. Estadísticas Inyectadas (Counters)
  // Accedemos a las variables globales definidas en el HTML
  const countersData = window.CHAMPION_COUNTERS
    ? window.CHAMPION_COUNTERS[id]
    : null;
  const countersList = document.getElementById("info-counters-list");
  countersList.innerHTML = "";

  if (
    countersData &&
    countersData.counters &&
    countersData.counters.length > 0
  ) {
    // Tomamos solo los top 5 para no saturar
    countersData.counters.slice(0, 5).forEach((c) => {
      const enemyName = CHAMPION_MAP[c.enemy_id]
        ? CHAMPION_MAP[c.enemy_id].name
        : `ID ${c.enemy_id}`;
      const li = document.createElement("li");
      // Nota: Si es counter, significa que MI winrate es bajo.
      // c.winrate es MI winrate contra él.
      li.innerHTML = `
                <span>vs ${enemyName}</span>
                <span class="winrate-low">${c.winrate}% WR</span>
            `;
      countersList.appendChild(li);
    });
  } else {
    countersList.innerHTML =
      "<li style='color:#666'>Sin datos suficientes</li>";
  }

  // 3. Estadísticas Inyectadas (Runas)
  const runesData = window.CHAMPION_RUNES ? window.CHAMPION_RUNES[id] : null;
  const runesList = document.getElementById("info-runes-list");
  runesList.innerHTML = "";

  if (runesData && runesData.length > 0) {
    runesData.slice(0, 3).forEach((r) => {
      const runeInfo = RUNE_MAP[r.rune_id];
      const runeName = runeInfo ? runeInfo.name : `Runa ${r.rune_id}`;
      // Icono opcional
      const iconUrl = runeInfo
        ? `https://ddragon.leagueoflegends.com/cdn/img/${runeInfo.icon}`
        : "";

      const li = document.createElement("li");
      li.innerHTML = `
                <span>${runeName}</span>
                <span class="winrate-high">${r.winrate}% WR</span>
            `;
      runesList.appendChild(li);
    });
  } else {
    runesList.innerHTML = "<li style='color:#666'>Sin datos de runas</li>";
  }
}

/**
 * Configura el input de búsqueda
 */
function setupSearchInput(inputId, selectName) {
  const input = document.getElementById(inputId);
  if (!input) return;

  // Calculamos el ID del contenedor basado en el nombre (team -> team-selects)
  const containerId = `${selectName}-selects`;

  input.addEventListener("input", () => {
    // En lugar de filtrar aquí, llamamos a la lógica maestra
    updateSelectAvailability(containerId);
  });
}

/**
 * Parsea los inputs para enviar al backend
 */
function parseChampionInputs(name) {
  const selects = Array.from(
    document.querySelectorAll(`select[name="${name}"]`),
  );
  return selects
    .map((sel) => sel.value.trim())
    .filter((v) => v !== "")
    .map((v) => Number(v))
    .filter((v) => Number.isFinite(v) && v >= 0);
}

// Inicialización
document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("prediction-form");
  const resultSection = document.getElementById("result");
  const winrateValue = document.getElementById("winrate-value");
  const errorMessage = document.getElementById("form-error");

  loadStaticData();

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    errorMessage.classList.add("hidden");
    resultSection.classList.add("hidden");

    const teamChampions = parseChampionInputs("team");
    const enemyChampions = parseChampionInputs("enemy");

    if (teamChampions.length < 5 || enemyChampions.length < 5) {
      errorMessage.textContent = "Debes seleccionar los 5 campeones de cada equipo para predecir.";
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
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || "Error en la predicción.");
      }

      const data = await response.json();
      const winrate = (data.winrate * 100).toFixed(1);

      // Color del resultado según probabilidad
      winrateValue.textContent = `${winrate}%`;
      winrateValue.className = "winrate"; // reset
      if (data.winrate > 0.55) winrateValue.classList.add("winrate-high");
      else if (data.winrate < 0.45) winrateValue.classList.add("winrate-low");

      resultSection.classList.remove("hidden");
    } catch (err) {
      console.error(err);
      errorMessage.textContent = err.message || "Error inesperado.";
      errorMessage.classList.remove("hidden");
    }
  });
});

function updateSelectAvailability(containerId) {
  const container = document.getElementById(containerId);
  const selects = Array.from(container.querySelectorAll("select"));

  // 1. Identificar el buscador asociado (team-selects -> team-filter)
  // Asumimos que tus IDs son consistentes: "team-selects" y "team-filter"
  const filterId = containerId.replace("selects", "filter");
  const filterInput = document.getElementById(filterId);
  const searchTerm = filterInput ? filterInput.value.toLowerCase() : "";

  // 2. ¿Qué campeones ya están pillados en este equipo?
  const selectedValues = selects.map((s) => s.value).filter((v) => v !== "");

  // 3. Recorrer CADA opción de CADA select
  selects.forEach((select) => {
    const myValue = select.value; // El que yo tengo puesto no se oculta

    Array.from(select.options).forEach((option) => {
      if (option.value === "") return; // Ignorar placeholder

      const isTaken = selectedValues.includes(option.value);
      const isMe = option.value === myValue;

      // Chequeo de búsqueda (si hay texto)
      const text = option.textContent.toLowerCase();
      const matchesSearch = text.includes(searchTerm);

      // LA REGLA DE ORO:
      // Se oculta si: (Está tomado Y no soy yo) O (No coincide con la búsqueda)
      if ((isTaken && !isMe) || !matchesSearch) {
        option.hidden = true;
        option.style.display = "none"; // Refuerzo para navegadores rebeldes
      } else {
        option.hidden = false;
        option.style.display = "";
      }
    });
  });
}

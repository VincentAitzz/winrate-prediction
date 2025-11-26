import json
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.v1.predictions import router as predictions_router
from app.api.v1.stats import router as stats_router

app = FastAPI(title="Can i win with these monkeys")

# Routes
app.include_router(predictions_router)
app.include_router(stats_router)

# Static files (CSS, JS)
app.mount(
    "/static",
    StaticFiles(directory="app/frontend/static"),
    name="static",
)

#Templates
templates = Jinja2Templates(directory="app/frontend/templates")

def load_stats():
    base_path = Path("data/processed")
    counters = {}
    runes = {}
    
    try:
        if (base_path / "champion_counters.json").exists():
            with open(base_path / "champion_counters.json", "r") as f:
                counters = json.load(f)
        
        if (base_path / "champion_runes.json").exists():
            with open(base_path / "champion_runes.json", "r") as f:
                runes = json.load(f)
    except Exception as e:
        print(f"Error cargando stats: {e}")
    
    return counters, runes

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):

    counters_data, runes_data = load_stats()

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "Can i win with these monkeys",
            "counters_data": counters_data,
            "runes_data": runes_data,
        },
    )
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):

    counters_data, runes_data = load_stats()

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "title": "LoL Winrate Dashboard",
            "counters_data": counters_data,
            "runes_data": runes_data,
        },
    )
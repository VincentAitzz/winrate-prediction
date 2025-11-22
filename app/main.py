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


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "Can i win with these monkeys",
        },
    )
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "title": "LoL Winrate Dashboard",
        },
    )
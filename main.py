from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from database.session import init_db, get_db
from api.endpoints.bookmark import router as bookmark_router
import crud.bookmark as bookmark_crud

app = FastAPI(title="Bookmark App")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(bookmark_router)

@app.on_event("startup")
def startup():
    init_db()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    with get_db() as conn:
        bookmarks = bookmark_crud.get_all_bookmarks(conn)
    return templates.TemplateResponse("index.html", {"request": request, "bookmarks": bookmarks})

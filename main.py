from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from starlette.middleware.sessions import SessionMiddleware

from database.session import init_db, get_db
from api.endpoints.bookmark import router as bookmark_router
from api.endpoints.auth import router as auth_router
from api.dependencies import require_login

import crud.bookmark as bookmark_crud
from api.templates import templates

app = FastAPI(title="Bookmark App")

app.add_middleware(SessionMiddleware, secret_key="dev-secret-change-in-production") # <----- "when we get to Docker we'll move this to an environment variable (same pattern as DB_PATH in session.py)"
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(bookmark_router)
app.include_router(auth_router)


@app.on_event("startup")
def startup():
    init_db()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, user_id: int = Depends(require_login)):
    with get_db() as conn:
        bookmarks = bookmark_crud.get_all_bookmarks(conn, user_id)
    return templates.TemplateResponse("index.html", {"request": request, "bookmarks": bookmarks})

@app.exception_handler(401)
async def not_authenticated(request: Request, exc: HTTPException):
    return RedirectResponse(url="/login", status_code=303)
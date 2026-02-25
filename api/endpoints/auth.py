from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from database.session import get_db
import crud.user as user_crud

from crud.user import pwd_context

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/login", response_class=HTMLResponse)
async def get_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login", response_class=HTMLResponse)
async def check_login(request: Request, username: str = Form(...), password: str = Form(...)):
    with get_db() as conn:
        result = user_crud.get_user_by_username(conn, username)
    if not result or not pwd_context.verify(password, result["password_hash"]):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})
    request.session["user_id"] = result["id"]
    return RedirectResponse(url="/", status_code=303)

@router.post("/logout",response_class=HTMLResponse)
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)
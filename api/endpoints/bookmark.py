from fastapi import APIRouter, HTTPException, Request, Form
from typing import List, Optional

from database.session import get_db
from models.schemas import Bookmark
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import crud.bookmark as bookmark_crud

templates = Jinja2Templates(directory="templates")
router = APIRouter(prefix="/api/bookmarks", tags=["bookmarks"]) # Prefix so we dont need to write "/api/bookmarks" on every @router. below. Tags is for documentation on /docs page

@router.get("", response_model=List[Bookmark])
async def get_bookmarks():
    with get_db() as conn:
        return bookmark_crud.get_all_bookmarks(conn)

@router.get("/by-tag/{tag_name}", response_model=List[Bookmark])
async def get_bookmarks_by_tag(tag_name: str):
    with get_db() as conn:
        return bookmark_crud.get_bookmarks_by_tag(conn, tag_name)

@router.post("", response_class=HTMLResponse)
async def create_bookmark(request: Request, url: str = Form(...), title: Optional[str] = Form(None), tags: List[str] = Form ([])):
    with get_db() as conn:
        result = bookmark_crud.create_bookmark(conn, url, title, favicon=None, tag_names=tags)
    return templates.TemplateResponse("bookmark_item.html", {"request": request, "bookmark": result})

@router.post("/{bookmark_id}/update", response_class=HTMLResponse)
async def update_bookmark(request: Request, bookmark_id: int, new_title: str = Form(...)):
    with get_db() as conn:
        result = bookmark_crud.update_bookmark_title(conn, bookmark_id, new_title)
    if not result:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    return templates.TemplateResponse("bookmark_item.html", {"request": request, "bookmark": result})

@router.post("/{bookmark_id}/delete")
async def delete_bookmark(bookmark_id: int):
    with get_db() as conn:
        deleted = bookmark_crud.delete_bookmark(conn, bookmark_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    return HTMLResponse(content="")
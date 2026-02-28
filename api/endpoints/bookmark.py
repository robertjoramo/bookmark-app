from fastapi import APIRouter, HTTPException, Request, Form, Depends
from typing import List, Optional

from database.session import get_db
from models.schemas import Bookmark
from fastapi.responses import HTMLResponse

from api.templates import templates

import crud.bookmark as bookmark_crud
from api.dependencies import require_login

import httpx
import re
import html

router = APIRouter(prefix="/api/bookmarks", tags=["bookmarks"]) # Prefix so we dont need to write "/api/bookmarks" on every @router. below. Tags is for documentation on /docs page


# GET METADATA FROM URL #
@router.get("/fetch-metadata", response_class=HTMLResponse)
async def fetch_metadata(url: str = "", user_id: int = Depends(require_login)):
    title = ""
    description = ""
    if url:
        try:
            async with httpx.AsyncClient(timeout=5, follow_redirects=True) as client:
                response = await client.get(url)
                match_title = re.search(r'<title>(.*?)<\/title>', response.text, re.IGNORECASE)
                if match_title:
                    title = match_title.group(1)
                match_desc = re.search(r'<meta[^>]+name=["\']description["\'][^>]*>', response.text, re.IGNORECASE)
                if match_desc:
                    content_match = re.search(r'content=["\'](.*?)["\']', match_desc.group(0), re.IGNORECASE)
                    if content_match:
                        description = content_match.group(1)
        except Exception:
            pass
    return f'''
        <input type="text" name="title" placeholder="Title" value="{html.escape(title)}">
        <textarea name="description" placeholder="Description">{html.escape(description)}</textarea>
    '''





@router.get("", response_model=List[Bookmark])
async def get_bookmarks(user_id: int = Depends(require_login)):
    with get_db() as conn:
        return bookmark_crud.get_all_bookmarks(conn, user_id)

@router.get("/by-tag/{tag_name}", response_model=List[Bookmark])
async def get_bookmarks_by_tag(tag_name: str, user_id: int = Depends(require_login)):
    with get_db() as conn:
        return bookmark_crud.get_bookmarks_by_tag(conn, tag_name, user_id)

@router.post("", response_class=HTMLResponse)
async def create_bookmark(request: Request, url: str = Form(...), title: Optional[str] = Form(None), description: Optional[str] = Form(None), tags: List[str] = Form ([]), user_id: int = Depends(require_login)):
    with get_db() as conn:
        result = bookmark_crud.create_bookmark(conn, url, title, favicon=None, description=description, tag_names=tags, user_id=user_id)
    return templates.TemplateResponse("bookmark_item.html", {"request": request, "bookmark": result})

@router.post("/{bookmark_id}/update", response_class=HTMLResponse)
async def update_bookmark(request: Request, bookmark_id: int, new_title: str = Form(...), new_url: str = Form(...), new_description: Optional[str] = Form(None), new_tags: List[str] = Form ([]), user_id: int = Depends(require_login)):
    with get_db() as conn:
        result = bookmark_crud.update_bookmark(conn, bookmark_id, new_title, new_url, new_description, new_tags, user_id)
    if not result:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    return templates.TemplateResponse("bookmark_item.html", {"request": request, "bookmark": result})

@router.post("/{bookmark_id}/delete")
async def delete_bookmark(bookmark_id: int, user_id: int = Depends(require_login)):
    with get_db() as conn:
        deleted = bookmark_crud.delete_bookmark(conn, bookmark_id, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    return HTMLResponse(content="")

@router.get("/{bookmark_id}", response_class=HTMLResponse)
async def get_bookmark(request: Request, bookmark_id: int, user_id: int = Depends(require_login)):
    with get_db() as conn:
        result = bookmark_crud.get_bookmark_by_id(conn, bookmark_id, user_id)
    if not result:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    return templates.TemplateResponse("bookmark_item.html", {"request": request, "bookmark": result})

@router.get("/{bookmark_id}/edit", response_class=HTMLResponse)
async def get_bookmark_edit(request: Request, bookmark_id: int, user_id: int = Depends(require_login)):
    with get_db() as conn:
        result = bookmark_crud.get_bookmark_by_id(conn, bookmark_id, user_id)
    if not result:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    return templates.TemplateResponse("bookmark_item_edit.html", {"request": request, "bookmark": result})

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import os

# Initialize FastAPI
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static") #Not used yet
templates = Jinja2Templates(directory="templates")


################
### DATABASE ###
################
DB_NAME = "bookmarks.db"

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row # Returns rows as dictionaries
    return conn

def init_db():
    with get_db() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS bookmarks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            title TEXT
            )
        """)
        conn.commit()

init_db()


class Bookmark(BaseModel):
    id: int
    url: str
    title: Optional[str] = None


# API: Get all bookmarks
@app.get("/api/bookmarks", response_model=List[Bookmark])
async def get_bookmarks():
    conn = get_db()
    cursor = conn.execute("SELECT id, url, title FROM bookmarks")
    bookmarks = [Bookmark(**dict(row)) for row in cursor.fetchall()]
    conn.close()
    return bookmarks

# API: Add a bookmark
@app.post("/api/bookmarks", response_model=Bookmark)
async def add_bookmark(url: str = Form(...), title: Optional[str] = Form(None)):
    conn = get_db()
    cursor = conn.execute(
        "INSERT INTO bookmarks (url, title) VALUES (?, ?) RETURNING id, url, title",
        (url, title)
    )
    bookmark = Bookmark(**dict(cursor.fetchone()))
    conn.commit()
    conn.close()
    return bookmark

# UI: Homepage
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    conn = get_db()
    cursor = conn.execute("SELECT id, url, title FROM bookmarks")
    bookmarks = cursor.fetchall()
    conn.close()
    return templates.TemplateResponse("index.html", {"request": request, "bookmarks": bookmarks})
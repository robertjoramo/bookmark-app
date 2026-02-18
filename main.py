from fastapi import FastAPI, Request, HTTPException, Form
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
        # Create bookmarks table
        conn.execute("""
        CREATE TABLE IF NOT EXISTS bookmarks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            title TEXT
            )
        """)

        # Create tags table
        conn.execute("""
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL         
            )          
        """)
        

        # Create "bookmarks" - "tags" junction/join table
        conn.execute("""
        CREATE TABLE IF NOT EXISTS bookmark_tags(
            bookmark_id INTEGER NOT NULL,
            tag_id INTEGER NOT NULL,
            PRIMARY KEY (bookmark_id, tag_id)
            FOREIGN KEY (bookmark_id) REFERENCES bookmarks(id) ON DELETE CASCADE,
            FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
            )
        """)

        conn.commit()


init_db()

class Tag(BaseModel):
    id: int
    name: str

class Bookmark(BaseModel):
    id: int
    url: str
    title: Optional[str] = None
    tags: List[Tag] = []


# API: Get all bookmarks
@app.get("/api/bookmarks", response_model=List[Bookmark])
async def get_bookmarks():
    conn = get_db()
    try:
        cursor = conn.execute(
        """
        SELECT b.id, b.url, b.title, t.id as tag_id, t.name as tag_name
        FROM bookmarks b
        LEFT JOIN bookmark_tags bt ON b.id = bt.bookmark_id
        LEFT JOIN tags t on bt.tag_id = t.id
        ORDER BY b.id
        """
        )
        rows = cursor.fetchall()

        # Group bookmarks and their tags
        bookmarks = {}
        for row in rows:
            bookmark_id = row["id"]
            if bookmark_id not in bookmarks:
                bookmarks[bookmark_id] = {
                    "id": bookmark_id,
                    "url": row["url"],
                    "title": row["title"],
                    "tags": [],
                }
            if row["tag_id"]:
                 bookmarks[bookmark_id]["tags"].append({"id": row["tag_id"], "name": row["tag_name"]})
        return list(bookmarks.values())
    finally:
         conn.close

# API: Add a bookmark
@app.post("/api/bookmarks", response_model=Bookmark)
async def add_bookmark(url: str = Form(...), title: Optional[str] = Form(None), tags: List[str] = Form([])):
    conn = get_db()
    try:
        # Insert bookmark
        cursor = conn.execute(
            "INSERT INTO bookmarks (url, title) VALUES (?, ?) RETURNING id, url, title",
            (url, title)
        )
        bookmark = cursor.fetchone()
        bookmark_id = bookmark["id"]

        all_tags = []
        for tag_input in tags:
             all_tags.extend([t.strip() for t in tag_input.split(",")])

        # Insert tags and link them to the bookmark
        for tag_name in all_tags:
            if not tag_name:
                continue
            # Get or create the tag
            tag_cursor = conn.execute(
                  "INSERT INTO tags (name) VALUES (?) ON CONFLICT(name) DO NOTHING RETURNING id, name",
                  (tag_name,),
            )
            tag = tag_cursor.fetchone()

            # If the tag didn't exist, fetch its ID
            if not tag:
                tag_cursor = conn.execute(
                     "SELECT id, name FROM tags WHERE name = ?",
                     (tag_name,),
                )
                tag = tag_cursor.fetchone()
            
            # Link the tag to the bookmark
            conn.execute(
                "INSERT INTO bookmark_tags (bookmark_id, tag_id) VALUES (?, ?)",
                (bookmark_id, tag["id"])
            )
        conn.commit()

        # Fetch the bookmark with its tags
        bookmark_cursor = conn.execute(
            """
            SELECT b.id, b.url, b.title, t.id as tag_id, t.name as tag_name
            FROM bookmarks b
            LEFT JOIN bookmark_tags bt ON b.id = bt.bookmark_id
            LEFT JOIN tags t on bt.tag_id = t.id
            WHERE b.id = ?
            """,
            (bookmark_id,),
        )
        rows = bookmark_cursor.fetchall()

        # Group tags
        bookmark_data = {
             "id": bookmark_id,
             "url": url,
             "title": title,
             "tags": [{"id": row["tag_id"], "name":row["tag_name"]} for row in rows if row["tag_id"]]
        }
        return bookmark_data
    finally:
         conn.close()
            


# API: Delete a bookmark
@app.post("/api/bookmarks/{id}/delete")
async def delete_bookmark(id):
    conn = get_db()
    cursor = conn.execute(
        "DELETE FROM bookmarks WHERE id=?",
        (id)
    )
    conn.commit()
    conn.close()
    return "Done"

# API: Update a bookmark
@app.post("/api/bookmarks/{id}/update")
async def edit_bookmark(id: int, new_title: str = Form(...)):
    conn = get_db()
    cursor = conn.execute(
        "UPDATE bookmarks SET title=? WHERE id=?",
        (new_title, id)
    )
    conn.commit()
    conn.close()
    return "Done"

# UI: Homepage
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    conn = get_db()
    try:
        cursor = conn.execute(
            """
            SELECT b.id, b.url, b.title, t.id as tag_id, t.name as tag_name
            FROM bookmarks b
            LEFT JOIN bookmark_tags bt ON b.id = bt.bookmark_id
            LEFT JOIN tags t ON bt.tag_id = t.id
            ORDER BY b.id
            """
        )
        rows = cursor.fetchall()

        # Gorup bookmarks and their tags
        bookmarks = {}
        for row in rows:
            bookmark_id = row["id"]
            if bookmark_id not in bookmarks:
                bookmarks[bookmark_id] = {
                    "id": bookmark_id,
                    "url": row["url"],
                    "title": row["title"],
                    "tags": [],
                }
            if row["tag_id"]:
                bookmarks[bookmark_id]["tags"].append({"id": row["tag_id"], "name": row["tag_name"]})

        return templates.TemplateResponse("index.html", {"request": request, "bookmarks": list(bookmarks.values())})
    finally:
        conn.close()

# API: Add New tag
@app.post("/api/tags", response_model=Tag)
async def add_tag(name: str = Form(...)):
	conn = get_db()
	try:
		cursor = conn.execute(
			"INSERT INTO tags (name) VALUES (?) RETURNING id, name",
			(name,),
		)
		tag = cursor.fetchone()
		conn.commit()
		return tag
	except sqlite3.IntegrityError:
		raise HTTPException(status_code=400, detail="Tag already exists")
	finally:
		conn.close()
          
# API: Get bookmarks by tag
@app.get("/api/bookmarks/by-tag/{tag_name}", response_model=List[Bookmark])
async def get_bookmark_by_tag(tag_name: str):
     conn = get_db()
     try:
          cursor = conn.execute(
            """
            SELECT b.id, b.url, b.title, t.id as tag_id, t.name as tag_name
            FROM bookmarks b
            JOIN bookmark_tags bt ON b.id = bt.bookmark_id
            JOIN tags t ON bt.tag_id = t.id
            WHERE t.name = ?
            ORDER BY b.id
            """,
            (tag_name,),
          )
          rows = cursor.fetchall()

          # Group bookmarks and their tags
          bookmarks = {}
          for row in rows:
                bookmark_id = row["id"]
                if bookmark_id not in bookmarks:
                    bookmarks[bookmark_id] = {
                        "id": bookmark_id,
                        "url": row["url"],
                        "title": row["title"],
                        "tags": [],
                    }
                bookmarks[bookmark_id]["tags"].append({"id": row["tag_id"], "name": row["tag_name"]})
          return list(bookmarks.values())
     finally:
          conn.close()
import sqlite3
from typing import List, Optional

BOOKMARK_SELECT = """
    SELECT b.id, b.url, b.title, b.favicon,
        t.id AS tag_id, t.name AS tag_name
    FROM bookmarks b
    LEFT JOIN bookmark_tags bt ON b.id = bt.bookmark_id
    LEFT JOIN tags t ON bt.tag_id = t.id
"""

def _rows_to_bookmarks(rows) -> List[dict]:
    bookmarks: dict = {}
    for row in rows:
        bid = row["id"]
        if bid not in bookmarks:
            bookmarks[bid] = {
                "id": bid,
                "url": row["url"],
                "title": row["title"],
                "favicon": row["favicon"],
                "tags": [],
            }
        if row["tag_id"]:
            bookmarks[bid]["tags"].append({"id": row["tag_id"], "name": row["tag_name"]})
    return list(bookmarks.values())

def get_all_bookmarks(conn: sqlite3.Connection) -> List[dict]:
    rows = conn.execute(BOOKMARK_SELECT + " ORDER BY b.id DESC").fetchall()
    return _rows_to_bookmarks(rows)

def get_bookmark_by_id(conn: sqlite3.Connection, bookmark_id: int) -> Optional[dict]:
    rows = conn.execute(BOOKMARK_SELECT + " WHERE b.id = ?", (bookmark_id,)).fetchall()
    results = _rows_to_bookmarks(rows)
    return results[0] if results else None

def get_bookmarks_by_tag(conn: sqlite3.Connection, tag_name: str) -> List[dict]:
    rows = conn.execute(
        BOOKMARK_SELECT + """
        WHERE b.id IN (
            SELECT bt2.bookmark_id
            FROM bookmark_tags bt2
            JOIN tags t2 ON bt2.tag_id = t2.id
            WHERE t2.name = ?
        )
        ORDER BY b.id DESC
        """,
        (tag_name,),
    ).fetchall()
    return _rows_to_bookmarks(rows)

def _get_or_create(conn: sqlite3.Connection, tag_name: str) -> int:
    conn.execute(
        "INSERT INTO tags (name) VALUES (?) ON CONFLICT(name) DO NOTHING",
        (tag_name,),
    )
    row = conn.execute("SELECT id FROM tags WHERE name = ?", (tag_name,)).fetchone()
    return row["id"]

def create_bookmark(
        conn: sqlite3.Connection,
        url: str,
        title: Optional[str],
        favicon: Optional[str],
        tag_names: List[str],
) -> Optional[dict]:
    cursor = conn.execute(
        "INSERT INTO bookmarks (url, title, favicon) VALUES (?, ?, ?) RETURNING id",
        (url, title, favicon),
    )
    bookmark_id = cursor.fetchone()["id"]

    for raw_tag in tag_names:
        for tag_name in raw_tag.split(","):
            tag_name = tag_name.strip()
            if not tag_name:
                continue
            tag_id = _get_or_create(conn, tag_name)
            conn.execute(
                "INSERT OR IGNORE INTO bookmark_tags (bookmark_id, tag_id) VALUES (?, ?)",
                (bookmark_id, tag_id)
            )
    return get_bookmark_by_id(conn, bookmark_id)

def update_bookmark_title(conn: sqlite3.Connection, bookmark_id: int, new_title: str) -> Optional[dict]:
    conn.execute(
        "UPDATE bookmarks SET title = ? WHERE id = ?",
        (new_title, bookmark_id),
    )
    return get_bookmark_by_id(conn, bookmark_id)

def delete_bookmark(conn: sqlite3.Connection, bookmark_id: int) -> bool:
    cursor = conn.execute(
        "DELETE FROM bookmarks WHERE id = ?", (bookmark_id,)
    )
    return cursor.rowcount > 0


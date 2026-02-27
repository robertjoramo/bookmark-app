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

def get_all_bookmarks(conn: sqlite3.Connection, user_id: int) -> List[dict]:
    rows = conn.execute(BOOKMARK_SELECT + " WHERE b.user_id = ? ORDER BY b.id DESC", (user_id,)).fetchall()
    return _rows_to_bookmarks(rows)

def get_bookmark_by_id(conn: sqlite3.Connection, bookmark_id: int, user_id: int) -> Optional[dict]:
    rows = conn.execute(BOOKMARK_SELECT + " WHERE b.id = ? AND b.user_id = ?", (bookmark_id, user_id)).fetchall()
    results = _rows_to_bookmarks(rows)
    return results[0] if results else None

def get_bookmarks_by_tag(conn: sqlite3.Connection, tag_name: str, user_id: int) -> List[dict]:
    rows = conn.execute(
        BOOKMARK_SELECT + """
        WHERE b.id IN (
            SELECT bt2.bookmark_id
            FROM bookmark_tags bt2
            JOIN tags t2 ON bt2.tag_id = t2.id
            WHERE t2.name = ?
        )
        AND b.user_id = ?
        ORDER BY b.id DESC
        """,
        (tag_name, user_id),
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
        user_id: int
) -> Optional[dict]:
    cursor = conn.execute(
        "INSERT INTO bookmarks (url, title, favicon, user_id) VALUES (?, ?, ?, ?) RETURNING id",
        (url, title, favicon, user_id),
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
    return get_bookmark_by_id(conn, bookmark_id, user_id)

def update_bookmark(conn: sqlite3.Connection, bookmark_id: int, new_title: Optional[str], new_url: Optional[str], new_tags: List[str], user_id: int) -> Optional[dict]:
    # Check the user owns this bookmark before changing anything
    existing = get_bookmark_by_id(conn, bookmark_id, user_id)
    if not existing:
        return None
    fields = []
    values = []

    if new_title is not None:
        fields.append("title= ?")
        values.append(new_title)
    
    if new_url is not None:
        fields.append("url = ?")
        values.append(new_url)

    values.append(bookmark_id)
    values.append(user_id)

    if fields:
        sql = f'UPDATE bookmarks SET {", ".join(fields)} WHERE id = ? AND user_id = ?'
        conn.execute(
            sql,
            values,
        )

    # DELETE exisitng tags
    conn.execute(
        "DELETE FROM bookmark_tags WHERE bookmark_id = ?",
        (bookmark_id,)
        )

    # ADD new tags
    for raw_tag in new_tags:
        for tag_name in raw_tag.split(","):
            tag_name = tag_name.strip()
            if not tag_name:
                continue
            tag_id = _get_or_create(conn, tag_name)
            conn.execute(
                "INSERT OR IGNORE INTO bookmark_tags (bookmark_id, tag_id) VALUES (?, ?)",
                (bookmark_id, tag_id)
            )
    return get_bookmark_by_id(conn, bookmark_id, user_id)


def delete_bookmark(conn: sqlite3.Connection, bookmark_id: int, user_id: int) -> bool:
    cursor = conn.execute(
        "DELETE FROM bookmarks WHERE id = ? AND user_id = ?", (bookmark_id, user_id)
    )
    return cursor.rowcount > 0
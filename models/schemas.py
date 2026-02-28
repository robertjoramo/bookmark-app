from pydantic import BaseModel
from typing import Optional, List


# TAGS

class TagBase(BaseModel):
    name: str

class Tag(TagBase):
    id: int

    class Config:
        from_attributes = True

# BOOKMARKS

class BookmarkCreate(BaseModel):
    url: str
    title: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = []

class BookmarkUpdate(BaseModel):
    url: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None


class Bookmark(BaseModel):
    id: int
    url: str
    title: Optional[str] = None
    description: Optional[str] = None
    favicon: Optional[str] = None
    tags: List[Tag] = []

    class Config:
        from_attributes = True
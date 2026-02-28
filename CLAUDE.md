# CLAUDE.md — Bookmark App

This file gives Claude context about the project and how to work with the developer (Robert). Read this at the start of every session.

---

## Project Overview

A lightweight, self-hosted bookmark/link manager for personal use and close family. Inspired primarily by [Linkding](https://github.com/sissbruecker/linkding). The goal is to keep it simple, fast, and easy to self-host.

**Target deployment:** Docker container on an Unraid home server.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI (Python) |
| Templating | Jinja2 |
| Frontend interactivity | HTMX |
| Styling | Custom CSS |
| Database | SQLite |
| Server | Uvicorn |
| Deployment | Docker |

> **Why this stack?** FastAPI is modern, fast, and Python-based (Robert knows Python). HTMX lets us add interactivity without writing a lot of JavaScript. SQLite is perfect for a small, self-hosted app — no separate database server needed.

---

## Planned Features

- [x] Clean, minimal UI (Linkding-inspired)
- [x] Add / edit / delete bookmarks (URL + title + tags)
- [ ] Tag-based organization and filtering
- [ ] Full-text search across bookmarks
- [x] Multi-user support (family members with their own bookmarks)
- [x] Auto-fill title from URL (fetches page title on input, via /api/bookmarks/fetch-metadata)
- [x] Favicon display (Google favicon service, domain extracted via Jinja2 filter)
- [ ] Docker deployment with simple setup
- [x] Description field for bookmarks
- [x] Auto-pull description field from url
- [ ] Notes field for bookmarks
- [ ] Settings page (Colors/Theme, toogle auto-fill title, toggle auto-fill description ++)
- [ ] Account settings page (export / Import feature?, other features?)
- [ ] Sort options of bookmarks (date, title, domain)
- [ ] Duplicate detection. If a bookmark url already exist, inform user
- [ ] Bookmark link checker
- [ ] Admin panel (UI) - Creating users etc.
- [ ] Dark/Light mode
- [ ] Redesign for mobile.
- [ ] Keyboard Shortcuts
- [ ] Tag ordering -> Add Group by tag/url etc

---

## Project Structure

```
bookmark-app/
├── CLAUDE.md                        ← you are here
├── main.py                          # FastAPI app entry point — registers routes, starts the app
├── create_user.py                   # CLI script to create users (run from project root)
├── api/
│   ├── dependencies.py              # Shared dependencies — require_login
│   ├── templates.py                 # Shared Jinja2Templates instance + custom filters (domain)
│   └── endpoints/
│       ├── bookmark.py              # Route handlers for bookmarks
│       └── auth.py                  # Login/logout routes
├── crud/
│   ├── bookmark.py                  # Database logic for bookmarks (all scoped by user_id)
│   └── user.py                      # Database logic for users
├── models/
│   └── schemas.py                   # Pydantic models — define the shape of our data
├── database/
│   └── session.py                   # SQLite connection management
├── templates/
│   ├── index.html                   # Main UI page
│   ├── bookmark_item.html           # Reusable bookmark component (used by HTMX)
│   ├── bookmark_item_edit.html      # Edit form component (used by HTMX)
│   └── login.html                   # Login page
└── static/
    └── style.css                    # All styling
```

---

## How Claude Should Help — IMPORTANT

**This is a learning project first.** Robert's goal is to understand every piece of code, not just have a working app.

### Default mode: Guide & Explain
- Point Robert in the right direction
- Explain the *why* behind decisions, not just the *what*
- Ask Robert to attempt the code himself before providing a solution
- Give hints, not answers — unless he's genuinely stuck

### Pair coding (for complex tasks)
- Claude writes part of the code, Robert writes part
- Claude explains every line he writes — assume nothing is obvious
- Even basic concepts (like what a `dict` is, or why we use a `return` statement) should be explained if they're relevant

### Rules
- **Never** drop a full solution without explanation
- **Always** explain new patterns, libraries, or concepts before using them
- **Assume nothing is obvious** — Robert has hobbyist-level experience with Python, HTML, CSS, and simple JS
- **Encourage attempts** — ask "what do you think this should look like?" before writing code
- **Teach patterns** — when introducing something (like a database query pattern), briefly explain what it is, why it exists, and why we're using it here

---

## Development Conventions

- **Python style**: Follow PEP 8 (clear variable names, spaces not tabs, functions have a single responsibility)
- **Comments**: Add comments to non-obvious code, especially anything Robert didn't write himself
- **Simplicity first**: Prefer readable, simple code over clever one-liners
- **Explain before adding**: Before adding a new dependency or pattern, explain what it does and why we need it

## Session Hygiene

At the end of each session (or when Robert asks), keep these two files in sync:

- **`CLAUDE.md`** (this file) — update the Planned Features checklist and add a dated entry to the Notes & Decisions Log
- **`/home/robert/.claude/projects/-home-robert-bookmark-app/memory/MEMORY.md`** — update completed/planned feature lists and any key architectural notes

Both files serve different purposes: CLAUDE.md is the project record (checked into git, human-readable); MEMORY.md is Claude's working notes across sessions. They should tell the same story.

--- 

## Running the App Locally

```bash
# Activate the virtual environment
source .venv/bin/activate

# Start the development server (auto-reloads on file changes)
uvicorn main:app --reload --host 0.0.0.0
```

Then open your browser at: `http://localhost:8000`

---

## Notes & Decisions Log

> Use this section to log important decisions made during development, so future sessions have context.

- **2026-02-25**: Project started. Stack chosen: FastAPI + HTMX + SQLite + Jinja2. Learning project — Robert writes as much as possible.
- **2026-02-26**: Auth fully completed and tested. Added: users table, user_id on bookmarks, crud/user.py, api/endpoints/auth.py, api/dependencies.py (require_login), login.html, SessionMiddleware, create_user.py. All bookmark routes and crud functions are now scoped by user_id. Logout button added to index.html.
- **2026-02-26**: Dependency notes — bcrypt must be pinned to 4.0.1 (newer versions break passlib). itsdangerous must be installed separately for SessionMiddleware.
- **2026-02-27**: Added auto-fill title from URL. New endpoint GET /api/bookmarks/fetch-title fetches page HTML and extracts the <title> tag using regex (httpx + re). HTMX triggers on `input delay:100ms` from the URL field and swaps the title input via outerHTML. html.escape() used on title to prevent broken HTML attributes.
- **2026-02-27**: Added favicon display using Google's favicon service (https://www.google.com/s2/favicons?domain=...). Domain extracted from URL using a custom Jinja2 filter (`domain`) registered in api/templates.py. Templates instance moved to api/templates.py (shared) to avoid duplicate instances and missing filters across routes. httpx added as a dependency (uv pip install httpx).
- **2026-03-01**: Added description field to bookmarks. DB migration via ALTER TABLE in init_db() wrapped in try/except. Description flows through all layers: DB → CRUD → schemas → API endpoint → templates. Displayed conditionally in bookmark_item.html, editable via textarea in both add form (index.html) and edit form (bookmark_item_edit.html). BookmarkUpdate schema also updated to include url and tags as Optional fields.
- **2026-03-01**: Replaced fetch-title endpoint with fetch-metadata (GET /api/bookmarks/fetch-metadata). Fetches page once, extracts both title (<title> tag) and description (<meta name="description"> content attribute via two-step regex). Returns both fields as HTML. HTMX targets a wrapper div (#metadata-fields) with innerHTML swap, so title and description update together in one request. After form submit, a resetForm() JS function replaces #metadata-fields innerHTML to clear the pre-filled values (form.reset() alone doesn't clear HTMX-injected values since it resets to the injected default).
- **2026-03-01**: CSS simplified significantly. Removed dead selectors (form.add-form, form[action*="update"], etc. — HTMX forms don't use action). Added textarea styling. Bookmark list uses flex-wrap + CSS order to show description on its own row below title/tags without changing HTML.

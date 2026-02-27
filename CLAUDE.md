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
- [x] Auto-fill title from URL (fetches page title on input, via /api/bookmarks/fetch-title)
- [x] Favicon display (Google favicon service, domain extracted via Jinja2 filter)
- [ ] Tag-based organization and filtering
- [ ] Full-text search across bookmarks
- [ ] Docker deployment with simple setup
- [ ] Description and Notes to bookmarks

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

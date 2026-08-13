# Kindling — Lead Management App

**Digital Heroes · Full Stack Development · Task A**

A lead management application a small sales team could actually use: a public capture form, an authenticated app with admin/member roles, a lead pipeline with assignment and notes, a documented JSON API, automated tests, and a live deployment.

## Why "Kindling"
The brief's own words: "many people are working on this exact brief right now." A generic blue-and-slate SaaS dashboard called "LeadFlow" is exactly what that produces at scale. Kindling reframes the pipeline as a spark-to-fire progression — Spark → Warming → Catching → Ablaze / Ash instead of New → Contacted → Qualified → Won / Lost — paired with a warm stone/amber palette and a serif display font (Fraunces) instead of the default all-sans SaaS look. The underlying data model stays plain and functional (the database still just stores `new`/`contacted`/`qualified`/`won`/`lost` — see `models.py`); only the presentation layer carries the theme, so the architecture isn't compromised for the sake of branding.

## Live URL
📍 *[add your deployed URL here]*

**Demo credentials:**
| Role | Email | Password |
|---|---|---|
| Admin | `admin@leadflow.demo` | `AdminDemo123!` |
| Member | `member@leadflow.demo` | `MemberDemo123!` |

## Permission model
This isn't specified beyond "two roles" in the brief, so here's the concrete policy implemented:
- **Admin** — full access to every lead; can assign a lead to any member; can create new user accounts.
- **Member** — can view every lead (team visibility); can only change status or add notes on leads assigned to *them*; can self-claim an unassigned lead, but cannot assign a lead to a different member (only an admin can do that or reassign an already-claimed lead).

## Architecture
- **Backend**: FastAPI, SQLAlchemy, PostgreSQL, JWT auth (python-jose), bcrypt password hashing.
  - `routers/` — thin controllers only (parse → call a service → return).
  - `services/` — all business logic and permission rules, unit-tested with no HTTP server involved.
  - `models.py` — User, Lead, Note, ActivityLog. Every status/assignment/note change writes an `ActivityLog` row automatically.
- **Frontend**: React, Redux Toolkit (auth session), React Router, Tailwind CSS.

## API reference

| Endpoint | Method | Auth | Purpose |
|---|---|---|---|
| `/api/public/leads` | POST | None | Public lead capture form |
| `/api/auth/login` | POST | None | Returns a JWT + role |
| `/api/users` | POST | Admin | Create a member/admin account |
| `/api/users` | GET | Any | List users (for the assign dropdown) |
| `/api/leads` | GET | Any | Paginated, filterable list — `?status=&assigned_to_id=&search=&page=&page_size=` |
| `/api/leads/{id}` | GET | Any | Lead detail incl. notes + activity trail |
| `/api/leads/{id}/status` | PATCH | Any* | Change status (*only if assigned to you, or admin) |
| `/api/leads/{id}/assign` | PATCH | Any* | Assign/self-claim (*members can only self-claim unassigned leads) |
| `/api/leads/{id}/notes` | POST | Any* | Add a note (*only if assigned to you, or admin) |

All list/detail responses return proper status codes: `200` success, `201` created, `401` no/invalid token, `403` permission denied, `404` not found, `422` validation error.

## Local setup

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

python -m pip install -r requirements.txt
```

Create `.env`:
```env
DATABASE_URL=postgresql://<user>:<password>@localhost:5432/leadflow_db
JWT_SECRET_KEY=<any long random string>
ALLOWED_ORIGINS=http://localhost:5173
```

```bash
createdb leadflow_db
python -m uvicorn app.main:app --reload --port 8000
python seed.py   # creates demo admin + member accounts
```

### Frontend
```bash
cd frontend
npm install
```
Create `.env`: 
```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

```bash
npm run dev
```

### Tests
```bash
cd backend
JWT_SECRET_KEY=test-key python -m pytest tests/ -v
```
14 tests: auth rules (login success/failure, protected-route rejection, admin-only user creation) and 2+ core flows (public capture → appears in list; the full member self-claim/status/notes permission workflow). Tests run against an in-memory SQLite database — no external DB needed to run them.

## Deployment (free tier)

**Backend + Postgres — Render:**
1. Push this repo to GitHub.
2. On [render.com](https://render.com): New → PostgreSQL (free tier) → note the connection string.
3. New → Web Service → connect the repo, root directory `backend`, build command `pip install -r requirements.txt`, start command `python seed.py && uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
4. Environment variables: `DATABASE_URL` (from step 2), `JWT_SECRET_KEY` (generate one), `ALLOWED_ORIGINS` (your frontend URL, added after step below).

**Frontend — Vercel or Netlify:**
1. Import the repo, root directory `frontend`, build command `npm run build`, output directory `dist`.
2. Environment variable: `VITE_API_BASE_URL` = your Render backend URL.
3. Once deployed, go back to the Render backend and set `ALLOWED_ORIGINS` to this frontend URL, then redeploy the backend.

## Note on AI usage
I used Claude to help design the permission model, scaffold the FastAPI/React code, and write the test suite. Writing the tests actually caught a real bug — a UUID stored as a string was being compared against a UUID object from the request schema, which silently broke the "member self-claims a lead" permission check. I fixed that myself once the failing test pointed at it. The specific permission rules (what exactly "member" can and can't do) were a judgment call I made and documented above, since the brief only said "two roles" without specifying the boundary.

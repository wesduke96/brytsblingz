# Bryt Piercing Studio

A booking and client management web app for Bryt's piercing services.

**Live site**: [bryt.nullroute.studio](https://bryt.nullroute.studio)
**Repository**: [github.com/wesduke96/brytsblingz](https://github.com/wesduke96/brytsblingz)

---

## Infrastructure

| Service | Details |
|---|---|
| **Domain** | `bryt.nullroute.studio` (via Squarespace / nullroute.studio) |
| **Hosting** | Railway — auto-deploys from `master` branch on GitHub |
| **Repository** | GitHub — `wesduke96/brytsblingz` |
| **Business email** | Google Workspace — `@nullroute.studio` |
| **Database** | SQLite (persisted on Railway) |

### Deployment Flow

Every push to `master` on GitHub triggers an automatic redeploy on Railway. No manual steps needed.

```
local dev → git push → GitHub → Railway auto-deploy → bryt.nullroute.studio
```

---

## Tech Stack

- **Backend**: FastAPI (Python 3.13)
- **Templates**: Jinja2
- **Styling**: Tailwind CSS (via CDN)
- **Database**: SQLite + SQLAlchemy (async) + aiosqlite + greenlet
- **Interactivity**: HTMX

---

## Local Development

### Prerequisites

- Python 3.10+
- pip

### Setup

```bash
# Clone the repo
git clone https://github.com/wesduke96/brytsblingz.git
cd brytsblingz

# Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Run the dev server
cd src
python main.py
# → http://127.0.0.1:8000
```

---

## Project Structure

```
bryt/
├── src/
│   ├── main.py              # FastAPI app entry point
│   ├── create_admin.py      # Script to create admin user
│   ├── seed_data.py         # Script to seed initial data
│   ├── routes/
│   │   ├── pages.py         # Public page routes (GET)
│   │   ├── api.py           # HTMX form endpoints (POST)
│   │   └── admin.py         # Admin dashboard (auth-gated)
│   ├── db/
│   │   ├── database.py      # Engine, session factory, init_db()
│   │   └── models.py        # SQLAlchemy models
│   ├── templates/
│   │   ├── base.html        # Base layout with nav
│   │   ├── pages/           # Full page templates
│   │   │   └── admin/       # Admin-only templates
│   │   └── components/      # Reusable HTMX partials
│   └── static/
│       └── images/          # Bryt photos + client gallery
├── railway.json             # Railway deployment config
├── requirements.txt
└── README.md
```

---

## Pages

### Public
| Route | Page |
|---|---|
| `/` | Home |
| `/services` | Services & pricing |
| `/booking` | Appointment booking form |
| `/shop` | Ear Creations shop |
| `/aftercare` | Aftercare guide |
| `/contact` | Contact form & FAQ |

### Admin (auth-gated)
| Route | Page |
|---|---|
| `/admin` | Dashboard overview |
| `/admin/appointments` | Manage appointments |
| `/admin/clients` | Client management |
| `/admin/services` | Service management |

---

## Design

**Aesthetic**: Dark, editorial, gothic-feminine
**Colors**: Monochromatic black & white with pink/red accents
**Typography**:
- Pinyon Script — logo / decorative
- Cormorant Garamond — headings
- Questrial — body text

---

## TODO

- [ ] Connect Ear Creations to actual products
- [ ] Set up email notifications for bookings
- [ ] Add calendar integration
- [ ] Persistent database volume on Railway (SQLite survives redeploys)

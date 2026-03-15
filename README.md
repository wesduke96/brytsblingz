# Bryt Piercing Studio

A booking and client management web application for Bryt's piercing services.

## Features

- **Services Showcase** - Display piercing services with pricing
- **Appointment Booking** - Clients can request appointments online
- **Ear Creations Shop** - Product showcase with Amazon storefront link
- **Admin Dashboard** - Manage appointments, clients, and services
- **Client Management** - Track client history and notes

## Tech Stack

- **Backend**: FastAPI (Python)
- **Templates**: Jinja2
- **Styling**: Tailwind CSS (via CDN)
- **Database**: SQLite + SQLAlchemy (async)
- **Interactivity**: HTMX

## Getting Started

### Prerequisites

- Python 3.10+
- pip

### Installation

1. Navigate to the project directory:
   ```bash
   cd C:\Users\wes.duke\Desktop\bryt
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the development server:
   ```bash
   cd src
   python main.py
   ```

5. Open your browser to: **http://127.0.0.1:8000**

## Project Structure

```
bryt/
├── src/
│   ├── main.py              # FastAPI application entry point
│   ├── routes/
│   │   ├── pages.py         # Public page routes
│   │   ├── api.py           # API endpoints
│   │   └── admin.py         # Admin dashboard routes
│   ├── templates/
│   │   ├── base.html        # Base template with navigation
│   │   ├── pages/           # Page templates
│   │   │   ├── home.html
│   │   │   ├── services.html
│   │   │   ├── booking.html
│   │   │   ├── shop.html
│   │   │   ├── contact.html
│   │   │   └── admin/       # Admin templates
│   │   └── components/      # Reusable components
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   └── db/
│       ├── database.py      # Database configuration
│       └── models.py        # SQLAlchemy models
├── style_reference/         # Design inspiration & assets
├── requirements.txt
└── README.md
```

## Pages

### Public
- `/` - Home page
- `/services` - Services & pricing
- `/booking` - Appointment booking form
- `/shop` - Ear Creations shop
- `/contact` - Contact form & FAQ

### Admin
- `/admin` - Dashboard overview
- `/admin/appointments` - Manage appointments
- `/admin/clients` - Client management
- `/admin/services` - Service management

## Design

**Aesthetic**: Clean, modern, feminine with comforting touches
**Colors**: Monochromatic (black & white)
**Typography**: 
- Pinyon Script (elegant script for logo)
- Cormorant Garamond (refined serif for headings)
- Questrial (clean sans-serif for body)

See `style_reference/` for design assets and inspiration.

## Development Notes

This is a local playground project - not version controlled.

### TODO
- [ ] Implement full CRUD for appointments
- [ ] Add authentication for admin area
- [ ] Connect Ear Creations to actual products
- [ ] Set up email notifications for bookings
- [ ] Add calendar integration


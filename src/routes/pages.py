"""
Public-facing page routes
"""

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from pathlib import Path
from collections import OrderedDict
from sqlalchemy import select

from db.database import async_session
from db.models import Service

router = APIRouter(tags=["pages"])

templates = Jinja2Templates(directory=Path(__file__).resolve().parent.parent / "templates")


@router.get("/")
async def home(request: Request):
    """Home page"""
    return templates.TemplateResponse("pages/home.html", {
        "request": request,
        "title": "Bryt's Blingz | Piercing Stylist"
    })


@router.get("/services")
async def services(request: Request):
    """Services page - showcase piercing offerings"""
    
    async with async_session() as session:
        result = await session.execute(
            select(Service).where(Service.is_active == True).order_by(Service.price)
        )
        all_services = result.scalars().all()
    
    # Group by category in desired order
    category_order = ["Ear", "Nose", "Face", "Oral", "Body", "Surface", "Other"]
    services_by_category = OrderedDict()
    
    for category in category_order:
        category_services = [s for s in all_services if s.category == category]
        if category_services:
            services_by_category[category] = category_services
    
    return templates.TemplateResponse("pages/services.html", {
        "request": request,
        "title": "Services | Bryt's Blingz",
        "services_by_category": services_by_category
    })


@router.get("/booking")
async def booking(request: Request):
    """Appointment booking page"""
    
    async with async_session() as session:
        result = await session.execute(
            select(Service).where(Service.is_active == True).order_by(Service.name)
        )
        all_services = result.scalars().all()
    
    # Group by category in desired order
    category_order = ["Ear", "Nose", "Face", "Oral", "Body", "Surface", "Other"]
    services_by_category = OrderedDict()
    
    for category in category_order:
        category_services = [s for s in all_services if s.category == category]
        if category_services:
            services_by_category[category] = category_services
    
    return templates.TemplateResponse("pages/booking.html", {
        "request": request,
        "title": "Book an Appointment | Bryt's Blingz",
        "services_by_category": services_by_category
    })


@router.get("/shop")
async def shop(request: Request):
    """Curations shop page"""
    return templates.TemplateResponse("pages/shop.html", {
        "request": request,
        "title": "Curations | Bryt's Blingz"
    })


@router.get("/aftercare")
async def aftercare(request: Request):
    """Aftercare guide page"""
    return templates.TemplateResponse("pages/aftercare.html", {
        "request": request,
        "title": "Aftercare Guide | Bryt's Blingz"
    })


@router.get("/contact")
async def contact(request: Request):
    """Contact page"""
    return templates.TemplateResponse("pages/contact.html", {
        "request": request,
        "title": "Contact | Bryt's Blingz"
    })


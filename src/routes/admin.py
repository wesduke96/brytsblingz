"""
Admin dashboard routes with authentication
"""

from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from sqlalchemy import select, func, delete, or_
from sqlalchemy.orm import selectinload
from datetime import date, timedelta, datetime, time as time_type, timezone
from typing import Optional
import secrets
import bcrypt

from db.database import async_session
from db.models import Client, Service, Appointment, ContactMessage, CurationRequest, AdminUser, AdminSession

router = APIRouter(tags=["admin"])

templates = Jinja2Templates(directory=Path(__file__).resolve().parent.parent / "templates")

SESSION_TTL_HOURS = 24


async def verify_admin(request: Request) -> bool:
    """Check if the request carries a valid, non-expired session token."""
    token = request.cookies.get("admin_session")
    if not token:
        return False
    async with async_session() as session:
        now = datetime.now(timezone.utc)
        row = (await session.execute(
            select(AdminSession).where(
                AdminSession.token == token,
                AdminSession.expires_at > now,
            )
        )).scalar_one_or_none()
        return row is not None


@router.get("/login")
async def admin_login_page(request: Request):
    """Admin login page"""
    if await verify_admin(request):
        return RedirectResponse(url="/admin", status_code=302)
    return templates.TemplateResponse("pages/admin/login.html", {
        "request": request,
        "title": "Admin Login | Bryt's Blingz",
        "error": None
    })


@router.post("/login")
async def admin_login(request: Request, password: str = Form(...)):
    """Handle admin login"""
    async with async_session() as session:
        user = (await session.execute(
            select(AdminUser).where(AdminUser.username == "admin")
        )).scalar_one_or_none()

        if not user or not bcrypt.checkpw(password.encode(), user.password_hash.encode()):
            return templates.TemplateResponse("pages/admin/login.html", {
                "request": request,
                "title": "Admin Login | Bryt's Blingz",
                "error": "Invalid password"
            })

        # Purge expired sessions, then create a new one
        now = datetime.now(timezone.utc)
        await session.execute(delete(AdminSession).where(AdminSession.expires_at <= now))
        token = secrets.token_hex(32)
        session.add(AdminSession(
            token=token,
            expires_at=now + timedelta(hours=SESSION_TTL_HOURS),
        ))
        await session.commit()

    response = RedirectResponse(url="/admin", status_code=302)
    response.set_cookie(key="admin_session", value=token, httponly=True, max_age=60 * 60 * SESSION_TTL_HOURS)
    return response


@router.get("/logout")
async def admin_logout(request: Request):
    """Handle admin logout"""
    token = request.cookies.get("admin_session")
    if token:
        async with async_session() as session:
            await session.execute(delete(AdminSession).where(AdminSession.token == token))
            await session.commit()
    response = RedirectResponse(url="/admin/login", status_code=302)
    response.delete_cookie("admin_session")
    return response


@router.get("/")
async def admin_dashboard(request: Request):
    """Admin dashboard home"""
    if not await verify_admin(request):
        return RedirectResponse(url="/admin/login", status_code=302)
    
    async with async_session() as session:
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        
        # Get stats
        pending_count = await session.scalar(
            select(func.count(Appointment.id)).where(Appointment.status == "pending")
        )
        
        today_count = await session.scalar(
            select(func.count(Appointment.id)).where(Appointment.appointment_date == today)
        )
        
        total_clients = await session.scalar(select(func.count(Client.id)))
        
        # Calculate this week's revenue (from completed appointments)
        week_appointments = await session.execute(
            select(Appointment)
            .options(selectinload(Appointment.service))
            .where(
                Appointment.appointment_date >= week_start,
                Appointment.status == "completed"
            )
        )
        week_revenue = sum(apt.total_price for apt in week_appointments.scalars().all())

        # Unread inbox count
        unread_contact = await session.scalar(
            select(func.count(ContactMessage.id)).where(ContactMessage.is_read == False)
        )
        unread_curations = await session.scalar(
            select(func.count(CurationRequest.id)).where(CurationRequest.is_read == False)
        )

        # Get recent appointments
        recent_result = await session.execute(
            select(Appointment)
            .options(selectinload(Appointment.client), selectinload(Appointment.service))
            .where(Appointment.appointment_date >= today)
            .order_by(Appointment.appointment_date, Appointment.appointment_time)
            .limit(5)
        )
        recent_appointments = recent_result.scalars().all()

        stats = {
            "pending_appointments": pending_count or 0,
            "today_appointments": today_count or 0,
            "total_clients": total_clients or 0,
            "this_week_revenue": int(week_revenue),
            "unread_messages": (unread_contact or 0) + (unread_curations or 0),
        }
    
    return templates.TemplateResponse("pages/admin/dashboard.html", {
        "request": request,
        "title": "Admin Dashboard | Bryt Piercing Studio",
        "stats": stats,
        "recent_appointments": recent_appointments
    })


@router.get("/appointments")
async def admin_appointments(request: Request, status: str = None):
    """Manage appointments"""
    if not await verify_admin(request):
        return RedirectResponse(url="/admin/login", status_code=302)
    
    async with async_session() as session:
        query = select(Appointment).options(
            selectinload(Appointment.client),
            selectinload(Appointment.service)
        ).order_by(Appointment.appointment_date.desc(), Appointment.appointment_time.desc())
        
        if status:
            query = query.where(Appointment.status == status)
        
        result = await session.execute(query)
        appointments = result.scalars().all()
        
        # Get counts for filters
        all_count = await session.scalar(select(func.count(Appointment.id)))
        pending_count = await session.scalar(
            select(func.count(Appointment.id)).where(Appointment.status == "pending")
        )
        confirmed_count = await session.scalar(
            select(func.count(Appointment.id)).where(Appointment.status == "confirmed")
        )
        completed_count = await session.scalar(
            select(func.count(Appointment.id)).where(Appointment.status == "completed")
        )
        cancelled_count = await session.scalar(
            select(func.count(Appointment.id)).where(Appointment.status == "cancelled")
        )
    
    return templates.TemplateResponse("pages/admin/appointments.html", {
        "request": request,
        "title": "Appointments | Admin",
        "appointments": appointments,
        "current_filter": status,
        "counts": {
            "all": all_count or 0,
            "pending": pending_count or 0,
            "confirmed": confirmed_count or 0,
            "completed": completed_count or 0,
            "cancelled": cancelled_count or 0
        }
    })


@router.get("/clients")
async def admin_clients(request: Request):
    """Manage clients"""
    if not await verify_admin(request):
        return RedirectResponse(url="/admin/login", status_code=302)
    
    async with async_session() as session:
        result = await session.execute(
            select(Client).order_by(Client.created_at.desc())
        )
        clients = result.scalars().all()
    
    return templates.TemplateResponse("pages/admin/clients.html", {
        "request": request,
        "title": "Clients | Admin",
        "clients": clients
    })


@router.get("/services")
async def admin_services(request: Request):
    """Manage services"""
    if not await verify_admin(request):
        return RedirectResponse(url="/admin/login", status_code=302)

    async with async_session() as session:
        result = await session.execute(
            select(Service).order_by(Service.category, Service.name)
        )
        services = result.scalars().all()

    return templates.TemplateResponse("pages/admin/services.html", {
        "request": request,
        "title": "Services | Admin",
        "services": services
    })


# ── Appointment CRUD ──────────────────────────────────────────────────────────

@router.post("/appointments/{apt_id}/status")
async def update_appointment_status(request: Request, apt_id: int, status: str = Form(...)):
    """Update appointment status (confirm / complete / cancel)"""
    if not await verify_admin(request):
        return HTMLResponse("Unauthorized", status_code=401)

    valid_statuses = {"pending", "confirmed", "completed", "cancelled"}
    if status not in valid_statuses:
        return HTMLResponse("Invalid status", status_code=400)

    async with async_session() as session:
        result = await session.execute(
            select(Appointment)
            .options(selectinload(Appointment.client), selectinload(Appointment.service))
            .where(Appointment.id == apt_id)
        )
        apt = result.scalar_one_or_none()
        if not apt:
            return HTMLResponse("Appointment not found", status_code=404)

        apt.status = status
        await session.commit()
        await session.refresh(apt)

    # Return updated row HTML for HTMX swap
    return templates.TemplateResponse("components/admin/appointment_row.html", {
        "request": request,
        "apt": apt,
    })


@router.delete("/appointments/{apt_id}")
async def delete_appointment(request: Request, apt_id: int):
    """Delete an appointment"""
    if not await verify_admin(request):
        return HTMLResponse("Unauthorized", status_code=401)

    async with async_session() as session:
        result = await session.execute(select(Appointment).where(Appointment.id == apt_id))
        apt = result.scalar_one_or_none()
        if not apt:
            return HTMLResponse("Not found", status_code=404)

        await session.delete(apt)
        await session.commit()

    # Return empty string — HTMX will swap the row out
    return HTMLResponse("")


@router.get("/appointments/{apt_id}/edit")
async def appointment_edit_form(request: Request, apt_id: int):
    """Return edit form HTML fragment for an appointment"""
    if not await verify_admin(request):
        return HTMLResponse("Unauthorized", status_code=401)

    async with async_session() as session:
        result = await session.execute(
            select(Appointment)
            .options(selectinload(Appointment.client), selectinload(Appointment.service))
            .where(Appointment.id == apt_id)
        )
        apt = result.scalar_one_or_none()
        if not apt:
            return HTMLResponse("Not found", status_code=404)

        services_result = await session.execute(select(Service).where(Service.is_active == True).order_by(Service.name))
        services = services_result.scalars().all()

    return templates.TemplateResponse("components/admin/appointment_edit.html", {
        "request": request,
        "apt": apt,
        "services": services,
    })


@router.post("/appointments/{apt_id}/edit")
async def update_appointment(
    request: Request,
    apt_id: int,
    service_id: int = Form(...),
    appointment_date: str = Form(...),
    appointment_time: str = Form(...),
    quantity: int = Form(1),
    notes: Optional[str] = Form(None),
):
    """Save edits to an appointment"""
    if not await verify_admin(request):
        return HTMLResponse("Unauthorized", status_code=401)

    async with async_session() as session:
        result = await session.execute(
            select(Appointment)
            .options(selectinload(Appointment.client), selectinload(Appointment.service))
            .where(Appointment.id == apt_id)
        )
        apt = result.scalar_one_or_none()
        if not apt:
            return HTMLResponse("Not found", status_code=404)

        try:
            apt.appointment_date = datetime.strptime(appointment_date, "%Y-%m-%d").date()
        except ValueError:
            return HTMLResponse(
                '<p class="text-red-400 text-sm p-2">Invalid date format.</p>', status_code=400
            )

        try:
            hour, minute = map(int, appointment_time.split(":"))
            apt.appointment_time = time_type(hour, minute)
        except (ValueError, AttributeError):
            return HTMLResponse(
                '<p class="text-red-400 text-sm p-2">Invalid time format.</p>', status_code=400
            )

        apt.service_id = service_id
        apt.quantity = quantity
        apt.notes = notes or ""
        await session.commit()
        await session.refresh(apt)

        # Re-fetch with relationships for the row render
        result2 = await session.execute(
            select(Appointment)
            .options(selectinload(Appointment.client), selectinload(Appointment.service))
            .where(Appointment.id == apt_id)
        )
        apt = result2.scalar_one()

    return templates.TemplateResponse("components/admin/appointment_row.html", {
        "request": request,
        "apt": apt,
    })


# ── Inbox ─────────────────────────────────────────────────────────────────────

@router.get("/messages")
async def admin_messages(request: Request):
    """Admin inbox — contact messages and curation requests"""
    if not await verify_admin(request):
        return RedirectResponse(url="/admin/login", status_code=302)

    async with async_session() as session:
        contact_result = await session.execute(
            select(ContactMessage).order_by(ContactMessage.is_read, ContactMessage.created_at.desc())
        )
        contact_messages = contact_result.scalars().all()

        curation_result = await session.execute(
            select(CurationRequest).order_by(CurationRequest.is_read, CurationRequest.created_at.desc())
        )
        curations = curation_result.scalars().all()

        contact_unread = sum(1 for m in contact_messages if not m.is_read)
        curation_unread = sum(1 for c in curations if not c.is_read)

    return templates.TemplateResponse("pages/admin/messages.html", {
        "request": request,
        "title": "Inbox | Admin",
        "contact_messages": contact_messages,
        "curations": curations,
        "contact_unread": contact_unread,
        "curation_unread": curation_unread,
    })


@router.post("/messages/{msg_id}/read")
async def mark_message_read(request: Request, msg_id: int):
    """Mark a contact message as read — returns updated row HTML"""
    if not await verify_admin(request):
        return HTMLResponse("Unauthorized", status_code=401)

    async with async_session() as session:
        msg = (await session.execute(
            select(ContactMessage).where(ContactMessage.id == msg_id)
        )).scalar_one_or_none()
        if not msg:
            return HTMLResponse("Not found", status_code=404)
        msg.is_read = True
        await session.commit()
        await session.refresh(msg)

    return HTMLResponse(content=f"""
        <div id="contact-{msg.id}" class="p-5 border border-bryt-charcoal bg-bryt-charcoal/10 transition-colors">
            <div class="flex items-start justify-between gap-4">
                <div class="flex-1 min-w-0">
                    <p class="text-bryt-white font-medium mb-1">{msg.name}</p>
                    <p class="text-sm text-bryt-silver mb-2">{msg.email}</p>
                </div>
                <div class="flex flex-col items-end gap-3 flex-shrink-0">
                    <p class="text-xs text-bryt-gray">{msg.created_at.strftime('%b %d, %Y') if msg.created_at else ''}</p>
                    <span class="text-xs text-bryt-gray">Read</span>
                </div>
            </div>
            <div class="mt-3 pt-3 border-t border-bryt-charcoal/50">
                <p class="text-sm text-bryt-pearl whitespace-pre-wrap">{msg.message}</p>
            </div>
        </div>
    """)


@router.post("/curations/{req_id}/read")
async def mark_curation_read(request: Request, req_id: int):
    """Mark a curation request as read — returns updated row HTML"""
    if not await verify_admin(request):
        return HTMLResponse("Unauthorized", status_code=401)

    async with async_session() as session:
        req = (await session.execute(
            select(CurationRequest).where(CurationRequest.id == req_id)
        )).scalar_one_or_none()
        if not req:
            return HTMLResponse("Not found", status_code=404)
        req.is_read = True
        await session.commit()
        await session.refresh(req)

    notes_html = f"""
        <div class="mt-3 pt-3 border-t border-bryt-charcoal/50">
            <p class="text-sm text-bryt-pearl whitespace-pre-wrap">{req.notes}</p>
        </div>
    """ if req.notes else ""

    socials_part = f" &middot; {req.socials}" if req.socials else ""

    return HTMLResponse(content=f"""
        <div id="curation-{req.id}" class="p-5 border border-bryt-charcoal bg-bryt-charcoal/10 transition-colors">
            <div class="flex items-start justify-between gap-4">
                <div class="flex-1 min-w-0">
                    <p class="text-bryt-white font-medium mb-1">{req.name}</p>
                    <p class="text-sm text-bryt-silver mb-2">{req.email}{socials_part}</p>
                    <div class="flex gap-4 text-xs">
                        <span class="text-bryt-gray">Area: <span class="text-bryt-pearl capitalize">{req.area}</span></span>
                        <span class="text-bryt-gray">Metal: <span class="text-bryt-pearl capitalize">{req.metal}</span></span>
                    </div>
                </div>
                <div class="flex flex-col items-end gap-3 flex-shrink-0">
                    <p class="text-xs text-bryt-gray">{req.created_at.strftime('%b %d, %Y') if req.created_at else ''}</p>
                    <span class="text-xs text-bryt-gray">Read</span>
                </div>
            </div>
            {notes_html}
        </div>
    """)


# ── Client CRUD ───────────────────────────────────────────────────────────────

@router.get("/clients")
async def admin_clients(request: Request, q: Optional[str] = None):
    """List / search clients"""
    if not await verify_admin(request):
        return RedirectResponse(url="/admin/login", status_code=302)

    async with async_session() as session:
        query = select(Client).order_by(Client.created_at.desc())
        if q:
            like = f"%{q}%"
            query = query.where(or_(Client.name.ilike(like), Client.email.ilike(like)))
        result = await session.execute(query)
        clients = result.scalars().all()

    # HTMX partial — return only the list fragment when hx-target is #clientsList
    if request.headers.get("HX-Target") == "clientsList":
        content = ""
        for client in clients:
            rendered = templates.get_template("components/admin/client_row.html").render(
                {"client": client, "request": request}
            )
            content += rendered
        if not clients:
            no_result_msg = f'No results for "{q}".' if q else "No clients yet."
            content = f"""
            <div class="border border-bryt-charcoal">
                <div class="p-12 text-center">
                    <p class="text-bryt-white text-lg mb-2">No clients found</p>
                    <p class="text-bryt-silver text-sm">{no_result_msg}</p>
                </div>
            </div>"""
        else:
            content += f'<div class="mt-2 text-center text-sm text-bryt-gray">Showing {len(clients)} client{"s" if len(clients) != 1 else ""}</div>'
        return HTMLResponse(content)

    return templates.TemplateResponse("pages/admin/clients.html", {
        "request": request,
        "title": "Clients | Admin",
        "clients": clients,
        "q": q or "",
    })


@router.get("/clients/new")
async def admin_client_new_form(request: Request):
    """Return the add-client form fragment"""
    if not await verify_admin(request):
        return HTMLResponse("Unauthorized", status_code=401)
    return templates.TemplateResponse("components/admin/client_new.html", {"request": request})


@router.post("/clients/new")
async def admin_client_create(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    phone: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
):
    """Create a new client — returns new row fragment"""
    if not await verify_admin(request):
        return HTMLResponse("Unauthorized", status_code=401)

    async with async_session() as session:
        existing = (await session.execute(
            select(Client).where(Client.email == email)
        )).scalar_one_or_none()
        if existing:
            return HTMLResponse(
                '<p class="text-red-400 text-sm p-2">A client with that email already exists.</p>',
                status_code=400
            )
        client = Client(name=name, email=email, phone=phone or "", notes=notes or "")
        session.add(client)
        await session.commit()
        await session.refresh(client)

    return templates.TemplateResponse("components/admin/client_row.html", {
        "request": request,
        "client": client,
    })


@router.get("/clients/{client_id}/edit")
async def admin_client_edit_form(request: Request, client_id: int):
    """Return edit form fragment for a client"""
    if not await verify_admin(request):
        return HTMLResponse("Unauthorized", status_code=401)

    async with async_session() as session:
        client = (await session.execute(
            select(Client).where(Client.id == client_id)
        )).scalar_one_or_none()
        if not client:
            return HTMLResponse("Not found", status_code=404)

    return templates.TemplateResponse("components/admin/client_edit.html", {
        "request": request,
        "client": client,
    })


@router.get("/clients/{client_id}/cancel-edit")
async def admin_client_cancel_edit(request: Request, client_id: int):
    """Clear the inline edit zone"""
    if not await verify_admin(request):
        return HTMLResponse("Unauthorized", status_code=401)
    return HTMLResponse("")


@router.post("/clients/{client_id}/edit")
async def admin_client_update(
    request: Request,
    client_id: int,
    name: str = Form(...),
    email: str = Form(...),
    phone: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
):
    """Save client edits — returns updated row fragment"""
    if not await verify_admin(request):
        return HTMLResponse("Unauthorized", status_code=401)

    async with async_session() as session:
        client = (await session.execute(
            select(Client).where(Client.id == client_id)
        )).scalar_one_or_none()
        if not client:
            return HTMLResponse("Not found", status_code=404)

        client.name = name
        client.email = email
        client.phone = phone or ""
        client.notes = notes or ""
        await session.commit()
        await session.refresh(client)

    return templates.TemplateResponse("components/admin/client_row.html", {
        "request": request,
        "client": client,
    })


@router.delete("/clients/{client_id}")
async def admin_client_delete(request: Request, client_id: int):
    """Delete a client"""
    if not await verify_admin(request):
        return HTMLResponse("Unauthorized", status_code=401)

    async with async_session() as session:
        client = (await session.execute(
            select(Client).where(Client.id == client_id)
        )).scalar_one_or_none()
        if not client:
            return HTMLResponse("Not found", status_code=404)
        await session.delete(client)
        await session.commit()

    return HTMLResponse("")


# ── Service CRUD ──────────────────────────────────────────────────────────────

@router.get("/services/new")
async def admin_service_new_form(request: Request):
    """Return the add-service form fragment"""
    if not await verify_admin(request):
        return HTMLResponse("Unauthorized", status_code=401)
    return templates.TemplateResponse("components/admin/service_new.html", {"request": request})


@router.post("/services/new")
async def admin_service_create(
    request: Request,
    name: str = Form(...),
    category: str = Form("Ear"),
    description: Optional[str] = Form(None),
    price: float = Form(...),
    pair_price: Optional[float] = Form(None),
    duration_minutes: int = Form(30),
    image_url: Optional[str] = Form(None),
    is_active: Optional[str] = Form(None),
):
    """Create a new service — returns new row fragment"""
    if not await verify_admin(request):
        return HTMLResponse("Unauthorized", status_code=401)

    async with async_session() as session:
        service = Service(
            name=name,
            category=category,
            description=description or "",
            price=price,
            pair_price=pair_price if pair_price else None,
            duration_minutes=duration_minutes,
            image_url=image_url or "",
            is_active=is_active == "1",
        )
        session.add(service)
        await session.commit()
        await session.refresh(service)

    return templates.TemplateResponse("components/admin/service_row.html", {
        "request": request,
        "service": service,
    })


@router.get("/services/{service_id}/edit")
async def admin_service_edit_form(request: Request, service_id: int):
    """Return edit form fragment for a service"""
    if not await verify_admin(request):
        return HTMLResponse("Unauthorized", status_code=401)

    async with async_session() as session:
        service = (await session.execute(
            select(Service).where(Service.id == service_id)
        )).scalar_one_or_none()
        if not service:
            return HTMLResponse("Not found", status_code=404)

    return templates.TemplateResponse("components/admin/service_edit.html", {
        "request": request,
        "service": service,
    })


@router.get("/services/{service_id}/cancel-edit")
async def admin_service_cancel_edit(request: Request, service_id: int):
    """Clear the inline edit zone"""
    if not await verify_admin(request):
        return HTMLResponse("Unauthorized", status_code=401)
    return HTMLResponse("")


@router.post("/services/{service_id}/edit")
async def admin_service_update(
    request: Request,
    service_id: int,
    name: str = Form(...),
    category: str = Form("Ear"),
    description: Optional[str] = Form(None),
    price: float = Form(...),
    pair_price: Optional[float] = Form(None),
    duration_minutes: int = Form(30),
    image_url: Optional[str] = Form(None),
    is_active: Optional[str] = Form(None),
):
    """Save service edits — returns updated row fragment"""
    if not await verify_admin(request):
        return HTMLResponse("Unauthorized", status_code=401)

    async with async_session() as session:
        service = (await session.execute(
            select(Service).where(Service.id == service_id)
        )).scalar_one_or_none()
        if not service:
            return HTMLResponse("Not found", status_code=404)

        service.name = name
        service.category = category
        service.description = description or ""
        service.price = price
        service.pair_price = pair_price if pair_price else None
        service.duration_minutes = duration_minutes
        service.image_url = image_url or ""
        service.is_active = is_active == "1"
        await session.commit()
        await session.refresh(service)

    return templates.TemplateResponse("components/admin/service_row.html", {
        "request": request,
        "service": service,
    })


@router.delete("/services/{service_id}")
async def admin_service_delete(request: Request, service_id: int):
    """Delete a service, or soft-delete if it has appointments"""
    if not await verify_admin(request):
        return HTMLResponse("Unauthorized", status_code=401)

    async with async_session() as session:
        service = (await session.execute(
            select(Service).where(Service.id == service_id)
        )).scalar_one_or_none()
        if not service:
            return HTMLResponse("Not found", status_code=404)

        has_appointments = await session.scalar(
            select(func.count(Appointment.id)).where(Appointment.service_id == service_id)
        )

        if has_appointments:
            service.is_active = False
            await session.commit()
            await session.refresh(service)
            return templates.TemplateResponse("components/admin/service_row.html", {
                "request": request,
                "service": service,
            })
        else:
            await session.delete(service)
            await session.commit()
            return HTMLResponse("")

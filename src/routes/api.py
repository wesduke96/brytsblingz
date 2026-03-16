"""
API routes for data operations
"""

from fastapi import APIRouter, Form
from fastapi.responses import HTMLResponse
from datetime import datetime, date, time
from typing import List, Optional
from sqlalchemy import select

from db.database import async_session
from db.models import Client, Service, Appointment, ContactMessage, CurationRequest

router = APIRouter(tags=["api"])


@router.post("/appointments")
async def create_appointment(
    client_name: str = Form(...),
    client_email: str = Form(...),
    client_phone: str = Form(...),
    services: List[int] = Form(...),
    quantities: List[int] = Form(...),
    appointment_date: str = Form(...),
    appointment_time: str = Form(...),
    notes: Optional[str] = Form(None)
):
    """Create appointment bookings for one or more services"""

    async with async_session() as session:
        # Upsert client
        result = await session.execute(
            select(Client).where(Client.email == client_email)
        )
        client = result.scalar_one_or_none()

        if not client:
            client = Client(
                name=client_name,
                email=client_email,
                phone=client_phone
            )
            session.add(client)
            await session.flush()
        else:
            client.name = client_name
            client.phone = client_phone

        # Parse date
        try:
            appt_date = datetime.strptime(appointment_date, "%Y-%m-%d").date()
        except Exception:
            return HTMLResponse(content="""
                <div class="p-4 border border-red-500/50 bg-red-900/20 text-center">
                    <p class="text-red-400">Invalid date format. Please try again.</p>
                </div>
            """, status_code=400)

        # Parse time
        try:
            hour, minute = map(int, appointment_time.split(":"))
            appt_time = time(hour, minute)
        except Exception:
            return HTMLResponse(content="""
                <div class="p-4 border border-red-500/50 bg-red-900/20 text-center">
                    <p class="text-red-400">Invalid time format. Please try again.</p>
                </div>
            """, status_code=400)

        # Pair services with quantities; pad quantities with 1 if fewer supplied
        pairs = list(zip(services, quantities + [1] * len(services)))[:len(services)]

        booked = []
        grand_total = 0.0

        for service_id, quantity in pairs:
            service_result = await session.execute(
                select(Service).where(Service.id == service_id)
            )
            service = service_result.scalar_one_or_none()

            if not service:
                return HTMLResponse(content="""
                    <div class="p-4 border border-red-500/50 bg-red-900/20 text-center">
                        <p class="text-red-400">One or more selected services are invalid. Please try again.</p>
                    </div>
                """, status_code=400)

            if quantity == 1:
                line_total = service.price
            elif service.pair_price:
                if quantity == 2:
                    line_total = service.pair_price
                else:
                    # First pair at pair_price, additional at half off
                    line_total = service.pair_price + (service.price / 2) * (quantity - 2)
            else:
                # No pair pricing for this service — full price per unit
                line_total = service.price * quantity

            appointment = Appointment(
                client_id=client.id,
                service_id=service_id,
                appointment_date=appt_date,
                appointment_time=appt_time,
                quantity=quantity,
                status="pending",
                notes=notes or ""
            )
            session.add(appointment)
            booked.append((service.name, quantity, line_total))
            grand_total += line_total

        await session.commit()

        display_time = appt_time.strftime("%I:%M %p")
        display_date = appt_date.strftime("%B %d, %Y")

        service_lines = "".join(
            f'<div class="flex justify-between text-sm">'
            f'<span class="text-bryt-silver">{name}{f" x{qty}" if qty > 1 else ""}</span>'
            f'<span class="text-bryt-pearl">${total:.0f}</span>'
            f'</div>'
            for name, qty, total in booked
        )

        return HTMLResponse(content=f"""
            <div class="p-6 border border-green-500/50 bg-green-900/20 text-center">
                <svg class="w-12 h-12 mx-auto mb-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                </svg>
                <h3 class="text-xl text-bryt-white mb-2">Appointment Requested!</h3>
                <p class="text-bryt-silver text-sm mb-4">
                    Thank you, <strong>{client_name}</strong>! Your appointment request for
                    <strong>{display_date}</strong> at <strong>{display_time}</strong> has been submitted.
                </p>
                <div class="text-left max-w-xs mx-auto space-y-1 mb-3">
                    {service_lines}
                    <div class="flex justify-between text-sm pt-2 border-t border-green-500/20">
                        <span class="text-bryt-silver font-medium">Estimated Total</span>
                        <span class="text-bryt-pink font-medium">${grand_total:.0f}</span>
                    </div>
                </div>
                <p class="text-bryt-gray text-xs mt-4">
                    Bryt will confirm your appointment via email within 48 hours.
                </p>
            </div>
        """)


@router.get("/appointments")
async def get_appointments():
    """Get all appointments (for admin)"""
    async with async_session() as session:
        result = await session.execute(select(Appointment))
        appointments = result.scalars().all()
        return {"appointments": [{"id": a.id, "date": str(a.appointment_date)} for a in appointments]}


@router.get("/services")
async def get_services():
    """Get all available services"""
    async with async_session() as session:
        result = await session.execute(select(Service).where(Service.is_active == True))
        services = result.scalars().all()
        return {
            "services": [
                {
                    "id": s.id,
                    "name": s.name,
                    "price": s.price,
                    "duration": s.duration_minutes
                }
                for s in services
            ]
        }


@router.post("/contact")
async def submit_contact(
    name: str = Form(...),
    email: str = Form(...),
    message: str = Form(...)
):
    """Submit contact form"""

    async with async_session() as session:
        contact_message = ContactMessage(
            name=name,
            email=email,
            message=message,
            is_read=False
        )
        session.add(contact_message)
        await session.commit()

        return HTMLResponse(content="""
            <div class="p-4 border border-green-500/50 bg-green-900/20 text-center">
                <p class="text-green-500">Message sent! Bryt will get back to you soon.</p>
            </div>
        """)


@router.post("/curations")
async def submit_curation(
    name: str = Form(...),
    email: str = Form(...),
    socials: Optional[str] = Form(None),
    area: str = Form(...),
    metal: str = Form(...),
    notes: Optional[str] = Form(None)
):
    """Submit a curation request"""

    async with async_session() as session:
        curation = CurationRequest(
            name=name,
            email=email,
            socials=socials or "",
            area=area,
            metal=metal,
            notes=notes or "",
            is_read=False
        )
        session.add(curation)
        await session.commit()

        return HTMLResponse(content=f"""
            <div class="p-6 border border-green-500/50 bg-green-900/20 text-center">
                <svg class="w-12 h-12 mx-auto mb-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                </svg>
                <h3 class="text-xl text-bryt-white mb-2">Request Submitted!</h3>
                <p class="text-bryt-silver text-sm mb-3">
                    Thanks, <strong>{name}</strong>! Your curation request has been received.
                    Bryt will review it and reach out to you at <strong>{email}</strong> within a few days.
                </p>
                <p class="text-bryt-gray text-xs">
                    Remember to send your reference photos via Instagram DM or email.
                </p>
            </div>
        """)

"""
Seed script to populate the database with sample data
Run with: python seed_data.py
"""

import asyncio
from datetime import date, time, datetime, timedelta
from sqlalchemy import text
from db.database import async_session, init_db
from db.models import Client, Service, Appointment, EarCreation, ContactMessage


async def seed_database():
    """Populate database with sample data"""
    
    # Initialize database tables
    await init_db()
    
    async with async_session() as session:
        # Clear existing data
        await session.execute(text("DELETE FROM appointments"))
        await session.execute(text("DELETE FROM services"))
        await session.execute(text("DELETE FROM clients"))
        await session.execute(text("DELETE FROM contact_messages"))
        
        # ═══════════════════════════════════════════════════════════════
        # SERVICES - Real Pricing from Bryt
        # ═══════════════════════════════════════════════════════════════
        
        services = [
            # ─────────────────────────────────────────────────────────────
            # EAR PIERCINGS
            # ─────────────────────────────────────────────────────────────
            Service(
                name="Lobes",
                category="Ear",
                description="Classic earlobe piercing - the perfect starting point",
                price=50.00,
                pair_price=75.00,
                duration_minutes=15,
                image_url="/static/images/piercings/lobes.jpg",
                is_active=True
            ),
            Service(
                name="Helix",
                category="Ear",
                description="Upper ear cartilage piercing along the outer rim",
                price=50.00,
                pair_price=75.00,
                duration_minutes=20,
                image_url="/static/images/piercings/helix.jpg",
                is_active=True
            ),
            Service(
                name="Tragus",
                category="Ear",
                description="Small cartilage flap in front of the ear canal",
                price=50.00,
                pair_price=80.00,
                duration_minutes=20,
                image_url="/static/images/piercings/tragus.jpg",
                is_active=True
            ),
            Service(
                name="Anti-Tragus",
                category="Ear",
                description="Cartilage ridge opposite the tragus, above the lobe",
                price=50.00,
                pair_price=80.00,
                duration_minutes=25,
                image_url="/static/images/piercings/anti-tragus.jpg",
                is_active=True
            ),
            Service(
                name="Surface Tragus",
                category="Ear",
                description="Surface piercing near the tragus area - consultation required",
                price=125.00,
                pair_price=None,
                duration_minutes=25,
                image_url="/static/images/piercings/surface-tragus.jpg",
                is_active=True
            ),
            Service(
                name="Snug",
                category="Ear",
                description="Inner cartilage ridge piercing (anti-helix)",
                price=50.00,
                pair_price=80.00,
                duration_minutes=25,
                image_url="/static/images/piercings/snug.jpg",
                is_active=True
            ),
            Service(
                name="Daith",
                category="Ear",
                description="Inner cartilage fold piercing - unique and elegant",
                price=60.00,
                pair_price=100.00,
                duration_minutes=25,
                image_url="/static/images/piercings/daith.jpg",
                is_active=True
            ),
            Service(
                name="Flat",
                category="Ear",
                description="Flat area of cartilage between the rim and inner ear",
                price=50.00,
                pair_price=80.00,
                duration_minutes=20,
                image_url="/static/images/piercings/flat.jpg",
                is_active=True
            ),
            Service(
                name="Industrial",
                category="Ear",
                description="Two connected piercings through the upper ear cartilage - consultation required",
                price=70.00,
                pair_price=None,  # Already a double piercing
                duration_minutes=30,
                image_url="/static/images/piercings/industrial.jpg",
                is_active=True
            ),
            Service(
                name="Conch",
                category="Ear",
                description="Inner ear cartilage - can be inner or outer conch",
                price=50.00,
                pair_price=80.00,
                duration_minutes=25,
                image_url="/static/images/piercings/conch.jpg",
                is_active=True
            ),
            Service(
                name="Forward Helix",
                category="Ear",
                description="Front upper cartilage where ear meets the head",
                price=50.00,
                pair_price=80.00,
                duration_minutes=20,
                image_url="/static/images/piercings/forward-helix.jpg",
                is_active=True
            ),
            Service(
                name="Rook",
                category="Ear",
                description="Upper inner cartilage fold, above the daith",
                price=50.00,
                pair_price=80.00,
                duration_minutes=25,
                image_url="/static/images/piercings/rook.jpg",
                is_active=True
            ),
            
            # ─────────────────────────────────────────────────────────────
            # NOSE PIERCINGS
            # ─────────────────────────────────────────────────────────────
            Service(
                name="Nostril",
                category="Nose",
                description="Classic nose piercing through the nostril",
                price=50.00,
                pair_price=80.00,
                duration_minutes=20,
                image_url="/static/images/piercings/nostril.jpg",
                is_active=True
            ),
            Service(
                name="Septum",
                category="Nose",
                description="Piercing through the nasal septum",
                price=70.00,
                pair_price=120.00,
                duration_minutes=25,
                image_url="/static/images/piercings/septum.jpg",
                is_active=True
            ),
            Service(
                name="Bridge",
                category="Nose",
                description="Horizontal piercing across the bridge of the nose",
                price=60.00,
                pair_price=100.00,
                duration_minutes=25,
                image_url="/static/images/piercings/bridge.jpg",
                is_active=True
            ),
            
            # ─────────────────────────────────────────────────────────────
            # FACE PIERCINGS
            # ─────────────────────────────────────────────────────────────
            Service(
                name="Eyebrow",
                category="Face",
                description="Vertical piercing through the eyebrow",
                price=50.00,
                pair_price=80.00,
                duration_minutes=20,
                image_url="/static/images/piercings/eyebrow.jpg",
                is_active=True
            ),
            Service(
                name="Anti-Eyebrow (Surface Piercing)",
                category="Face",
                description="Surface piercing below the eye or above the cheekbone - consultation required",
                price=125.00,
                pair_price=None,
                duration_minutes=25,
                image_url="/static/images/piercings/anti-eyebrow.jpg",
                is_active=True
            ),
            Service(
                name="Dahlia",
                category="Oral",
                description="Paired piercings at the corners of the mouth",
                price=75.00,
                pair_price=None,  # Usually done as pair at this price
                duration_minutes=30,
                image_url="/static/images/piercings/dahlia.jpg",
                is_active=True
            ),
            
            # ─────────────────────────────────────────────────────────────
            # ORAL PIERCINGS
            # ─────────────────────────────────────────────────────────────
            Service(
                name="Ashley",
                category="Oral",
                description="Single piercing through the center of the lower lip",
                price=60.00,
                pair_price=None,
                duration_minutes=25,
                image_url="/static/images/piercings/ashley.jpg",
                is_active=True
            ),
            Service(
                name="Bottom Lip",
                category="Oral",
                description="Classic labret piercing below the lower lip",
                price=50.00,
                pair_price=80.00,
                duration_minutes=20,
                image_url="/static/images/piercings/bottom-lip.jpg",
                is_active=True
            ),
            Service(
                name="Vertical Labret",
                category="Oral",
                description="Vertical piercing through the lower lip",
                price=60.00,
                pair_price=None,
                duration_minutes=25,
                image_url="/static/images/piercings/vertical-labret.jpg",
                is_active=True
            ),
            Service(
                name="Top Lip",
                category="Oral",
                description="Piercing above the upper lip (Monroe/Madonna style)",
                price=60.00,
                pair_price=100.00,
                duration_minutes=20,
                image_url="/static/images/piercings/top-lip.jpg",
                is_active=True
            ),
            Service(
                name="Jestrum",
                category="Oral",
                description="Vertical piercing through the philtrum/cupid's bow",
                price=70.00,
                pair_price=None,
                duration_minutes=25,
                image_url="/static/images/piercings/jestrum.jpg",
                is_active=True
            ),
            Service(
                name="Angel Fangs",
                category="Oral",
                description="Paired piercings through the upper lip",
                price=120.00,
                pair_price=None,  # Already a pair
                duration_minutes=30,
                image_url="/static/images/piercings/angel-fangs.jpg",
                is_active=True
            ),
            
            # ─────────────────────────────────────────────────────────────
            # BODY PIERCINGS
            # ─────────────────────────────────────────────────────────────
            Service(
                name="Navel",
                category="Body",
                description="Classic belly button piercing",
                price=50.00,
                pair_price=80.00,
                duration_minutes=25,
                image_url="/static/images/piercings/navel.jpg",
                is_active=True
            ),
            Service(
                name="Nipples",
                category="Body",
                description="Nipple piercing",
                price=60.00,
                pair_price=90.00,
                duration_minutes=25,
                image_url="/static/images/piercings/nipples.jpg",
                is_active=True
            ),
            Service(
                name="Female Genitals",
                category="Body",
                description="Female intimate piercings - consultation required",
                price=100.00,
                pair_price=None,
                image_url=None,
                is_active=True
            ),
            
            # ─────────────────────────────────────────────────────────────
            # OTHER SERVICES
            # ─────────────────────────────────────────────────────────────
            Service(
                name="Genital Change Outs",
                category="Other",
                description="Jewelry change for genital piercings",
                price=40.00,
                pair_price=None,
                duration_minutes=15,
                image_url=None,
                is_active=True
            ),
            Service(
                name="Jewelry Assistance",
                category="Other",
                description="Help with changing or adjusting existing jewelry",
                price=10.00,
                pair_price=None,
                duration_minutes=15,
                image_url="/static/images/piercings/jewelry-assistance.jpg",
                is_active=True
            ),
            Service(
                name="Taper",
                category="Other",
                description="Stretching a shrinking piercing channel back to size",
                price=20.00,
                pair_price=None,
                duration_minutes=20,
                image_url="/static/images/piercings/taper.jpg",
                is_active=True
            ),
        ]
        
        for service in services:
            session.add(service)
        await session.flush()
        
        # ═══════════════════════════════════════════════════════════════
        # SAMPLE CLIENTS
        # ═══════════════════════════════════════════════════════════════
        
        clients = [
            Client(
                name="Sarah Mitchell",
                email="sarah.m@email.com",
                phone="(555) 123-4567",
                notes="First time client, nervous about pain"
            ),
            Client(
                name="Emma Rodriguez",
                email="emma.r@email.com",
                phone="(555) 234-5678",
                notes="Regular client, loves gold jewelry"
            ),
            Client(
                name="Olivia Chen",
                email="olivia.c@email.com",
                phone="(555) 345-6789",
                notes="Allergic to nickel - titanium only"
            ),
            Client(
                name="Ava Thompson",
                email="ava.t@email.com",
                phone="(555) 456-7890",
                notes=""
            ),
            Client(
                name="Mia Johnson",
                email="mia.j@email.com",
                phone="(555) 567-8901",
                notes="Interested in full ear curation"
            ),
        ]
        
        for client in clients:
            session.add(client)
        await session.flush()
        
        # ═══════════════════════════════════════════════════════════════
        # SAMPLE APPOINTMENTS
        # ═══════════════════════════════════════════════════════════════
        
        today = date.today()
        
        appointments = [
            Appointment(
                client_id=1,
                service_id=2,  # Helix
                appointment_date=today,
                appointment_time=time(10, 0),
                quantity=1,
                status="confirmed",
                notes="Wants left ear"
            ),
            Appointment(
                client_id=2,
                service_id=10,  # Conch
                appointment_date=today,
                appointment_time=time(14, 30),
                quantity=1,
                status="confirmed",
                notes="Gold jewelry preferred"
            ),
            Appointment(
                client_id=3,
                service_id=1,  # Lobes
                appointment_date=today,
                appointment_time=time(16, 0),
                quantity=2,  # Pair
                status="pending",
                notes="Double lobe piercing"
            ),
            Appointment(
                client_id=4,
                service_id=7,  # Daith
                appointment_date=today + timedelta(days=1),
                appointment_time=time(11, 0),
                quantity=1,
                status="pending",
                notes=""
            ),
            Appointment(
                client_id=5,
                service_id=9,  # Industrial
                appointment_date=today + timedelta(days=1),
                appointment_time=time(13, 0),
                quantity=1,
                status="confirmed",
                notes="Has wanted this for years!"
            ),
            Appointment(
                client_id=1,
                service_id=3,  # Tragus
                appointment_date=today + timedelta(days=3),
                appointment_time=time(15, 0),
                quantity=1,
                status="pending",
                notes="Follow-up from helix"
            ),
            Appointment(
                client_id=2,
                service_id=1,  # Lobes
                appointment_date=today - timedelta(days=7),
                appointment_time=time(10, 0),
                quantity=2,
                status="completed",
                notes="Pair went great!"
            ),
            Appointment(
                client_id=3,
                service_id=2,  # Helix
                appointment_date=today - timedelta(days=14),
                appointment_time=time(14, 0),
                quantity=1,
                status="completed",
                notes="Healing well at checkup"
            ),
        ]
        
        for appointment in appointments:
            session.add(appointment)
        
        # Sample contact message
        message = ContactMessage(
            name="Jessica Williams",
            email="jessica.w@email.com",
            message="Hi! I'm interested in getting multiple piercings done. Do you offer any packages or discounts for booking multiple at once? Thanks!",
            is_read=False
        )
        session.add(message)
        
        await session.commit()
        
        print("Database seeded successfully!")
        print(f"   - {len(services)} services added")
        print(f"   - {len(clients)} clients added")
        print(f"   - {len(appointments)} appointments added")
        print(f"   - 1 contact message added")


if __name__ == "__main__":
    asyncio.run(seed_database())

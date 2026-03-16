"""
Database configuration and initialization
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from pathlib import Path

# Database path
DB_PATH = Path(__file__).resolve().parent / "bryt.db"
DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Session factory
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    """Base class for all models"""
    pass


async def init_db():
    """Initialize database tables and seed default data"""
    from . import models  # Import models to register them
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    from sqlalchemy import select, func
    from .models import AdminUser, Service
    async with async_session() as session:
        # Seed default admin user
        existing_admin = (await session.execute(
            select(AdminUser).where(AdminUser.username == "admin")
        )).scalar_one_or_none()
        if not existing_admin:
            session.add(AdminUser(
                username="admin",
                password_hash="$2b$12$XYiGK07pb5FUbDHXoZgjDeJ.TX9/7d8A72SX4COiWnq/.L1UAQnGm"
            ))

        # Seed services if table is empty
        service_count = await session.scalar(select(func.count(Service.id)))
        if service_count == 0:
            default_services = [
                # Ear
                Service(name="Lobes", category="Ear", description="Classic earlobe piercing - the perfect starting point", price=50.00, pair_price=75.00, duration_minutes=15, image_url="/static/images/piercings/lobes.jpg"),
                Service(name="Helix", category="Ear", description="Upper ear cartilage piercing along the outer rim", price=50.00, pair_price=75.00, duration_minutes=20, image_url="/static/images/piercings/helix.jpg"),
                Service(name="Tragus", category="Ear", description="Small cartilage flap in front of the ear canal", price=50.00, pair_price=80.00, duration_minutes=20, image_url="/static/images/piercings/tragus.jpg"),
                Service(name="Anti-Tragus", category="Ear", description="Cartilage ridge opposite the tragus, above the lobe", price=50.00, pair_price=80.00, duration_minutes=25, image_url="/static/images/piercings/anti-tragus.jpg"),
                Service(name="Surface Tragus", category="Ear", description="Surface piercing near the tragus area - consultation required", price=125.00, pair_price=None, duration_minutes=25, image_url="/static/images/piercings/surface-tragus.jpg"),
                Service(name="Snug", category="Ear", description="Inner cartilage ridge piercing (anti-helix)", price=50.00, pair_price=80.00, duration_minutes=25, image_url="/static/images/piercings/snug.jpg"),
                Service(name="Daith", category="Ear", description="Inner cartilage fold piercing - unique and elegant", price=60.00, pair_price=100.00, duration_minutes=25, image_url="/static/images/piercings/daith.jpg"),
                Service(name="Flat", category="Ear", description="Flat area of cartilage between the rim and inner ear", price=50.00, pair_price=80.00, duration_minutes=20, image_url="/static/images/piercings/flat.jpg"),
                Service(name="Industrial", category="Ear", description="Two connected piercings through the upper ear cartilage - consultation required", price=70.00, pair_price=None, duration_minutes=30, image_url="/static/images/piercings/industrial.jpg"),
                Service(name="Conch", category="Ear", description="Inner ear cartilage - can be inner or outer conch", price=50.00, pair_price=80.00, duration_minutes=25, image_url="/static/images/piercings/conch.jpg"),
                Service(name="Forward Helix", category="Ear", description="Front upper cartilage where ear meets the head", price=50.00, pair_price=80.00, duration_minutes=20, image_url="/static/images/piercings/forward-helix.jpg"),
                Service(name="Rook", category="Ear", description="Upper inner cartilage fold, above the daith", price=50.00, pair_price=80.00, duration_minutes=25, image_url="/static/images/piercings/rook.jpg"),
                # Nose
                Service(name="Nostril", category="Nose", description="Classic nose piercing through the nostril", price=50.00, pair_price=80.00, duration_minutes=20, image_url="/static/images/piercings/nostril.jpg"),
                Service(name="Septum", category="Nose", description="Piercing through the nasal septum", price=70.00, pair_price=120.00, duration_minutes=25, image_url="/static/images/piercings/septum.jpg"),
                Service(name="Bridge", category="Nose", description="Horizontal piercing across the bridge of the nose", price=60.00, pair_price=100.00, duration_minutes=25, image_url="/static/images/piercings/bridge.jpg"),
                # Face
                Service(name="Eyebrow", category="Face", description="Vertical piercing through the eyebrow", price=50.00, pair_price=80.00, duration_minutes=20, image_url="/static/images/piercings/eyebrow.jpg"),
                Service(name="Anti-Eyebrow (Surface Piercing)", category="Face", description="Surface piercing below the eye or above the cheekbone - consultation required", price=125.00, pair_price=None, duration_minutes=25, image_url="/static/images/piercings/anti-eyebrow.jpg"),
                # Oral
                Service(name="Dahlia", category="Oral", description="Paired piercings at the corners of the mouth", price=75.00, pair_price=None, duration_minutes=30, image_url="/static/images/piercings/dahlia.jpg"),
                Service(name="Ashley", category="Oral", description="Single piercing through the center of the lower lip", price=60.00, pair_price=None, duration_minutes=25, image_url="/static/images/piercings/ashley.jpg"),
                Service(name="Bottom Lip", category="Oral", description="Classic labret piercing below the lower lip", price=50.00, pair_price=80.00, duration_minutes=20, image_url="/static/images/piercings/bottom-lip.jpg"),
                Service(name="Vertical Labret", category="Oral", description="Vertical piercing through the lower lip", price=60.00, pair_price=None, duration_minutes=25, image_url="/static/images/piercings/vertical-labret.jpg"),
                Service(name="Top Lip", category="Oral", description="Piercing above the upper lip (Monroe/Madonna style)", price=60.00, pair_price=100.00, duration_minutes=20, image_url="/static/images/piercings/top-lip.jpg"),
                Service(name="Jestrum", category="Oral", description="Vertical piercing through the philtrum/cupid's bow", price=70.00, pair_price=None, duration_minutes=25, image_url="/static/images/piercings/jestrum.jpg"),
                Service(name="Angel Fangs", category="Oral", description="Paired piercings through the upper lip", price=120.00, pair_price=None, duration_minutes=30, image_url="/static/images/piercings/angel-fangs.jpg"),
                # Body
                Service(name="Navel", category="Body", description="Classic belly button piercing", price=50.00, pair_price=80.00, duration_minutes=25, image_url="/static/images/piercings/navel.jpg"),
                Service(name="Nipples", category="Body", description="Nipple piercing", price=60.00, pair_price=90.00, duration_minutes=25, image_url="/static/images/piercings/nipples.jpg"),
                Service(name="Female Genitals", category="Body", description="Female intimate piercings - consultation required", price=100.00, pair_price=None, image_url=None),
                # Other
                Service(name="Genital Change Outs", category="Other", description="Jewelry change for genital piercings", price=40.00, pair_price=None, duration_minutes=15, image_url=None),
                Service(name="Jewelry Assistance", category="Other", description="Help with changing or adjusting existing jewelry", price=10.00, pair_price=None, duration_minutes=15, image_url="/static/images/piercings/jewelry-assistance.jpg"),
                Service(name="Taper", category="Other", description="Stretching a shrinking piercing channel back to size", price=20.00, pair_price=None, duration_minutes=20, image_url="/static/images/piercings/taper.jpg"),
            ]
            for svc in default_services:
                session.add(svc)

        await session.commit()


async def get_session() -> AsyncSession:
    """Get database session"""
    async with async_session() as session:
        yield session


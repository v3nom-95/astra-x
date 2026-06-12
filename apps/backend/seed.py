"""
ASTRA-X Database Seeder.
Seeds the database with initial data from CSV and a default admin user.
"""
import os
import sys
import pandas as pd
import logging

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.engine import engine, SessionLocal
from models import Base, User, Asset
from utils.data_processor import validate_csv, df_to_assets

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seed")


def seed_database():
    """Seed the database with initial data."""
    logger.info("Creating tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Seed default admin user
        existing_user = db.query(User).filter(User.username == "admin").first()
        if not existing_user:
            admin = User(
                username="admin",
                email="admin@astra-x.io",
                role="admin",
                is_active=True,
            )
            db.add(admin)
            logger.info("Admin user created")
        else:
            logger.info("Admin user already exists")

        # Seed assets from CSV
        csv_paths = [
            os.path.join(os.path.dirname(__file__), "..", "..", "data", "assets.csv"),
            os.path.join(os.path.dirname(__file__), "data", "assets.csv"),
            "../../data/assets.csv",
        ]

        csv_path = None
        for p in csv_paths:
            resolved = os.path.abspath(p)
            if os.path.exists(resolved):
                csv_path = resolved
                break

        if csv_path:
            logger.info(f"Loading seed data from {csv_path}")
            with open(csv_path, "r") as f:
                content = f.read()

            df, errors = validate_csv(content)
            if errors:
                logger.warning(f"Validation warnings: {errors}")

            assets = df_to_assets(df)
            loaded = 0
            for asset_data in assets:
                existing = db.query(Asset).filter(Asset.asset_id == asset_data["asset_id"]).first()
                if not existing:
                    db_asset = Asset(**{k: v for k, v in asset_data.items() if hasattr(Asset, k)})
                    db.add(db_asset)
                    loaded += 1

            logger.info(f"Seeded {loaded} assets")
        else:
            logger.warning("No seed CSV found")

        db.commit()
        logger.info("Database seeding complete!")

    except Exception as e:
        logger.error(f"Seeding failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()

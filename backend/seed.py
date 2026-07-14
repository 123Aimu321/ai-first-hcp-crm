from app.database import SessionLocal
from app.models.hcp import HCP


def seed_hcps():
    db = SessionLocal()

    try:
        existing_names = {
            h.name for h in db.query(HCP).all()
        }

        hcps = [
            HCP(
                name="Dr. Ananya Rao",
                specialty="Cardiology",
                organization="Apollo Hospitals",
            ),
            HCP(
                name="Dr. Rahul Sharma",
                specialty="Neurology",
                organization="Manipal Hospitals",
            ),
            HCP(
                name="Dr. Priya Nair",
                specialty="Cardiology",
                organization="Fortis Hospital",
            ),
            HCP(
                name="Dr. Arjun Mehta",
                specialty="Dermatology",
                organization="Skin Care Clinic",
            ),
        ]

        new_hcps = [
            hcp for hcp in hcps
            if hcp.name not in existing_names
        ]

        db.add_all(new_hcps)
        db.commit()

        print(f"Inserted {len(new_hcps)} new HCPs.")

    except Exception as error:
        db.rollback()
        print("Seed failed:", error)

    finally:
        db.close()


if __name__ == "__main__":
    seed_hcps()
from __future__ import annotations

import argparse
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from app.infrastructure.database.connection import SessionLocal, init_db
from app.infrastructure.database.models import ProfileModel
from app.infrastructure.security.password_hasher import PasswordHasher


def create_admin(full_name: str, email: str, password: str) -> None:
    init_db()
    hasher = PasswordHasher()

    with SessionLocal() as db:
        existing = db.query(ProfileModel).filter(ProfileModel.email == email).first()
        if existing:
            existing.role = "admin"
            db.commit()
            print(f"Rol de '{email}' actualizado a admin.")
            return

        profile = ProfileModel(
            id=str(uuid.uuid4()),
            full_name=full_name,
            email=email,
            password_hash=hasher.hash(password),
            role="admin",
        )
        db.add(profile)
        db.commit()
        print(f"Admin creado exitosamente: {email}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crear o promover cuenta de administrador")
    parser.add_argument("--email", required=True, help="Correo del administrador")
    parser.add_argument("--password", required=True, help="Contraseña")
    parser.add_argument("--name", default="Administrador", help="Nombre completo")
    args = parser.parse_args()
    create_admin(args.name, args.email, args.password)

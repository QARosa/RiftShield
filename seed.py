import asyncio
import os
import sys

import bcrypt
from beanie import init_beanie
from pymongo import AsyncMongoClient

# Adiciona o diretório 'src' ao path para permitir importações de módulos da aplicação
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "backend", "src")))

from modules.auth.models.user_model import User
from modules.inference.agents.stride_kb import COUNTERMEASURE_KB, VULNERABILITY_KB
from modules.inference.models.kb_model import KBCountermeasure, KBVulnerability


async def seed_users():
    """Limpa a coleção de usuários e cria um usuário administrador padrão."""
    print("Seeding users...")
    await User.delete_all()

    hashed_password = bcrypt.hashpw("test123".encode("utf-8"), bcrypt.gensalt())
    admin_user = User(
        name="Test Admin",
        email="test@riftshield.com",
        password=hashed_password.decode("utf-8"),
        role="ADMIN",
        is_active=True,
    )
    await admin_user.insert()
    print(f"-> Created admin user: {admin_user.email}")


async def seed_kb():
    """Popula a Base de Conhecimento com vulnerabilidades e contramedidas."""
    print("Seeding knowledge base...")
    await KBVulnerability.delete_all()
    await KBCountermeasure.delete_all()

    vulns_to_insert = [KBVulnerability(**vuln) for vuln in VULNERABILITY_KB]
    await KBVulnerability.insert_many(vulns_to_insert)
    print(f"-> Inserted {len(vulns_to_insert)} vulnerabilities.")

    cm_to_insert = [KBCountermeasure(**cm) for cm in COUNTERMEASURE_KB]
    await KBCountermeasure.insert_many(cm_to_insert)
    print(f"-> Inserted {len(cm_to_insert)} countermeasures.")


async def main():
    """Função principal para executar o processo de seeding."""
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL não foi definida no ambiente.")

    print(f"Connecting to database at {db_url}...")
    client = AsyncMongoClient(db_url)
    database = client.get_database("riftshield_test")

    await init_beanie(
        database=database,
        document_models=[User, KBVulnerability, KBCountermeasure],
    )
    print("Database initialized.")

    await seed_users()
    await seed_kb()

    print("\n✅ Database seeding completed successfully!")


if __name__ == "__main__":
    # Define um loop de eventos se não houver um (necessário para alguns ambientes)
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    loop.run_until_complete(main())
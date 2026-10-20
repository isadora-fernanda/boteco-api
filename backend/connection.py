import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.pool import StaticPool

load_dotenv()

# Sem configuração, a API usa um arquivo SQLite local.
# Para usar PostgreSQL (por exemplo, no Neon), defina DATABASE_URL no .env.
URL_PADRAO = "sqlite:///boteco.db"


def criar_engine(url: str | None = None) -> Engine:
    url = url or os.getenv("DATABASE_URL") or os.getenv("NEON_STRING") or URL_PADRAO

    if url.startswith("sqlite"):
        opcoes = {"connect_args": {"check_same_thread": False}}
        if ":memory:" in url:
            # Mantém o mesmo banco em memória entre as requisições (usado nos testes)
            opcoes["poolclass"] = StaticPool
        return create_engine(url, **opcoes)

    return create_engine(url, pool_pre_ping=True)

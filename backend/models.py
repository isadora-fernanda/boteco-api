from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, func, true
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


# ==========================
# Cliente
# ==========================
class Cliente(Base):
    __tablename__ = "clientes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    cpf: Mapped[str] = mapped_column(String(15), nullable=False, unique=True)

    cartoes: Mapped[list["Cartao"]] = relationship(
        back_populates="cliente",
        cascade="all, delete-orphan",
    )


# ==========================
# Cartão
# ==========================
class Cartao(Base):
    __tablename__ = "cartoes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    cliente_id: Mapped[int] = mapped_column(
        ForeignKey("clientes.id"),
        nullable=False,
    )

    data_aquisicao: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    ativo: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=true(),
    )

    cliente: Mapped["Cliente"] = relationship(back_populates="cartoes")

    recargas: Mapped[list["Recarga"]] = relationship(
        back_populates="cartao",
        cascade="all, delete-orphan",
    )

    consumos: Mapped[list["Consumo"]] = relationship(
        back_populates="cartao",
        cascade="all, delete-orphan",
    )

    saldo: Mapped["Saldo"] = relationship(
        back_populates="cartao",
        uselist=False,
        cascade="all, delete-orphan",
    )


# ==========================
# Recarga
# ==========================
class Recarga(Base):
    __tablename__ = "recargas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    cartao_id: Mapped[int] = mapped_column(
        ForeignKey("cartoes.id"),
        nullable=False,
    )

    recarga_em: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    valor_recarga: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    cartao: Mapped["Cartao"] = relationship(back_populates="recargas")


# ==========================
# Produto
# ==========================
class Produto(Base):
    __tablename__ = "produtos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    descricao: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # Preço por mililitro
    valorML: Mapped[Decimal] = mapped_column(
        Numeric(10, 3),
        nullable=False,
    )

    consumos: Mapped[list["Consumo"]] = relationship(
        back_populates="produto",
    )


# ==========================
# Consumo
# ==========================
class Consumo(Base):
    __tablename__ = "consumo"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    cartao_id: Mapped[int] = mapped_column(
        ForeignKey("cartoes.id"),
        nullable=False,
    )

    produto_id: Mapped[int] = mapped_column(
        ForeignKey("produtos.id"),
        nullable=False,
    )

    # Quantidade servida, em mililitros
    quantidade: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    cartao: Mapped["Cartao"] = relationship(back_populates="consumos")

    produto: Mapped["Produto"] = relationship(back_populates="consumos")


# ==========================
# Saldo
# ==========================
class Saldo(Base):
    __tablename__ = "saldo"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    cartao_id: Mapped[int] = mapped_column(
        ForeignKey("cartoes.id"),
        nullable=False,
        unique=True,
    )

    saldo: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    cartao: Mapped["Cartao"] = relationship(back_populates="saldo")

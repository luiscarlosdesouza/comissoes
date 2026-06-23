from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Comissao(Base):
    __tablename__ = "comissoes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    url = Column(String)
    data_atualizacao = Column(DateTime, default=datetime.utcnow)
    
    membros = relationship("Membro", back_populates="comissao", cascade="all, delete-orphan")

class Membro(Base):
    __tablename__ = "membros"

    id = Column(Integer, primary_key=True, index=True)
    comissao_id = Column(Integer, ForeignKey("comissoes.id"))
    nome = Column(String)
    cargo = Column(String)
    periodo = Column(String, nullable=True)
    
    comissao = relationship("Comissao", back_populates="membros")

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)

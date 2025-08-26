from sqlalchemy import Column, Integer, String
from database.base import Base

class WatchedWallet(Base):
    __tablename__ = 'watched_wallets'

    id = Column(Integer, primary_key=True)
    address = Column(String, unique=True, nullable=False, index=True)
    label = Column(String) # Метка, например "Кит 1" или "Мой холодный кошелек"

    def __repr__(self):
        return f"<WatchedWallet(address='{self.address}', label='{self.label}')>"
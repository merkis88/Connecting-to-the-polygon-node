from sqlalchemy import Column, Integer, String, BigInteger
from database.base import Base

class WatchedWallet(Base):
    __tablename__ = 'watched_wallets'

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    address = Column(String, nullable=False, index=True)
    label = Column(String) # Метка, например "Кит 1" или "Мой холодный кошелек"

    def __repr__(self):
        return f"<WatchedWallet(address='{self.address}', label='{self.label}, user_id='{self.user_id}')>"
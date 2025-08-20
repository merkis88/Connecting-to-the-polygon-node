from sqlalchemy import (Column, Integer, String, Numeric, BigInteger)
from database.base import Base

class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)
    tx_hash = Column(String, unique=True, nullable=False)
    block_number = Column(BigInteger, nullable=False, index=True)
    from_address = Column(String, nullable=False, index=True)
    to_address = Column(String, nullable=True, index=True) #nullable=True - нужен на тот случай, если загружается новый смарт-контракт в блокчейн
    value = Column(Numeric, nullable=False)

    def __repr__(self):
        return f"<Transaction(hash='{self.tx_hash[:10]}...')>"
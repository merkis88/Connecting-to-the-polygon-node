import enum
from datetime import datetime
from sqlalchemy import String, func, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base

class WalletLabel(enum.Enum):
    LEGIT = 'legit'
    SUSPICIOUS = "suspicious"
    SCAM = 'scam'

class LabeledWallet(Base):
    __tablename__ = "labeled_wallets_arbitrum"

    id: Mapped[int] = mapped_column(primary_key=True)
    address: Mapped[str] = mapped_column(String(70), unique=True, index=True, nullable=False)
    label: Mapped[WalletLabel] = mapped_column(Enum(WalletLabel), nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    def __repr__(self) -> str:
        return f"<LabeledWallet(address='{self.address}', label='{self.label.value}')>"

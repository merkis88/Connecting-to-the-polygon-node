import datetime

from sqlalchemy import ForeignKey, Integer, Numeric, DateTime, func, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.base import Base

class WalletFeature(Base):
    __tablename__ = "wallet_features"

    wallet_id: Mapped[int] = mapped_column(ForeignKey("labeled_wallets_arbitrum.id"), primary_key=True)
    transaction_count: Mapped[int] = mapped_column(BigInteger)
    wallet_age_days: Mapped[int] = mapped_column(Integer)
    balance_eth: Mapped[float] = mapped_column(Numeric(precision=30, scale=18))
    last_update_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    created_token_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default='0')

    labeled_wallet = relationship("LabeledWallet", back_populates="features")

    def __repr__(self) -> str:
        return f"<WalletFeature(wallet_id={self.wallet_id}, tx_count={self.transaction_count})>"



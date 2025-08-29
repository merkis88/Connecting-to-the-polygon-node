from sqlalchemy import select, label
from sqlalchemy.ext.asyncio import AsyncSession
from database.models.wallet import WatchedWallet

async def add_wallet(session: AsyncSession, user_id, wallet_address, wallet_name):
    try:
        query = select(WatchedWallet).where(WatchedWallet.user_id == user_id,WatchedWallet.address == wallet_address.lower())
        result = await session.execute(query)
        existing = result.scalars().first()

        if existing:
            return "exists"

        new_wallet = WatchedWallet(
            user_id=user_id,
            address=wallet_address.lower(),
            label=wallet_name

        )
        session.add(new_wallet)
        await session.commit()
        return "added"

    except Exception as e:
        await session.rollback()
        print(f"Ошибка при добавление кошелька: {e}")
        return "error"




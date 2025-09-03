# Исправленный service/list_wallet.py

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.models.wallet import WatchedWallet

async def get_user_wallet(session: AsyncSession, user_id):
    """Получаем кошельки из БД"""
    try:
        query = select(WatchedWallet).where(WatchedWallet.user_id == user_id).order_by(WatchedWallet.id.desc())
        result = await session.execute(query)
        wallets = result.scalars().all()

        return [
            {
                "address": wallet.address,
                "label": wallet.label,
                "id": wallet.id
            }
            for wallet in wallets
        ]

    except Exception as e:
        print(f"Ошибка при получении кошельков: {e}")
        return []

async def wallet_message(wallets):
    if not wallets:
        return "📭 **У вас нет отслеживаемых кошельков**"

    message = "🗂️ **Ваши отслеживаемые кошельки:**\n\n"

    for i, wallet in enumerate(wallets, 1):
        address = wallet["address"]
        label = wallet["label"]

        message += (
            f"**{i}.** {label}\n"
            f"   📎 `{address}`\n"
            f"   🔗 [Посмотреть на Arbiscan](https://arbiscan.io/address/{address})\n\n"
        )

    message += (
        f"📊 **Всего кошельков:** {len(wallets)}\n\n"
    )

    return message
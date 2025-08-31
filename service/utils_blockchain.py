from soupsieve.util import lower
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from decimal import Decimal
from database.models.wallet import WatchedWallet
from database.models.transaction import Transaction
from sqlalchemy import select
from aiogram import Bot
from service.price_service import get_eth_price

WEI_TO_ETH = Decimal("1000000000000000000")


async def save_transactions_from_block(session: AsyncSession, block_data: dict):
    raw_transactions = block_data.get('transactions', [])
    if not raw_transactions:
        return

    new_transactions = []
    for tx in raw_transactions:
        value_in_wei = int(tx.get('value', '0x0'), 16)
        value_in_eth = Decimal(value_in_wei) / WEI_TO_ETH

        transaction_obj = Transaction(
            tx_hash=tx.get('hash'),
            block_number=int(tx.get('blockNumber', '0x0'), 16),
            from_address=tx.get('from'),
            to_address=tx.get('to'),
            value=value_in_eth
        )
        new_transactions.append(transaction_obj)

    session.add_all(new_transactions)

    try:
        await session.commit()
        print(f"  -> ✅ Сохранено {len(new_transactions)} транзакций в БД.")
    except IntegrityError:
        await session.rollback()
        print("  -> ❕ Обнаружены дубликаты, транзакции не сохранены.")


async def check_transactions_for_watched_wallets(session: AsyncSession, transactions: list[dict], bot: Bot):
    if not transactions:
        return

    eth_price_usd = await get_eth_price()
    if eth_price_usd is None:
        print("Не удалось получить цену ETH")

    involved_addresses = {tx.get('from', '').lower() for tx in transactions} | {tx.get('to', '').lower() for tx in transactions}
    involved_addresses.discard('') # Множество уникальных адресов из блока

    if not involved_addresses:
        return

    query = select(WatchedWallet).where(WatchedWallet.address.in_(involved_addresses))
    result = await session.execute(query) # Проверка на совпадения тех адресов которые лежат в бд и прилетели с множества

    watched_map = {wallet.address: wallet for wallet in result.scalars().all()} # Превращаем список из БД в словарь, где ключ - это адрес, а значение - весь объект кошелька
    if not watched_map:
        return

    for tx in transactions:
        watched_address = None
        from_address = tx.get('from', '').lower()
        to_address = tx.get('to', '').lower()


        if from_address in watched_map:
            watched_address = from_address
        elif to_address in watched_map:
            watched_address = to_address

        if watched_address:
            wallet_data = watched_map[watched_address]
            user_to_notify = wallet_data.user_id
            wallet_label = wallet_data.label or wallet_data.address

            direction = "📤 **Исходящая**" if watched_address == from_address else "📥 **Входящая**"
            value_eth = Decimal(int(tx.get('value', '0x0'), 16)) / WEI_TO_ETH
            tx_hash = tx.get('hash')
            arbiscan_link = f"https://arbiscan.io/tx/{tx_hash}"

            message_text = (
                f"🔔 **Активность на кошельке: {wallet_label}**\n\n"
                f"{direction} транзакция\n\n"
                f"💰 Сумма: **{value_eth:.6f} ETH**"
            )

            if eth_price_usd:
                value_usd = float(value_eth) * eth_price_usd
                message_text += f" (~${value_usd:,.2f} USD)"

            message_text += (
                f"\n\nОт: `{from_address}`\n"
                f"Кому: `{to_address}`\n\n"
                f"[🔗 Посмотреть на Arbiscan]({arbiscan_link})"
            )

            try:
                await bot.send_message(
                    chat_id=user_to_notify,
                    text=message_text,
                    parse_mode="Markdown",
                    disable_web_page_preview=True
                )
            except Exception as e:
                print(f"❌ Не удалось отправить уведомление пользователю {user_to_notify}: {e}")







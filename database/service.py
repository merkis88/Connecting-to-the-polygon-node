from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from decimal import Decimal
from database.models.wallet import WatchedWallet
from database.models.transaction import Transaction
from sqlalchemy import select

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


async def check_transactions_for_watched_wallets(session: AsyncSession, transactions: list[dict]):
    if not transactions:
        return

    involved_addresses = set()
    for tx in transactions:
        if tx.get('from'):
            involved_addresses.add(tx.get('from').lower())
        if tx.get('to'):
            involved_addresses.add(tx.get('to').lower())

    involved_addresses.discard(None)

    if not involved_addresses:
        return

    query = select(WatchedWallet).where(WatchedWallet.address.in_(involved_addresses))
    result = await session.execute(query)
    found_wallets = result.scalars().all()

    if found_wallets:
        for wallet in found_wallets:
            print("=" * 50)
            print(f"🚨 ВНИМАНИЕ! Обнаружена активность кошелька: {wallet.label} ({wallet.address})")
            print("=" * 50)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from decimal import Decimal
from database.models.transaction import Transaction

WEI_TO_ETH = Decimal("1000000000000000000")

async def save_transactions_from_block(session, block_data):
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
        print(f"  - Хэш: {transaction_obj.tx_hash}")
        print(f"    От: {transaction_obj.from_address}")
        print(f"    Кому: {transaction_obj.to_address}")
        print(f"    Сумма: {transaction_obj.value} ETH")
        print("-" * 20)


    session.add_all(new_transactions)

    try:
        await session.commit()
        print(f" Сохранено {len(new_transactions)} транзакций в БД")
    except IntegrityError:
        await session.rollback()
        print("Обнаружены дубликаты, транзакции не сохранены")
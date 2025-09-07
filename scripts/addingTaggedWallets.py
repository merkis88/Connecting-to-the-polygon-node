import asyncio
import sys
import os

from sqlalchemy.exc import IntegrityError
from database.engine import get_db_session
from database.models.labeled_wallet import LabeledWallet, WalletLabel
from sqlalchemy import select

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

wallet_to_seed = [

    #SCAM
    {"address": "0x12cf2782b30451e2279a7da25a6922a933f48a60", "label": WalletLabel.SCAM,"source": "Hope Finance Exploit", "description": "Exploiter wallet"},
    {"address": "0x633a2902c6113b2cd2c3a31c034509673a3332d5", "label": WalletLabel.SCAM, "source": "Arbiscan Comments","description": "Reported phishing wallet"},
    {"address": "0x76916b11e222a77a1e1e048259d1e2b64a2ee6e9", "label": WalletLabel.SCAM, "source": "Sentiment Exploit","description": "Exploiter funds destination"},

    #SUSPICIOUS
    {"address": "0xa9a55734e3e32e01365823e2a3c7c8582f3d9d7f", "label": WalletLabel.SUSPICIOUS, "source": "MEV Bot Analysis", "description": "Active MEV bot (sandwich attacks)"},
    {"address": "0x2e65c08f435e8a4855cf1b4f2c510864388e2288", "label": WalletLabel.SUSPICIOUS, "source": "On-chain Analysis", "description": "Systematic airdrop hunter"},

    # LEGIT
    {"address": "0xdb6ab450178bab193459a1f18636f1e854b2a8d3", "label": WalletLabel.LEGIT, "source": "GMX Docs","description": "GMX: Rewards Router V2"},
    {"address": "0xebba467ecb6b21239178033189ceae27ca12eadf", "label": WalletLabel.LEGIT,"source": "Treasure DAO Website", "description": "Treasure DAO NFT Contract"},
    {"address": "0x0d8ee83f2a1b04be2172ca7b52d43e5a95616b2e", "label": WalletLabel.LEGIT,"source": "Arbitrum Foundation", "description": "Arbitrum Foundation: Token Vesting"},
]

async def uploading_data():
    async with get_db_session() as session:
        print("Сессия с бд получена")

        for wallet_data in wallet_to_seed:
            query = select(LabeledWallet).where(LabeledWallet.address == wallet_data["address"])
            result = await  session.execute(query)
            exiting_wallet = result.scalar_one_or_none()

            if exiting_wallet:
                print(f"Кошелёк {wallet_data['address']} уже есть, пропускаю")
                continue

            new_wallet = LabeledWallet(**wallet_data)
            session.add(new_wallet)
            print(f"\nГотовлю кошельки для добавления")

            try:
                await session.commit()
                print("Добавил в бд")
            except IntegrityError as e:
                await session.rolbeck()
                print(f"\nПроизошла ошибка: {e}")

if __name__ == "__main__":
    wallet_to_seed = [
        # SCAM
        {"address": "0x12cf2782b30451e2279a7da25a6922a933f48a60", "label": WalletLabel.SCAM,"source": "Hope Finance Exploit", "description": "Exploiter wallet"},
        {"address": "0x633a2902c6113b2cd2c3a31c034509673a3332d5", "label": WalletLabel.SCAM,"source": "Arbiscan Comments", "description": "Reported phishing wallet"},
        {"address": "0x76916b11e222a77a1e1e048259d1e2b64a2ee6e9", "label": WalletLabel.SCAM,"source": "Sentiment Exploit", "description": "Exploiter funds destination"},

        # SUSPICIOUS
        {"address": "0xa9a55734e3e32e01365823e2a3c7c8582f3d9d7f", "label": WalletLabel.SUSPICIOUS,"source": "MEV Bot Analysis", "description": "Active MEV bot (sandwich attacks)"},
        {"address": "0x2e65c08f435e8a4855cf1b4f2c510864388e2288", "label": WalletLabel.SUSPICIOUS,"source": "On-chain Analysis", "description": "Systematic airdrop hunter"},

        # LEGIT
        {"address": "0xdb6ab450178bab193459a1f18636f1e854b2a8d3", "label": WalletLabel.LEGIT, "source": "GMX Docs","description": "GMX: Rewards Router V2"},
        {"address": "0xebba467ecb6b21239178033189ceae27ca12eadf", "label": WalletLabel.LEGIT,"source": "Treasure DAO Website", "description": "Treasure DAO NFT Contract"},
        {"address": "0x0d8ee83f2a1b04be2172ca7b52d43e5a95616b2e", "label": WalletLabel.LEGIT,"source": "Arbitrum Foundation", "description": "Arbitrum Foundation: Token Vesting"},
    ]
    asyncio.run(uploading_data())


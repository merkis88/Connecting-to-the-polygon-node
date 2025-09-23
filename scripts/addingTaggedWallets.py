import asyncio
import sys
import os

from sqlalchemy.exc import IntegrityError
from database.engine import get_db_session
from database.models.labeled_wallet import LabeledWallet, WalletLabel
from sqlalchemy import select

wallet_to_seed = [
    # LEGIT - Биржевые кошельки (очень высокая активность)
    {"address": "0xf977814e90da44bfa03b6295a0616a897441acec", "label": WalletLabel.LEGIT, "source": "Binance","description": "Binance Hot Wallet - очень активный"},
    {"address": "0x28c6c06298d514db089934071355e5743bf21d60", "label": WalletLabel.LEGIT, "source": "Binance","description": "Binance 14 - высокий объем транзакций"},
    {"address": "0x21a31ee1afc51d94c2efccaa2092ad1028285549", "label": WalletLabel.LEGIT, "source": "Binance","description": "Binance 15 - институциональный кошелек"},
    {"address": "0x5bdf85216ec1e38D6458C870992A69e38e03F7Ef", "label": WalletLabel.LEGIT, "source": "Bitget","description": "Bitget 5 - биржевой кошелёк, 3 млн транзакций"},
    {"address": "0xcB89E891c581FBE0bea4Fac2ba9829D816515a81", "label": WalletLabel.LEGIT, "source": "Arbiscan","description": "Arbitrum: Sequencer Inbox - системный контракт для транзакций"},
    {"address": "0x34365f472a3af2ff8167970A519931437E2C2094", "label": WalletLabel.LEGIT, "source": "Arbiscan","description": "Обычный кошелёк на Arbitrum"},
    {"address": "0x7223AcA8801bB66dE35E76398ae1584D2D6a6393", "label": WalletLabel.LEGIT, "source": "Arbiscan","description": "Обычный кошелёк на Arbitrum"},
    {"address": "0x4DAEDd0c7906b0d5e7E5805f283B0d8805735971", "label": WalletLabel.LEGIT, "source": "Arbiscan","description": "Обычный кошелёк на Arbitrum"},
    {"address": "0x4BAe2D1B5D3a9038bC11b36dA072155313BAaaE2", "label": WalletLabel.LEGIT, "source": "Arbiscan","description": "Обычный кошелёк на Arbitrum"},
    {"address": "0x0fcFcBDCc3a7994372332b29c73488811f0A2072", "label": WalletLabel.LEGIT, "source": "Arbiscan","description": "Обычный кошелёк на Arbitrum"},
    {"address": "0x07ED0d53F8198EFa5740B80881D4eFD05287d83B", "label": WalletLabel.LEGIT, "source": "Arbiscan","description": "Обычный кошелёк на Arbitrum"},
    {"address": "0xFAba2E91bdeF073117aBA162e5790F54ff82F3E8", "label": WalletLabel.LEGIT, "source": "Arbiscan","description": "Обычный кошелёк на Arbitrum"},
    {"address": "0x02d6a726d9f7397a31E2AD648a6bd4ECdB97AD2A", "label": WalletLabel.LEGIT, "source": "Arbiscan","description": "Обычный кошелёк на Arbitrum"},
    {"address": "0x63DFE4e34A3bFC00eB0220786238a7C6cEF8Ffc4", "label": WalletLabel.LEGIT, "source": "WOO X","description": "WOO X - высокий объём"},
    {"address": "0x9b64203878F24eB0CDF55c8c6fA7D08Ba0cF77E5", "label": WalletLabel.LEGIT, "source": "MEXC","description": "MEXC 10 - высокий объём и очень активный"},
    {"address": "0x77134cbC06cB00b66F4c7e623D5fdBF6777635EC", "label": WalletLabel.LEGIT, "source": "Bitfinex","description": "Bitfinex: Hot Wallet - горячий кошелёк"},
    {"address": "0xB38e8c17e38363aF6EbdCb3dAE12e0243582891D", "label": WalletLabel.LEGIT, "source": "Binance","description": "Binance 54 - огромный объём и транзакций"},


    # НОВЫЕ LEGIT - из Arbiscan Top Accounts
    {"address": "0x131F001aF400D5f212e1894846469FBa70f8bCc9", "label": WalletLabel.LEGIT,"source": "Arbiscan Top Accounts", "description": "Bithumb 8 - биржевой кошелек"},

    # LEGIT - DeFi протоколы (высокая активность)
    {"address": "0x82af49447d8a07e3bd95bd0d56f35241523fbab1", "label": WalletLabel.LEGIT, "source": "WETH Contract","description": "Wrapped ETH на Arbitrum"},
    {"address": "0xff970a61a04b1ca14834a43f5de4533ebddb5cc8", "label": WalletLabel.LEGIT, "source": "USDC Contract","description": "USDC контракт токена"},
    {"address": "0x912ce59144191c1204e64559fe8253a0e49e6548", "label": WalletLabel.LEGIT, "source": "ARB Token","description": "Arbitrum токен управления"},

    # LEGIT - DEX и DeFi (средняя-высокая активность)
    {"address": "0x1111111254eeb25477b68fb85ed929f73a960582", "label": WalletLabel.LEGIT, "source": "1inch","description": "1inch v4 router - DEX агрегатор"},
    {"address": "0xe592427a0aece92de3edee1f18e0157c05861564", "label": WalletLabel.LEGIT, "source": "Uniswap","description": "SwapRouter - DEX"},
    {"address": "0x68b3465833fb72a70ecdf485e0e4c7bd8665fc45", "label": WalletLabel.LEGIT, "source": "Uniswap V3","description": "SwapRouter02 - активный DEX"},


    # SUSPICIOUS - MEV боты и высокочастотные трейдеры
    {"address": "0x77696bb39917c91a0c3908d577d5e322095425ca", "label": WalletLabel.SUSPICIOUS, "source": "MEV Scanner","description": "MEV searcher - арбитражный бот"},
    {"address": "0x48c04ed5691981c42154c6167398f95e8f38a7ff", "label": WalletLabel.SUSPICIOUS,"source": "Whale Analysis", "description": "Подозрительные паттерны кита"},

    # НОВЫЕ SUSPICIOUS
    # Кошельки-создатели подозрительных токенов (данные GoPlus Security)
    {"address": "0xC0a56aeE755Bd397235367008f7c2c4599768395", "label": WalletLabel.SUSPICIOUS, "source": "GoPlus Security", "description": "Создатель подозрительного токена 0x53e562..."},
    {"address": "0x0ce72A0F7249412dF38D656695c9FA3644f40D78", "label": WalletLabel.SUSPICIOUS, "source": "GoPlus Security", "description": "Создатель подозрительного токена 0x1c8391..."},
    # Типичный "аирдроп-хантер" или сибилл-адрес
    {"address": "0x000000a432c5608502591a3c5a320504bb053c0e", "label": WalletLabel.SUSPICIOUS, "source": "Nansen", "description": "Airdrop Hunter / Sybil Address - множество однотипных транзакций"},

    # SCAM - Документированные эксплойтеры (осторожно с классификацией)
    {"address": "0x59728544b08ab483533076417fbbb2fd0b17ce3a", "label": WalletLabel.SCAM, "source": "Rug Pull","description": "Бенефициар rug pull в DeFi"},

    # НОВЫЕ SCAM
    # Адреса, связанные с санкционным миксером Tornado Cash
    {"address": "0x8589427373D6D84E98730D7795D8f6f8731FDA16", "label": WalletLabel.SCAM, "source": "OFAC Sanctions", "description": "Tornado Cash 1 ETH - санкционный адрес"},
    {"address": "0xFD8610d20aA15b7B2E3Be39B396a1bC3516c7144", "label": WalletLabel.SCAM, "source": "OFAC Sanctions", "description": "Tornado Cash 100 ETH - санкционный адрес"},
    # Взломщик протокола Euler Finance (крупный взлом)
    {"address": "0x01e2919679362dfbc9ee1644ba9c6da6d6245bb1", "label": WalletLabel.SCAM, "source": "Euler Hack", "description": "Euler Finance Exploiter - задокументированный взломщик"},
    # Адрес, помеченный Etherscan как фишинговый
    {"address": "0x00001186425d6b41a27e39e52c2b3d8aa8b27345", "label": WalletLabel.SCAM, "source": "Etherscan Label", "description": "Fake_Phishing18930 - адрес фишинговой атаки"},
    # Взломщик протокола Ronin Bridge (один из крупнейших взломов в истории)
    {"address": "0x098B716B8Aaf21512996dC57EB0615e2383E2f96", "label": WalletLabel.SCAM, "source": "Ronin Hack", "description": "Ronin Bridge Exploiter - крупный взломщик"},

    # Дополнительные LEGIT для баланса датасета
    {"address": "0xa69babef1ca67a37ffaf7a485dfff3382056e78c", "label": WalletLabel.LEGIT, "source": "Coinbase","description": "Coinbase институциональный кошелек"},
    {"address": "0x489ee077994b6658eafa855c308275ead8097c4a", "label": WalletLabel.LEGIT, "source": "OpenSea","description": "OpenSea реестр - NFT маркетплейс"},
]


async def uploading_data():
    async with get_db_session() as session:
        print("Сессия с БД получена")

        for wallet_data in wallet_to_seed:
            query = select(LabeledWallet).where(LabeledWallet.address == wallet_data["address"])
            result = await session.execute(query)
            existing_wallet = result.scalar_one_or_none()

            if existing_wallet:
                print(f"Кошелек {wallet_data['address']} уже есть, пропускаю")
                continue

            new_wallet = LabeledWallet(**wallet_data)
            session.add(new_wallet)
            print(f"Готовлю кошелек для добавления: {wallet_data['address']} ({wallet_data['label'].value})")

            try:
                await session.commit()
                print(f"Добавил в БД: {wallet_data['description']}")
            except IntegrityError as e:
                await session.rollback()
                print(f"Произошла ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(uploading_data())
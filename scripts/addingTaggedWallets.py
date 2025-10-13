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

    # LEGIT - Опытные пользователи, боты, мультисиги
    {"address": "0xACe9b2a0949dBC89D4c1da1880385F145234F2b4", "label": WalletLabel.LEGIT, "source": "Etherscan Label", "description": "CoW Protocol Solver - MEV-бот"},
    {"address": "0x196beae17C9577256A4C20d72a3C01cAe5D00e9E", "label": WalletLabel.LEGIT, "source": "Etherscan Label", "description": "Gnosis Safe Proxy - Мультисиг кошелек"},
    {"address": "0x8c19E9AD4D2c3db1a0966b1b91DE325274E233cf", "label": WalletLabel.LEGIT, "source": "On-chain Analysis", "description": "Активный DeFi пользователь"},
    {"address": "0xB61D188c0fcab00843Aa28369BfF41A0d1385a0e", "label": WalletLabel.LEGIT, "source": "On-chain Analysis", "description": "Активный DeFi пользователь"},
    {"address": "0xB8BAa1A6cCc6bfBf17a3Ca3B7Fe3654936EFc656", "label": WalletLabel.LEGIT, "source": "On-chain Analysis", "description": "Активный DeFi пользователь"},
    {"address": "0x6E4Cdab88293372D23a992448B21D50b5F9959Ff", "label": WalletLabel.LEGIT, "source": "On-chain Analysis", "description": "Активный DeFi пользователь"},
    {"address": "0x3D469ef18C9e514e5DcdC6Cb2dFd33c4FCF3bc86", "label": WalletLabel.LEGIT, "source": "On-chain Analysis", "description": "Активный DeFi пользователь"},
    {"address": "0x8c6dF41fD13F18148c5A407F269eAc9Dc10cE736", "label": WalletLabel.LEGIT, "source": "ENS", "description": "Опытный пользователь (ENS: cagyafar.eth)"},
    {"address": "0x108eF0197187B2eF90f9cECA656C6cE801AC7B63", "label": WalletLabel.LEGIT, "source": "ENS", "description": "Опытный пользователь (ENS: garanori.eth)"},
    {"address": "0xEd2e8a73F44B62C723DC286Fc0193321D512F8aA", "label": WalletLabel.LEGIT, "source": "ENS", "description": "Опытный пользователь (ENS: bularor.eth)"},
    {"address": "0x80FEFB61E6B1f4b66acFC1E5E34812Afd097077f", "label": WalletLabel.LEGIT, "source": "ENS", "description": "Опытный пользователь (ENS: rkidist.eth)"},
    {"address": "0xa33126Ceb7b7452af6b1e97400cc5665a8bBF74B", "label": WalletLabel.LEGIT, "source": "ENS", "description": "Опытный пользователь (ENS: xiertfa.eth)"},
    {"address": "0x0d21d6CF1E927835B8E611240B9b68Ac58cf7b8f", "label": WalletLabel.LEGIT, "source": "ENS", "description": "Опытный пользователь (ENS: amanth.eth)"},
    {"address": "0x555caad39E30afa178973418295F5b380f88cd99", "label": WalletLabel.LEGIT, "source": "ENS", "description": "Опытный пользователь (ENS: stuedota.eth)"},
    {"address": "0xe225215497dE484c415FA508875555393f358b07", "label": WalletLabel.LEGIT, "source": "ENS", "description": "Опытный пользователь (ENS: haiterar.eth)"},
    {"address": "0xdeF6FB9Ff04f207eD4dc8E63147692c60b5811e1", "label": WalletLabel.LEGIT, "source": "ENS", "description": "Опытный пользователь (ENS: ganthon.eth)"},
    {"address": "0xa69babef1ca67a37ffaf7a485dfff3382056e78c", "label": WalletLabel.LEGIT, "source": "Coinbase","description": "Coinbase институциональный кошелек"},
    {"address": "0x489ee077994b6658eafa855c308275ead8097c4a", "label": WalletLabel.LEGIT, "source": "OpenSea","description": "OpenSea реестр - NFT маркетплейс"},

    # SUSPICIOUS - MEV боты, создатели подозрительных токенов, сибиллы
    {"address": "0x77696bb39917c91a0c3908d577d5e322095425ca", "label": WalletLabel.SUSPICIOUS, "source": "MEV Scanner","description": "MEV searcher - арбитражный бот"},
    {"address": "0x48c04ed5691981c42154c6167398f95e8f38a7ff", "label": WalletLabel.SUSPICIOUS,"source": "Whale Analysis", "description": "Подозрительные паттерны кита"},
    {"address": "0xC0a56aeE755Bd397235367008f7c2c4599768395", "label": WalletLabel.SUSPICIOUS, "source": "GoPlus Security", "description": "Создатель подозрительного токена (создал 1 контракт)"},
    {"address": "0x000000a432c5608502591a3c5a320504bb053c0e", "label": WalletLabel.SUSPICIOUS, "source": "Nansen", "description": "Airdrop Hunter / Sybil Address - множество однотипных транзакций"},

    # SCAM - Документированные взломщики, фишеры, санкционные адреса
    {"address": "0x59728544b08ab483533076417fbbb2fd0b17ce3a", "label": WalletLabel.SCAM, "source": "Rug Pull","description": "Бенефициар rug pull в DeFi"},
    {"address": "0x8589427373D6D84E98730D7795D8f6f8731FDA16", "label": WalletLabel.SCAM, "source": "OFAC Sanctions", "description": "Tornado Cash 1 ETH - санкционный адрес"},
    {"address": "0xFD8610d20aA15b7B2E3Be39B396a1bC3516c7144", "label": WalletLabel.SCAM, "source": "OFAC Sanctions", "description": "Tornado Cash 100 ETH - санкционный адрес"},
    {"address": "0x01e2919679362dfbc9ee1644ba9c6da6d6245bb1", "label": WalletLabel.SCAM, "source": "Euler Hack", "description": "Euler Finance Exploiter - задокументированный взломщик"},
    {"address": "0x00001186425d6b41a27e39e52c2b3d8aa8b27345", "label": WalletLabel.SCAM, "source": "Etherscan Label", "description": "Fake_Phishing18930 - адрес фишинговой атаки"},
    {"address": "0x098B716B8Aaf21512996dC57EB0615e2383E2f96", "label": WalletLabel.SCAM, "source": "Ronin Hack", "description": "Ronin Bridge Exploiter - крупный взломщик"},
    {"address": "0x0ce72A0F7249412dF38D656695c9FA3644f40D78", "label": WalletLabel.SCAM, "source": "GoPlus Security", "description": "Серийный создатель скам-токенов (14 контрактов)"},
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
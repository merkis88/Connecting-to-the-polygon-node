import asyncio
import sys
import os

from sqlalchemy.exc import IntegrityError
from database.engine import get_db_session
from database.models.labeled_wallet import LabeledWallet, WalletLabel
from sqlalchemy import select

wallet_to_seed = [
    {"address": "0xf977814e90da44bfa03b6295a0616a897441acec", "label": WalletLabel.LEGIT, "source": "Binance",
     "description": "Binance Hot Wallet - очень активный"},
    {"address": "0x28c6c06298d514db089934071355e5743bf21d60", "label": WalletLabel.LEGIT, "source": "Binance",
     "description": "Binance 14 - высокий объем транзакций"},
    {"address": "0x21a31ee1afc51d94c2efccaa2092ad1028285549", "label": WalletLabel.LEGIT, "source": "Binance",
     "description": "Binance 15 - институциональный кошелек"},
    {"address": "0x5bdf85216ec1e38D6458C870992A69e38e03F7Ef", "label": WalletLabel.LEGIT, "source": "Bitget",
     "description": "Bitget 5 - биржевой кошелёк"},
    {"address": "0xcB89E891c581FBE0bea4Fac2ba9829D816515a81", "label": WalletLabel.LEGIT, "source": "Arbiscan",
     "description": "Arbitrum: Sequencer Inbox"},
    {"address": "0x63DFE4e34A3bFC00eB0220786238a7C6cEF8Ffc4", "label": WalletLabel.LEGIT, "source": "WOO X",
     "description": "WOO X - высокий объём"},
    {"address": "0x9b64203878F24eB0CDF55c8c6fA7D08Ba0cF77E5", "label": WalletLabel.LEGIT, "source": "MEXC",
     "description": "MEXC 10 - высокий объём"},
    {"address": "0x77134cbC06cB00b66F4c7e623D5fdBF6777635EC", "label": WalletLabel.LEGIT, "source": "Bitfinex",
     "description": "Bitfinex: Hot Wallet"},
    {"address": "0xB38e8c17e38363aF6EbdCb3dAE12e0243582891D", "label": WalletLabel.LEGIT, "source": "Binance",
     "description": "Binance 54 - огромный объём"},
    {"address": "0x131F001aF400D5f212e1894846469FBa70f8bCc9", "label": WalletLabel.LEGIT,
     "source": "Arbiscan Top Accounts", "description": "Bithumb 8"},

    {"address": "0x4dbd4fc535ac27206064b68ffcf827b0a60bab3f", "label": WalletLabel.LEGIT, "source": "Arbiscan Top",
     "description": "Binance 7 - Cold storage"},
    {"address": "0x4976a4a02f38326660d17bf34b431dc6e2eb2327", "label": WalletLabel.LEGIT, "source": "Arbiscan Top",
     "description": "Binance 49"},
    {"address": "0x0d0707963952f2fba59dd06f2b425ace40b492fe", "label": WalletLabel.LEGIT, "source": "Arbiscan Top",
     "description": "Gate.io Hot Wallet"},
    {"address": "0x1b02da8cb0d097eb8d57a175b88c7d8b47997506", "label": WalletLabel.LEGIT, "source": "Arbiscan Top",
     "description": "Sushiswap Router"},
    {"address": "0x46340b20830761efd32832A74d7169B29FEB9758", "label": WalletLabel.LEGIT, "source": "Arbiscan Top",
     "description": "Huobi Exchange"},

    # LEGIT - DeFi протоколы (контракты)
    {"address": "0x82af49447d8a07e3bd95bd0d56f35241523fbab1", "label": WalletLabel.LEGIT, "source": "WETH Contract",
     "description": "Wrapped ETH на Arbitrum"},
    {"address": "0xff970a61a04b1ca14834a43f5de4533ebddb5cc8", "label": WalletLabel.LEGIT, "source": "USDC Contract",
     "description": "USDC контракт токена"},
    {"address": "0x912ce59144191c1204e64559fe8253a0e49e6548", "label": WalletLabel.LEGIT, "source": "ARB Token",
     "description": "Arbitrum токен управления"},
    {"address": "0x1111111254eeb25477b68fb85ed929f73a960582", "label": WalletLabel.LEGIT, "source": "1inch",
     "description": "1inch v4 router - DEX агрегатор"},
    {"address": "0xe592427a0aece92de3edee1f18e0157c05861564", "label": WalletLabel.LEGIT, "source": "Uniswap",
     "description": "SwapRouter - DEX"},
    {"address": "0x68b3465833fb72a70ecdf485e0e4c7bd8665fc45", "label": WalletLabel.LEGIT, "source": "Uniswap V3",
     "description": "SwapRouter02 - активный DEX"},

    # НОВЫЕ DeFi протоколы
    {"address": "0xfc5A1A6EB076a2C7aD06eD22C90d7E710E35ad0a", "label": WalletLabel.LEGIT, "source": "GMX Protocol",
     "description": "GMX V2 Contract"},
    {"address": "0x489ee077994b6658eafa855c308275ead8097c4a", "label": WalletLabel.LEGIT, "source": "OpenSea",
     "description": "OpenSea Seaport"},
    {"address": "0xba12222222228d8ba445958a75a0704d566bf2c8", "label": WalletLabel.LEGIT, "source": "Balancer",
     "description": "Balancer V2 Vault"},
    {"address": "0x1231deb6f5749ef6ce6943a275a1d3e7486f4eae", "label": WalletLabel.LEGIT, "source": "LiFi",
     "description": "LiFi Diamond - Bridge aggregator"},
    {"address": "0xdef1c0ded9bec7f1a1670819833240f027b25eff", "label": WalletLabel.LEGIT, "source": "0x Protocol",
     "description": "0x Exchange Proxy"},
    {"address": "0x3fc91a3afd70395cd496c647d5a6cc9d4b2b7fad", "label": WalletLabel.LEGIT, "source": "Uniswap",
     "description": "Uniswap Universal Router"},
    {"address": "0x5e325eda8064b456f4781070c0738d849c824258", "label": WalletLabel.LEGIT, "source": "Stargate",
     "description": "Stargate Router"},
    {"address": "0xd50cf00b6e600dd036ba8ef475677d816d6c4281", "label": WalletLabel.LEGIT, "source": "Radiant Capital",
     "description": "Radiant Lending Pool"},
    {"address": "0x53bf833a5d6c4dda888f69c22c88c9f356a41614", "label": WalletLabel.LEGIT, "source": "Stargate",
     "description": "Stargate Bridge"},
    {"address": "0xfd086bc7cd5c481dcc9c85ebe478a1c0b69fcbb9", "label": WalletLabel.LEGIT, "source": "USDT Contract",
     "description": "Tether USDT on Arbitrum"},
    {"address": "0x2f2a2543b76a4166549f7aab2e75bef0aefc5b0f", "label": WalletLabel.LEGIT, "source": "WBTC Contract",
     "description": "Wrapped Bitcoin on Arbitrum"},
    {"address": "0xda10009cbd5d07dd0cecc66161fc93d7c9000da1", "label": WalletLabel.LEGIT, "source": "DAI Contract",
     "description": "DAI Stablecoin on Arbitrum"},
    {"address": "0xaf88d065e77c8cc2239327c5edb3a432268e5831", "label": WalletLabel.LEGIT, "source": "USDC Native",
     "description": "USDC Native on Arbitrum"},
    {"address": "0x4e352cf164e64adcbad318c3a1e222e9eba4ce42", "label": WalletLabel.LEGIT, "source": "MUX Protocol",
     "description": "MUX Protocol Vault"},


    # LEGIT - Опытные пользователи, боты
    {"address": "0xACe9b2a0949dBC89D4c1da1880385F145234F2b4", "label": WalletLabel.LEGIT, "source": "Etherscan Label",
     "description": "CoW Protocol Solver - MEV-бот"},
    {"address": "0x196beae17C9577256A4C20d72a3C01cAe5D00e9E", "label": WalletLabel.LEGIT, "source": "Etherscan Label",
     "description": "Gnosis Safe Proxy - Мультисиг"},
    {"address": "0x8c19E9AD4D2c3db1a0966b1b91DE325274E233cf", "label": WalletLabel.LEGIT, "source": "On-chain Analysis",
     "description": "Активный DeFi пользователь"},
    {"address": "0xB61D188c0fcab00843Aa28369BfF41A0d1385a0e", "label": WalletLabel.LEGIT, "source": "On-chain Analysis",
     "description": "Активный DeFi пользователь"},
    {"address": "0xB8BAa1A6cCc6bfBf17a3Ca3B7Fe3654936EFc656", "label": WalletLabel.LEGIT, "source": "On-chain Analysis",
     "description": "Активный DeFi пользователь"},
    {"address": "0x6E4Cdab88293372D23a992448B21D50b5F9959Ff", "label": WalletLabel.LEGIT, "source": "On-chain Analysis",
     "description": "Активный DeFi пользователь"},
    {"address": "0x3D469ef18C9e514e5DcdC6Cb2dFd33c4FCF3bc86", "label": WalletLabel.LEGIT, "source": "On-chain Analysis",
     "description": "Активный DeFi пользователь"},
    {"address": "0x8c6dF41fD13F18148c5A407F269eAc9Dc10cE736", "label": WalletLabel.LEGIT, "source": "ENS",
     "description": "Опытный пользователь (ENS: cagyafar.eth)"},
    {"address": "0x108eF0197187B2eF90f9cECA656C6cE801AC7B63", "label": WalletLabel.LEGIT, "source": "ENS",
     "description": "Опытный пользователь (ENS: garanori.eth)"},
    {"address": "0xEd2e8a73F44B62C723DC286Fc0193321D512F8aA", "label": WalletLabel.LEGIT, "source": "ENS",
     "description": "Опытный пользователь (ENS: bularor.eth)"},
    {"address": "0x80FEFB61E6B1f4b66acFC1E5E34812Afd097077f", "label": WalletLabel.LEGIT, "source": "ENS",
     "description": "Опытный пользователь (ENS: rkidist.eth)"},
    {"address": "0xa33126Ceb7b7452af6b1e97400cc5665a8bBF74B", "label": WalletLabel.LEGIT, "source": "ENS",
     "description": "Опытный пользователь (ENS: xiertfa.eth)"},
    {"address": "0x0d21d6CF1E927835B8E611240B9b68Ac58cf7b8f", "label": WalletLabel.LEGIT, "source": "ENS",
     "description": "Опытный пользователь (ENS: amanth.eth)"},
    {"address": "0x555caad39E30afa178973418295F5b380f88cd99", "label": WalletLabel.LEGIT, "source": "ENS",
     "description": "Опытный пользователь (ENS: stuedota.eth)"},
    {"address": "0xe225215497dE484c415FA508875555393f358b07", "label": WalletLabel.LEGIT, "source": "ENS",
     "description": "Опытный пользователь (ENS: haiterar.eth)"},
    {"address": "0xdeF6FB9Ff04f207eD4dc8E63147692c60b5811e1", "label": WalletLabel.LEGIT, "source": "ENS",
     "description": "Опытный пользователь (ENS: ganthon.eth)"},
    {"address": "0xa69babef1ca67a37ffaf7a485dfff3382056e78c", "label": WalletLabel.LEGIT, "source": "Coinbase",
     "description": "Coinbase институциональный кошелек"},
    {"address": "0x00000000219ab540356cbb839cbe05303d7705fa", "label": WalletLabel.LEGIT,
     "source": "Ethereum Foundation", "description": "ETH2 Deposit Contract"},
    {"address": "0xd8da6bf26964af9d7eed9e03e53415d37aa96045", "label": WalletLabel.LEGIT, "source": "Vitalik Buterin",
     "description": "Vitalik.eth - Ethereum founder"},
    {"address": "0xab5801a7d398351b8be11c439e05c5b3259aec9b", "label": WalletLabel.LEGIT, "source": "Vitalik Buterin",
     "description": "Vitalik wallet 2"},
    {"address": "0x220866b1a2219f40e72f5c628b65d54268ca3a9d", "label": WalletLabel.LEGIT, "source": "Binance",
     "description": "Binance Beacon Depositor"},
    {"address": "0x0000000000a39bb272e79075ade125fd351887ac", "label": WalletLabel.LEGIT, "source": "Blur Marketplace",
     "description": "Blur NFT Marketplace"},
    {"address": "0xc36442b4a4522e871399cd717abdd847ab11fe88", "label": WalletLabel.LEGIT, "source": "Uniswap",
     "description": "Uniswap V3 Positions NFT"},
    {"address": "0x000000000000ad05ccc4f10045630fb830b95127", "label": WalletLabel.LEGIT, "source": "LayerZero",
     "description": "LayerZero Endpoint"},
    {"address": "0x267be1c1d684f78cb4f6a176c4911b741e4ffdc0", "label": WalletLabel.LEGIT, "source": "Crypto.com",
     "description": "Crypto.com Exchange"},
    {"address": "0x6cc5f688a315f3dc28a7781717a9a798a59fda7b", "label": WalletLabel.LEGIT, "source": "OKX",
     "description": "OKX Exchange Wallet"},
    {"address": "0x503828976d22510aad0201ac7ec88293211d23da", "label": WalletLabel.LEGIT, "source": "KuCoin",
     "description": "KuCoin Hot Wallet"},


    # SUSPICIOUS - MEV боты, Sybil, подозрительные
    {"address": "0x77696bb39917c91a0c3908d577d5e322095425ca", "label": WalletLabel.SUSPICIOUS, "source": "MEV Scanner",
     "description": "MEV searcher - арбитражный бот"},
    {"address": "0x48c04ed5691981c42154c6167398f95e8f38a7ff", "label": WalletLabel.SUSPICIOUS,
     "source": "Whale Analysis", "description": "Подозрительные паттерны кита"},
    {"address": "0xC0a56aeE755Bd397235367008f7c2c4599768395", "label": WalletLabel.SUSPICIOUS,
     "source": "GoPlus Security", "description": "Создатель подозрительного токена (1 контракт)"},
    {"address": "0x1ddbf60792aac896aed180eaa6810fccd7839ada", "label": WalletLabel.SUSPICIOUS, "source": "Arbitrum Sybil List",
     "description": "Sybil-кошелек (Cluster 319) - подтвержденный Nansen/Hop Protocol"},
    {"address": "0xc7bb9b943fd2a04f651cc513c17eb5671b90912d", "label": WalletLabel.SUSPICIOUS, "source": "Arbitrum Sybil List",
     "description": "Sybil-кошелек (Cluster 1544) - подтвержденный Nansen/Hop Protocol"},
    {"address": "0x3fb4c01b5ceecf307010f84c9a858aeaeab0b9fa", "label": WalletLabel.SUSPICIOUS, "source": "Arbitrum Sybil List",
     "description": "Sybil-кошелек (Cluster 2554) - подтвержденный Nansen/Hop Protocol"},
    {"address": "0x15bc18bb8c378c94c04795d72621957497130400", "label": WalletLabel.SUSPICIOUS, "source": "Arbitrum Sybil List",
     "description": "Sybil-кошелек (Cluster 3316) - подтвержденный Nansen/Hop Protocol"},

    # SCAM - Документированные хаки, фишинг
    {"address": "0x59728544b08ab483533076417fbbb2fd0b17ce3a", "label": WalletLabel.SCAM, "source": "Rug Pull",
     "description": "Бенефициар rug pull в DeFi"},
    {"address": "0x59d4087f3ff91da6a492b596cbde7140c34afb19", "label": WalletLabel.SCAM,
     "source": "Arkham Intelligence", "description": "ARB Airdrop Phishing Attack"},
    {"address": "0xd90e2f925DA726b50C4Ed8D0Fb90Ad053324F31b", "label": WalletLabel.SCAM, "source": "OFAC Sanctions",
     "description": "Tornado Cash Router"},
    {"address": "0x910Cbd523D972eb0a6f4cAe4618aD62622b39DbF", "label": WalletLabel.SCAM, "source": "OFAC Sanctions",
     "description": "Tornado Cash Instance"},
    {"address": "0xA160cdAB225685dA1d56aa342Ad8841c3b53f291", "label": WalletLabel.SCAM, "source": "OFAC Sanctions",
     "description": "Tornado Cash Pool"},
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
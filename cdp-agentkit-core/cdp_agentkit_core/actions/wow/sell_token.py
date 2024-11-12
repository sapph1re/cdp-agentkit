from cdp import Wallet
from uniswap.index import get_has_graduated

from cdp_agentkit_core.actions.wow.constants import (
    WOW_ABI,
)
from cdp_agentkit_core.actions.wow.quotes import get_sell_quote

WOW_SELL_TOKEN_PROMPT = """
This tool will sell a Zora Wow ERC20 memecoin for ETH. This tool takes the WOW token contract address, and the amount of tokens to sell (in wei, meaning 1 is 1 wei or 0.000000000000000001 of the token). It is only supported on Base Sepolia and Base Mainnet.
"""


async def sell_wow_tokens(wallet: Wallet, contract_address: str, amount_tokens: str):
    """Sell WOW tokens for ETH.

    Args:
        wallet (Wallet): The wallet to sell the tokens from.
        contract_address (str): The WOW token contract address, such as `0x036CbD53842c5426634e7929541eC2318f3dCF7e`
        amount_tokens (str): Amount of tokens to sell (in wei), meaning 1 is 1 wei or 0.000000000000000001 of the token

    """
    # Get quote for selling
    eth_quote = await get_sell_quote(contract_address, amount_tokens)
    has_graduated = get_has_graduated(contract_address)

    # Multiply by 98/100 and floor to get 98% of quote as minimum (slippage protection)
    min_eth = str(int((eth_quote * 98) // 100))

    invocation = wallet.invoke_contract(
        contract_address=contract_address,
        method="sell",
        abi=WOW_ABI,
        args={
            "tokensToSell": str(amount_tokens),
            "recipient": wallet.default_address.address_id,
            "orderReferrer": "0x0000000000000000000000000000000000000000",
            "comment": "",
            "expectedMarketType": has_graduated and "1" or "0",
            "minPayoutSize": min_eth,
            "sqrtPriceLimitX96": "0",
        },
    ).wait()

    return invocation

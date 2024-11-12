from collections.abc import Callable

from cdp import Wallet
from pydantic import BaseModel, Field

from cdp_agentkit_core.actions.cdp_action import CdpAction
from cdp_agentkit_core.actions.wow.constants import (
    WOW_ABI,
)
from cdp_agentkit_core.actions.wow.quotes import get_sell_quote
from cdp_agentkit_core.actions.wow.uniswap.index import get_has_graduated

WOW_SELL_TOKEN_PROMPT = """
This tool will sell a Zora Wow ERC20 memecoin for ETH. This tool takes the WOW token contract address, and the amount of tokens to sell (in wei, meaning 1 is 1 wei or 0.000000000000000001 of the token). The minimum to sell is 100000000000000 wei which is 0.0000001 ether. The amount is a string and cannot have any decimal points, since the unit of measurement is wei. Make sure to use the exact amount provided, and if there's any doubt, check by getting more information before continuing with the action. It is only supported on Base Sepolia and Base Mainnet.
"""


class WowSellTokenInput(BaseModel):
    """Input argument schema for sell token action."""

    contract_address: str = Field(
        ...,
        description="The WOW token contract address, such as `0x036CbD53842c5426634e7929541eC2318f3dCF7e`",
    )

    amount_tokens: str = Field(
        ...,
        description="Amount of tokens to sell (in wei), meaning 1 is 1 wei or 0.000000000000000001 of the token",
    )


def sell_wow_tokens(wallet: Wallet, contract_address: str, amount_tokens: str):
    """Sell WOW tokens for ETH.

    Args:
        wallet (Wallet): The wallet to sell the tokens from.
        contract_address (str): The WOW token contract address, such as `0x036CbD53842c5426634e7929541eC2318f3dCF7e`
        amount_tokens (str): Amount of tokens to sell (in wei), meaning 1 is 1 wei or 0.000000000000000001 of the token

    """
    # Get quote for selling
    eth_quote = get_sell_quote(wallet.network_id, contract_address, amount_tokens)
    has_graduated = get_has_graduated(wallet.network_id, contract_address)

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


class WowSellTokenAction(CdpAction):
    """Zora Wow sell token action."""

    name: str = "wow_sell_token"
    description: str = WOW_SELL_TOKEN_PROMPT
    args_schema: type[BaseModel] | None = WowSellTokenInput
    func: Callable[..., str] = sell_wow_tokens

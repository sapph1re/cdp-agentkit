from collections.abc import Callable

from cdp import Wallet
from pydantic import BaseModel, Field
from uniswap import get_has_graduated

from cdp_agentkit_core.actions import CdpAction
from cdp_agentkit_core.actions.wow.constants import (
    WOW_ABI,
)
from cdp_agentkit_core.actions.wow.quotes import get_buy_quote

WOW_BUY_TOKEN_PROMPT = """
This tool will buy a Zora Wow ERC20 memecoin with ETH. This tool takes the WOW token contract address, the address to receive the tokens, and the amount of ETH to spend (in wei, meaning "1" is 1 wei or 0.000000000000000001 of ETH). It is only supported on Base Sepolia and Base Mainnet.
"""


class WowBuyTokenInput(BaseModel):
    """Input argument schema for buy token action."""

    contract_address: str = Field(
        ...,
        description="The WOW token contract address, such as `0x036CbD53842c5426634e7929541eC2318f3dCF7e`",
    )

    recipient: str = Field(
        ...,
        description="Address to receive the tokens, e.g. the agent's wallet address such as `0x036CbD53842c5426634e7929541eC2318f3dCF7e`",
    )

    amount_eth: str = Field(
        ...,
        description="Amount of ETH to spend (in wei), meaning 1 is 1 wei or 0.000000000000000001 of ETH",
    )


async def wow_buy_token(wallet: Wallet, contract_address: str, amount_eth: str) -> str:
    """Buy a Zora Wow ERC20 memecoin with ETH.

    Args:
        wallet (Wallet): The wallet to create the token from.
        contract_address (str): The WOW token contract address, such as `0x036CbD53842c5426634e7929541eC2318f3dCF7e`
        recipient (str): Address to receive the tokens, e.g. the agent's wallet address such as `0x036CbD53842c5426634e7929541eC2318f3dCF7e`
        amount_eth (str): Amount of ETH to spend (in wei), meaning 1 is 1 wei or 0.000000000000000001 of ETH

    Returns:
        str: A message containing the token purchase details.

    """
    # Get quote
    token_quote = await get_buy_quote(contract_address, amount_eth)

    # Multiply by 99/100 and floor to get 99% of quote as minimum
    min_tokens = str(int((token_quote * 99) // 100))  # Using integer division to floor the result

    has_graduated = get_has_graduated(contract_address)
    print(f"Address: {wallet.default_address.address_id}")
    print(min_tokens)
    invocation = wallet.invoke_contract(
        contract_address=contract_address,
        method="buy",
        abi=WOW_ABI,
        args={
            "recipient": wallet.default_address.address_id,
            "refundRecipient": wallet.default_address.address_id,
            "orderReferrer": "0x0000000000000000000000000000000000000000",
            "expectedMarketType": has_graduated and "1" or "0",
            "minOrderSize": min_tokens,
            "sqrtPriceLimitX96": "0",  # TODO
            "comment": "",
        },
        amount=amount_eth,
        asset_id="wei",
    ).wait()

    return f"Purchased WoW ERC20 memecoin with transaction hash: {invocation.transaction.transaction_hash}"


class WowBuyTokenAction(CdpAction):
    """Zora Wow buy token action."""

    name: str = "wow_buy_token"
    description: str = WOW_BUY_TOKEN_PROMPT
    args_schema: type[BaseModel] | None = WowBuyTokenInput
    func: Callable[..., str] = wow_buy_token

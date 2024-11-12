from cdp import SmartContract
from constants import WOW_ABI
from uniswap.index import get_has_graduated, get_uniswap_quote


def get_current_supply(token_address):
    """Get the current supply of a token.

    Args:
        token_address: Address of the token contract, such as `0x036CbD53842c5426634e7929541eC2318f3dCF7e`

    """
    test = SmartContract.read(
        "base-sepolia",
        token_address,
        "totalSupply",
        WOW_ABI,
    )
    print(test)
    return test


async def get_buy_quote(token_address, amount_eth):
    """Get quote for buying tokens.

    Args:
        token_address: Address of the token contract, such as `0x036CbD53842c5426634e7929541eC2318f3dCF7e`
        amount_eth: Amount of ETH to buy (in wei), meaning 1 is 1 wei or 0.000000000000000001 of ETH

    """
    has_graduated = get_has_graduated(token_address)
    token_quote = (
        has_graduated
        and (await get_uniswap_quote("base-sepolia", token_address, amount_eth, "buy")).amount_out
        or SmartContract.read(
            "base-sepolia",
            token_address,
            "getEthBuyQuote",
            abi=WOW_ABI,
            args={"ethOrderSize": str(amount_eth)},
        )
    )
    print(token_quote)
    return token_quote


async def get_sell_quote(token_address, amount_tokens):
    """Get quote for selling tokens.

    Args:
        token_address: Address of the token contract, such as `0x036CbD53842c5426634e7929541eC2318f3dCF7e`
        amount_tokens (str): Amount of tokens to sell (in wei), meaning 1 is 1 wei or 0.000000000000000001 of the token

    """
    has_graduated = get_has_graduated(token_address)
    token_quote = (
        has_graduated
        and (
            await get_uniswap_quote("base-sepolia", token_address, amount_tokens, "sell")
        ).amount_out
        or SmartContract.read(
            "base-sepolia",
            token_address,
            "getTokenSellQuote",
            WOW_ABI,
            args={"tokenOrderSize": str(amount_tokens)},
        )
    )
    print(f"Sell quote for {amount_tokens} tokens: {token_quote}")
    return token_quote

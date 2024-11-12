from cdp import SmartContract
from cdp_agentkit_core.actions.wow.constants import WOW_ABI
from cdp_agentkit_core.actions.wow.uniswap.index import get_has_graduated, get_uniswap_quote


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


def get_buy_quote(network_id: str, token_address: str, amount_eth: str):
    """Get quote for buying tokens.

    Args:
        token_address: Address of the token contract, such as `0x036CbD53842c5426634e7929541eC2318f3dCF7e`
        amount_eth: Amount of ETH to buy (in wei), meaning 1 is 1 wei or 0.000000000000000001 of ETH

    """
    has_graduated = get_has_graduated(network_id, token_address)
    print(f"Has graduated: {has_graduated}")
    print(f"Amount ETH: {amount_eth}")
    print(f"Network ID: {network_id}")
    print(f"Token address: {token_address}")
    token_quote = (
        has_graduated
        and (get_uniswap_quote(network_id, token_address, amount_eth, "buy")).amount_out
        or SmartContract.read(
            network_id,
            token_address,
            "getEthBuyQuote",
            abi=WOW_ABI,
            args={"ethOrderSize": str(amount_eth)},
        )
    )
    print(f"Token quote: {token_quote}")
    return token_quote


def get_sell_quote(network_id: str, token_address: str, amount_tokens: str):
    """Get quote for selling tokens.

    Args:
        token_address: Address of the token contract, such as `0x036CbD53842c5426634e7929541eC2318f3dCF7e`
        amount_tokens (str): Amount of tokens to sell (in wei), meaning 1 is 1 wei or 0.000000000000000001 of the token

    """
    has_graduated = get_has_graduated(network_id, token_address)
    token_quote = (
        has_graduated
        and (get_uniswap_quote(network_id, token_address, amount_tokens, "sell")).amount_out
        or SmartContract.read(
            network_id,
            token_address,
            "getTokenSellQuote",
            WOW_ABI,
            args={"tokenOrderSize": str(amount_tokens)},
        )
    )
    print(f"Sell quote for {amount_tokens} tokens: {token_quote}")
    return token_quote

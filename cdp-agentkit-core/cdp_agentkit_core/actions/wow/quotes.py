import json
from constants import WOW_ABI
from uniswap.index import get_has_graduated, get_uniswap_quote

from cdp import  SmartContract


def get_current_supply(token_address):
  test = SmartContract.read(
    "base-sepolia",
    token_address,
    "totalSupply",
    WOW_ABI,
  )
  print(test)
  return test

async def get_buy_quote(token_address, amount_eth):
    has_graduated = get_has_graduated(token_address)
    token_quote = has_graduated and (await get_uniswap_quote(
        "base-sepolia",
        token_address,
        amount_eth,
        "buy"
    )).amount_out or SmartContract.read(
        "base-sepolia",
        token_address,
        "getEthBuyQuote",
        abi=WOW_ABI,
        args={"ethOrderSize":str(amount_eth)}
    )
    print(token_quote)
    return token_quote

async def get_sell_quote(token_address, amount_tokens):
    """
    Get quote for selling tokens
    
    Args:
        token_address: Address of the token contract
        amount_tokens: Amount of tokens to sell (in wei)
    """
    has_graduated = get_has_graduated(token_address)
    token_quote = has_graduated and (await get_uniswap_quote(
        "base-sepolia",
        token_address,
        amount_tokens,
        "sell"
    )).amount_out or SmartContract.read(
        "base-sepolia",
        token_address,
        "getTokenSellQuote",
        WOW_ABI,
        args={"tokenOrderSize": str(amount_tokens)}
    )
    print(f"Sell quote for {amount_tokens} tokens: {token_quote}")
    return token_quote
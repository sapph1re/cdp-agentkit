from dataclasses import dataclass
from decimal import Decimal
from typing import Literal

from cdp import SmartContract
from cdp_agentkit_core.actions.wow.constants import WOW_ABI, addresses
from cdp_agentkit_core.actions.wow.uniswap.constants import UNISWAP_QUOTER_ABI, UNISWAP_V3_ABI
from web3 import Web3
from web3.types import Wei


@dataclass
class PriceInfo:
    """Price info for a given token."""

    eth: Wei
    usd: Decimal


@dataclass
class Balance:
    """Balance for a given token."""

    erc20z: Wei
    weth: Wei


@dataclass
class Price:
    """Price info for a given token."""

    per_token: PriceInfo
    total: PriceInfo


@dataclass
class Quote:
    """Quote for a given uniswap v3 swap."""

    amount_in: int
    amount_out: int
    balance: Balance | None
    fee: float | None
    error: str | None


@dataclass
class PoolInfo:
    """Pool info for a given uniswap v3 pool."""

    token0: str
    balance0: int  # Using int for bigint
    token1: str
    balance1: int
    fee: int  # Using int for number
    liquidity: int
    sqrt_price_x96: int


def create_price_info(wei_amount: Wei, eth_price_in_usd: float) -> PriceInfo:
    """Create a PriceInfo object from wei amount and ETH price.

    Args:
        wei_amount: Amount in wei
        eth_price_in_usd: Current ETH price in USD

    Returns:
        PriceInfo: A PriceInfo object containing the amount in ETH and USD

    """
    amount_in_eth = Web3.from_wei(wei_amount, "ether")
    usd = float(amount_in_eth) * eth_price_in_usd
    return PriceInfo(eth=wei_amount, usd=Decimal(str(usd)))


# Initialize web3 with your provider (e.g., Infura, Alchemy, or local node)
w3 = Web3(Web3.HTTPProvider("https://base-sepolia.gateway.tenderly.co/6GhpfVtPzsbJkGjwfgUjBW"))


# Replace SmartContract.read calls with web3.py contract calls
def get_has_graduated(network_id: str, token_address: str) -> bool:
    """Check if a token has graduated from the Zora Wow protocol.

    Args:
        network_id: Network ID
        token_address: Token address

    Returns:
        bool: True if the token has graduated, False otherwise

    """
    marketType = SmartContract.read(
        network_id,
        contract_address=token_address,
        method="marketType",
        abi=WOW_ABI,
    )
    print(f"Market type: {marketType}")
    return marketType == 1


def get_pool_info(network_id: str, pool_address: str) -> PoolInfo:
    """Get pool info for a given uniswap v3 pool address.

    Args:
        network_id: Network ID
        pool_address: Uniswap v3 pool address

    Returns:
        PoolInfo: A PoolInfo object containing the token0, balance0, token1, balance1, fee, liquidity, and sqrt_price_x96.

    """
    pool_contract = w3.eth.contract(
        address=Web3.to_checksum_address(pool_address), abi=UNISWAP_V3_ABI
    )

    try:
        # Parallel execution of contract calls
        token0 = SmartContract.read(
            network_id,
            pool_address,
            "token0",
            abi=UNISWAP_V3_ABI,
        )
        token1 = SmartContract.read(
            network_id,
            pool_address,
            "token1",
            abi=UNISWAP_V3_ABI,
        )
        fee = SmartContract.read(
            network_id,
            pool_address,
            "fee",
            abi=UNISWAP_V3_ABI,
        )
        liquidity = SmartContract.read(
            network_id,
            pool_address,
            "liquidity",
            abi=UNISWAP_V3_ABI,
        )
        slot0 = SmartContract.read(
            network_id,
            pool_address,
            "slot0",
            abi=UNISWAP_V3_ABI,
        )

        balance0 = SmartContract.read(
            network_id,
            token0,
            "balanceOf",
            abi=WOW_ABI,
            args={"account": pool_address},
        )

        balance1 = SmartContract.read(
            network_id,
            token1,
            "balanceOf",
            abi=WOW_ABI,
            args={"account": pool_address},
        )

        return PoolInfo(
            token0=token0,
            balance0=balance0,
            token1=token1,
            balance1=balance1,
            fee=fee,
            liquidity=liquidity,
            sqrt_price_x96=slot0[0],
        )
    except Exception as error:
        raise Exception(f"Failed to fetch pool information: {error!s}") from error


def exact_input_single(
    network_id: str, token_in: str, token_out: str, amount_in: int, fee: int
) -> int:
    """Get exact input quote from Uniswap.

    Args:
        network_id: Network ID
        token_in: Token address to swap from
        token_out: Token address to swap to
        amount_in: Amount of tokens to swap (in Wei)
        fee: Fee for the swap

    Returns:
        int: Amount of tokens to receive (in Wei)

    """
    quoter_contract = w3.eth.contract(
        address=Web3.to_checksum_address(addresses[network_id]["UniswapQuoter"]),
        abi=UNISWAP_QUOTER_ABI,
    )

    try:
        params = {
            "tokenIn": Web3.to_checksum_address(token_in),
            "tokenOut": Web3.to_checksum_address(token_out),
            "fee": fee,
            "amountIn": amount_in,
            "sqrtPriceLimitX96": 0,
        }
        # Get just the first value from the returned array
        amount = quoter_contract.functions.quoteExactInputSingle(params).call()[0]

        return amount
    except Exception as error:
        print(f"Quoter error: {error}")
        return 0


def get_uniswap_quote(
    network_id: str, token_address: str, amount: int, quote_type: Literal["buy", "sell"]
) -> Quote:
    """Get Uniswap quote for buying or selling tokens.

    Args:
        network_id: Network ID
        token_address: Token address
        amount: Amount of tokens (in Wei)
        quote_type: 'buy' or 'sell'

    Returns:
        Quote: A Quote object containing the amount in, amount out, balance, fee, and any error messages.

    """
    pool = None
    tokens = None
    balances = None
    eth_price_in_usd = None
    quote_result = None
    utilization = Wei(0)
    insufficient_liquidity = False

    pool_address = get_pool_address(token_address)
    invalid_pool_error = "Invalid pool address" if not pool_address else None
    print("pool address: " + pool_address)

    try:
        pool_info = get_pool_info(network_id, pool_address)
        token0, token1 = pool_info.token0, pool_info.token1
        balance0, balance1 = pool_info.balance0, pool_info.balance1
        fee = pool_info.fee

        pool = pool_info
        tokens = (token0, token1)
        balances = (balance0, balance1)

        is_token0_weth = token0.lower() == addresses[network_id]["WETH"].lower()
        token_in = (
            token0
            if (quote_type == "buy" and is_token0_weth)
            or (quote_type == "sell" and not is_token0_weth)
            else token1
        )

        token_out, balance_out = (token1, balance1) if token_in == token0 else (token0, balance0)
        print("123", balance_out, amount)
        print(type(balance_out), type(amount))
        insufficient_liquidity = quote_type == "buy" and amount > balance_out
        utilization = Wei(int(amount / balance_out)) if quote_type == "buy" else Wei(0)

        quote_result = exact_input_single(network_id, token_in, token_out, amount, fee)
        print("quote_result", quote_result)
    except Exception as error:
        print(f"Error fetching quote: {error}")

    insufficient_liquidity = (
        quote_type == "sell" and pool and not quote_result
    ) or insufficient_liquidity

    error_msg = None
    if not pool or not eth_price_in_usd:
        error_msg = "Failed fetching pool"
    elif insufficient_liquidity:
        error_msg = "Insufficient liquidity"
    elif not quote_result and utilization >= Wei(int(0.9 * 1e18)):
        error_msg = "Price impact too high"
    elif not quote_result:
        error_msg = "Failed fetching quote"

    print(tokens)
    balance_result = None
    if tokens and balances:
        is_weth_token0 = tokens[0].lower() == addresses[network_id]["WETH"].lower()
        balance_result = Balance(
            erc20z=Wei(balances[1]) if is_weth_token0 else Wei(balances[0]),
            weth=Wei(balances[0]) if is_weth_token0 else Wei(balances[1]),
        )

    return Quote(
        amount_in=amount,
        amount_out=quote_result if quote_result else Wei(0),
        balance=balance_result,
        fee=pool.fee / 1000000 if pool else None,
        error=invalid_pool_error or error_msg,
    )


def get_pool_address(token_address: str) -> str:
    """Fetch the uniswap v3 pool address for a given token.

    Args:
        token_address (str): The address of the token contract.

    Returns:
        str: The uniswap v3 pool address associated with the token.

    """
    pool_address = SmartContract.read("base-sepolia", token_address, "poolAddress", abi=WOW_ABI)
    return str(pool_address)

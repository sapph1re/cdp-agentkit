import json
from dataclasses import dataclass
from typing import Optional, Literal
from decimal import Decimal
from web3.types import Wei
from web3 import Web3
from cdp import SmartContract
from constants import addresses

with open('examples/wow_agent/wow_abi.json', 'r') as f:
    abi = json.load(f)

with open('examples/wow_agent/wow_factory_abi.json', 'r') as f:
    factory_abi = json.load(f)

with open('examples/wow_agent/uniswap_quoter_abi.json', 'r') as f:
    uniswap_quoter_abi = json.load(f)

with open('examples/wow_agent/uniswap_v3_abi.json', 'r') as f:
    uniswap_v3_abi = json.load(f)


@dataclass
class PriceInfo:
    eth: Wei
    usd: Decimal

@dataclass
class Balance:
    erc20z: Wei
    weth: Wei

@dataclass
class Price:
    per_token: PriceInfo
    total: PriceInfo

@dataclass
class Quote:
    amount_in: int
    amount_out: int
    balance: Optional[Balance]
    fee: Optional[float]
    error: Optional[str]

@dataclass
class PoolInfo:
    token0: str
    balance0: int  # Using int for bigint
    token1: str
    balance1: int
    fee: int      # Using int for number
    liquidity: int
    sqrtPriceX96: int


def create_price_info(wei_amount: Wei, eth_price_in_usd: float) -> PriceInfo:
    """
    Create a PriceInfo object from wei amount and ETH price
    
    Args:
        wei_amount: Amount in wei
        eth_price_in_usd: Current ETH price in USD
    """
    amount_in_eth = Web3.from_wei(wei_amount, 'ether')
    usd = float(amount_in_eth) * eth_price_in_usd
    return PriceInfo(
        eth=wei_amount,
        usd=Decimal(str(usd))
    )



# Initialize web3 with your provider (e.g., Infura, Alchemy, or local node)
w3 = Web3(Web3.HTTPProvider('https://base-sepolia.gateway.tenderly.co/6GhpfVtPzsbJkGjwfgUjBW'))

# Replace SmartContract.read calls with web3.py contract calls
def get_has_graduated(token_address: str) -> bool:
    contract = w3.eth.contract(
        address=Web3.to_checksum_address(token_address),
        abi=abi
    )
    return contract.functions.marketType().call()

async def get_pool_info(pool_address: str, chain_id: int) -> PoolInfo:
    pool_contract = w3.eth.contract(
        address=Web3.to_checksum_address(pool_address),
        abi=uniswap_v3_abi
    )
    
    try:
        # Parallel execution of contract calls
        token0 = pool_contract.functions.token0().call()
        token1 = pool_contract.functions.token1().call()
        fee = pool_contract.functions.fee().call()
        liquidity = pool_contract.functions.liquidity().call()
        slot0 = pool_contract.functions.slot0().call()

        # Create token contracts
        token0_contract = w3.eth.contract(
            address=Web3.to_checksum_address(token0),
            abi=abi
        )
        token1_contract = w3.eth.contract(
            address=Web3.to_checksum_address(token1),
            abi=abi
        )
        
        balance0 = token0_contract.functions.balanceOf(pool_address).call()
        balance1 = token1_contract.functions.balanceOf(pool_address).call()
        
        return PoolInfo(
            token0=token0,
            balance0=balance0,
            token1=token1,
            balance1=balance1,
            fee=fee,
            liquidity=liquidity,
            sqrtPriceX96=slot0[0]
        )
    except Exception as error:
        raise Exception(f"Failed to fetch pool information: {str(error)}") from error


async def exact_input_single(
    token_in: str,
    token_out: str,
    amount_in: int,
    fee: int,
    chain_id: int
) -> int:
    """
    Get exact input quote from Uniswap
    """
    quoter_contract = w3.eth.contract(
        address=Web3.to_checksum_address(addresses[chain_id]["UniswapQuoter"]),
        abi=uniswap_quoter_abi
    )
    
    try:
        params = {
            'tokenIn': Web3.to_checksum_address(token_in),
            'tokenOut': Web3.to_checksum_address(token_out),
            'fee': fee,
            'amountIn': amount_in,
            'sqrtPriceLimitX96': 0
        }
        # Get just the first value from the returned array
        amount = quoter_contract.functions.quoteExactInputSingle(params).call()[0]
        
        return amount
    except Exception as error:
        print(f"Quoter error: {error}")
        return 0

async def get_uniswap_quote(
    chain_id: int,
    token_address: str,
    amount: int,
    quote_type: Literal['buy', 'sell']
) -> Quote:
    """
    Get Uniswap quote for buying or selling tokens
    
    Args:
        chain_id: Chain ID
        pool_address: Uniswap pool address
        amount: Amount of tokens (in Wei)
        quote_type: 'buy' or 'sell'
    """
    pool = None
    tokens = None 
    balances = None
    eth_price_in_usd = None
    quote_result = None
    utilization = Wei(0)
    insufficient_liquidity = False

    pool_address = await get_pool_address(token_address)
    invalid_pool_error = "Invalid pool address" if not pool_address else None
    print("pool address: " + pool_address)

    try:
        pool_info = await get_pool_info(pool_address, chain_id)
        token0, token1 = pool_info.token0, pool_info.token1
        balance0, balance1 = pool_info.balance0, pool_info.balance1
        fee = pool_info.fee

        pool = pool_info
        tokens = (token0, token1)
        balances = (balance0, balance1)

        is_token0_weth = token0.lower() == addresses[chain_id]["WETH"].lower()
        token_in = token0 if (quote_type == 'buy' and is_token0_weth) or (quote_type == 'sell' and not is_token0_weth) else token1

        token_out, balance_out = (token1, balance1) if token_in == token0 else (token0, balance0)
        print("123",balance_out,amount)
        print(type(balance_out),type(amount))
        insufficient_liquidity = quote_type == 'buy' and amount > balance_out
        utilization = Wei(int(amount / balance_out)) if quote_type == 'buy' else Wei(0)

        quote_result = await exact_input_single(token_in, token_out, amount, fee, chain_id)
        print("quote_result",quote_result)
    except Exception as error:
        print(f"Error fetching quote: {error}")


    insufficient_liquidity = (quote_type == 'sell' and pool and not quote_result) or insufficient_liquidity

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
        is_weth_token0 = tokens[0].lower() == addresses[chain_id]["WETH"].lower()
        balance_result = Balance(
            erc20z=Wei(balances[1]) if is_weth_token0 else Wei(balances[0]),
            weth=Wei(balances[0]) if is_weth_token0 else Wei(balances[1])
        )



    return Quote(
        amount_in=amount,
        amount_out=quote_result if quote_result else Wei(0),
        balance=balance_result,
        fee=pool.fee / 1000000 if pool else None,
        error=invalid_pool_error or error_msg
    )

async def get_pool_address(token_address: str) -> str:
    pool_address = SmartContract.read(
        "base-sepolia",
        token_address,
        "poolAddress",
        abi=abi
    )
    return str(pool_address)
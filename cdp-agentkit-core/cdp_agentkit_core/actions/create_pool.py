from cdp import Wallet
from pydantic import BaseModel, Field

CREATE_POOL_PROMPT = """
This tool will create a Uniswap v3 pool for trading 2 tokens, one of which can be the native gas token. For native gas token, use the address 0x4200000000000000000000000000000000000006. This tool takes the address of the first token, address of the second token, and the fee to charge for trades as inputs. The fee is denominated in hundredths of a bip (i.e. 1e-6) and must be passed a string. Acceptable fee values are 100, 500, 3000, and 10000."""

UNISWAP_V3_FACTORY_ABI = [
    {"inputs": [], "stateMutability": "nonpayable", "type": "constructor"},
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "internalType": "uint24", "name": "fee", "type": "uint24"},
            {"indexed": True, "internalType": "int24", "name": "tickSpacing", "type": "int24"},
        ],
        "name": "FeeAmountEnabled",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "internalType": "address", "name": "oldOwner", "type": "address"},
            {"indexed": True, "internalType": "address", "name": "newOwner", "type": "address"},
        ],
        "name": "OwnerChanged",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "internalType": "address", "name": "token0", "type": "address"},
            {"indexed": True, "internalType": "address", "name": "token1", "type": "address"},
            {"indexed": True, "internalType": "uint24", "name": "fee", "type": "uint24"},
            {"indexed": False, "internalType": "int24", "name": "tickSpacing", "type": "int24"},
            {"indexed": False, "internalType": "address", "name": "pool", "type": "address"},
        ],
        "name": "PoolCreated",
        "type": "event",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "tokenA", "type": "address"},
            {"internalType": "address", "name": "tokenB", "type": "address"},
            {"internalType": "uint24", "name": "fee", "type": "uint24"},
        ],
        "name": "createPool",
        "outputs": [{"internalType": "address", "name": "pool", "type": "address"}],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint24", "name": "fee", "type": "uint24"},
            {"internalType": "int24", "name": "tickSpacing", "type": "int24"},
        ],
        "name": "enableFeeAmount",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "uint24", "name": "", "type": "uint24"}],
        "name": "feeAmountTickSpacing",
        "outputs": [{"internalType": "int24", "name": "", "type": "int24"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "", "type": "address"},
            {"internalType": "address", "name": "", "type": "address"},
            {"internalType": "uint24", "name": "", "type": "uint24"},
        ],
        "name": "getPool",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "owner",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "parameters",
        "outputs": [
            {"internalType": "address", "name": "factory", "type": "address"},
            {"internalType": "address", "name": "token0", "type": "address"},
            {"internalType": "address", "name": "token1", "type": "address"},
            {"internalType": "uint24", "name": "fee", "type": "uint24"},
            {"internalType": "int24", "name": "tickSpacing", "type": "int24"},
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "address", "name": "_owner", "type": "address"}],
        "name": "setOwner",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
]


class CreatePoolInput(BaseModel):
    """Input argument schema for create pool action."""

    token_a: str = Field(
        ...,
        description="The address of the first token to trade`",
    )
    token_b: str = Field(
        ...,
        description="The address of the second token to trade`",
    )
    fee: str = Field(
        ...,
        description="The fee to charge for trades, denominated in hundredths of a bip (i.e. 1e-6)",
    )


def create_pool(wallet: Wallet, token_a: str, token_b: str, fee: str) -> str:
    """Create a Uniswap v3 pool for trading 2 tokens, one of which can be the native gas token.

    Args:
        wallet (Wallet): The wallet to create the pool from.
        token_a (str): The address of the first token to trade.
        token_b (str): The address of the second token to trade.
        fee (str): The fee to charge for trades, denominated in hundredths of a bip (i.e. 1e-6).

    Returns:
        str: A message containing the pool creation details.

    """
    pool = wallet.invoke_contract(
        contract_address="0x4752ba5DBc23f44D87826276BF6Fd6b1C372aD24",  # TODO - set this based on network id
        method="createPool",
        abi=UNISWAP_V3_FACTORY_ABI,
        args={
            "tokenA": token_a,
            "tokenB": token_b,
            "fee": fee,
        },
    ).wait()
    return f"Created pool for {token_a} and {token_b} with fee {fee} on network {wallet.network_id}.\nTransaction hash for the pool creation: {pool.transaction.transaction_hash}\nTransaction link for the pool creation: {pool.transaction.transaction_link}"

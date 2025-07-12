import time
import os
from eth_account import Account

from dspy_evm_wallet import config
from dspy_evm_wallet.token_types import TokenType
from dspy_evm_wallet.primitive_evm_functions import (
    create_new_wallet,
    transfer_token,
    get_balance
)

# Global variables
last_evm_user_wallet_created = None 


def get_evm_funding_wallet_public_key() -> str:
    """
    Gets the public key of the EVM funding wallet.
    """

    if not config.EVM_FUNDING_WALLET_PRIVATE_KEY:
        raise Exception("EVM funding wallet private key not configured")
    
    funding_wallet = Account.from_key(config.EVM_FUNDING_WALLET_PRIVATE_KEY)

    print(f'funding wallet public key: {funding_wallet.address}')

    return {
        'funding_wallet_public_key': funding_wallet.address
    }

def create_evm_wallet() -> str:
    """
    Creates a new EVM wallet and return the public key.
    
    Returns:
        public_key
    """
    global last_evm_user_wallet_created

    new_wallet = create_new_wallet()

    last_evm_user_wallet_created = new_wallet['public_key']

    print(f'last_user_wallet_created: {last_evm_user_wallet_created}')
    print(f'created wallet {new_wallet["public_key"]}')
    
    return {
        'new_wallet_public_key': new_wallet['public_key'],
        'new_wallet_private_key': new_wallet['private_key']
    }

def get_last_evm_user_wallet_created() -> str:
    """
    Gets the public key of the last EVM user wallet created.
    """
    return last_evm_user_wallet_created

def get_last_evm_user_wallet_balance(user_wallet_public_key: str, token_type: str) -> float:
    """
    Gets the current balance of a specific token type for the last EVM user wallet created.
    
    Args:
        user_wallet_public_key (str): The public key of the user wallet
        token_type (str): The type of token to get balance for ('ETH', 'USDC', 'PYUSD', or 'USDG')
        
    Returns:
        float: The formatted balance of the specified token
    """
    token_enum = TokenType.from_string(token_type)
    
    user_wallet_public_key = get_last_evm_user_wallet_created()

    print(f'DSPY function entered: get_last_evm_user_wallet_balance, token_type: {token_type}, wallet_public_key: {user_wallet_public_key}')

    balance = get_balance(user_wallet_public_key, token_enum)

    print(f'DSPY function exit: get_last_evm_user_wallet_balance, token_type: {token_type}, balance: {balance}')

    return balance

def send_evm_token_from_funding_wallet(user_wallet_public_key: str, amount: float, token_type: str) -> dict:
    """
    Send tokens (ETH, USDC, PYUSD, or USDG) from the EVM funding wallet to the user wallet.
    
    Args:
        user_wallet_public_key (str): The public key of the user wallet
        amount (float): The amount of tokens to transfer
        token_type (str): The type of token to transfer ('ETH', 'USDC', 'PYUSD', or 'USDG')
        
    Returns:
        dict: A dictionary containing:
            - success (bool): True if the transfer was successful
            - funding_wallet_public_key (str): The public key of the funding wallet
            - user_wallet_public_key (str): The public key of the user wallet
            - amount (float): The amount of tokens transferred
            - token_type (str): The type of token that was transferred
    """
    if not config.EVM_FUNDING_WALLET_PRIVATE_KEY:
        raise Exception("EVM funding wallet private key not configured")
    
    token_enum = TokenType.from_string(token_type)
    
    funding_wallet = Account.from_key(config.EVM_FUNDING_WALLET_PRIVATE_KEY)
    
    print(f'DSPY function entered: send_evm_token_from_funding_wallet, token_type: {token_type}, amount: {amount}, destination wallet_public_key: {user_wallet_public_key}')

    tx_hash = transfer_token(
        config.EVM_FUNDING_WALLET_PRIVATE_KEY,
        user_wallet_public_key,
        token_enum,
        amount
    )
    
    print(f'tx_hash: {tx_hash}')
    print(f'DSPY function exited: send_evm_token_from_funding_wallet, token_type: {token_type}, amount: {amount}, destination wallet_public_key: {user_wallet_public_key}')

    return {
        'success': True,
        'funding_wallet_public_key': funding_wallet.address,
        'user_wallet_public_key': user_wallet_public_key,
        'amount': amount,
        'token_type': token_type.upper(),
        'transaction_hash': tx_hash
    } 
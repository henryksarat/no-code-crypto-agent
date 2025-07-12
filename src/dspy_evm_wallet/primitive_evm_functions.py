import os
import time
from web3 import Web3
from eth_account import Account
from dspy_evm_wallet.config import ETH_RPC_URL
from dspy_evm_wallet.token_types import TokenType
from dspy_evm_wallet.abi import ERC20_ABI

w3 = Web3(Web3.HTTPProvider(ETH_RPC_URL))


def _get_nonce_with_delay(address):
    """
    Get the current nonce for an address with a delay to avoid conflicts.
    
    Args:
        address (str): The wallet address
        
    Returns:
        int: The current nonce
    """
    nonce = w3.eth.get_transaction_count(address)
    time.sleep(1)
    return nonce


def create_new_wallet():
    """Create a new EVM wallet (Ethereum/Arbitrum)."""
    acct = Account.create()
    return {
        'private_key': acct.key.hex(),
        'public_key': acct.address
    }


def get_balance(wallet_address, token_type):
    """Get the balance of a wallet (ETH or specific token)."""
    if token_type == TokenType.ETH:
        balance_wei = w3.eth.get_balance(wallet_address)
        return w3.from_wei(balance_wei, 'ether')
    else:
        contract = w3.eth.contract(address=token_type.contract_address, abi=ERC20_ABI)
        balance = contract.functions.balanceOf(wallet_address).call()
        return token_type.from_token_amount(balance)


def transfer_eth(private_key, to_address, amount_eth):
    """Transfer ETH from the wallet to another address."""
    acct = Account.from_key(private_key)
    
    # Get current nonce with delay
    nonce = _get_nonce_with_delay(acct.address)
    
    tx = {
        'nonce': nonce,
        'to': to_address,
        'value': w3.to_wei(amount_eth, 'ether'),
        'gas': 21000,
        'gasPrice': w3.eth.gas_price,
        'chainId': w3.eth.chain_id
    }
    signed_tx = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    return tx_hash.hex()


def transfer_token(private_key, to_address, token_type, amount):
    """Transfer any ERC20 token from the wallet to another address."""
    if token_type == TokenType.ETH:
        return transfer_eth(private_key, to_address, amount)
    
    acct = Account.from_key(private_key)
    
    # Get current nonce with delay
    nonce = _get_nonce_with_delay(acct.address)
    
    contract = w3.eth.contract(address=token_type.contract_address, abi=ERC20_ABI)
    amount_wei = token_type.to_token_amount(amount)
    
    # Use a slightly higher gas price to avoid "replacement transaction underpriced" errors
    gas_price = int(w3.eth.gas_price * 1.1)  # 10% higher gas price
    
    tx = contract.functions.transfer(to_address, amount_wei).build_transaction({
        'chainId': w3.eth.chain_id,
        'gas': 100000,
        'gasPrice': gas_price,
        'nonce': nonce
    })
    signed_tx = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    return tx_hash.hex() 
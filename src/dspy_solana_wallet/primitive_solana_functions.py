import base58
import requests
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.hash import Hash
from solders.system_program import TransferParams, transfer
from solders.instruction import Instruction, AccountMeta
from solders.transaction import Transaction
import httpx
import time

from . import config
from .token_types import TokenType, ASSOCIATED_TOKEN_PROGRAM_ID

def create_new_wallet():
    """Create a new Solana wallet."""
    keypair = Keypair()
    print(f"New wallet created!")
    print(f"Public key: {keypair.pubkey()}")
    print(f"Private key: {base58.b58encode(bytes(keypair.to_bytes())).decode('ascii')}")
    return keypair

def fund_wallet_with_sol_from_faucet(wallet_public_key, amount=1):
    """Fund a wallet with SOL using the devnet faucet."""
    
    print(f'funding wallet with sol from faucet {wallet_public_key} amount {amount}')

    if config.SOLANA_NETWORK != "devnet":
        raise Exception("Faucet is only available on devnet")
    
    print(f'requesting airdrop for {wallet_public_key} amount {amount}')
    try:
        response = requests.post(
            "https://api.devnet.solana.com",
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "requestAirdrop",
                "params": [str(wallet_public_key), int(amount * 1_000_000_000)]  # Convert SOL to lamports
            }
        )
        
        result = response.json()
        print(f'result from attempting to fund wallet with sol from faucet: {result}')
        
        if not "error" in result:
            print(f"Successfully funded wallet with {amount} SOL, response= {response.text}")
            return True
        else:
            print(f"Failed to fund wallet: {response.text}")
            return False 
    except Exception as e:
        print(f"Error funding wallet: {str(e)}")
        return False

def get_associated_token_address(wallet_address, token_type: TokenType):
    """Get the associated token account address for a wallet and token type."""

    print(f'getting associated token address for {wallet_address} {token_type}')

    return Pubkey.find_program_address(
        [
            bytes(wallet_address),
            bytes(Pubkey.from_string(token_type.program_id)),
            bytes(Pubkey.from_string(token_type.value))
        ],
        Pubkey.from_string(ASSOCIATED_TOKEN_PROGRAM_ID)
    )[0]

def create_associated_token_account_instruction(
    payer: Pubkey,
    owner: Pubkey,
    mint: Pubkey,
    associated_token: Pubkey,
    token_type: TokenType
) -> Instruction:
    """Create an instruction to create an associated token account."""
    return Instruction(
        program_id=Pubkey.from_string(ASSOCIATED_TOKEN_PROGRAM_ID),
        accounts=[
            AccountMeta(pubkey=payer, is_signer=True, is_writable=True),
            AccountMeta(pubkey=associated_token, is_signer=False, is_writable=True),
            AccountMeta(pubkey=owner, is_signer=False, is_writable=False),
            AccountMeta(pubkey=mint, is_signer=False, is_writable=False),
            AccountMeta(pubkey=Pubkey.from_string("11111111111111111111111111111111"), is_signer=False, is_writable=False),
            AccountMeta(pubkey=Pubkey.from_string(token_type.program_id), is_signer=False, is_writable=False),
            AccountMeta(pubkey=Pubkey.from_string("SysvarRent111111111111111111111111111111111"), is_signer=False, is_writable=False),
        ],
        data=bytes([1])  # Create instruction
    )

def create_associated_token_account_transaction(funding_wallet, to_wallet_public_key, token_type):
    """Create a transaction for creating an associated token account."""
    # Get associated token account
    to_token_account = get_associated_token_address(to_wallet_public_key, token_type)
    mint_pubkey = Pubkey.from_string(token_type.value)

    print(f'creating associated token account for {to_wallet_public_key} {token_type}')
    
    create_ata_ix = create_associated_token_account_instruction(
        funding_wallet.pubkey(),
        to_wallet_public_key,
        mint_pubkey,
        to_token_account,
        token_type
    )

    # Get recent blockhash
    recent_blockhash = _get_latest_blockhash()

    # Create transaction
    transaction = Transaction.new_with_payer(
        [create_ata_ix],
        funding_wallet.pubkey()
    )
    
    # Sign the transaction
    transaction.sign([funding_wallet], recent_blockhash)
    
    return transaction

def create_token_transfer_transaction(funding_wallet, to_wallet_public_key, token_type, amount):
    """Create a transaction for transferring tokens."""
    # Get associated token accounts
    from_token_account = get_associated_token_address(funding_wallet.pubkey(), token_type)
    to_token_account = get_associated_token_address(to_wallet_public_key, token_type)

    mint_pubkey = Pubkey.from_string(token_type.value)
    # Create transfer instruction
    transfer_ix = _transfer_token_instruction(
        from_token_account,
        to_token_account,
        funding_wallet.pubkey(),
        mint_pubkey,
        amount,
        token_type
    )

    # Get recent blockhash
    recent_blockhash = _get_latest_blockhash()

    # Create transaction
    transaction = Transaction.new_with_payer(
        [transfer_ix],
        funding_wallet.pubkey()
    )
    
    # Sign the transaction
    transaction.sign([funding_wallet], recent_blockhash)
    
    return transaction


def transfer_sol(from_wallet, to_wallet_public_key, amount):
    """Transfer SOL from one wallet to another."""
    # Create transfer instruction
    try:
        print('attempting to transfer sol')
        params = TransferParams(
            from_pubkey=from_wallet.pubkey(),
            to_pubkey=to_wallet_public_key,
            lamports=int(amount * 1_000_000_000)  # Convert SOL to lamports
        )

        print('executing transfer')
        transfer_ix = transfer(params)

        print('transfer instruction created')

        # Get recent blockhash
        recent_blockhash = _get_latest_blockhash()

        # Create transaction
        transaction = Transaction.new_with_payer(
            [transfer_ix],
            from_wallet.pubkey()
        )
        
        # Sign the transaction
        transaction.sign([from_wallet], recent_blockhash)
        
        print(f'transaction created')
        # Execute the transaction
        result = _send_transaction(bytes(transaction))
        print(f"SOL transfer initiated. Transaction signature: {result}")
        return True
    except Exception as e:
        print(f'error sending transaction: {e}')
        return False

def create_associated_token_account(funding_wallet, owner_public_key, token_type):
    """Create and broadcast an associated token account transaction."""
    # Create ATA transaction
    print(f'creating associated token account for {owner_public_key}')
    try:
        ata_transaction = create_associated_token_account_transaction(
            funding_wallet,
            owner_public_key,
            token_type
        )
        # Broadcast transaction
        result = _broadcast_transaction(ata_transaction)
        print(f"ATA creation transaction signature: {result}")
        
        # Wait 5 seconds for transaction to be processed
        print("Waiting 5 seconds for ATA creation to be processed...")
        time.sleep(5)
        
        return result
    except Exception as e:
        print(f'error creating associated token account: {e}')
        return False

def transfer_token(funding_wallet, recipient_public_key, token_type, amount):
    """Create and broadcast a token transfer transaction."""
    # Create token transfer transaction
    print(f'creating token transfer transaction')
    print(f'DEBUG: Original amount: {amount}')
    print(f'DEBUG: Token type: {token_type.name}')
    
    converted_amount = token_type.to_token_amount(amount)
    print(f'DEBUG: Converted amount: {converted_amount}')
    
    try:
        transfer_transaction = create_token_transfer_transaction(
            funding_wallet,
            recipient_public_key,
            token_type,
            converted_amount
        )
        result = _broadcast_transaction(transfer_transaction)
        print(f"Token transfer transaction signature: {result}")

        return True
    except Exception as e:
        print(f'error creating token transfer transaction: {e}')
        return False
    
def get_balance(wallet_address: Pubkey, token_type: TokenType) -> int:
    """
    Get the balance for a wallet, either SOL or a specific token.
    
    Args:
        wallet_address: The wallet's public key
        token_type: The type of token to check (SOL, USDG, or USDC)
        
    Returns:
        int: The balance in raw units (lamports for SOL, token units for tokens)
    """
    try:
        # Prepare RPC request
        if token_type == TokenType.SOL:
            method = "getBalance"
            params = [str(wallet_address)]
            print(f'trying to get sol balance')
        else:
            method = "getTokenAccountBalance"
            ata = get_associated_token_address(wallet_address, token_type)
            print(f'ata retrieved: {ata}')
            params = [str(ata)]

        # Make RPC request
        result = _make_rpc_request(method, params)

        # Handle errors
        if "error" in result:
            print(f"RPC Error: {result['error']}")
            if "could not find account" in result['error']['message']:
                print(f"ATA does not exist. So balance is 0")
                return 0
            return -1

        if not result.get('result', {}).get('value'):
            print(f"No {token_type.name} balance found.")
            return 0

        print(f'result: {result}')
        # Extract raw value
        raw_value = result['result']['value']['amount'] if token_type != TokenType.SOL else result['result']['value']

        return int(raw_value)

    except Exception as e:
        print(f"Error getting {token_type.name} balance: {str(e)}")
        return -1 

def _send_rpc_request(method, params=None):
    """Send an RPC request to the Solana node."""
    headers = {"Content-Type": "application/json"}
    data = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params or []
    }
    
    response = httpx.post(config.FAUCET_URL, json=data, headers=headers)
    return response.json()

def _send_transaction(transaction_bytes):
    """Send a transaction to the Solana node."""
    params = [
        base58.b58encode(transaction_bytes).decode('ascii'),
        {"skipPreflight": True, "preflightCommitment": "processed"}
    ]
    response = _send_rpc_request("sendTransaction", params)
    return response["result"]

def _get_latest_blockhash():
    """Get the latest blockhash from the Solana node."""
    response = _send_rpc_request("getLatestBlockhash")
    blockhash_str = response["result"]["value"]["blockhash"]
    return Hash.from_string(blockhash_str)

def _make_rpc_request(method: str, params: list) -> dict:
    """
    Make an RPC request to the Solana node.
    
    Args:
        method: The RPC method to call
        params: The parameters for the RPC call
        
    Returns:
        dict: The JSON response from the RPC call
    """
    RPC_URL = "https://api.devnet.solana.com"
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params
    }
    
    response = httpx.post(RPC_URL, json=payload)
    return response.json()

def _broadcast_transaction(transaction):
    """Broadcast a signed transaction to the network."""
    result = _send_transaction(bytes(transaction))
    return result
  
def _transfer_token_instruction(
    source: Pubkey,
    destination: Pubkey,
    owner: Pubkey,
    mint: Pubkey,
    amount: int,
    token_type: TokenType
) -> Instruction:
    """Create a token transfer instruction using transfer_checked."""    
    # Use transfer_checked instruction (code 12) with proper format
    # transfer_checked: amount (8 bytes) + decimals (1 byte)
    instruction_data = bytes([12]) + amount.to_bytes(8, 'little', signed=False) + bytes([token_type.decimals])
    
    return Instruction(
        program_id=Pubkey.from_string(token_type.program_id),
        accounts=[
            AccountMeta(pubkey=source, is_signer=False, is_writable=True),
            AccountMeta(pubkey=mint, is_signer=False, is_writable=False),
            AccountMeta(pubkey=destination, is_signer=False, is_writable=True),
            AccountMeta(pubkey=owner, is_signer=True, is_writable=False),
        ],
        data=instruction_data
    )
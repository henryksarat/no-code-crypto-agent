# import base58
# import time
# import os
# from solders.keypair import Keypair
# from solders.pubkey import Pubkey

# from dspy_solana_wallet import config
# from dspy_solana_wallet.token_types import TokenType
# from dspy_solana_wallet.primitive_solana_functions import (
#     create_new_wallet,
#     fund_wallet_with_sol_from_faucet,
#     create_associated_token_account,
#     transfer_token,
#     transfer_sol,
#     get_balance
# )

# # Global variables
# last_user_wallet_created = None 


# def get_funding_wallet_public_key() -> str:
#     """
#     Gets the public key of the funding wallet.
#     """

#     if not config.FUNDING_WALLET_PRIVATE_KEY:
#         raise Exception("Funding wallet private key not configured")
    
#     funding_wallet = Keypair.from_bytes(
#         base58.b58decode(config.FUNDING_WALLET_PRIVATE_KEY)
#     )

#     print(f'funding wallet public key: {funding_wallet.pubkey()}')

#     return {
#         'funding_wallet_public_key': funding_wallet.pubkey()
#     }

# def create_solana_wallet() -> str:
#     """
#     Creates a new Solana wallet and return the public key.
    
#     Returns:
#         public_key
#     """
#     global last_user_wallet_created

#     new_wallet = create_new_wallet()

#     last_user_wallet_created = new_wallet.pubkey()

#     print(f'last_user_wallet_created: {last_user_wallet_created}')
#     print(f'created wallet {new_wallet.pubkey()}')
    
#     private_key = base58.b58encode(bytes(new_wallet.to_bytes())).decode('ascii')

#     return {
#         'new_wallet_public_key': new_wallet.pubkey(),
#         'new_wallet_private_key': private_key
#     }

# def get_last_solana_user_wallet_created() -> str:
#     """
#     Gets the public key of the last solanauser wallet created.
#     """
#     return last_user_wallet_created

# def create_associated_token_account_for_token(user_wallet_public_key: str, token_type: str) -> bool:
#     """
#     Creates a new associated token account for the given public key and token type. This will allow the public key
#     to hold the specified token. The fees will be paid from the funding wallet.
    
#     Args:
#         user_wallet_public_key (str): The public key of the user wallet
#         token_type (str): The type of token ('USDC', 'PYUSD', or 'USDG')
        
#     Returns:
#         bool: True if successful
#     """
#     if not config.FUNDING_WALLET_PRIVATE_KEY:
#         raise Exception("Funding wallet private key not configured")
    
#     token_enum = TokenType.from_string(token_type)
    
#     funding_wallet_object = Keypair.from_bytes(
#         base58.b58decode(config.FUNDING_WALLET_PRIVATE_KEY)
#     )

#     print(f'creating {token_type.lower()} associated token account for {user_wallet_public_key}')
#     print(f'last_user_wallet_created in ata: {last_user_wallet_created}')
    
#     user_pubkey = Pubkey.from_string(user_wallet_public_key)

#     create_associated_token_account(
#         funding_wallet_object,
#         user_pubkey,
#         token_enum
#     )
#     return True

# def fund_user_wallet_with_sol_from_devnet(public_key: str, amount: float) -> bool:
#     """
#     Funds a user wallet with SOL on devnet.
    
#     Args:
#         public_key: The new wallet's public key
#         amount: Amount of SOL to fund (default: 0.01)
    
#     Returns:
#         bool: True if successful, False otherwise
#     """

#     print(f'funding wallet with devnet {public_key} amount {amount}')

#     result = fund_wallet_with_sol_from_faucet(public_key, amount)

#     global last_user_wallet_balance_sol
#     last_user_wallet_balance_sol += amount

#     print(f'funding wallet with devnet {result}')

#     return {
#         'success': result
#     }

# def get_last_user_wallet_balance(user_wallet_public_key: str, token_type: str) -> float:
#     """
#     Gets the current balance of a specific token type for the last user wallet created.
    
#     Args:
#         user_wallet_public_key (str): The public key of the user wallet
#         token_type (str): The type of token to get balance for ('SOL', 'USDC', 'PYUSD', or 'USDG')
        
#     Returns:
#         float: The formatted balance of the specified token
#     """
#     token_enum = TokenType.from_string(token_type)
    
#     user_wallet_public_key = get_last_solana_user_wallet_created()

#     print(f'DSPY function entered: get_last_user_wallet_balance, token_type: {token_type}, wallet_public_key: {user_wallet_public_key}')

#     balance = get_balance(user_wallet_public_key, token_enum)
#     formatted_balance = token_enum.from_token_amount(balance)

#     print(f'DSPY function exit: get_last_user_wallet_balance, token_type: {token_type}, balance: {formatted_balance}')

#     return formatted_balance

# def send_token_from_funding_wallet(user_wallet_public_key: str, amount: float, token_type: str) -> dict:
#     """
#     Send tokens (SOL, USDC, PYUSD, or USDG) from the funding wallet to the user wallet.
    
#     Args:
#         user_wallet_public_key (str): The public key of the user wallet
#         amount (float): The amount of tokens to transfer
#         token_type (str): The type of token to transfer ('SOL', 'USDC', 'PYUSD', or 'USDG')
        
#     Returns:
#         dict: A dictionary containing:
#             - success (bool): True if the transfer was successful
#             - funding_wallet_public_key (str): The public key of the funding wallet
#             - user_wallet_public_key (str): The public key of the user wallet
#             - amount (float): The amount of tokens transferred
#             - token_type (str): The type of token that was transferred
#     """
#     if not config.FUNDING_WALLET_PRIVATE_KEY:
#         raise Exception("Funding wallet private key not configured")
    
#     token_enum = TokenType.from_string(token_type)
    
#     funding_wallet_object = Keypair.from_bytes(
#         base58.b58decode(config.FUNDING_WALLET_PRIVATE_KEY)
#     )
    
#     user_pubkey = Pubkey.from_string(user_wallet_public_key)
#     print(f'DSPY function entered: send_token_from_funding_wallet, token_type: {token_type}, amount: {amount}, destination wallet_public_key: {user_wallet_public_key}')

#     if token_enum == TokenType.SOL:
#         transfer_sol(funding_wallet_object, user_pubkey, amount)
#     else:
#         transfer_token(funding_wallet_object, user_pubkey, token_enum, amount)
    
#     print(f'DSPY function exited: send_token_from_funding_wallet, token_type: {token_type}, amount: {amount}, destination wallet_public_key: {user_wallet_public_key}')

#     return {
#         'success': True,
#         'funding_wallet_public_key': funding_wallet_object.pubkey(),
#         'user_wallet_public_key': user_wallet_public_key,
#         'amount': amount,
#         'token_type': token_type.upper()
#     }

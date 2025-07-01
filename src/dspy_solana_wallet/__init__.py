"""
DSPy Solana Wallet - A Solana wallet management system using DSPy agents.

This package provides functionality for creating and managing Solana wallets,
handling token transfers, and integrating with DSPy for intelligent wallet operations.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

# Import main components for easy access
from .agent_with_complex_usdg_validation import agent_with_usdg_validation, DSPyWalletServiceSerice
from .agent_tools import (
    create_wallet,
    get_last_user_wallet_created,
    create_associated_token_account_for_token,
    fund_user_wallet_with_sol_from_devnet,
    send_token_from_funding_wallet,
    get_last_user_wallet_balance
)
from .token_types import TokenType
from .primitive_solana_functions import (
    create_new_wallet,
    transfer_sol,
    transfer_token,
    get_balance,
    create_associated_token_account,
    fund_wallet_with_sol_from_faucet
)

__all__ = [
    "agent_with_usdg_validation",
    "DSPyWalletServiceSerice", 
    "TokenType",
    "create_wallet",
    "get_last_user_wallet_created",
    "create_associated_token_account_for_token",
    "fund_user_wallet_with_sol_from_devnet",
    "send_token_from_funding_wallet",
    "get_last_user_wallet_balance",
    "create_new_wallet",
    "transfer_sol",
    "transfer_token", 
    "get_balance",
    "create_associated_token_account",
    "fund_wallet_with_sol_from_faucet"
] 
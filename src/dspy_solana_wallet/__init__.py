"""
DSPy Solana Wallet - A Solana wallet management system using DSPy agents.

This package provides functionality for creating and managing Solana wallets,
handling token transfers, and integrating with DSPy for intelligent wallet operations.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

# Import main components for easy access
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
    "TokenType",
    "create_new_wallet",
    "transfer_sol",
    "transfer_token", 
    "get_balance",
    "create_associated_token_account",
    "fund_wallet_with_sol_from_faucet"
] 
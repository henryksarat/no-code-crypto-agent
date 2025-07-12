"""
DSPy Agents Package

A generic package for DSPy-based agents that can work with different blockchain networks.
"""

from .agent_basic import agent_basic, DSPyWalletServiceSericeBasic
from .agent_with_complex_usdg_validation import agent_with_usdg_validation, DSPyWalletServiceSerice

# Solana agent tools
from .agent_tools_solana import (
    create_solana_wallet,
    create_solana_associated_token_account_for_token,
    fund_solana_user_wallet_with_sol_from_devnet,
    send_solana_token_from_funding_wallet,
    get_last_solana_user_wallet_created,
    get_last_solana_user_wallet_balance,
    get_solana_funding_wallet_public_key
)

# EVM agent tools
from .agent_tools_evm import (
    create_evm_wallet,
    send_evm_token_from_funding_wallet,
    get_last_evm_user_wallet_created,
    get_last_evm_user_wallet_balance,
    get_evm_funding_wallet_public_key
)

__all__ = [
    # Agent classes
    'agent_basic',
    'DSPyWalletServiceSericeBasic',
    'agent_with_usdg_validation',
    'DSPyWalletServiceSerice',
    
    # Solana functions
    'create_solana_wallet',
    'create_solana_associated_token_account_for_token',
    'fund_solana_user_wallet_with_sol_from_devnet',
    'send_solana_token_from_funding_wallet',
    'get_last_solana_user_wallet_created',
    'get_last_solana_user_wallet_balance',
    'get_solana_funding_wallet_public_key',
    
    # EVM functions
    'create_evm_wallet',
    'send_evm_token_from_funding_wallet',
    'get_last_evm_user_wallet_created',
    'get_last_evm_user_wallet_balance',
    'get_evm_funding_wallet_public_key'
] 
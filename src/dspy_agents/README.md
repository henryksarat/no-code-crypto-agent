# DSPy Agents Package

This package contains generic DSPy-based agents that can work with different blockchain networks.

## Structure

- `agent_basic.py` - Basic agent implementation (currently Solana-specific)
- `agent_tools_solana.py` - Solana-specific tool functions for the agents
- `agent_tools_evm.py` - EVM-specific tool functions for the agents
- `__init__.py` - Package initialization and exports

## Usage

```python
from dspy_agents import (
    # Agent classes
    agent_basic,
    
    # Solana functions
    create_solana_wallet,
    send_solana_token_from_funding_wallet,
    get_last_solana_user_wallet_created,
    
    # EVM functions
    create_evm_wallet,
    send_evm_token_from_funding_wallet,
    get_last_evm_user_wallet_created
)

# Use the basic agent
agent = agent_basic()

# Create wallets
solana_wallet = create_solana_wallet()
evm_wallet = create_evm_wallet()
```

## Available Functions

### Solana Functions
- `create_solana_wallet()` - Create a new Solana wallet
- `create_associated_token_account_for_token()` - Create ATA for tokens
- `fund_user_wallet_with_sol_from_devnet()` - Fund with SOL from devnet
- `send_solana_token_from_funding_wallet()` - Send tokens from funding wallet
- `get_last_solana_user_wallet_created()` - Get last created Solana wallet
- `get_last_solana_user_wallet_balance()` - Get wallet balance
- `get_solana_funding_wallet_public_key()` - Get funding wallet public key

### EVM Functions
- `create_evm_wallet()` - Create a new EVM wallet
- `send_evm_token_from_funding_wallet()` - Send tokens from funding wallet
- `get_last_evm_user_wallet_created()` - Get last created EVM wallet
- `get_last_evm_user_wallet_balance()` - Get wallet balance
- `get_evm_funding_wallet_public_key()` - Get funding wallet public key

## Future Plans

This package is designed to be extended to support multiple blockchain networks:
- Solana (current)
- Ethereum/EVM chains (current)
- Other blockchain networks

## Notes

The current implementation supports both Solana and EVM operations with separate tool sets for each network. 
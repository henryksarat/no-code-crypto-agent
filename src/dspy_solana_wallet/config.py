import os
from dotenv import load_dotenv

# Load environment variables from project root
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

# Solana network configuration
SOLANA_NETWORK = "devnet"  

# Funding wallet configuration
FUNDING_WALLET_PRIVATE_KEY = os.getenv("FUNDING_WALLET_PRIVATE_KEY")
FUNDING_WALLET_PUBLIC_KEY = os.getenv("FUNDING_WALLET_PUBLIC_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

RANDOM = os.getenv("RANDOM")

# Token configuration
TOKEN_AMOUNT = 1  # Amount to transfer

# Faucet configuration
FAUCET_URL = "https://api.devnet.solana.com" if SOLANA_NETWORK == "devnet" else None 
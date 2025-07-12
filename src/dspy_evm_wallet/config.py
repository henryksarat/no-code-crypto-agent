import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

ETH_RPC_URL = os.getenv('ETH_RPC_URL', 'https://eth-sepolia.g.alchemy.com/v2/4s5JZaCx99DPrO3RXoaxUYeAgNlQyzby')

# EVM funding wallet configuration
EVM_FUNDING_WALLET_PRIVATE_KEY = os.getenv('EVM_FUNDING_WALLET_PRIVATE_KEY')
EVM_FUNDING_WALLET_PUBLIC_KEY = os.getenv('EVM_FUNDING_WALLET_PUBLIC_KEY')

# OpenAI API configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY') 
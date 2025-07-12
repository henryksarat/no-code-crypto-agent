import unittest
import time
import os
import base58
from dspy_solana_wallet.primitive_solana_functions import get_balance
from dspy_solana_wallet.token_types import TokenType
from dspy_solana_wallet import config
from solders.keypair import Keypair

# Test constants for minimum balance requirements
SOL_MIN_BALANCE = 0.1  # Minimum SOL needed for fees
TRANSACTION_WAIT_TIME = 20  # Seconds to wait for transactions

class BaseDSPyAgentTest(unittest.TestCase):
    
    def setUp(self, required_balances):
        """Set up test fixtures before each test method."""
            
        print("\n" + "="*60)
        print("SETTING UP DSPY AGENT TEST...")
        print("="*60)

        # Verify we're on devnet
        if config.SOLANA_NETWORK != "devnet":
            print("❌ SKIPPING: Tests only work on devnet")
            self.skipTest("Tests only work on devnet")

        if not config.SOLANA_FUNDING_WALLET_PRIVATE_KEY:
            print("❌ SKIPPING: Solana funding wallet private key not configured")
            self.skipTest("Solana funding wallet private key not configured")

        if not config.OPENAI_API_KEY:
            print("❌ SKIPPING: OPENAI_API_KEY not configured")
            self.skipTest("OPENAI_API_KEY not configured")
        
        os.environ["OPENAI_API_KEY"] = config.OPENAI_API_KEY
        
        if not config.SOLANA_FUNDING_WALLET_PUBLIC_KEY:
            print("❌ SKIPPING: Solana funding wallet public key not configured")
            self.skipTest("Solana funding wallet public key not configured")

        print(f"✅ Network configuration: {config.SOLANA_NETWORK}")
        print(f"✅ Solana funding wallet configured: {config.SOLANA_FUNDING_WALLET_PUBLIC_KEY}")

        # Create funding wallet object for balance checks
        self.funding_wallet = Keypair.from_bytes(
            base58.b58decode(config.SOLANA_FUNDING_WALLET_PRIVATE_KEY)
        )
        print(f"ℹ️  Funding wallet: {self.funding_wallet.pubkey()}")
        
        # Check funding wallet balances
        print("\nChecking funding wallet balances...")
        
        # Check each token balance
        for token_type, min_amount, token_name in required_balances:
            self.check_funding_wallet_balance(token_type, min_amount, token_name)
        
        print("✅ Funding wallet has sufficient balances for all tests")
        print("="*60)
    
    def check_funding_wallet_balance(self, token_type, min_amount, token_name):
        """Helper method to check if funding wallet has sufficient balance for a specific token."""
        balance_raw = get_balance(self.funding_wallet.pubkey(), token_type)
        balance = token_type.from_token_amount(balance_raw)
        print(f"Funding wallet {token_name} balance: {balance} {token_name}")
        
        if balance < min_amount:
            print(f"❌ SKIPPING: Insufficient {token_name} balance: {balance} {token_name} (need at least {min_amount} {token_name})")
            self.skipTest(f"Insufficient {token_name} balance: {balance} {token_name} (need at least {min_amount} {token_name})")
    
    def wait_for_transaction(self, seconds=15, description="transaction"):
        """Helper method to wait for transactions to be processed."""
        print(f"Waiting {seconds} seconds for {description} to be processed...")
        time.sleep(seconds)
    
    def verify_token_balance(self, wallet_pubkey, token_type, expected_amount, description=""):
        """Generic helper method to verify token balance matches expected amount."""
        token_name = token_type.name
        print(f"Checking {token_name} balance{description}...")

        balance_raw = get_balance(wallet_pubkey, token_type)

        formatted_balance = token_type.from_token_amount(balance_raw)
        self.assertEqual(formatted_balance, expected_amount)
        
        print(f"✅ {token_name} balance is exactly as expected: {expected_amount}") 
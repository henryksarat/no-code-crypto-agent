import unittest
import sys
import os
import pytest
import time
from unittest.mock import patch, MagicMock

from dspy_solana_wallet.primitive_solana_functions import create_new_wallet, fund_wallet_with_sol_from_faucet, get_balance
from dspy_solana_wallet.token_types import TokenType
from dspy_solana_wallet import config

class TestFaucetIntegration(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Skip this test when running all tests, but allow direct execution
        if 'test_faucet_integration.py' not in ' '.join(sys.argv):
            pytest.skip("Run this test explicitly with: python -m pytest tests/test_faucet_integration.py -v -s")
        
        print("\n" + "="*60)
        print("SETTING UP FAUCET INTEGRATION TEST...")
        print("="*60)
        
        # Verify we're on devnet (faucet only works on devnet)
        if config.SOLANA_NETWORK != "devnet":
            print("❌ SKIPPING: Faucet tests only work on devnet")
            self.skipTest("Faucet tests only work on devnet")
        
        print(f"✅ Network configuration: {config.SOLANA_NETWORK}")
        print("="*60)
    
    def create_and_verify_wallet(self, test_name=""):
        """Helper method to create a new wallet and verify it was created properly."""
        print(f"Creating new wallet for {test_name} test...")
        new_wallet = create_new_wallet()
        
        # Verify wallet was created
        self.assertIsNotNone(new_wallet)
        self.assertIsNotNone(new_wallet.pubkey())
        print(f"New wallet created: {new_wallet.pubkey()}")
        
        return new_wallet
    
    def wait_for_transaction(self, seconds=15, description="transaction"):
        """Helper method to wait for transactions to be processed."""
        print(f"Waiting {seconds} seconds for {description} to be processed...")
        time.sleep(seconds)
    
    def verify_sol_balance(self, wallet_pubkey, expected_amount, description=""):
        """Helper method to verify SOL balance matches expected amount."""
        print(f"Checking SOL balance{description}...")
        balance_raw = get_balance(wallet_pubkey, TokenType.SOL)
        
        # Verify we got a valid balance
        self.assertIsNotNone(balance_raw)
        self.assertGreaterEqual(balance_raw, 0)
        print(f"Raw SOL balance (lamports): {balance_raw}")
        
        # Convert to human-readable format
        human_readable_balance = TokenType.SOL.from_token_amount(balance_raw)
        print(f"Human-readable SOL balance: {human_readable_balance} SOL")
        
        # Verify the balance is at least the expected amount
        self.assertGreaterEqual(human_readable_balance, expected_amount)
        
        return human_readable_balance

    def test_faucet_funding_success(self):
        """Test successful funding of a wallet with SOL from the devnet faucet."""
        
        print("\n🧪 Testing faucet funding success...")
        
        # Step 1: Create a new wallet
        new_wallet = self.create_and_verify_wallet("faucet funding")
                
        # Step 2: Fund wallet with SOL from faucet
        print("Funding wallet with SOL from faucet...")
        funding_amount = 1  # 1 SOL
        funding_result = fund_wallet_with_sol_from_faucet(new_wallet.pubkey(), funding_amount)
        
        # Verify funding was successful
        self.assertTrue(funding_result, 'Faucet funding failed. This might be due to rate limiting. Try again later.')
        print(f"✅ Faucet funding successful: {funding_amount} SOL requested")
        
        # Step 3: Wait for transaction to be processed
        self.wait_for_transaction(20, "faucet funding")  # Longer wait for faucet
        
        # Step 4: Verify SOL balance increased
        final_balance = self.verify_sol_balance(new_wallet.pubkey(), funding_amount, " (after funding)")
        
        # Verify the balance increased by the funding amount
        self.assertEqual(final_balance, funding_amount)
        
        print("✅ Faucet funding integration test completed successfully!")

if __name__ == '__main__':
    unittest.main() 
import unittest
import os
import sys
from unittest.mock import patch, MagicMock

from dspy_evm_wallet.primitive_evm_functions import create_new_wallet, transfer_token, get_balance
from dspy_evm_wallet.token_types import TokenType
from dspy_evm_wallet import config
from eth_account import Account
import time

# Test constants for transfer amounts
ETH_TRANSFER_AMOUNT = 0.001  # Small amount for testing
USDC_TRANSFER_AMOUNT = 0.1  # Small amount for testing

ETH_MIN_BALANCE = 0.01  # Minimum ETH needed for testing
USDC_MIN_BALANCE = 0.5  # Minimum USDC needed for testing
TRANSACTION_WAIT_TIME = 45  # Wait time for transactions to be processed

class TestEVMWalletFlow(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        print("\n" + "="*60)
        print("SETTING UP EVM TEST - Checking funding wallet...")
        print("="*60)
        
        if not config.EVM_FUNDING_WALLET_PRIVATE_KEY:
            print("❌ SKIPPING: EVM funding wallet private key not configured")
            self.skipTest("EVM funding wallet private key not configured")
        
        self.funding_wallet_private_key = config.EVM_FUNDING_WALLET_PRIVATE_KEY
        self.funding_wallet_public_key = config.EVM_FUNDING_WALLET_PUBLIC_KEY
        
        # Create account object from private key
        self.funding_account = Account.from_key(self.funding_wallet_private_key)
        
        print(f"Funding wallet: {self.funding_account.address}")
        print("="*60)
    
    def create_and_verify_wallet(self, test_name=""):
        """Helper method to create a new wallet and verify it was created properly."""
        print(f"Creating new EVM wallet for {test_name} test...")
        new_wallet = create_new_wallet()
        
        # Verify wallet was created
        self.assertIsNotNone(new_wallet)
        self.assertIsNotNone(new_wallet['private_key'])
        self.assertIsNotNone(new_wallet['public_key'])
        self.assertTrue(new_wallet['public_key'].startswith('0x'))
        print(f"New wallet created: {new_wallet['public_key']}")
        
        return new_wallet
    
    def wait_for_transaction(self, seconds=15, description="transaction"):
        """Helper method to wait for transactions to be processed."""
        print(f"Waiting {seconds} seconds for {description} to be processed...")
        time.sleep(seconds)
    
    def verify_balance(self, wallet_address, token_type, expected_amount):
        """Helper method to verify balance matches expected amount for any token type."""
        token_name = token_type.name if token_type != TokenType.ETH else "ETH"
        print(f"Checking {token_name} balance...")
        balance = get_balance(wallet_address, token_type)
        
        # Verify we got a valid balance
        self.assertIsNotNone(balance)
        self.assertGreaterEqual(balance, 0)
        print(f"{token_name} balance: {balance}")
        
        # Verify the balance is exactly the expected amount (handle Decimal vs float)
        self.assertEqual(float(balance), float(expected_amount))
        
        return balance

    def check_balance(self, token_type, min_amount):
        """Helper method to check if funding wallet has sufficient balance for any token type."""
        token_name = token_type.name if token_type != TokenType.ETH else "ETH"
        print(f"\nChecking {token_name} balance...")
        balance = get_balance(self.funding_account.address, token_type)
        print(f"Funding wallet {token_name} balance: {balance}")
        
        if balance < min_amount:
            print(f"❌ SKIPPING: Insufficient {token_name} balance: {balance} (need at least {min_amount})")
            self.skipTest(f"Insufficient {token_name} balance: {balance} (need at least {min_amount})")
        
        print(f"✅ Sufficient {token_name} balance: {balance}")
        return balance

    def _test_wallet_flow(self, token_type, transfer_amount, min_balance, test_name):
        """Generic end-to-end integration test: create wallet, transfer tokens, check balance."""
        
        # Check balance before starting test
        self.check_balance(token_type, min_balance)
        
        # Step 1: Create new wallet
        new_wallet = self.create_and_verify_wallet(test_name)
        
        # Step 2: Transfer tokens from funding wallet to new wallet
        token_name = token_type.name if token_type != TokenType.ETH else "ETH"
        print(f"Transferring {token_name}...")
        tx_hash = transfer_token(self.funding_wallet_private_key, new_wallet['public_key'], token_type, transfer_amount)
        
        # Verify transfer was successful
        self.assertIsNotNone(tx_hash)
        print(f"{token_name} transfer successful: {transfer_amount}")
        print(f"Transaction hash: {tx_hash}")
        
        # Step 3: Wait for transaction to be processed
        self.wait_for_transaction(TRANSACTION_WAIT_TIME, f"{token_name} transaction")
        
        # Step 4: Verify balance
        self.verify_balance(new_wallet['public_key'], token_type, transfer_amount)
        
        print(f"✅ End-to-end {token_name} wallet flow test completed successfully!")

    def test_wallet_flow_with_eth(self):
        """End-to-end integration test: create wallet, transfer ETH, check balance."""
        self._test_wallet_flow(TokenType.ETH, ETH_TRANSFER_AMOUNT, ETH_MIN_BALANCE, "ETH")

    def test_wallet_flow_with_usdc(self):
        """End-to-end integration test: create wallet, transfer USDC, check balance."""
        self._test_wallet_flow(TokenType.USDC, USDC_TRANSFER_AMOUNT, USDC_MIN_BALANCE, "USDC")

    def test_wallet_creation_only(self):
        """Test wallet creation without any transfers."""
        print("Testing wallet creation only...")
        
        # Create new wallet
        new_wallet = self.create_and_verify_wallet("creation only")
        
        # Verify wallet structure
        self.assertIn('private_key', new_wallet)
        self.assertIn('public_key', new_wallet)
        self.assertTrue(len(new_wallet['private_key']) == 64)  # 32 bytes = 64 hex chars
        self.assertTrue(new_wallet['public_key'].startswith('0x'))
        self.assertTrue(len(new_wallet['public_key']) == 42)  # 0x + 20 bytes = 42 chars
        
        print("✅ Wallet creation test completed successfully!")

    def test_balance_checking_only(self):
        """Test balance checking functionality."""
        print("Testing balance checking...")
        
        # Define tokens to check
        tokens_to_check = [TokenType.ETH, TokenType.USDC]
        
        for token_type in tokens_to_check:
            balance = get_balance(self.funding_account.address, token_type)
            
            # Verify balance is valid
            self.assertIsNotNone(balance)
            self.assertGreaterEqual(balance, 0)
            
            token_name = token_type.name if token_type != TokenType.ETH else "ETH"
            print(f"Funding wallet {token_name} balance: {balance}")
        
        print("✅ Balance checking test completed successfully!")

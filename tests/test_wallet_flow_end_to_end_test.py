import unittest
import os
import sys
from unittest.mock import patch, MagicMock

from dspy_solana_wallet.primitive_solana_functions import create_new_wallet, transfer_sol, get_balance, create_associated_token_account, transfer_token
from dspy_solana_wallet.token_types import TokenType
from dspy_solana_wallet import config
from solders.keypair import Keypair
import base58
import time

# Test constants for transfer amounts
USDG_TRANSFER_AMOUNT = 0.2
USDC_TRANSFER_AMOUNT = 0.1
SOL_TRANSFER_AMOUNT = 0.05

SOL_MIN_BALANCE = 0.2
TRANSACTION_WAIT_TIME = 20

class TestWalletFlow(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        print("\n" + "="*60)
        print("SETTING UP TEST - Checking funding wallet...")
        print("="*60)
        
        if not config.FUNDING_WALLET_PRIVATE_KEY:
            print("❌ SKIPPING: Funding wallet private key not configured")
            self.skipTest("Funding wallet private key not configured")
        
        self.funding_wallet = Keypair.from_bytes(
            base58.b58decode(config.FUNDING_WALLET_PRIVATE_KEY)
        )
        print(f"Funding wallet: {self.funding_wallet.pubkey()}")
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
    
    def verify_token_balance(self, wallet_pubkey, token_type, expected_amount, token_name):
        """Helper method to verify token balance matches expected amount."""
        print(f"Checking {token_name} balance...")
        balance_raw = get_balance(wallet_pubkey, token_type)
        
        # Verify we got a valid balance
        self.assertIsNotNone(balance_raw)
        self.assertGreaterEqual(balance_raw, 0)
        print(f"Raw {token_name} balance: {balance_raw}")
        
        # Convert to human-readable format
        human_readable_balance = token_type.from_token_amount(balance_raw)
        print(f"Human-readable {token_name} balance: {human_readable_balance} {token_name}")
        
        # Verify the balance is exactly the expected amount
        self.assertEqual(human_readable_balance, expected_amount)
        
        return human_readable_balance

    def check_token_balance(self, token_type, min_amount, token_name):
        """Helper method to check if funding wallet has sufficient balance for a specific token."""
        print(f"\nChecking {token_name} balance...")
        balance_raw = get_balance(self.funding_wallet.pubkey(), token_type)
        balance = token_type.from_token_amount(balance_raw)
        print(f"Funding wallet {token_name} balance: {balance} {token_name}")
        
        if balance < min_amount:
            print(f"❌ SKIPPING: Insufficient {token_name} balance: {balance} {token_name} (need at least {min_amount} {token_name})")
            self.skipTest(f"Insufficient {token_name} balance: {balance} {token_name} (need at least {min_amount} {token_name})")
        
        print(f"✅ Sufficient {token_name} balance: {balance} {token_name}")
        return balance

    def test_wallet_flow_with_sol(self):
        """End-to-end integration test: create wallet, transfer SOL, check balance."""
        
        # Check SOL balance before starting test
        self.check_token_balance(TokenType.SOL, SOL_MIN_BALANCE, "SOL")
        
        # Step 1: Create new wallet
        new_wallet = self.create_and_verify_wallet("SOL")
        
        # Step 2: Transfer SOL from funding wallet to new wallet
        print("Transferring SOL...")
        transfer_result = transfer_sol(self.funding_wallet, new_wallet.pubkey(), SOL_TRANSFER_AMOUNT)
        
        # Verify transfer was successful
        self.assertTrue(transfer_result)
        print(f"SOL transfer successful: {SOL_TRANSFER_AMOUNT} SOL")
        
        # Step 3: Wait for transaction to be processed
        self.wait_for_transaction(TRANSACTION_WAIT_TIME, "SOL transaction")
        
        # Step 4: Verify SOL balance
        self.verify_token_balance(new_wallet.pubkey(), TokenType.SOL, SOL_TRANSFER_AMOUNT, "SOL")
        
        print("✅ End-to-end SOL wallet flow test completed successfully!")

    def test_wallet_flow_with_usdg(self):
        """End-to-end integration test: create wallet, create USDG ATA, transfer USDG, check balance."""
        
        # Check USDG balance before starting test
        self.check_token_balance(TokenType.USDG, USDG_TRANSFER_AMOUNT, "USDG")
        
        # Step 1: Create new wallet
        new_wallet = self.create_and_verify_wallet("USDG")
        
        # Step 2: Create USDG associated token account
        print("Creating USDG associated token account...")
        ata_result = create_associated_token_account(self.funding_wallet, new_wallet.pubkey(), TokenType.USDG)
        
        # Verify ATA creation was successful
        self.assertIsNotNone(ata_result)
        print(f"USDG ATA creation successful: {ata_result}")
        
        # Step 3: Wait for ATA creation to be processed
        self.wait_for_transaction(TRANSACTION_WAIT_TIME, "USDG ATA creation")
        
        # Step 4: Transfer USDG from funding wallet to new wallet
        print("Transferring USDG...")
        transfer_result = transfer_token(self.funding_wallet, new_wallet.pubkey(), TokenType.USDG, USDG_TRANSFER_AMOUNT)
        
        # Verify transfer was successful
        self.assertTrue(transfer_result)
        print(f"USDG transfer successful: {USDG_TRANSFER_AMOUNT} USDG")
        
        # Step 5: Wait for transaction to be processed
        self.wait_for_transaction(TRANSACTION_WAIT_TIME, "USDG transaction")
        
        # Step 6: Verify USDG balance
        self.verify_token_balance(new_wallet.pubkey(), TokenType.USDG, USDG_TRANSFER_AMOUNT, "USDG")
        
        print("✅ End-to-end USDG wallet flow test completed successfully!")

    def test_wallet_flow_with_usdc(self):
        """End-to-end integration test: create wallet, create USDC ATA, transfer USDC, check balance."""
        
        # Check USDC balance before starting test
        self.check_token_balance(TokenType.USDC, USDC_TRANSFER_AMOUNT, "USDC")
        
        # Step 1: Create new wallet
        new_wallet = self.create_and_verify_wallet("USDC")
        
        # Step 2: Create USDC associated token account
        print("Creating USDC associated token account...")
        ata_result = create_associated_token_account(self.funding_wallet, new_wallet.pubkey(), TokenType.USDC)
        
        # Verify ATA creation was successful
        self.assertIsNotNone(ata_result)
        print(f"USDC ATA creation successful: {ata_result}")
        
        # Step 3: Wait for ATA creation to be processed
        self.wait_for_transaction(TRANSACTION_WAIT_TIME, "USDC ATA creation")
        
        # Step 4: Transfer USDC from funding wallet to new wallet
        print("Transferring USDC...")
        transfer_result = transfer_token(self.funding_wallet, new_wallet.pubkey(), TokenType.USDC, USDC_TRANSFER_AMOUNT)
        
        # Verify transfer was successful
        self.assertTrue(transfer_result)
        print(f"USDC transfer successful: {USDC_TRANSFER_AMOUNT} USDC")
        
        # Step 5: Wait for transaction to be processed
        self.wait_for_transaction(TRANSACTION_WAIT_TIME, "USDC transaction")
        
        # Step 6: Verify USDC balance
        self.verify_token_balance(new_wallet.pubkey(), TokenType.USDC, USDC_TRANSFER_AMOUNT, "USDC")
        
        print("✅ End-to-end USDC wallet flow test completed successfully!")

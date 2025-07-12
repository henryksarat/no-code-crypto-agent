import unittest
import time
import os
import base58
from eth_account import Account
from solders.keypair import Keypair

# EVM imports
from dspy_evm_wallet.primitive_evm_functions import get_balance as get_evm_balance
from dspy_evm_wallet import config as evm_config

# Solana imports
from dspy_solana_wallet.primitive_solana_functions import get_balance as get_solana_balance
from dspy_solana_wallet import config as solana_config

class BaseMultiChainDSPyTest(unittest.TestCase):
    """Base class for multichain DSPy tests with common setup functionality."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        print("\n" + "="*80)
        print("SETTING UP DSPY AGENT MULTICHAIN TEST...")
        print("="*80)
        
        # Set up both chains
        self._setUpEVM()
        self._setUpSolana()
        
        print("✅ Both EVM and Solana chains are ready for testing")
        print("="*80)
    
    def _setUpEVM(self):
        """Set up EVM test fixtures."""
        print("\n" + "-"*40)
        print("SETTING UP EVM CHAIN...")
        print("-"*40)
        
        if not evm_config.EVM_FUNDING_WALLET_PRIVATE_KEY:
            print("❌ SKIPPING: EVM funding wallet private key not configured")
            self.skipTest("EVM funding wallet private key not configured")

        if not evm_config.OPENAI_API_KEY:
            print("❌ SKIPPING: OPENAI_API_KEY not configured")
            self.skipTest("OPENAI_API_KEY not configured")
        
        # Set environment variable for OpenAI
        os.environ["OPENAI_API_KEY"] = evm_config.OPENAI_API_KEY

        print(f"✅ EVM RPC URL: {evm_config.ETH_RPC_URL}")
        print(f"✅ EVM Funding wallet configured")

        # Create funding wallet object for balance checks
        self.evm_funding_wallet = Account.from_key(evm_config.EVM_FUNDING_WALLET_PRIVATE_KEY)
        print(f"ℹ️  EVM Funding wallet: {self.evm_funding_wallet.address}")
        
        # Check EVM funding wallet balances
        print("\nChecking EVM funding wallet balances...")
        self._checkEVMBalances()
        
        print("✅ EVM funding wallet has sufficient balances for all tests")
        print("-"*40)
    
    def _setUpSolana(self):
        """Set up Solana test fixtures."""
        print("\n" + "-"*40)
        print("SETTING UP SOLANA CHAIN...")
        print("-"*40)
        
        # Verify we're on devnet
        if solana_config.SOLANA_NETWORK != "devnet":
            print("❌ SKIPPING: Solana tests only work on devnet")
            self.skipTest("Solana tests only work on devnet")

        if not solana_config.SOLANA_FUNDING_WALLET_PRIVATE_KEY:
            print("❌ SKIPPING: Solana funding wallet private key not configured")
            self.skipTest("Solana funding wallet private key not configured")

        if not solana_config.SOLANA_FUNDING_WALLET_PUBLIC_KEY:
            print("❌ SKIPPING: Solana funding wallet public key not configured")
            self.skipTest("Solana funding wallet public key not configured")

        print(f"✅ Solana Network configuration: {solana_config.SOLANA_NETWORK}")
        print(f"✅ Solana Funding wallet configured: {solana_config.SOLANA_FUNDING_WALLET_PUBLIC_KEY}")

        # Create funding wallet object for balance checks
        self.solana_funding_wallet = Keypair.from_bytes(
            base58.b58decode(solana_config.SOLANA_FUNDING_WALLET_PRIVATE_KEY)
        )
        print(f"ℹ️  Solana Funding wallet: {self.solana_funding_wallet.pubkey()}")
        
        # Check Solana funding wallet balances
        print("\nChecking Solana funding wallet balances...")
        self._checkSolanaBalances()
        
        print("✅ Solana funding wallet has sufficient balances for all tests")
        print("-"*40)
    
    def _checkEVMBalances(self):
        """Check EVM funding wallet balances. Override in subclasses to specify required balances."""
        # Default implementation - subclasses should override with specific balance requirements
        pass
    
    def _checkSolanaBalances(self):
        """Check Solana funding wallet balances. Override in subclasses to specify required balances."""
        # Default implementation - subclasses should override with specific balance requirements
        pass
    
    def _check_evm_funding_wallet_balance(self, token_type, min_amount, token_name):
        """Helper method to check if EVM funding wallet has sufficient balance for a specific token."""
        balance = get_evm_balance(self.evm_funding_wallet.address, token_type)
        print(f"EVM Funding wallet {token_name} balance: {balance} {token_name}")
        
        if balance < min_amount:
            print(f"❌ SKIPPING: Insufficient EVM {token_name} balance: {balance} {token_name} (need at least {min_amount} {token_name})")
            self.skipTest(f"Insufficient EVM {token_name} balance: {balance} {token_name} (need at least {min_amount} {token_name})")
    
    def _check_solana_funding_wallet_balance(self, token_type, min_amount, token_name):
        """Helper method to check if Solana funding wallet has sufficient balance for a specific token."""
        balance_raw = get_solana_balance(self.solana_funding_wallet.pubkey(), token_type)
        balance = token_type.from_token_amount(balance_raw)
        print(f"Solana Funding wallet {token_name} balance: {balance} {token_name}")
        
        if balance < min_amount:
            print(f"❌ SKIPPING: Insufficient Solana {token_name} balance: {balance} {token_name} (need at least {min_amount} {token_name})")
            self.skipTest(f"Insufficient Solana {token_name} balance: {balance} {token_name} (need at least {min_amount} {token_name})")
    
    def _wait_for_transaction(self, seconds=15, description="transaction"):
        """Helper method to wait for transactions to be processed."""
        print(f"Waiting {seconds} seconds for {description} to be processed...")
        time.sleep(seconds)
    
    def _verify_evm_token_balance(self, wallet_address, token_type, expected_amount, description=""):
        """Generic helper method to verify EVM token balance matches expected amount."""
        print(f"Checking EVM {token_type.name} balance{description}...")

        balance = get_evm_balance(wallet_address, token_type)
        self.assertEqual(float(balance), float(expected_amount))
        
        print(f"✅ EVM {token_type.name} balance is exactly as expected: {expected_amount}")
    
    def _verify_solana_token_balance(self, wallet_pubkey, token_type, expected_amount, description=""):
        """Generic helper method to verify Solana token balance matches expected amount."""
        token_name = token_type.name
        print(f"Checking Solana {token_name} balance{description}...")

        balance_raw = get_solana_balance(wallet_pubkey, token_type)
        formatted_balance = token_type.from_token_amount(balance_raw)
        self.assertEqual(formatted_balance, expected_amount)
        
        print(f"✅ Solana {token_name} balance is exactly as expected: {expected_amount}")


class BaseEVMOnlyDSPyTest(unittest.TestCase):
    """Base class for EVM-only DSPy tests."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        print("\n" + "="*60)
        print("SETTING UP DSPY AGENT EVM TEST...")
        print("="*60)
        
        self._setUpEVM()
        print("SETTING UP DSPY AGENT EVM INTEGRATION TEST...")
    
    def _setUpEVM(self):
        """Set up EVM test fixtures."""
        # Debug: Print what's loaded from config
        print(f"DEBUG: EVM_FUNDING_WALLET_PRIVATE_KEY = {evm_config.EVM_FUNDING_WALLET_PRIVATE_KEY}")
        print(f"DEBUG: OPENAI_API_KEY = {evm_config.OPENAI_API_KEY}")
        
        if not evm_config.EVM_FUNDING_WALLET_PRIVATE_KEY:
            print("❌ SKIPPING: EVM funding wallet private key not configured")
            self.skipTest("EVM funding wallet private key not configured")

        if not evm_config.OPENAI_API_KEY:
            print("❌ SKIPPING: OPENAI_API_KEY not configured")
            self.skipTest("OPENAI_API_KEY not configured")
        
        os.environ["OPENAI_API_KEY"] = evm_config.OPENAI_API_KEY

        print(f"✅ EVM RPC URL: {evm_config.ETH_RPC_URL}")
        print(f"✅ Funding wallet configured")

        # Create funding wallet object for balance checks
        self.funding_wallet = Account.from_key(evm_config.EVM_FUNDING_WALLET_PRIVATE_KEY)
        print(f"ℹ️  Funding wallet: {self.funding_wallet.address}")
        
        # Check funding wallet balances
        print("\nChecking funding wallet balances...")
        self._checkEVMBalances()
        
        print("✅ Funding wallet has sufficient balances for all tests")
        print("="*60)
    
    def _checkEVMBalances(self):
        """Check EVM funding wallet balances. Override in subclasses to specify required balances."""
        # Default implementation - subclasses should override with specific balance requirements
        pass
    
    def _check_funding_wallet_balance(self, token_type, min_amount, token_name):
        """Helper method to check if funding wallet has sufficient balance for a specific token."""
        balance = get_evm_balance(self.funding_wallet.address, token_type)
        print(f"Funding wallet {token_name} balance: {balance} {token_name}")
        
        if balance < min_amount:
            print(f"❌ SKIPPING: Insufficient {token_name} balance: {balance} {token_name} (need at least {min_amount} {token_name})")
            self.skipTest(f"Insufficient {token_name} balance: {balance} {token_name} (need at least {min_amount} {token_name})")
    
    def _wait_for_transaction(self, seconds=15, description="transaction"):
        """Helper method to wait for transactions to be processed."""
        print(f"Waiting {seconds} seconds for {description} to be processed...")
        time.sleep(seconds)
    
    def _verify_token_balance(self, wallet_address, token_type, expected_amount, description=""):
        """Generic helper method to verify token balance matches expected amount."""
        print(f"Checking {token_type.name} balance{description}...")

        balance = get_evm_balance(wallet_address, token_type)
        self.assertEqual(float(balance), float(expected_amount))
        
        print(f"✅ {token_type.name} balance is exactly as expected: {expected_amount}") 
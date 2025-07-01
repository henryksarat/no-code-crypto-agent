import unittest
import pytest
import sys
from unittest.mock import patch, MagicMock

# Import after adding to path
from dspy_solana_wallet.agent_with_complex_usdg_validation import agent_with_usdg_validation
from dspy_solana_wallet.agent_tools import get_last_user_wallet_created
from dspy_solana_wallet.token_types import TokenType
from .test_dspy_base import BaseDSPyAgentTest, TRANSACTION_WAIT_TIME

# Test constants for transfer amounts
USDG_TRANSFER_AMOUNT = 10.0
PYUSD_TRANSFER_AMOUNT = 10.0
SOL_MIN_BALANCE = 0.1  # Minimum SOL needed for fees

class TestDSPyAgentComplexUSDGValidation(BaseDSPyAgentTest):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        required_balances = [
            (TokenType.SOL, SOL_MIN_BALANCE, "SOL"), 
            (TokenType.USDG, USDG_TRANSFER_AMOUNT, "USDG"),  
            (TokenType.PYUSD, PYUSD_TRANSFER_AMOUNT, "PYUSD")   
        ]
                # Skip this test when running all tests, but allow direct execution
        if 'test_dspy_agent_with_complex_usdg_validation.py' not in ' '.join(sys.argv):
            pytest.skip("Run this test explicitly with: python -m pytest tests/test_dspy_agent_with_complex_usdg_validation.py -v -s")

        super().setUp(required_balances)
        print("SETTING UP DSPY AGENT COMPLEX USDG VALIDATION TEST...")

    def test_dspy_agent_usdg_limit_total_balance(self):
        """End-to-end integration test: 
        * create wallet via DSPy agent
        * Send 2.0 USDG to the wallet
        * Send 2.0 USDG to the wallet
        * Attempt to send 2.0 USDG to the wallet
        * Verify that the final balance is 4.0 USDG and that the third 2.0 USDG transfer was rejected.
        """
        create_wallet_request = (
                f"create a new wallet. This will be the user wallet. fund it with 2.0 USDG."
                f"Please return the wallet public key and let me know how much USDG you funded it."
        )
        print(f"💻 Create wallet and deposit USDG.")
        print(f"ℹ️  User_request to agent: {create_wallet_request}")

        try:
            create_result = agent_with_usdg_validation(user_request=create_wallet_request)
            print(f"✅ User_request response agent result: {create_result.process_result}")
            
            # Verify wallet was created
            self.assertIsNotNone(create_result.process_result)
            self.assertIn("wallet", create_result.process_result.lower())
            self.assertIn("usdg", create_result.process_result.lower())
            
            expected_wallet_public_key = get_last_user_wallet_created()

            self.wait_for_transaction(TRANSACTION_WAIT_TIME, "USDG transfers")
            self.verify_token_balance(expected_wallet_public_key, TokenType.USDG, 2.0, " (direct verification)")

            fund_wallet_request = (f"Use the last user wallet created and send it 2.0 USDG.")
            print(f"ℹ️  User_request to agent: {fund_wallet_request}")
            create_result = agent_with_usdg_validation(user_request=fund_wallet_request)
            print(f"✅ User_request response agent result: {create_result.process_result}")
            self.wait_for_transaction(TRANSACTION_WAIT_TIME, "USDG transfers")

            self.verify_token_balance(expected_wallet_public_key, TokenType.USDG, 4.0, " (direct verification)")

            fund_wallet_request = (f"Send 2.0 USDG to the last user wallet created.")
            print(f"ℹ️  User_request to agent: {fund_wallet_request}")
            create_result = agent_with_usdg_validation(user_request=fund_wallet_request)
            print(f"✅ User_request response agent result: {create_result}")
            self.wait_for_transaction(TRANSACTION_WAIT_TIME, "USDG transfers")
            self.assertIn("you are being greedy", create_result.process_result.lower())
            self.verify_token_balance(expected_wallet_public_key, TokenType.USDG, 4.0, " (direct verification)")
        except Exception as e:
            print(f"❌ Wallet creation failed: {e}")
            self.fail(f"Wallet creation failed: {e}")

    def test_dspy_agent_usdg_limit_does_not_affect_other_tokens(self):
        """End-to-end integration test: 
        * create wallet via DSPy agent
        * Send 2.0 PYUSD to the wallet
        * Send 2.0 PYUSD to the wallet
        * Send 2.0 PYUSD to the wallet
        * Verify that the final balance is 6.0 PYUSD.
        """
        create_wallet_request = (
                f"create a new wallet. This will be the user wallet. fund it with 2.0 PYUSD."
                f"Please return the wallet public key and let me know how much PYUSD you funded it."
        )
        print(f"💻 Create wallet and deposit PYUSD.")
        print(f"ℹ️  User_request to agent: {create_wallet_request}")

        try:
            create_result = agent_with_usdg_validation(user_request=create_wallet_request)
            print(f"✅ User_request response agent result: {create_result.process_result}")
            
            # Verify wallet was created
            self.assertIsNotNone(create_result.process_result)
            self.assertIn("wallet", create_result.process_result.lower())
            self.assertIn("pyusd", create_result.process_result.lower())
            
            expected_wallet_public_key = get_last_user_wallet_created()

            self.wait_for_transaction(TRANSACTION_WAIT_TIME, "PYUSD transfers")
            self.verify_token_balance(expected_wallet_public_key, TokenType.PYUSD, 2.0, " (direct verification)")

            fund_wallet_request = (f"Use the last user wallet created and send it 2.0 PYUSD.")
            print(f"ℹ️  User_request to agent: {fund_wallet_request}")
            create_result = agent_with_usdg_validation(user_request=fund_wallet_request)
            print(f"✅ User_request response agent result: {create_result.process_result}")
            self.wait_for_transaction(TRANSACTION_WAIT_TIME, "PYUSD transfers")

            self.verify_token_balance(expected_wallet_public_key, TokenType.PYUSD, 4.0, " (direct verification)")

            fund_wallet_request = (f"Send 2.0 PYUSD to the last user wallet created.")
            print(f"ℹ️  User_request to agent: {fund_wallet_request}")
            create_result = agent_with_usdg_validation(user_request=fund_wallet_request)
            print(f"✅ User_request response agent result: {create_result}")
            self.wait_for_transaction(TRANSACTION_WAIT_TIME, "PYUSD transfers")
            self.assertNotIn("greedy", create_result.process_result.lower())
            self.verify_token_balance(expected_wallet_public_key, TokenType.PYUSD, 6.0, " (direct verification)")
        except Exception as e:
            print(f"❌ Wallet creation failed: {e}")
            self.fail(f"Wallet creation failed: {e}")

    def test_dspy_agent_usdg_one_transfer_limit(self):
        """End-to-end integration test: 
        * create wallet via DSPy agent
        * Send 0.1 USDG to the wallet successfully
        * Attempt to send 4.0 USDG to the wallet but it should be rejected
        * Send 0.2 USDG to the wallet successfully
        * Verify that the final balance is 0.3 USDG
        """
        create_wallet_request = (
                f"create a new wallet. This will be the user wallet. fund it with 0.1 USDG."
                f"Please return the wallet public key and let me know how much USDG you funded it."
        )
        print(f"💻 Create wallet and deposit USDG.")
        print(f"ℹ️  User_request to agent: {create_wallet_request}")

        try:
            create_result = agent_with_usdg_validation(user_request=create_wallet_request)
            print(f"✅ User_request response agent result: {create_result}")
            
            # Verify wallet was created
            self.assertIsNotNone(create_result.process_result)
            self.assertIn("wallet", create_result.process_result.lower())
            self.assertIn("usdg", create_result.process_result.lower())
            
            expected_wallet_public_key = get_last_user_wallet_created()

            self.wait_for_transaction(TRANSACTION_WAIT_TIME, "USDG transfers")
            self.verify_token_balance(expected_wallet_public_key, TokenType.USDG, 0.1, " (direct verification)")

            # Attempt to send 4.0 USDG - should be rejected due to single transfer limit
            fund_wallet_request = (f"Send 4.0 USDG to the last user wallet created.")
            print(f"ℹ️  User_request to agent: {fund_wallet_request}")
            create_result = agent_with_usdg_validation(user_request=fund_wallet_request)
            print(f"✅ User_request response agent result: {create_result}")
            self.assertIn("thief", create_result.process_result.lower())
            
            # Verify balance is still 0.1 USDG after rejected transfer
            self.verify_token_balance(expected_wallet_public_key, TokenType.USDG, 0.1, " (after rejected transfer)")

            # Send 0.2 USDG - should be successful
            fund_wallet_request = (f"Send 0.2 USDG to the last user wallet created.")
            print(f"ℹ️  User_request to agent: {fund_wallet_request}")
            create_result = agent_with_usdg_validation(user_request=fund_wallet_request)
            print(f"✅ User_request response agent result: {create_result}")
            self.wait_for_transaction(TRANSACTION_WAIT_TIME, "USDG transfers")
            
            # Verify final balance is 0.3 USDG (0.1 + 0.2)
            self.verify_token_balance(expected_wallet_public_key, TokenType.USDG, 0.3, " (final verification)")
        except Exception as e:
            print(f"❌ Wallet creation failed: {e}")
            self.fail(f"Wallet creation failed: {e}")

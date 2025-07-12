import unittest
import time

# Import after adding to path
from dspy_agents.agent_basic import agent_basic
from dspy_agents import get_last_evm_user_wallet_created
from dspy_evm_wallet.token_types import TokenType
from .test_dspy_multichain_base import BaseEVMOnlyDSPyTest

# Test constants for transfer amounts
ETH_TRANSFER_AMOUNT = 0.001  # Small amount for testing
USDC_TRANSFER_AMOUNT = 0.1   # Small amount for testing
PYUSD_TRANSFER_AMOUNT = 0.2  # Small amount for testing

# Test constants for minimum balance requirements
ETH_MIN_BALANCE = 0.01  # Minimum ETH needed for fees
USDC_MIN_BALANCE = 0.5  # Minimum USDC needed for testing
PYUSD_MIN_BALANCE = 1.0 # Minimum PYUSD needed for testing
TRANSACTION_WAIT_TIME = 45  # Seconds to wait for transactions

class TestDSPyAgentEVMIntegration(BaseEVMOnlyDSPyTest):
    
    def _checkEVMBalances(self):
        """Check EVM funding wallet balances for this specific test."""
        required_balances = [
            (TokenType.ETH, ETH_MIN_BALANCE, "ETH"), 
            (TokenType.USDC, USDC_MIN_BALANCE, "USDC"),  
            (TokenType.PYUSD, PYUSD_MIN_BALANCE, "PYUSD")   
        ]
        
        for token_type, min_amount, token_name in required_balances:
            self._check_funding_wallet_balance(token_type, min_amount, token_name)
    
    def test_dspy_agent_wallet_creation_and_eth_transfer(self):
        """End-to-end integration test: 
        * create wallet via DSPy agent
        * verify public key returned in specific format
        * send ETH
        * send USDC
        * send PYUSD
        * verify balance in a specific format.
        """
        
        print("\n🧪 Testing DSPy agent wallet creation and ETH, USDC, PYUSD transfer...")
        
        # Note: This test assumes the DSPy agent has been updated to support EVM operations
        # For now, this is a placeholder test structure
        
        create_wallet_request = (
            f"create a new EVM wallet. This will be the user wallet. "
            f"Send {ETH_TRANSFER_AMOUNT} ETH. "
            f"Please return the wallet public key and let me know how much ETH you funded it."
        )
        
        try:
            print(f"💻 Create wallet and deposit ETH.")
            print(f"ℹ️  User_request to agent: {create_wallet_request}")
            # Note: This would need to be updated to use an EVM-capable agent
            create_result = agent_basic(user_request=create_wallet_request)
            print(f"✅ User_request response agent result: {create_result.process_result}")
            print(f"✅ User_request response agent result: {create_result.reasoning}")
            
            # For now, just create a wallet directly for testing
            self.assertIsNotNone(create_result.process_result)
            self.assertIn("wallet", create_result.process_result.lower())
            self.assertIn(str(0.001), create_result.process_result.lower())
            self.assertIn("eth", create_result.process_result.lower())
        except Exception as e:
            print(f"❌ Wallet creation failed: {e}")
            self.fail(f"Wallet creation failed: {e}")
        
        try:
            print(f"💻 Get wallet public key")
            expected_wallet_public_key = get_last_evm_user_wallet_created()
            get_wallet_public_key_request = f"What is public key of the last wallet that was just created. Return it in the format: wallet_public_key={{public_key}}."
            print(f"ℹ️  User_request to agent: {get_wallet_public_key_request}")
            get_wallet_public_key_result = agent_basic(user_request=get_wallet_public_key_request)
            print(f"✅ User_request response agent result: {get_wallet_public_key_result.process_result}")
            
            self.assertEqual(get_wallet_public_key_result.process_result, f"wallet_public_key={expected_wallet_public_key}")
            print(f"✅ Retrieved wallet public key in correct format: {get_wallet_public_key_result.process_result,}")
        except Exception as e:
            print(f"❌ Wallet public key retrieval failed: {e}")
            self.fail(f"Wallet public key retrieval failed: {e}")

        try:
            balance_request = f"Do not create a new wallet. Fund the wallet with {USDC_TRANSFER_AMOUNT} USDC on ethereum from the funding wallet. Make sure it is usdc and not usdg."
            print(f"💻 Fund wallet with USDC")
            print(f"ℹ️  User_request to agent: {balance_request}")
            balance_result = agent_basic(user_request=balance_request)
            print(f"✅ Ethereum USDC funding result: {balance_result.process_result}")
            self.assertIsNotNone(balance_result.process_result)

            # Add a delay between transfers to avoid nonce conflicts
            print("⏳ Waiting 5 seconds between transfers to avoid nonce conflicts...")
            time.sleep(5)

            balance_request = f"Fund the wallet with {PYUSD_TRANSFER_AMOUNT} PYUSD on ethereum from the funding wallet. "
            print(f"💻 Fund wallet with PYUSD")
            print(f"ℹ️  User_request to agent: {balance_request}")
            balance_result = agent_basic(user_request=balance_request)
            print(f"✅ Ethereum PYUSD funding result: {balance_result.process_result}")
            self.assertIsNotNone(balance_result.process_result)
            
            self._wait_for_transaction(TRANSACTION_WAIT_TIME, "ETH, USDC, PYUSD transfers")

            self._verify_token_balance(expected_wallet_public_key, TokenType.PYUSD, PYUSD_TRANSFER_AMOUNT, " (direct verification)")
            self._verify_token_balance(expected_wallet_public_key, TokenType.ETH, ETH_TRANSFER_AMOUNT, " (direct verification)")
            self._verify_token_balance(expected_wallet_public_key, TokenType.USDC, USDC_TRANSFER_AMOUNT, " (direct verification)")
            print(f"✅ Wallet correctly funded. Verified via direct function call. Now will test agent retrieval of balance.")
        except Exception as e:
            print(f"❌ Balance retrieval failed: {e}")
            self.fail(f"Balance retrieval failed: {e}")
        
        try:
            print(f"💻 Get balance of wallet")
            print(f"ℹ️  User_request to agent: {balance_request}")
            balance_request = (
                f"return me the pyusd, eth, and usdc that was funded for the last evm wallet. Have the "
                f"result be in the format: pyusd={{PYUSD_amount}};usdc={{USDC_amount}};eth={{ETH_amount}}. "
                f"Make sure that the amount is formatted with 2 decimal places."
            )

            balance_result = agent_basic(user_request=balance_request)
            print(f"✅ Balance retrieval result: {balance_result.process_result}")
            
            result_text = balance_result.process_result
            print(f"Result text: '{result_text}'")
                    
            # Verify the reported amount matches the actual balance
            expected_format = f"pyusd={PYUSD_TRANSFER_AMOUNT:.2f};usdc={USDC_TRANSFER_AMOUNT:.2f};eth={ETH_TRANSFER_AMOUNT:.2f}"
            self.assertEqual(result_text, expected_format)
            print(f"✅ Reported format is exactly as expected: {result_text}")
        except Exception as e:
            print(f"❌ Balance retrieval failed: {e}")
            self.fail(f"Balance retrieval failed: {e}")

        print("✅ DSPy agent integration test completed successfully!")

    def test_dspy_agent_error_handling(self):
        """Test DSPy agent error handling for invalid requests."""
        
        print("\n🧪 Testing DSPy agent error handling...")
        
        # Test with an invalid request
        invalid_request = "this is an invalid request that should not work"
        
        try:
            result = agent_basic(invalid_request)
            print(f"Agent response to invalid request: {result.process_result}")
            
            # The agent should handle invalid requests gracefully
            self.assertIsNotNone(result.process_result)
            
        except Exception as e:
            print(f"Agent handled invalid request with exception: {e}")
            # This is also acceptable behavior
            
        print("✅ DSPy agent error handling test completed!")
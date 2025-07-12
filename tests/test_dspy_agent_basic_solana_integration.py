import unittest
from unittest.mock import patch, MagicMock

# Import after adding to path
from dspy_agents.agent_basic import agent_basic
from dspy_agents import get_last_solana_user_wallet_created
from dspy_solana_wallet.token_types import TokenType
from .test_dspy_base import BaseDSPyAgentTest, TRANSACTION_WAIT_TIME, SOL_MIN_BALANCE

# Test constants for transfer amounts
USDG_TRANSFER_AMOUNT = 0.2
USDC_TRANSFER_AMOUNT = 0.1
SOL_TRANSFER_AMOUNT = 0.02

class TestDSPyAgentIntegration(BaseDSPyAgentTest):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        required_balances = [
            (TokenType.SOL, SOL_MIN_BALANCE, "SOL"), 
            (TokenType.USDG, USDG_TRANSFER_AMOUNT, "USDG"),  
            (TokenType.USDC, USDC_TRANSFER_AMOUNT, "USDC")   
        ]
        super().setUp(required_balances)
        print("SETTING UP DSPY AGENT INTEGRATION TEST...")
    
    def test_dspy_agent_wallet_creation_and_usdg_transfer(self):
        """End-to-end integration test: 
        * create wallet via DSPy agent
        * verify public key returned in specific format
        * send USDG
        * send SOL
        * send USDC
        * verify balance in a speicifc format.
        """
        
        print("\n🧪 Testing DSPy agent wallet creation and USDG, SOL, USDC transfer...")
        

        create_wallet_request = (
            f"create a new wallet. This will be the user wallet. "
            f"Send {USDG_TRANSFER_AMOUNT} USDG. "
            f"Please return the wallet public key and let me know how much USDG you funded it."
        )
        
        try:
            print(f"💻 Create wallet and deposit USDG.")
            print(f"ℹ️  User_request to agent: {create_wallet_request}")
            create_result = agent_basic(user_request=create_wallet_request)
            print(f"✅ User_request response agent result: {create_result.process_result}")
            
            # Verify wallet was created
            self.assertIsNotNone(create_result.process_result)
            self.assertIn("wallet", create_result.process_result.lower())
            self.assertIn(str(USDG_TRANSFER_AMOUNT), create_result.process_result.lower())
            self.assertIn("usdg", create_result.process_result.lower())
        except Exception as e:
            print(f"❌ Wallet creation failed: {e}")
            self.fail(f"Wallet creation failed: {e}")
        
        try:
            print(f"💻 Get wallet public key")
            expected_wallet_public_key = get_last_solana_user_wallet_created()
            get_wallet_public_key_request = f"What is public key of the last wallet that was just created. Return it in the format: wallet_public_key={{public_key}}."
            print(f"ℹ️  User_request to agent: {get_wallet_public_key_request}")
            get_wallet_public_key_result = agent_basic(user_request=get_wallet_public_key_request)
            print(f"✅ User_request response agent result: {get_wallet_public_key_result.process_result}")
            
            self.assertEqual(get_wallet_public_key_result.process_result, f"wallet_public_key={expected_wallet_public_key}")
            print(f"✅ Retrieved wallet public key in correct format: {get_wallet_public_key_result.process_result,}")
        except Exception as e:
            print(f"❌ Wallet public key retrieval failed: {e}")
            self.fail(f"Wallet public key retrieval failed: {e}")


        balance_request = f"Do not create a new wallet. fund the last wallet with {SOL_TRANSFER_AMOUNT} SOL and do not use the faucet and use the funding wallet instead. Fund the wallet with {USDC_TRANSFER_AMOUNT} USDC from teh funding wallet too. Make sure it is USDC and NOT USDG."

        try:
            print(f"💻 Fund wallet with SOL and USDC")
            print(f"ℹ️  User_request to agent: {balance_request}")
            balance_result = agent_basic(user_request=balance_request)
            print(f"✅ SOL and USDC funding result: {balance_result.process_result}")
            
            # Verify the result format matches the expected pattern
            self.assertIsNotNone(balance_result.process_result)
            
            # Step 4: Wait for transaction to be processed
            self.wait_for_transaction(TRANSACTION_WAIT_TIME, "USDG, USDC, SOL transfers")

            # Step 5: Verify balances using direct function call
            self.verify_token_balance(expected_wallet_public_key, TokenType.USDG, USDG_TRANSFER_AMOUNT, " (direct verification)")
            self.verify_token_balance(expected_wallet_public_key, TokenType.SOL, SOL_TRANSFER_AMOUNT, " (direct verification)")
            self.verify_token_balance(expected_wallet_public_key, TokenType.USDC, USDC_TRANSFER_AMOUNT, " (direct verification)")
            print(f"✅ Wallet correctly funded. Verified via direct function call. Now will test agent retrieval of balance.")
        except Exception as e:
            print(f"❌ Balance retrieval failed: {e}")
            self.fail(f"Balance retrieval failed: {e}")
        
        try:
            print(f"💻 Get balance of wallet")
            print(f"ℹ️  User_request to agent: {balance_request}")
            balance_request = (
                f"return me the usdg that was funded for the last wallet. Have the "
                f"result be in the format: usdg={{USDG_amount}};usdc={{USDC_amount}};sol={{SOL_amount}}. "
                f"Make sure that the amount is formatted with 2 decimal places."
            )

            balance_result = agent_basic(user_request=balance_request)
            print(f"✅ Balance retrieval result: {balance_result.process_result}")
            
            result_text = balance_result.process_result
            print(f"Result text: '{result_text}'")
                    
            # Verify the reported amount matches the actual balance
            expected_format = f"usdg={USDG_TRANSFER_AMOUNT:.2f};usdc={USDC_TRANSFER_AMOUNT:.2f};sol={SOL_TRANSFER_AMOUNT:.2f}"
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

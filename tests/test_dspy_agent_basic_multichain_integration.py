import unittest
import time

# Import after adding to path
from dspy_agents.agent_basic import agent_basic
from dspy_agents import get_last_evm_user_wallet_created, get_last_solana_user_wallet_created
from dspy_evm_wallet.token_types import TokenType as EVMTokenType
from dspy_solana_wallet.token_types import TokenType as SolanaTokenType
from .test_dspy_multichain_base import BaseMultiChainDSPyTest

# Test constants for transfer amounts
ETH_TRANSFER_AMOUNT = 0.001  
USDC_EVM_TRANSFER_AMOUNT = 0.1 
USDC_SOLANA_TRANSFER_AMOUNT = 0.2
PYUSD_EVM_TRANSFER_AMOUNT = 0.2  
USDG_SOLANA_TRANSFER_AMOUNT = 0.3
SOL_TRANSFER_AMOUNT = 0.02 

# Test constants for minimum balance requirements
ETH_MIN_BALANCE = 0.01  
USDC_MIN_BALANCE = 0.5  
PYUSD_MIN_BALANCE = 1.0 
SOL_MIN_BALANCE = 0.1   
USDG_MIN_BALANCE = 0.5  
TRANSACTION_WAIT_TIME = 45 

class TestDSPyAgentMultiChainIntegration(BaseMultiChainDSPyTest):
    
    def _checkEVMBalances(self):
        """Check EVM funding wallet balances for this specific test."""
        evm_required_balances = [
            (EVMTokenType.ETH, ETH_MIN_BALANCE, "ETH"), 
            (EVMTokenType.USDC, USDC_MIN_BALANCE, "USDC"),  
            (EVMTokenType.PYUSD, PYUSD_MIN_BALANCE, "PYUSD")   
        ]
        
        for token_type, min_amount, token_name in evm_required_balances:
            self._check_evm_funding_wallet_balance(token_type, min_amount, token_name)
    
    def _checkSolanaBalances(self):
        """Check Solana funding wallet balances for this specific test."""
        solana_required_balances = [
            (SolanaTokenType.SOL, SOL_MIN_BALANCE, "SOL"), 
            (SolanaTokenType.USDG, USDG_MIN_BALANCE, "USDG"),  
            (SolanaTokenType.USDC, USDC_MIN_BALANCE, "USDC")   
        ]
        
        for token_type, min_amount, token_name in solana_required_balances:
            self._check_solana_funding_wallet_balance(token_type, min_amount, token_name)
    
    def _interact_with_agent(self, action_description, user_request):
        """Helper method to standardize agent interactions."""
        print(f"💻 {action_description}...")
        print(f"ℹ️  User request to agent: {user_request}")
        
        result = agent_basic(user_request=user_request)
        print(f"✅ Agent response: {result.process_result}")
        
        return result

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
            f"create a new EVM wallet and a new solana wallet."
            f"Send {ETH_TRANSFER_AMOUNT} ETH to the EVM wallet and {SOL_TRANSFER_AMOUNT} SOL to the solana wallet. "
            f"Please return the two wallet public keys and let me know how much ETH and SOL you funded it."
        )
        
        try:
            create_result = self._interact_with_agent(
                "Creating wallets and depositing ETH and SOL",
                create_wallet_request
            )
            
            # For now, just create a wallet directly for testing
            self.assertIsNotNone(create_result.process_result)
            self.assertIn("wallet", create_result.process_result.lower())
            self.assertIn("eth", create_result.process_result.lower())
            self.assertIn("sol", create_result.process_result.lower())
            self.assertIn(str(ETH_TRANSFER_AMOUNT), create_result.process_result.lower())
            self.assertIn(str(SOL_TRANSFER_AMOUNT), create_result.process_result.lower())
        except Exception as e:
            print(f"❌ Wallet creation failed: {e}")
            self.fail(f"Wallet creation failed: {e}")
        
        try:
            expected_evm_wallet_public_key = get_last_evm_user_wallet_created()
            expected_solana_wallet_public_key = get_last_solana_user_wallet_created()
            get_wallet_public_key_request = f"What is public key of the last EVM and Solana wallet that was just created. Return it in the format: evm_wallet_public_key={{public_key}}, solana_wallet_public_key={{public_key}}."
            
            get_wallet_public_key_result = self._interact_with_agent(
                "Getting wallet public keys",
                get_wallet_public_key_request
            )
            
            self.assertEqual(get_wallet_public_key_result.process_result, f"evm_wallet_public_key={expected_evm_wallet_public_key}, solana_wallet_public_key={expected_solana_wallet_public_key}")
            print(f"✅ Retrieved wallet public key in correct format: {get_wallet_public_key_result.process_result,}")
        except Exception as e:
            print(f"❌ Wallet public key retrieval failed: {e}")
            self.fail(f"Wallet public key retrieval failed: {e}")

        try:
            balance_request = f"Do not create a new wallet. Fund the evm wallet with {USDC_EVM_TRANSFER_AMOUNT} USDC on ethereum from the evm funding wallet. Also, fund the solana wallet with {USDC_SOLANA_TRANSFER_AMOUNT} USDC from the solana funding wallet. Make sure it is usdc and not usdg."
            balance_result = self._interact_with_agent(
                "Funding wallets with USDC",
                balance_request
            )
            self.assertIsNotNone(balance_result.process_result)

            balance_request = f"Fund the evm wallet with {PYUSD_EVM_TRANSFER_AMOUNT} PYUSD on ethereum from the funding wallet. "
            balance_result = self._interact_with_agent(
                "Funding EVM wallet with PYUSD",
                balance_request
            )
            self.assertIsNotNone(balance_result.process_result)

            balance_request = f"Fund the solana wallet with {USDG_SOLANA_TRANSFER_AMOUNT} USDG on solana from the solana funding wallet. "
            balance_result = self._interact_with_agent(
                "Funding Solana wallet with USDG",
                balance_request
            )
            self.assertIsNotNone(balance_result.process_result)
            
            self._wait_for_transaction(TRANSACTION_WAIT_TIME, "USDC, PYUSD, USDG transfers")

            self._verify_evm_token_balance(expected_evm_wallet_public_key, EVMTokenType.PYUSD, PYUSD_EVM_TRANSFER_AMOUNT, " (direct verification)")
            self._verify_evm_token_balance(expected_evm_wallet_public_key, EVMTokenType.USDC, USDC_EVM_TRANSFER_AMOUNT, " (direct verification)")
            self._verify_solana_token_balance(expected_solana_wallet_public_key, SolanaTokenType.USDC, USDC_SOLANA_TRANSFER_AMOUNT, " (direct verification)")
            self._verify_solana_token_balance(expected_solana_wallet_public_key, SolanaTokenType.USDG, USDG_SOLANA_TRANSFER_AMOUNT, " (direct verification)")
            print(f"✅ All wallets correctly funded and verified")
        except Exception as e:
            print(f"❌ Balance retrieval failed: {e}")
            self.fail(f"Balance retrieval failed: {e}")

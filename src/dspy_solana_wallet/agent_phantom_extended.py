import dspy
import os
import sys
import requests
from pathlib import Path

# Add the project root to Python path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.dspy_solana_wallet.agent_tools import (
        create_wallet,
        create_associated_token_account_for_token,
        fund_user_wallet_with_sol_from_devnet,
        send_token_from_funding_wallet,
        get_last_user_wallet_created,
        get_last_user_wallet_balance
    )
except ImportError as e:
    print(f"Warning: Could not import original agent tools: {e}")
    # Create placeholder functions for demo
    def create_wallet():
        return {"public_key": "Demo mode - original function not available"}
    def create_associated_token_account_for_token(*args):
        return {"result": "Demo mode - original function not available"}
    def fund_user_wallet_with_sol_from_devnet(*args):
        return {"result": "Demo mode - original function not available"}
    def send_token_from_funding_wallet(*args):
        return {"result": "Demo mode - original function not available"}
    def get_last_user_wallet_created():
        return {"public_key": "Demo mode - original function not available"}
    def get_last_user_wallet_balance(*args):
        return {"balance": "Demo mode - original function not available"}

# Solana RPC endpoint (devnet)
SOLANA_RPC_URL = "https://api.devnet.solana.com"

# New Phantom-specific functions
def show_wallet_information(wallet_address):
    """
    Show comprehensive wallet information for the connected Phantom wallet
    
    Args:
        wallet_address (str): The Phantom wallet address
        
    Returns:
        dict: Wallet information including address, network, and basic stats
    """
    try:
        # Get SOL balance
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getBalance",
            "params": [wallet_address]
        }
        
        response = requests.post(SOLANA_RPC_URL, json=payload)
        data = response.json()
        
        sol_balance = 0
        if 'result' in data:
            sol_balance = data['result']['value'] / 1e9
        
        # Get account info
        account_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getAccountInfo",
            "params": [wallet_address]
        }
        
        account_response = requests.post(SOLANA_RPC_URL, json=account_payload)
        account_data = account_response.json()
        
        account_exists = account_data.get('result', {}).get('value') is not None
        
        # Get token accounts count
        token_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getTokenAccountsByOwner",
            "params": [
                wallet_address,
                {"programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"},
                {"encoding": "jsonParsed"}
            ]
        }
        
        token_response = requests.post(SOLANA_RPC_URL, json=token_payload)
        token_data = token_response.json()
        
        token_accounts = 0
        if 'result' in token_data and 'value' in token_data['result']:
            token_accounts = len(token_data['result']['value'])
        
        return {
            'wallet_address': wallet_address,
            'network': 'Solana Devnet',
            'sol_balance': sol_balance,
            'account_exists': account_exists,
            'token_accounts_count': token_accounts,
            'wallet_type': 'Phantom Wallet'
        }
        
    except Exception as e:
        return {'error': f'Failed to get wallet information: {str(e)}'}

def get_wallet_transaction_history(wallet_address, limit=10):
    """
    Get transaction history for the connected Phantom wallet
    
    Args:
        wallet_address (str): The Phantom wallet address
        limit (int): Number of recent transactions to fetch
        
    Returns:
        dict: Transaction history with details
    """
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getSignaturesForAddress",
            "params": [wallet_address, {"limit": limit}]
        }
        
        response = requests.post(SOLANA_RPC_URL, json=payload)
        data = response.json()
        
        transactions = []
        if 'result' in data and data['result']:
            for tx in data['result']:
                transactions.append({
                    'signature': tx['signature'],
                    'slot': tx['slot'],
                    'block_time': tx.get('blockTime'),
                    'status': 'Success' if tx['err'] is None else 'Failed',
                    'error': tx.get('err')
                })
        
        return {
            'wallet_address': wallet_address,
            'transaction_count': len(transactions),
            'transactions': transactions
        }
        
    except Exception as e:
        return {'error': f'Failed to get transaction history: {str(e)}'}

class PhantomExtendedWalletService(dspy.Signature):
    """
    You are the Solana Phantom Wallet Assistant with Extended Capabilities
    
    You support ALL the original 6 core functions plus 2 new wallet information functions:
    
    ORIGINAL 6 CORE FUNCTIONS:
    1. create_wallet() - Creates a new Solana wallet
    2. create_associated_token_account_for_token() - Creates token accounts
    3. fund_user_wallet_with_sol_from_devnet() - Funds wallet from devnet faucet
    4. send_token_from_funding_wallet() - Sends tokens from funding wallet
    5. get_last_user_wallet_created() - Gets last created wallet public key
    6. get_last_user_wallet_balance() - Gets wallet balance for specific token
    
    NEW PHANTOM-SPECIFIC FUNCTIONS:
    7. show_wallet_information() - Shows comprehensive wallet info
    8. get_wallet_transaction_history() - Gets transaction history
    
    OPERATION MODES:
    - For original 6 functions: Use traditional agent tools with user's wallet
    - For new functions: Use Phantom wallet address directly
    - For send operations: Guide user through Phantom transaction signing
    
    SECURITY MODEL:
    - Phantom wallet: Private keys stay in browser, transactions signed by user
    - Original functions: May require backend wallet operations for some features
    - Always prioritize user's Phantom wallet when possible
    
    IMPORTANT GUIDELINES:
    - Always explain which method is being used
    - For Phantom operations, emphasize security (keys never leave browser)
    - For original functions, explain any backend requirements
    - Provide educational information about each operation
    - Suggest safer alternatives when appropriate
    """
    
    user_request: str = dspy.InputField()
    wallet_address: str = dspy.InputField(desc="Connected Phantom wallet address")
    wallet_connected: bool = dspy.InputField(desc="Whether Phantom wallet is connected")
    
    process_result: str = dspy.OutputField(
        desc=(
            "Comprehensive response handling both original 6 functions and new Phantom features. "
            "Clearly explain which system is being used and why. "
            "For Phantom operations, emphasize security benefits. "
            "For original functions, explain capabilities and requirements."
        )
    )

def create_phantom_extended_agent():
    """Create the extended Phantom wallet agent with multiple AI model support"""
    try:
        # Try to get model preference from environment, default to OpenAI
        model_provider = os.getenv("AI_MODEL_PROVIDER", "openai").lower()
        
        if model_provider == "deepseek":
            # DeepSeek configuration
            deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
            if not deepseek_api_key:
                print("Warning: DEEPSEEK_API_KEY not found, falling back to OpenAI")
                model_provider = "openai"
            else:
                # Configure DeepSeek
                lm = dspy.LM(
                    model="deepseek/deepseek-chat",
                    api_key=deepseek_api_key,
                    api_base="https://api.deepseek.com"
                )
                print("✅ Using DeepSeek AI model (Free)")
        
        if model_provider == "openai":
            # OpenAI configuration (default)
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if not openai_api_key:
                raise Exception("No AI API key found. Please set OPENAI_API_KEY or DEEPSEEK_API_KEY")
            
            lm = dspy.LM("openai/gpt-4o-mini", api_key=openai_api_key)
            print("✅ Using OpenAI GPT-4o-mini model")
        
        dspy.configure(lm=lm)
        
        # Create agent with access to all functions
        return dspy.ReAct(
            PhantomExtendedWalletService,
            tools=[
                create_wallet,
                create_associated_token_account_for_token,
                fund_user_wallet_with_sol_from_devnet,
                send_token_from_funding_wallet,
                get_last_user_wallet_created,
                get_last_user_wallet_balance,
                show_wallet_information,
                get_wallet_transaction_history
            ]
        )
    except Exception as e:
        print(f"Warning: Could not create extended Phantom agent: {e}")
        return None

# Create the agent instance
phantom_extended_agent = create_phantom_extended_agent()

def process_phantom_extended_request(user_request, wallet_address, wallet_connected=True):
    """
    Process user request through the extended Phantom wallet agent
    
    Args:
        user_request (str): Natural language command from user
        wallet_address (str): Connected Phantom wallet address  
        wallet_connected (bool): Whether wallet is currently connected
    
    Returns:
        dict: Response with process_result or error
    """
    if not phantom_extended_agent:
        return {
            'error': 'Extended Phantom agent not available. Please check OpenAI API configuration.'
        }
    
    try:
        if not wallet_connected:
            return {
                'process_result': '''🔗 Wallet Connection Required

Please connect your Phantom wallet to use this service.

This agent supports:
• All 6 original core functions (create wallet, fund, send, balance, etc.)
• New Phantom-specific features (wallet info, transaction history)

Steps to connect:
1. Install Phantom wallet extension
2. Click "Connect Phantom" button  
3. Approve connection in your wallet

Your private keys never leave your browser!'''
            }
        
        if not wallet_address:
            return {
                'error': 'Wallet address is required for operations'
            }
        
        # Execute through DSPy agent with all tools available
        result = phantom_extended_agent(
            user_request=user_request,
            wallet_address=wallet_address,
            wallet_connected=wallet_connected
        )
        
        return {
            'process_result': result.process_result
        }
        
    except Exception as e:
        return {
            'error': f'Error processing request: {str(e)}'
        }

# Example usage and testing
if __name__ == "__main__":
    test_wallet = "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM"
    
    print("Testing Extended Phantom Wallet Agent...")
    print("=" * 60)
    
    # Test original function
    print("1. Testing original function - create wallet:")
    result = process_phantom_extended_request("Create a new wallet", test_wallet, True)
    print(result.get('process_result', result.get('error')))
    print()
    
    # Test new function - wallet info
    print("2. Testing new function - wallet information:")
    result = process_phantom_extended_request("Show my wallet information", test_wallet, True)
    print(result.get('process_result', result.get('error')))
    print()
    
    # Test new function - transaction history
    print("3. Testing new function - transaction history:")
    result = process_phantom_extended_request("Get my wallet's transaction history", test_wallet, True)
    print(result.get('process_result', result.get('error')))
    print()
    
    # Test original function - balance
    print("4. Testing original function - balance check:")
    result = process_phantom_extended_request("Check my wallet balance", test_wallet, True)
    print(result.get('process_result', result.get('error')))
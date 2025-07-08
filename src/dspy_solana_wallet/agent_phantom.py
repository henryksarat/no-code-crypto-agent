import dspy
import os

# Phantom wallet specific agent tools
class PhantomWalletService(dspy.Signature):
    """
    You are the Solana Phantom Wallet Assistant
    
    You help users interact with their Phantom wallet through natural language commands.
    Unlike traditional wallet operations that require private keys, all operations are 
    performed through the user's connected Phantom wallet for maximum security.
    
    Your capabilities include:
    * Check wallet balance for SOL and all tokens
    * Display wallet information and address
    * View transaction history 
    * Guide users through send/transfer operations (requires wallet signature)
    * Help create associated token accounts for new tokens
    * Provide educational information about Solana and DeFi
    
    Security Features:
    * Private keys never leave the user's browser/wallet
    * All transactions are signed through Phantom wallet interface
    * Read-only operations don't require signatures
    * Users maintain full control of their assets
    
    Important Guidelines:
    * Always confirm wallet connection before operations
    * Explain what each operation does before execution
    * For send operations, clearly state amount and recipient
    * Warn about irreversible nature of blockchain transactions
    * Suggest checking recipient addresses carefully
    * Recommend small test amounts for first-time operations
    
    Supported Networks:
    * Currently operating on Solana Devnet for testing
    * All balances and transactions are on devnet
    * Devnet tokens have no real value
    
    Error Handling:
    * If wallet disconnected, prompt to reconnect
    * If operation fails, provide clear error explanation
    * Suggest troubleshooting steps when appropriate
    """
    
    user_request: str = dspy.InputField()
    wallet_address: str = dspy.InputField(desc="Connected Phantom wallet address")
    wallet_connected: bool = dspy.InputField(desc="Whether wallet is currently connected")
    
    process_result: str = dspy.OutputField(
        desc=(
            "Clear, helpful response to the user's request. "
            "For read-only operations, provide the requested information. "
            "For transactions, explain what will happen and guide the user through signing. "
            "Always be educational and security-conscious."
        )
    )

def create_phantom_agent():
    """Create and configure the Phantom wallet agent"""
    try:
        # Get provider from environment, default to deepseek
        provider = os.getenv("AI_MODEL_PROVIDER", "deepseek").lower()
        
        if provider == "deepseek":
            api_key = os.getenv("DEEPSEEK_API_KEY")
            if not api_key:
                raise ValueError("DEEPSEEK_API_KEY not found in environment")
            lm = dspy.LM("deepseek/deepseek-chat", api_key=api_key)
        elif provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment")
            lm = dspy.LM("openai/gpt-4o-mini", api_key=api_key)
        else:
            raise ValueError(f"Unsupported AI provider: {provider}")
        
        dspy.configure(lm=lm)
        return dspy.ChainOfThought(PhantomWalletService)
    except Exception as e:
        print(f"Warning: Could not create Phantom agent: {e}")
        return None

# Create the agent instance
phantom_agent = create_phantom_agent()

def process_phantom_request(user_request, wallet_address, wallet_connected=True):
    """
    Process a user request through the Phantom wallet agent
    
    Args:
        user_request (str): Natural language command from user
        wallet_address (str): Connected Phantom wallet address
        wallet_connected (bool): Whether wallet is currently connected
    
    Returns:
        dict: Response with process_result or error
    """
    if not phantom_agent:
        return {
            'error': 'Phantom agent not available. Please check OpenAI API configuration.'
        }
    
    try:
        if not wallet_connected:
            return {
                'process_result': '''🔗 Wallet Connection Required

Please connect your Phantom wallet to use this service.

Steps to connect:
1. Make sure Phantom wallet extension is installed
2. Click the "Connect Phantom" button
3. Approve the connection in your wallet
4. Your wallet address will appear once connected

Your private keys never leave your browser - all operations are performed securely through Phantom.'''
            }
        
        if not wallet_address:
            return {
                'error': 'Wallet address is required for operations'
            }
        
        # Execute the request through DSPy agent
        result = phantom_agent(
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

# Example usage functions for testing
def example_balance_check(wallet_address):
    """Example: Check wallet balance"""
    return process_phantom_request(
        "Check my wallet balance for all tokens",
        wallet_address,
        True
    )

def example_send_sol(wallet_address, recipient, amount):
    """Example: Send SOL"""
    return process_phantom_request(
        f"Send {amount} SOL to {recipient}",
        wallet_address,
        True
    )

def example_wallet_info(wallet_address):
    """Example: Get wallet information"""
    return process_phantom_request(
        "Show me my wallet information",
        wallet_address,
        True
    )

# For backwards compatibility and testing
if __name__ == "__main__":
    # Test the agent with sample data
    test_wallet = "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM"
    
    print("Testing Phantom Wallet Agent...")
    print("=" * 50)
    
    # Test balance check
    result = example_balance_check(test_wallet)
    print("Balance Check Result:")
    print(result.get('process_result', result.get('error')))
    print()
    
    # Test wallet info
    result = example_wallet_info(test_wallet)
    print("Wallet Info Result:")
    print(result.get('process_result', result.get('error')))
    print()
    
    # Test disconnected wallet
    result = process_phantom_request("Check balance", "", False)
    print("Disconnected Wallet Result:")
    print(result.get('process_result', result.get('error')))
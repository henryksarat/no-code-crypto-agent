from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import sys
import logging
import json
import base64
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from solders.pubkey import Pubkey
    from solders.transaction import Transaction
    from solders.system_program import TransferParams, transfer
    from solders.rpc.responses import SendTransactionResp
    import requests
    from src.dspy_solana_wallet.agent_phantom_extended import process_phantom_extended_request
except ImportError as e:
    print(f"Warning: Could not import dependencies: {e}")
    process_phantom_extended_request = None

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Solana RPC endpoint (devnet)
SOLANA_RPC_URL = "https://api.devnet.solana.com"

@app.route('/')
def index():
    """Serve the Phantom wallet integrated HTML page"""
    return send_from_directory('.', 'index_phantom.html')

@app.route('/api/execute-phantom', methods=['POST'])
def execute_phantom_command():
    """Execute a natural language command with Phantom wallet integration"""
    try:
        data = request.get_json()
        
        if not data or 'user_request' not in data:
            return jsonify({'error': 'Missing user_request in request body'}), 400
        
        user_request = data['user_request'].strip()
        wallet_address = data.get('wallet_address')
        wallet_connected = data.get('wallet_connected', False)
        
        if not user_request:
            return jsonify({'error': 'Empty user_request'}), 400
        
        if not wallet_connected or not wallet_address:
            return jsonify({'error': 'Wallet not connected'}), 400
        
        logger.info(f"Executing Phantom command: {user_request} for wallet: {wallet_address}")
        
        # Use the extended agent if available, otherwise fall back to basic processing
        if process_phantom_extended_request:
            result = process_phantom_extended_request(user_request, wallet_address, wallet_connected)
            logger.info(f"AI Agent result: {result}")
            
            # If AI agent returns empty or unclear result, fallback to basic processing
            if not result or not result.get('process_result') or result.get('process_result', '').strip() == '':
                logger.info("AI Agent returned empty result, falling back to basic processing")
                result = process_phantom_command(user_request, wallet_address)
                logger.info(f"Basic processing fallback result: {result}")
        else:
            # Fallback to basic processing
            result = process_phantom_command(user_request, wallet_address)
            logger.info(f"Basic processing result: {result}")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error executing Phantom command: {str(e)}")
        return jsonify({
            'error': f'Failed to execute command: {str(e)}'
        }), 500

def process_phantom_command(user_request, wallet_address):
    """Process natural language commands for Phantom wallet operations"""
    command_lower = user_request.lower()
    
    try:
        # Balance check commands
        if any(word in command_lower for word in ['balance', 'check', 'show', 'how much']):
            return get_wallet_balance(wallet_address)
        
        # Wallet info commands
        elif any(word in command_lower for word in ['wallet info', 'address', 'public key']):
            return get_wallet_info(wallet_address)
        
        # Send/transfer commands
        elif any(word in command_lower for word in ['send', 'transfer']):
            return handle_send_command(user_request, wallet_address)
        
        # Token account creation
        elif 'token account' in command_lower:
            return handle_token_account_creation(user_request, wallet_address)
        
        # Transaction history
        elif any(word in command_lower for word in ['history', 'transactions']):
            return get_transaction_history(wallet_address)
        
        else:
            return {
                'process_result': f"""I understand you want to: "{user_request}"

However, I can only help with these operations through Phantom wallet:
• Check wallet balance
• View wallet information  
• Send SOL or tokens (requires transaction signing)
• Create token accounts
• View transaction history

Please try rephrasing your request or use one of the example commands."""
            }
            
    except Exception as e:
        return {'error': f'Error processing command: {str(e)}'}

def get_wallet_balance(wallet_address):
    """Get the balance of the connected wallet"""
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
        
        if 'result' in data:
            sol_balance = data['result']['value'] / 1e9  # Convert lamports to SOL
        else:
            sol_balance = 0
        
        # Get token accounts
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
        
        token_balances = []
        if 'result' in token_data and 'value' in token_data['result']:
            for account in token_data['result']['value']:
                token_info = account['account']['data']['parsed']['info']
                if float(token_info['tokenAmount']['uiAmount'] or 0) > 0:
                    token_balances.append({
                        'mint': token_info['mint'],
                        'amount': token_info['tokenAmount']['uiAmount'],
                        'decimals': token_info['tokenAmount']['decimals']
                    })
        
        # Format result
        result = f"Wallet Balance for {wallet_address[:8]}...{wallet_address[-8:]}:\n\n"
        result += f"SOL: {sol_balance:.6f}\n\n"
        
        if token_balances:
            result += "Token Balances:\n"
            for token in token_balances:
                result += f"• {token['mint'][:8]}...{token['mint'][-8:]}: {token['amount']}\n"
        else:
            result += "No token balances found.\n"
        
        return {'process_result': result}
        
    except Exception as e:
        return {'error': f'Failed to get wallet balance: {str(e)}'}

def get_wallet_info(wallet_address):
    """Get basic wallet information"""
    return {
        'process_result': f"""Wallet Information:

Address: {wallet_address}
Network: Solana Devnet
Wallet Type: Phantom Wallet

This wallet is connected and ready for transactions.
You can now use commands like:
• Check my balance
• Send SOL to another address
• View transaction history"""
    }

def handle_send_command(user_request, wallet_address):
    """Handle send/transfer commands - these require transaction signing"""
    return {
        'needs_signature': True,
        'process_result': 'This operation requires transaction signing through your Phantom wallet.',
        'error': 'Send operations require backend integration with transaction building. This is a demo response.'
    }

def handle_token_account_creation(user_request, wallet_address):
    """Handle token account creation commands"""
    return {
        'process_result': f"""Token account creation for wallet {wallet_address[:8]}...{wallet_address[-8:]}

This operation would create an associated token account for the specified token.
In a full implementation, this would:
1. Build a transaction to create the associated token account
2. Request your signature through Phantom
3. Submit the signed transaction to the network

Note: This is a demonstration response. Full implementation requires transaction building logic."""
    }

def get_transaction_history(wallet_address):
    """Get transaction history for the wallet"""
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getSignaturesForAddress",
            "params": [wallet_address, {"limit": 10}]
        }
        
        response = requests.post(SOLANA_RPC_URL, json=payload)
        data = response.json()
        
        if 'result' in data and data['result']:
            result = f"Recent Transactions for {wallet_address[:8]}...{wallet_address[-8:]}:\n\n"
            
            for i, tx in enumerate(data['result'][:5], 1):
                signature = tx['signature']
                slot = tx['slot']
                status = "✅ Success" if tx['err'] is None else "❌ Failed"
                
                result += f"{i}. {signature[:8]}...{signature[-8:]}\n"
                result += f"   Slot: {slot}\n"
                result += f"   Status: {status}\n\n"
            
            result += f"View full details on Solana Explorer (Devnet)"
            
        else:
            result = f"No recent transactions found for {wallet_address[:8]}...{wallet_address[-8:]}"
        
        return {'process_result': result}
        
    except Exception as e:
        return {'error': f'Failed to get transaction history: {str(e)}'}

@app.route('/api/submit-transaction', methods=['POST'])
def submit_transaction():
    """Submit a signed transaction to the network"""
    try:
        data = request.get_json()
        signed_transaction = data.get('signed_transaction')
        original_request = data.get('original_request')
        
        # In a real implementation, you would submit the signed transaction here
        # For now, return a demo response
        
        return jsonify({
            'process_result': f"""Transaction signed and submitted successfully!

Original request: {original_request}

⚠️ Note: This is a demonstration response. 
In a full implementation, the signed transaction would be submitted to the Solana network.

Transaction would appear in your wallet and on Solana Explorer within seconds."""
        })
        
    except Exception as e:
        logger.error(f"Error submitting transaction: {str(e)}")
        return jsonify({
            'error': f'Failed to submit transaction: {str(e)}'
        }), 500

@app.route('/api/health-phantom', methods=['GET'])
def health_check_phantom():
    """Health check endpoint for Phantom integration"""
    return jsonify({
        'status': 'healthy',
        'phantom_integration': True,
        'requires_wallet_connection': True,
        'supported_operations': [
            'balance_check',
            'wallet_info',
            'transaction_history',
            'send_transactions',
            'token_account_creation'
        ]
    })

if __name__ == '__main__':
    print("🚀 Starting Solana No-code Agent with Phantom Integration")
    print("👻 Connect your Phantom wallet to get started")
    print("🔗 Phantom wallet extension required")
    
    # Run the Flask app
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"🌐 Web interface available at: http://localhost:{port}")
    print("📱 Make sure you have Phantom wallet installed in your browser")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
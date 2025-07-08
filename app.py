from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import sys
import logging
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from dspy_solana_wallet.agent_basic import agent_basic
except ImportError as e:
    print(f"Warning: Could not import agent_basic: {e}")
    agent_basic = None

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    """Serve the main HTML page"""
    return send_from_directory('.', 'index.html')

@app.route('/api/execute', methods=['POST'])
def execute_command():
    """Execute a natural language command using the DSPy agent"""
    try:
        data = request.get_json()
        
        if not data or 'user_request' not in data:
            return jsonify({'error': 'Missing user_request in request body'}), 400
        
        user_request = data['user_request'].strip()
        
        if not user_request:
            return jsonify({'error': 'Empty user_request'}), 400
        
        logger.info(f"Executing command: {user_request}")
        
        # Check if agent is available
        if agent_basic is None:
            return jsonify({
                'error': 'DSPy agent not available. Please check your environment setup and .env file.'
            }), 500
        
        # Execute the command using the DSPy agent
        result = agent_basic(user_request=user_request)
        
        logger.info(f"Command executed successfully")
        
        return jsonify({
            'success': True,
            'process_result': result.process_result,
            'user_request': user_request
        })
        
    except Exception as e:
        logger.error(f"Error executing command: {str(e)}")
        return jsonify({
            'error': f'Failed to execute command: {str(e)}'
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'agent_available': agent_basic is not None,
        'python_version': sys.version,
        'working_directory': os.getcwd()
    })

@app.route('/api/functions', methods=['GET'])
def get_available_functions():
    """Get list of available functions"""
    functions = [
        {
            'name': 'create_wallet',
            'description': 'Create a new Solana wallet and return the public key'
        },
        {
            'name': 'create_associated_token_account_for_token',
            'description': 'Create an associated token account for a specific token'
        },
        {
            'name': 'fund_user_wallet_with_sol_from_devnet',
            'description': 'Fund a wallet with SOL from the devnet faucet'
        },
        {
            'name': 'send_token_from_funding_wallet',
            'description': 'Send tokens (SOL, USDC, PYUSD, USDG) from funding wallet'
        },
        {
            'name': 'get_last_user_wallet_created',
            'description': 'Get the public key of the last created wallet'
        },
        {
            'name': 'get_last_user_wallet_balance',
            'description': 'Get the balance of the last created wallet'
        }
    ]
    
    return jsonify({
        'functions': functions,
        'supported_tokens': ['SOL', 'USDC', 'PYUSD', 'USDG']
    })

if __name__ == '__main__':
    # Check if .env file exists
    env_file = Path('.env')
    if not env_file.exists():
        print("Warning: .env file not found. Please create it with your API keys.")
        print("Required variables: OPENAI_API_KEY, FUNDING_WALLET_PRIVATE_KEY, FUNDING_WALLET_PUBLIC_KEY")
    
    # Run the Flask app
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"Starting Solana Wallet Agent Web Interface on port {port}")
    print(f"Visit: http://localhost:{port}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
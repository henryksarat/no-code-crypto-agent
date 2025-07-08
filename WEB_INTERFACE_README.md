# Solana Wallet Agent Web Interface

A user-friendly web interface for the Solana Wallet Agent that allows users to interact with Solana wallets using natural language commands.

## Features

- **Natural Language Interface**: Type commands in plain English to manage Solana wallets
- **Real-time Execution**: Direct integration with the DSPy agent for live blockchain operations
- **Responsive Design**: Works on desktop and mobile devices
- **Demo Mode**: Fallback simulation when backend is not available
- **Multiple Token Support**: Handle SOL, USDC, PYUSD, and USDG tokens

## Quick Start

### 1. Install Dependencies

```bash
# Install Flask dependencies
pip install flask flask-cors

# Or install all dependencies
pip install -r requirements.txt
```

### 2. Set Up Environment

Create a `.env` file with your credentials:

```env
OPENAI_API_KEY=your_openai_api_key_here
FUNDING_WALLET_PRIVATE_KEY=your_funding_wallet_private_key
FUNDING_WALLET_PUBLIC_KEY=your_funding_wallet_public_key
```

### 3. Start the Web Interface

```bash
# Option 1: Use the startup script
python start_web_interface.py

# Option 2: Run Flask directly
python app.py
```

### 4. Open in Browser

Visit `http://localhost:5000` in your web browser.

## Usage Examples

### Wallet Management
- "Create a new wallet and fund it with 0.5 SOL"
- "Get the public key of my last wallet"
- "Check balance of my last wallet"

### Token Operations
- "Send 10 USDC to my last created wallet"
- "Create associated token account for PYUSD"
- "Fund my wallet with 3 USDG from the funding wallet"

### Balance Queries
- "Show me the balance of my last wallet"
- "How much SOL do I have in my last wallet?"

## API Endpoints

The web interface exposes the following REST API endpoints:

- `POST /api/execute` - Execute natural language commands
- `GET /api/health` - Check backend health status
- `GET /api/functions` - List available functions

## Demo Mode

If the backend is not available, the interface automatically falls back to demo mode, which provides simulated responses for testing the UI.

## Available Functions

The agent supports these core functions:

1. **create_wallet** - Create a new Solana wallet
2. **create_associated_token_account_for_token** - Create token accounts
3. **fund_user_wallet_with_sol_from_devnet** - Fund with SOL from faucet
4. **send_token_from_funding_wallet** - Transfer tokens
5. **get_last_user_wallet_created** - Get last wallet info
6. **get_last_user_wallet_balance** - Check wallet balance

## Supported Tokens

- **SOL** - Solana native token
- **USDC** - USD Coin
- **PYUSD** - PayPal USD
- **USDG** - Paxos Gold backed USD

## Security Notes

- Private keys are never displayed in the web interface
- All operations are performed on Solana Devnet
- Keep your `.env` file secure and never commit it to version control

## Troubleshooting

### Backend Not Available
- Check that your `.env` file exists and contains valid API keys
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Verify your virtual environment is activated

### API Errors
- Check the console output for detailed error messages
- Verify your OpenAI API key is valid
- Ensure your funding wallet has sufficient balance

### Connection Issues
- Make sure the Flask server is running on port 5000
- Check for firewall blocking the connection
- Try accessing `http://localhost:5000/api/health` directly

## Development

To modify the web interface:

1. **Frontend**: Edit `index.html` for UI changes
2. **Backend**: Edit `app.py` for API modifications
3. **Styling**: CSS is embedded in the HTML file

## License

This web interface is part of the Solana Wallet Agent project and follows the same license terms.
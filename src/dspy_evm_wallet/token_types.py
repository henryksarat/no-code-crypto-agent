from enum import Enum

class TokenType(Enum):
    ETH = 'ETH' 
    USDC = '0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238'  
    PYUSD = '0xCaC524BcA292aaade2DF8A05cC58F0a65B1B3bB9' 
    USDG = '0xfBb2A78CceEb415b00300925e464C3E44E6e06b0'  

    @property
    def contract_address(self) -> str:
        """Returns the contract address for this token type."""
        if self == TokenType.ETH:
            return None  # ETH is native, no contract
        return self.value

    @property
    def decimals(self) -> int:
        """Returns the number of decimals for this token type."""
        if self == TokenType.ETH:
            return 18  # ETH has 18 decimals
        return 6  # USDC, PYUSD, USDG have 6 decimals

    def to_token_amount(self, amount: float) -> int:
        """
        Convert a token amount to its proper decimal representation.
        
        Args:
            amount: The amount of tokens (e.g., 1.5 USDC)
            
        Returns:
            int: The amount in the smallest unit (e.g., 1.5 USDC = 1,500,000)
        """
        return int(amount * (10 ** self.decimals))

    def from_token_amount(self, amount: int) -> float:
        """
        Convert a token amount from its decimal representation to human-readable format.
        
        Args:
            amount: The amount in the smallest unit (e.g., 1,500,000)
            
        Returns:
            float: The human-readable amount (e.g., 1.5 USDC)
        """
        return amount / (10 ** self.decimals)

    @staticmethod
    def from_string(token_type: str) -> 'TokenType':
        """
        Convert string token type to TokenType enum.
        
        Args:
            token_type (str): The token type string ('ETH', 'USDC', 'PYUSD', 'USDG')
            
        Returns:
            TokenType: The corresponding TokenType enum
            
        Raises:
            ValueError: If the token type is not supported
        """
        try:
            return TokenType[token_type.upper()]
        except KeyError:
            raise ValueError(f"Unsupported token type: {token_type}. Supported types are 'ETH', 'USDC', 'PYUSD', and 'USDG'") 
from enum import Enum

class TokenType(Enum):
    SOL = "So11111111111111111111111111111111111111112"  # Native SOL
    USDG = "4F6PM96JJxngmHnZLBh9n58RH4aTVNWvDs2nuwrT5BP7"
    USDC = "4zMMC9srt5Ri5X14GAgXhaHii3GnPAEERYPJgZJDncDU"
    PYUSD = "CXk2AMBfi3TwaEL2468s6zP8xq9NxTXjp9gjMgzeUynM"

    TOKEN_2022_PROGRAM_ID = "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb"  # Token-2022 Program
    SPL_TOKEN_PROGRAM_ID = "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"  # Regular SPL Token Program

    @property
    def program_id(self) -> str:
        """Returns the appropriate token program ID for this token type."""
        if self == TokenType.SOL:
            return "11111111111111111111111111111111"  # System Program
        if self == TokenType.USDG or self == TokenType.PYUSD:
            return TokenType.TOKEN_2022_PROGRAM_ID.value
        return TokenType.SPL_TOKEN_PROGRAM_ID.value

    @property
    def decimals(self) -> int:
        """Returns the number of decimals for this token type."""
        if self == TokenType.SOL:
            return 9  # SOL has 9 decimals
        return 6  # Both USDG, PYUSD, and USDC have 6 decimals

    def to_token_amount(self, amount: float) -> int:
        """
        Convert a token amount to its proper decimal representation.
        
        Args:
            amount: The amount of tokens (e.g., 1.5 USDG)
            
        Returns:
            int: The amount in the smallest unit (e.g., 1.5 USDG = 1,500,000)
        """
        return int(amount * (10 ** self.decimals))

    def from_token_amount(self, amount: int) -> float:
        """
        Convert a token amount from its decimal representation to human-readable format.
        
        Args:
            amount: The amount in the smallest unit (e.g., 1,500,000)
            
        Returns:
            float: The human-readable amount (e.g., 1.5 USDG)
        """
        return amount / (10 ** self.decimals)

    @staticmethod
    def from_string(token_type: str) -> 'TokenType':
        """
        Convert string token type to TokenType enum.
        
        Args:
            token_type (str): The token type string ('SOL', 'USDC', or 'USDG')
            
        Returns:
            TokenType: The corresponding TokenType enum
            
        Raises:
            ValueError: If the token type is not supported
        """
        try:
            return TokenType[token_type.upper()]
        except KeyError:
            raise ValueError(f"Unsupported token type: {token_type}. Supported types are 'SOL', 'USDC', 'PYUSD' and 'USDG'")

# SPL Token Program IDs
ASSOCIATED_TOKEN_PROGRAM_ID = "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL" 
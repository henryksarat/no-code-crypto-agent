import unittest
import os
import sys
from unittest.mock import patch, MagicMock

from dspy_solana_wallet.primitive_solana_functions import create_new_wallet

class TestCreateNewWallet(unittest.TestCase):
    
    def test_create_new_wallet(self):
        """Test creating a new wallet."""
        # Create mock objects
        mock_keypair = MagicMock()
        mock_pubkey = MagicMock()
        
        # Set up mock return values
        mock_keypair.pubkey.return_value = mock_pubkey
        mock_keypair.to_bytes.return_value = b'test_private_key_bytes'
        mock_pubkey.__str__ = MagicMock(return_value="test_public_key_string")
        
        with patch('dspy_solana_wallet.primitive_solana_functions.Keypair') as mock_keypair_class:
            mock_keypair_class.return_value = mock_keypair
            
            with patch('dspy_solana_wallet.primitive_solana_functions.base58.b58encode') as mock_b58encode:
                mock_b58encode.return_value.decode.return_value = "test_private_key_b58"
                
                # Call the function
                result = create_new_wallet()
                
                # Verify Keypair was created
                mock_keypair_class.assert_called_once()
                
                # Verify the result is the mock keypair
                self.assertEqual(result, mock_keypair)
                
                # Verify pubkey() was called (for printing)
                mock_keypair.pubkey.assert_called_once()
                
                # Verify to_bytes() was called (for private key encoding)
                mock_keypair.to_bytes.assert_called_once()
                
                # Verify base58 encoding was called with the correct bytes
                mock_b58encode.assert_called_once_with(b'test_private_key_bytes')

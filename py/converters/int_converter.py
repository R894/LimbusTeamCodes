"""Integer list to Base64 converter.

Replicates the assembly-level IntListBase64Converter for encoding/decoding
lists of 32-bit integers to/from Base64 strings.
"""

import base64
import struct
from typing import List


class IntListBase64Converter:
    """
    Replication of the assembly-level IntListBase64Converter::Encode.
    Converts a list of 32-bit integers into a Base64 string.
    """

    @staticmethod
    def encode(int_list: List[int]) -> str:
        """
        Encodes a list of integers to Base64.

        Assembly Logic:
        1. Allocates a byte buffer (rax_1) equal to list size * 4.
        2. Iterates through the input list (arg1).
        3. For each integer (rsi_1), it uses BlockCopy to move 4 bytes.
        4. Returns System.Convert::ToBase64String.
        """
        if int_list is None:
            # Assembly 18095dce5 throws ArgumentNullException
            raise ValueError("Input list cannot be None")

        if not int_list:
            return ""

        # Create a byte buffer. '<i' means little-endian 32-bit integer.
        # This replicates the memory layout created by BlockCopy in the assembly.
        byte_buffer = bytearray()
        for val in int_list:
            # Ensure the value fits in a 32-bit signed integer
            # Replicates: rax_3[4].d = rsi_1
            byte_buffer.extend(struct.pack('<i', val))

        # Replicates: System.Convert::ToBase64String(&var_18, 0)
        return base64.b64encode(byte_buffer).decode('ascii')

    @staticmethod
    def decode(b64_string: str) -> List[int]:
        """
        Reverse operation: Converts Base64 string back to a list of int32.
        """
        if not b64_string:
            return []

        try:
            decoded_bytes = base64.b64decode(b64_string)
            # Ensure we have full 4-byte chunks
            count = len(decoded_bytes) // 4
            # Unpack 'count' number of little-endian 32-bit integers
            return list(struct.unpack(f'<{count}i', decoded_bytes[:count * 4]))
        except Exception as e:
            print(f"Decoding error: {e}")
            return []

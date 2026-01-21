"""Boolean list to Base64 converter.

Converts between bool arrays and Base64 strings.
"""

import base64
from typing import List


class BoolListBase64Converter:
    """Converts between bool arrays and base64 strings."""

    @staticmethod
    def from_base64(b64_string: str, expected_count: int = 0) -> List[bool]:
        if not b64_string:
            return []
        try:
            data = base64.b64decode(b64_string)
        except Exception as e:
            print(f"Base64 decode error: {e}")
            return []

        bools = []
        for bit_index in range(expected_count if expected_count > 0 else len(data) * 8):
            byte_index = bit_index >> 3
            if byte_index >= len(data):
                break
            bit_in_byte = bit_index & 7
            byte_value = data[byte_index]
            bit_position = 7 - bit_in_byte
            bit_value = (byte_value & (1 << bit_position)) != 0
            bools.append(bit_value)
        return bools

    @staticmethod
    def to_base64(bools: List[bool]) -> str:
        if not bools:
            return ""
        bytes_list = []
        for i in range(0, len(bools), 8):
            byte_val = 0
            for j in range(8):
                if i + j < len(bools) and bools[i + j]:
                    bit_position = 7 - j
                    byte_val |= (1 << bit_position)
            bytes_list.append(byte_val)
        return base64.b64encode(bytes(bytes_list)).decode('ascii')

"""Text compression and decompression utility.

Provides compression/decompression using gzip and Base64 encoding.
"""

import base64
import gzip
import io


class TextCompressionUtility:
    """Compression/decompression utility for the outer layer."""

    @staticmethod
    def decompress(compressed_string: str) -> str:
        if not compressed_string:
            return ""
        try:
            compressed_bytes = base64.b64decode(compressed_string)
            memory_stream = io.BytesIO(compressed_bytes)
            with gzip.GzipFile(fileobj=memory_stream, mode='rb') as gzip_stream:
                decompressed_bytes = gzip_stream.read()
            return decompressed_bytes.decode('utf-8')
        except Exception as e:
            print(f"Decompression error: {e}")
            return ""

    @staticmethod
    def compress(text: str) -> str:
        if not text:
            return ""
        try:
            text_bytes = text.encode('utf-8')
            compressed_stream = io.BytesIO()
            with gzip.GzipFile(fileobj=compressed_stream, mode='wb') as gzip_stream:
                gzip_stream.write(text_bytes)
            compressed_bytes = compressed_stream.getvalue()
            return base64.b64encode(compressed_bytes).decode('ascii')
        except Exception as e:
            print(f"Compression error: {e}")
            return ""

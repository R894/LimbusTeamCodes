/**
 * Text compression and decompression utility.
 *
 * Provides compression/decompression using gzip and Base64 encoding.
 */

import * as pako from "pako";

/**
 * Compression/decompression utility for the outer layer.
 */
export class TextCompressionUtility {
  /**
   * Decompresses a gzip+base64 encoded string.
   */
  static decompress(compressedString: string): string {
    if (!compressedString) {
      return "";
    }

    try {
      // Decode base64
      const compressedBytes = Buffer.from(compressedString, "base64");

      // Decompress gzip
      const decompressedBytes = pako.ungzip(compressedBytes);

      // Convert to UTF-8 string
      return new TextDecoder("utf-8").decode(decompressedBytes);
    } catch (e) {
      console.error("Decompression error:", e);
      return "";
    }
  }

  /**
   * Compresses a string using gzip and base64 encoding.
   */
  static compress(text: string): string {
    if (!text) {
      return "";
    }

    try {
      // Convert to bytes
      const textBytes = new TextEncoder().encode(text);

      // Compress with gzip
      const compressedBytes = pako.gzip(textBytes);

      // Encode to base64
      return Buffer.from(compressedBytes).toString("base64");
    } catch (e) {
      console.error("Compression error:", e);
      return "";
    }
  }
}

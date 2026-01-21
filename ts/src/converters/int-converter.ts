/**
 * Integer list to Base64 converter.
 *
 * Replicates the assembly-level IntListBase64Converter for encoding/decoding
 * lists of 32-bit integers to/from Base64 strings.
 */

/**
 * Replication of the assembly-level IntListBase64Converter::Encode.
 * Converts a list of 32-bit integers into a Base64 string.
 */
export class IntListBase64Converter {
  /**
   * Encodes a list of integers to Base64.
   *
   * Assembly Logic:
   * 1. Allocates a byte buffer equal to list size * 4.
   * 2. Iterates through the input list.
   * 3. For each integer, it uses BlockCopy to move 4 bytes.
   * 4. Returns System.Convert::ToBase64String.
   */
  static encode(intList: number[]): string {
    if (intList === null || intList === undefined) {
      throw new Error("Input list cannot be null or undefined");
    }

    if (intList.length === 0) {
      return "";
    }

    // Create a byte buffer. Little-endian 32-bit integers.
    const buffer = Buffer.allocUnsafe(intList.length * 4);

    for (let i = 0; i < intList.length; i++) {
      // Write as little-endian 32-bit signed integer
      buffer.writeInt32LE(intList[i], i * 4);
    }

    // Convert to base64
    return buffer.toString("base64");
  }

  /**
   * Reverse operation: Converts Base64 string back to a list of int32.
   */
  static decode(b64String: string): number[] {
    if (!b64String) {
      return [];
    }

    try {
      const decodedBytes = Buffer.from(b64String, "base64");

      // Ensure we have full 4-byte chunks
      const count = Math.floor(decodedBytes.length / 4);
      const result: number[] = [];

      for (let i = 0; i < count; i++) {
        result.push(decodedBytes.readInt32LE(i * 4));
      }

      return result;
    } catch (e) {
      console.error("Decoding error:", e);
      return [];
    }
  }
}

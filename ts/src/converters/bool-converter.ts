/**
 * Boolean list to Base64 converter.
 *
 * Converts between bool arrays and Base64 strings.
 */

/**
 * Converts between bool arrays and base64 strings.
 */
export class BoolListBase64Converter {
  /**
   * Converts a base64 string to a boolean array.
   */
  static fromBase64(b64String: string, expectedCount: number = 0): boolean[] {
    if (!b64String) {
      return [];
    }

    try {
      const data = Buffer.from(b64String, "base64");
      const bools: boolean[] = [];
      const maxBits = expectedCount > 0 ? expectedCount : data.length * 8;

      for (let bitIndex = 0; bitIndex < maxBits; bitIndex++) {
        const byteIndex = bitIndex >> 3;

        if (byteIndex >= data.length) {
          break;
        }

        const bitInByte = bitIndex & 7;
        const byteValue = data[byteIndex];
        const bitPosition = 7 - bitInByte;
        const bitValue = (byteValue & (1 << bitPosition)) !== 0;

        bools.push(bitValue);
      }

      return bools;
    } catch (e) {
      console.error("Base64 decode error:", e);
      return [];
    }
  }

  /**
   * Converts a boolean array to a base64 string.
   */
  static toBase64(bools: boolean[]): string {
    if (!bools || bools.length === 0) {
      return "";
    }

    const bytesList: number[] = [];

    for (let i = 0; i < bools.length; i += 8) {
      let byteVal = 0;

      for (let j = 0; j < 8; j++) {
        if (i + j < bools.length && bools[i + j]) {
          const bitPosition = 7 - j;
          byteVal |= 1 << bitPosition;
        }
      }

      bytesList.push(byteVal);
    }

    return Buffer.from(bytesList).toString("base64");
  }
}

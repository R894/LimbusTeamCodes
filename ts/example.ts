/**
 * Example usage of the Limbus Formation Deck Code library
 */

import { FormationDeckCode, FormationDetailInfo } from "./src";

// Example: Decode a formation deck code
function exampleDecode() {
  // This would be a real encoded deck code from the game
  const encoded = "H4sIAAAAAAAACnMMdEx3BAInR2cQ5ejq6AmmqSLsaGsLANDKykhgAAAA";

  const result = FormationDeckCode.decode(encoded, true);

  console.log("Decoded formations:", result.formations);
  console.log("Had errors:", result.hadErrors);

  return result;
}

// Example: Encode formations
function exampleEncode() {
  const formations: FormationDetailInfo[] = [
    {
      slot: 1,
      personalityId: 10101,
      ego1: 20101,
      ego2: 20102,
      ego3: 0,
      ego4: 0,
      ego5: 0,
      enabled: true,
      slotType: 1,
    },
    {
      slot: 2,
      personalityId: 10201,
      ego1: 20201,
      ego2: 0,
      ego3: 0,
      ego4: 0,
      ego5: 0,
      enabled: true,
      slotType: 1,
    },
  ];

  const encoded = FormationDeckCode.encode(formations);
  console.log("Encoded:", encoded);

  return encoded;
}

// Example: Round-trip encoding/decoding
function exampleRoundTrip() {
  console.log("\n=== Round-trip test ===");

  const originalFormations: FormationDetailInfo[] = [
    {
      slot: 1,
      personalityId: 10101,
      ego1: 20101,
      ego2: 20102,
      ego3: 20103,
      ego4: 0,
      ego5: 0,
      enabled: true,
      slotType: 1,
    },
  ];

  console.log("Original:", originalFormations);

  // Encode
  const encoded = FormationDeckCode.encode(originalFormations);
  console.log("Encoded:", encoded);

  // Decode
  const decoded = FormationDeckCode.decode(encoded);
  console.log("Decoded:", decoded.formations);

  // Verify they match
  const match =
    JSON.stringify(originalFormations) === JSON.stringify(decoded.formations);
  console.log("Match:", match);
}

// Run examples
if (require.main === module) {
  console.log("=== Limbus Formation Deck Code Examples ===\n");

  console.log("--- Example 1: Decode ---");
  exampleDecode();

  console.log("\n--- Example 2: Encode ---");
  exampleEncode();

  console.log("\n--- Example 3: Round-trip ---");
  exampleRoundTrip();
}

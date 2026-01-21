import { FormationDeckCode, FormationDetailInfo } from "./index";

describe("FormationDeckCode", () => {
  it("should perform a round-trip encoding and decoding correctly", () => {
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

    // Encode
    const encoded = FormationDeckCode.encode(originalFormations);
    expect(encoded).toBeDefined();
    expect(typeof encoded).toBe("string");

    // Decode
    const decoded = FormationDeckCode.decode(encoded);

    // Verify they match
    expect(decoded.formations).toEqual(originalFormations);
    expect(decoded.hadErrors).toBe(false);
  });

  it("should handle an empty list of formations", () => {
    const encoded = FormationDeckCode.encode([]);
    const decoded = FormationDeckCode.decode(encoded);
    expect(decoded.formations).toEqual([]);
  });
});

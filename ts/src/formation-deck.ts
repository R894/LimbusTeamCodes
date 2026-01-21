/**
 * Formation deck code encoder and decoder.
 *
 * Provides functionality to encode and decode Limbus Company formation deck codes.
 */

import {
  IntListBase64Converter,
  TextCompressionUtility,
  BoolListBase64Converter,
} from "./converters";
import { FormationDetailInfo } from "./models";

/**
 * Result of decoding a formation deck code.
 */
export interface DecodeResult {
  /** List of formations */
  formations: FormationDetailInfo[];
  /** Whether any errors were encountered during decoding */
  hadErrors: boolean;
}

/**
 * Decoder for formation deck codes.
 */
export class FormationDeckCode {
  /**
   * Decode formation deck code to list of formations.
   *
   * Assembly reference (1812247b0):
   * The key insight from the assembly is that bits are read and assembled using:
   * `value = (value * 2) | bit` - this builds the number LSB-first
   *
   * @param encoded - Base64+gzip encoded deck code
   * @param validate - Whether to perform basic validation
   * @returns DecodeResult containing formations list and error flag
   */
  static decode(encoded: string, validate: boolean = false): DecodeResult {
    if (!encoded) {
      return { formations: [], hadErrors: false };
    }

    // Line 1812248be: Decompress and convert to bools
    const innerB64 = TextCompressionUtility.decompress(encoded);
    if (!innerB64) {
      return { formations: [], hadErrors: false };
    }

    const bools = BoolListBase64Converter.fromBase64(innerB64, 0x229);
    if (!bools || bools.length === 0) {
      return { formations: [], hadErrors: false };
    }

    const formations: FormationDetailInfo[] = [];
    let hadErrors = false;

    // Start from bit index 1, not 0 (line 181224930: rdi_1 = 1)
    let bitIndex = 1;

    // Line 181224935: Loop through slots 1-12
    for (let slotNum = 1; slotNum <= 12; slotNum++) {
      // Lines 18122496c-181224999: Read 7 bits for personality
      // Assembly: r10_1 = (r10_1 * 2) | bit
      // This means: bit 0 goes to LSB, bit 6 goes to MSB
      let personalityMod = 0;
      for (let i = 0; i < 7; i++) {
        if (bitIndex < bools.length) {
          const bit = bools[bitIndex] ? 1 : 0;
          personalityMod = (personalityMod * 2) | bit;
          bitIndex++;
        }
      }

      // Lines 1812249a4-1812249c5: Read 4 bits for slot_type
      // Assembly: rdx_3 = (rdx_3 * 2) | bit
      let slotType = 0;
      for (let i = 0; i < 4; i++) {
        if (bitIndex < bools.length) {
          const bit = bools[bitIndex] ? 1 : 0;
          slotType = (slotType * 2) | bit;
          bitIndex++;
        }
      }

      // Lines 1812249cd-181224aa4: Read 7 bits each for 5 EGO slots
      // All use the same pattern: value = (value * 2) | bit
      const egoMods: number[] = [];
      for (let egoIdx = 0; egoIdx < 5; egoIdx++) {
        let egoMod = 0;
        for (let i = 0; i < 7; i++) {
          if (bitIndex < bools.length) {
            const bit = bools[bitIndex] ? 1 : 0;
            egoMod = (egoMod * 2) | bit;
            bitIndex++;
          }
        }
        egoMods.push(egoMod);
      }

      // Line 181224ab0: slot_offset = slot_num * 100
      const slotOffset = slotNum * 100;

      // Lines 181224abb-181224ac7: Reconstruct personality ID
      let personalityId: number;
      if (personalityMod > 0) {
        personalityId = personalityMod + 10000 + slotOffset;
      } else {
        personalityId = 0;
      }

      // Lines 181224acc-181224b1e: Reconstruct EGO IDs
      const egos: number[] = [];
      for (const egoMod of egoMods) {
        if (egoMod > 0) {
          egos.push(egoMod + 20000 + slotOffset);
        } else {
          egos.push(0);
        }
      }

      // Basic validation (not game data validation)
      if (validate) {
        // Check personality ID is in valid range
        if (
          personalityId > 0 &&
          (personalityId < 10000 || personalityId > 99999)
        ) {
          hadErrors = true;
          personalityId = 0;
        }

        // Check EGO IDs are in valid range
        for (let i = 0; i < egos.length; i++) {
          if (egos[i] > 0 && (egos[i] < 20000 || egos[i] > 99999)) {
            hadErrors = true;
            egos[i] = 0;
          }
        }

        // Check slot_type is valid (0-15)
        if (slotType < 0 || slotType > 15) {
          hadErrors = true;
          slotType = 0;
        }
      }

      // Line 181224c60: enabled = slot_type > 0
      // Line 181224c9c: Create FormationDetailInfo
      if (personalityMod > 0 || egos.some((e) => e > 0)) {
        const formation: FormationDetailInfo = {
          slot: slotNum,
          personalityId: personalityId,
          ego1: egos[0],
          ego2: egos[1],
          ego3: egos[2],
          ego4: egos[3],
          ego5: egos[4],
          enabled: slotType > 0,
          slotType: slotType,
        };
        formations.push(formation);
      }
    }

    return { formations, hadErrors };
  }

  /**
   * Encode formations to a deck code.
   * Replicates LimbusCompany.Formation.DeckCode.FormationDeckCode::Encode
   *
   * @param formations - List of formations to encode
   * @param outOfRule - Whether to use the out-of-rule encoding (integer list instead of bit packing)
   * @returns Encoded deck code string
   */
  static encode(
    formations: FormationDetailInfo[],
    outOfRule: boolean = false,
  ): string {
    if (!formations || formations.length === 0) {
      return "";
    }

    let innerB64: string;

    // Step 1: Logic choice based on 'IsOutOfRule'
    if (outOfRule) {
      // Assembly 18122478f (top path): Uses IntListBase64Converter
      const intList: number[] = [];
      for (const f of formations) {
        intList.push(
          f.personalityId,
          f.slotType,
          f.ego1,
          f.ego2,
          f.ego3,
          f.ego4,
          f.ego5,
        );
      }

      innerB64 = IntListBase64Converter.encode(intList);
    } else {
      // Assembly 1812245af (standard path): Bit packing
      // The assembly starts at bit index 1 (rdi_1 = 1 in decoder)
      const allBits: boolean[] = [true];

      // The game expects 12 slots exactly in the bitstream
      // We create a map for easy lookup
      const formationMap = new Map<number, FormationDetailInfo>();
      for (const f of formations) {
        formationMap.set(f.slot, f);
      }

      for (let slotNum = 1; slotNum <= 12; slotNum++) {
        const f = formationMap.get(slotNum);

        let pMod: number;
        let sType: number;
        let eMods: number[];

        if (f) {
          // Convert IDs back to modifiers (id % 100)
          pMod = f.personalityId > 0 ? f.personalityId % 100 : 0;
          sType = f.slotType;
          eMods = [
            f.ego1 > 0 ? f.ego1 % 100 : 0,
            f.ego2 > 0 ? f.ego2 % 100 : 0,
            f.ego3 > 0 ? f.ego3 % 100 : 0,
            f.ego4 > 0 ? f.ego4 % 100 : 0,
            f.ego5 > 0 ? f.ego5 % 100 : 0,
          ];
        } else {
          pMod = 0;
          sType = 0;
          eMods = [0, 0, 0, 0, 0];
        }

        // Pack bits: Personality (7), SlotType (4), EGOs (7 each)
        allBits.push(...this._intToBools(pMod, 7));
        allBits.push(...this._intToBools(sType, 4));
        for (const eMod of eMods) {
          allBits.push(...this._intToBools(eMod, 7));
        }
      }

      innerB64 = BoolListBase64Converter.toBase64(allBits);
    }

    // Step 2: Final Compression (Gzip + Base64)
    return TextCompressionUtility.compress(innerB64);
  }

  /**
   * Replicates ConvertIntToBool (value = (value * 2) | bit logic)
   * Matches the MSB-first assembly build.
   */
  private static _intToBools(value: number, bitCount: number): boolean[] {
    const bools: boolean[] = [];
    for (let i = bitCount - 1; i >= 0; i--) {
      bools.push(((value >> i) & 1) !== 0);
    }
    return bools;
  }
}

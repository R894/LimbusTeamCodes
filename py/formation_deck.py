"""Formation deck code encoder and decoder.

Provides functionality to encode and decode Limbus Company formation deck codes.
"""

from typing import List, Tuple

from converters import (
    IntListBase64Converter,
    TextCompressionUtility,
    BoolListBase64Converter
)
from models import FormationDetailInfo


class FormationDeckCode:
    """Decoder for formation deck codes."""

    @staticmethod
    def decode(encoded: str, validate: bool = False) -> Tuple[List[FormationDetailInfo], bool]:
        """
        Decode formation deck code to list of formations.

        Assembly reference (1812247b0):
        The key insight from the assembly is that bits are read and assembled using:
        `value = (value * 2) | bit` - this builds the number LSB-first

        Args:
            encoded: Base64+gzip encoded deck code
            validate: Whether to perform basic validation

        Returns:
            Tuple of (formations list, had_errors flag)
        """
        if not encoded:
            return [], False

        # Line 1812248be: Decompress and convert to bools
        inner_b64 = TextCompressionUtility.decompress(encoded)
        if not inner_b64:
            return [], False

        bools = BoolListBase64Converter.from_base64(inner_b64, 0x229)
        if not bools:
            return [], False

        formations = []
        had_errors = False
        bit_index = 0

        # Start from bit index 1, not 0 (line 181224930: rdi_1 = 1)
        bit_index = 1

        # Line 181224935: Loop through slots 1-12
        for slot_num in range(1, 13):

            # Lines 18122496c-181224999: Read 7 bits for personality
            # Assembly: r10_1 = (r10_1 * 2) | bit
            # This means: bit 0 goes to LSB, bit 6 goes to MSB
            personality_mod = 0
            for i in range(7):
                if bit_index < len(bools):
                    bit = 1 if bools[bit_index] else 0
                    personality_mod = (personality_mod * 2) | bit
                    bit_index += 1

            # Lines 1812249a4-1812249c5: Read 4 bits for slot_type
            # Assembly: rdx_3 = (rdx_3 * 2) | bit
            slot_type = 0
            for i in range(4):
                if bit_index < len(bools):
                    bit = 1 if bools[bit_index] else 0
                    slot_type = (slot_type * 2) | bit
                    bit_index += 1

            # Lines 1812249cd-181224aa4: Read 7 bits each for 5 EGO slots
            # All use the same pattern: value = (value * 2) | bit
            ego_mods = []
            for ego_idx in range(5):
                ego_mod = 0
                for i in range(7):
                    if bit_index < len(bools):
                        bit = 1 if bools[bit_index] else 0
                        ego_mod = (ego_mod * 2) | bit
                        bit_index += 1
                ego_mods.append(ego_mod)

            # Line 181224ab0: slot_offset = slot_num * 100
            slot_offset = slot_num * 100

            # Lines 181224abb-181224ac7: Reconstruct personality ID
            if personality_mod > 0:
                personality_id = personality_mod + 10000 + slot_offset
            else:
                personality_id = 0

            # Lines 181224acc-181224b1e: Reconstruct EGO IDs
            egos = []
            for ego_mod in ego_mods:
                if ego_mod > 0:
                    egos.append(ego_mod + 20000 + slot_offset)
                else:
                    egos.append(0)

            # Basic validation (not game data validation)
            if validate:
                # Check personality ID is in valid range
                if personality_id > 0 and (personality_id < 10000 or personality_id > 99999):
                    had_errors = True
                    personality_id = 0

                # Check EGO IDs are in valid range
                for i, ego_id in enumerate(egos):
                    if ego_id > 0 and (ego_id < 20000 or ego_id > 99999):
                        had_errors = True
                        egos[i] = 0

                # Check slot_type is valid (0-15)
                if slot_type < 0 or slot_type > 15:
                    had_errors = True
                    slot_type = 0

            # Line 181224c60: enabled = slot_type > 0
            # Line 181224c9c: Create FormationDetailInfo
            if personality_mod > 0 or any(egos):
                formation = FormationDetailInfo(
                    slot=slot_num,
                    personality_id=personality_id,
                    ego1=egos[0],
                    ego2=egos[1],
                    ego3=egos[2],
                    ego4=egos[3],
                    ego5=egos[4],
                    enabled=slot_type > 0,
                    slot_type=slot_type
                )
                formations.append(formation)

        return formations, had_errors

    @staticmethod
    def encode(formations: List[FormationDetailInfo], out_of_rule: bool = False) -> str:
        """
        Replicates LimbusCompany.Formation.DeckCode.FormationDeckCode::Encode
        """
        if not formations:
            return ""

        # Step 1: Logic choice based on 'IsOutOfRule'
        if out_of_rule:
            # Assembly 18122478f (top path): Uses IntListBase64Converter
            int_list = []
            for f in formations:
                int_list.extend([f.personality_id, f.slot_type,
                                f.ego1, f.ego2, f.ego3, f.ego4, f.ego5])

            inner_b64 = IntListBase64Converter.encode(int_list)
        else:
            # Assembly 1812245af (standard path): Bit packing
            # The assembly starts at bit index 1 (rdi_1 = 1 in decoder)
            all_bits = [True]

            # The game expects 12 slots exactly in the bitstream
            # We create a map for easy lookup
            formation_map = {f.slot: f for f in formations}

            for slot_num in range(1, 13):
                f = formation_map.get(slot_num)

                if f:
                    # Convert IDs back to modifiers (id % 100)
                    p_mod = f.personality_id % 100 if f.personality_id > 0 else 0
                    s_type = f.slot_type
                    e_mods = [
                        f.ego1 % 100 if f.ego1 > 0 else 0,
                        f.ego2 % 100 if f.ego2 > 0 else 0,
                        f.ego3 % 100 if f.ego3 > 0 else 0,
                        f.ego4 % 100 if f.ego4 > 0 else 0,
                        f.ego5 % 100 if f.ego5 > 0 else 0,
                    ]
                else:
                    p_mod, s_type, e_mods = 0, 0, [0, 0, 0, 0, 0]

                # Pack bits: Personality (7), SlotType (4), EGOs (7 each)
                all_bits.extend(FormationDeckCode._int_to_bools(p_mod, 7))
                all_bits.extend(FormationDeckCode._int_to_bools(s_type, 4))
                for e_mod in e_mods:
                    all_bits.extend(FormationDeckCode._int_to_bools(e_mod, 7))

            inner_b64 = BoolListBase64Converter.to_base64(all_bits)

        # Step 2: Final Compression (Gzip + Base64)
        return TextCompressionUtility.compress(inner_b64)

    @staticmethod
    def _int_to_bools(value: int, bit_count: int) -> List[bool]:
        """
        Replicates ConvertIntToBool (value = (value * 2) | bit logic)
        Matches the MSB-first assembly build.
        """
        bools = []
        for i in range(bit_count - 1, -1, -1):
            bools.append(bool((value >> i) & 1))
        return bools

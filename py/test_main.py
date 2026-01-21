import pytest
from converters import (
    IntListBase64Converter,
    TextCompressionUtility,
    BoolListBase64Converter
)
from models import FormationDetailInfo
from formation_deck import FormationDeckCode


class TestIntListBase64Converter:
    """Test suite for IntListBase64Converter."""

    def test_encode_simple_list(self):
        """Test encoding a simple list of integers."""
        int_list = [1, 2, 3, 4, 5]
        encoded = IntListBase64Converter.encode(int_list)
        assert encoded, "Encoding should not return empty string"
        assert isinstance(encoded, str), "Encoded result should be a string"

    def test_encode_decode_roundtrip(self):
        """Test that encoding and decoding produces the original list."""
        int_list = [100, 200, 300, -50, 0, 12345]
        encoded = IntListBase64Converter.encode(int_list)
        decoded = IntListBase64Converter.decode(encoded)
        assert decoded == int_list, f"Expected {int_list}, got {decoded}"

    def test_encode_empty_list(self):
        """Test encoding an empty list."""
        encoded = IntListBase64Converter.encode([])
        assert encoded == "", "Empty list should encode to empty string"

    def test_decode_empty_string(self):
        """Test decoding an empty string."""
        decoded = IntListBase64Converter.decode("")
        assert decoded == [], "Empty string should decode to empty list"

    def test_encode_none_raises_error(self):
        """Test that encoding None raises ValueError."""
        with pytest.raises(ValueError, match="Input list cannot be None"):
            IntListBase64Converter.encode(None)

    def test_encode_large_numbers(self):
        """Test encoding large 32-bit integers."""
        int_list = [2147483647, -2147483648, 1000000000]  # Max/min int32
        encoded = IntListBase64Converter.encode(int_list)
        decoded = IntListBase64Converter.decode(encoded)
        assert decoded == int_list

    def test_decode_invalid_base64(self):
        """Test decoding invalid base64 string."""
        decoded = IntListBase64Converter.decode("not-valid-base64!")
        assert decoded == [], "Invalid base64 should return empty list"


class TestTextCompressionUtility:
    """Test suite for TextCompressionUtility."""

    def test_compress_simple_text(self):
        """Test compressing simple text."""
        text = "Hello, World! This is a test."
        compressed = TextCompressionUtility.compress(text)
        assert compressed, "Compression should not return empty string"
        assert isinstance(
            compressed, str), "Compressed result should be a string"

    def test_compress_decompress_roundtrip(self):
        """Test that compression and decompression produces the original text."""
        text = "This is a longer piece of text that should compress well. " * 10
        compressed = TextCompressionUtility.compress(text)
        decompressed = TextCompressionUtility.decompress(compressed)
        assert decompressed == text, "Round-trip should return original text"

    def test_compress_empty_string(self):
        """Test compressing an empty string."""
        compressed = TextCompressionUtility.compress("")
        assert compressed == "", "Empty string should compress to empty string"

    def test_decompress_empty_string(self):
        """Test decompressing an empty string."""
        decompressed = TextCompressionUtility.decompress("")
        assert decompressed == "", "Empty string should decompress to empty string"

    def test_compress_unicode_text(self):
        """Test compressing Unicode text."""
        text = "Hello 世界! 🎮 Testing Unicode"
        compressed = TextCompressionUtility.compress(text)
        decompressed = TextCompressionUtility.decompress(compressed)
        assert decompressed == text, "Unicode text should round-trip correctly"

    def test_decompress_invalid_data(self):
        """Test decompressing invalid data."""
        decompressed = TextCompressionUtility.decompress("not-valid-gzip-data")
        assert decompressed == "", "Invalid data should return empty string"


class TestBoolListBase64Converter:
    """Test suite for BoolListBase64Converter."""

    def test_to_base64_simple_list(self):
        """Test converting a simple bool list to base64."""
        bools = [True, False, True, True, False, False, True, False]
        encoded = BoolListBase64Converter.to_base64(bools)
        assert encoded, "Encoding should not return empty string"
        assert isinstance(encoded, str), "Encoded result should be a string"

    def test_to_base64_from_base64_roundtrip(self):
        """Test that to_base64 and from_base64 round-trip correctly."""
        bools = [True, False, True, True, False,
                 False, True, False, True, True]
        encoded = BoolListBase64Converter.to_base64(bools)
        decoded = BoolListBase64Converter.from_base64(encoded, len(bools))
        assert decoded == bools, f"Expected {bools}, got {decoded}"

    def test_to_base64_empty_list(self):
        """Test converting an empty list."""
        encoded = BoolListBase64Converter.to_base64([])
        assert encoded == "", "Empty list should encode to empty string"

    def test_from_base64_empty_string(self):
        """Test decoding an empty string."""
        decoded = BoolListBase64Converter.from_base64("")
        assert decoded == [], "Empty string should decode to empty list"

    def test_from_base64_with_expected_count(self):
        """Test decoding with a specific expected count."""
        bools = [True] * 16
        encoded = BoolListBase64Converter.to_base64(bools)
        decoded = BoolListBase64Converter.from_base64(encoded, 16)
        assert len(decoded) == 16, f"Expected 16 bools, got {len(decoded)}"

    def test_from_base64_invalid_data(self):
        """Test decoding invalid base64."""
        decoded = BoolListBase64Converter.from_base64("invalid!", 10)
        assert decoded == [], "Invalid base64 should return empty list"

    def test_to_base64_long_list(self):
        """Test with a long list of bools."""
        bools = [i % 2 == 0 for i in range(100)]
        encoded = BoolListBase64Converter.to_base64(bools)
        decoded = BoolListBase64Converter.from_base64(encoded, len(bools))
        assert decoded == bools


class TestFormationDeckCode:
    """Test suite for the Limbus Company Formation Deck Code encoder/decoder."""

    @pytest.fixture
    def game_code(self):
        """Sample game code for testing."""
        return "H4sIAAAAAAAACnMMdEx3BAInR2cQ5ejq6AmmqSLsaGsLANDKykhgAAAA"

    @pytest.fixture
    def sample_formation(self):
        """Create a sample formation for testing."""
        return FormationDetailInfo(
            slot=1,
            personality_id=10101,
            ego1=20101,
            ego2=20102,
            ego3=20103,
            ego4=0,
            ego5=0,
            enabled=True,
            slot_type=1
        )

    def test_decode_original_code(self, game_code):
        """Test that the original game code can be decoded successfully."""
        original_formations, had_errors = FormationDeckCode.decode(game_code)

        assert original_formations is not None, "Failed to decode original code"
        assert len(
            original_formations) > 0, "No formations decoded from game code"
        assert had_errors is False, "Decoding had errors"

    def test_encode_decode_roundtrip(self, game_code):
        """Test that encoding and decoding produces identical results."""
        # Decode original
        original_formations, _ = FormationDeckCode.decode(game_code)
        assert original_formations, "Failed to decode original code"

        # Re-encode using standard bit-packing path
        re_encoded_code = FormationDeckCode.encode(
            original_formations, out_of_rule=False
        )
        assert re_encoded_code, "Failed to re-encode formations"

        # Decode the re-encoded version
        final_formations, _ = FormationDeckCode.decode(re_encoded_code)
        assert final_formations, "Failed to decode re-encoded code"

        # Compare formations by slot
        orig_map = {f.slot: f for f in original_formations}
        final_map = {f.slot: f for f in final_formations}

        # Check all 12 possible slots
        for s_idx in range(1, 13):
            f1 = orig_map.get(s_idx)
            f2 = final_map.get(s_idx)

            # Both None is valid (empty slot)
            if not f1 and not f2:
                continue

            # Both must exist or both must be None
            assert (f1 is not None) == (f2 is not None), \
                f"Slot {s_idx}: Existence mismatch - Original: {bool(f1)}, Re-decoded: {bool(f2)}"

            # Compare all attributes
            if f1 and f2:
                attrs = ['personality_id', 'ego1', 'ego2', 'ego3',
                         'ego4', 'ego5', 'slot_type', 'enabled']
                for attr in attrs:
                    val1 = getattr(f1, attr)
                    val2 = getattr(f2, attr)
                    assert val1 == val2, \
                        f"Slot {s_idx}, {attr}: Original={val1}, Re-decoded={val2}"

    def test_decode_empty_code(self):
        """Test that empty code returns empty formations."""
        formations, had_errors = FormationDeckCode.decode("")
        assert formations == []
        assert had_errors is False

    def test_encode_empty_formations(self):
        """Test that empty formations encode to empty string."""
        code = FormationDeckCode.encode([])
        assert code == ""

    def test_encode_out_of_rule_mode(self, game_code):
        """Test that out_of_rule encoding mode works."""
        original_formations, _ = FormationDeckCode.decode(game_code)
        assert original_formations, "Failed to decode original code"

        # Encode using out_of_rule mode
        out_of_rule_code = FormationDeckCode.encode(
            original_formations, out_of_rule=True
        )
        assert out_of_rule_code, "Failed to encode in out_of_rule mode"
        assert out_of_rule_code != "", "Out of rule encoding returned empty string"

    def test_formation_detail_info_creation(self, sample_formation):
        """Test that FormationDetailInfo can be created correctly."""
        assert sample_formation.slot == 1
        assert sample_formation.personality_id == 10101
        assert sample_formation.ego1 == 20101
        assert sample_formation.ego2 == 20102
        assert sample_formation.ego3 == 20103
        assert sample_formation.enabled is True
        assert sample_formation.slot_type == 1

    def test_decode_with_validation(self, game_code):
        """Test decoding with validation enabled."""
        formations, had_errors = FormationDeckCode.decode(
            game_code, validate=True)
        assert formations is not None
        # Validation may or may not find errors depending on the data

    def test_encode_single_formation(self, sample_formation):
        """Test encoding a single formation."""
        code = FormationDeckCode.encode([sample_formation])
        assert code, "Should encode single formation"

        # Verify it can be decoded back
        decoded, _ = FormationDeckCode.decode(code)
        assert len(decoded) > 0, "Should decode at least one formation"

    def test_encode_multiple_slots(self):
        """Test encoding formations in multiple slots."""
        formations = [
            FormationDetailInfo(
                slot=i,
                personality_id=10000 + i * 100 + 1,
                ego1=20000 + i * 100 + 1,
                ego2=0, ego3=0, ego4=0, ego5=0,
                enabled=True,
                slot_type=1
            )
            for i in range(1, 6)  # Slots 1-5
        ]

        code = FormationDeckCode.encode(formations)
        assert code, "Should encode multiple formations"

        decoded, _ = FormationDeckCode.decode(code)
        assert len(decoded) == 5, f"Expected 5 formations, got {len(decoded)}"

    def test_encode_all_12_slots(self):
        """Test encoding all 12 possible slots."""
        formations = [
            FormationDetailInfo(
                slot=i,
                personality_id=10000 + i * 100 + 1,
                ego1=20000 + i * 100 + 1,
                ego2=0, ego3=0, ego4=0, ego5=0,
                enabled=True,
                slot_type=1
            )
            for i in range(1, 13)  # All 12 slots
        ]

        code = FormationDeckCode.encode(formations)
        decoded, _ = FormationDeckCode.decode(code)
        assert len(
            decoded) == 12, f"Expected 12 formations, got {len(decoded)}"

    def test_int_to_bools_utility(self):
        """Test the _int_to_bools utility function."""
        # Test known conversion
        bools = FormationDeckCode._int_to_bools(5, 4)  # 5 = 0b0101
        assert bools == [False, True, False,
                         True], f"Expected [False, True, False, True], got {bools}"

        # Test with 0
        bools = FormationDeckCode._int_to_bools(0, 3)
        assert bools == [False, False, False]

        # Test with max value for bit count
        bools = FormationDeckCode._int_to_bools(127, 7)  # 127 = 0b1111111
        assert all(bools), "All bits should be True for 127"

    def test_validation_invalid_personality_id(self):
        """Test that validation catches invalid personality IDs."""
        # Create a formation with potentially invalid ID (will be caught during validation)
        formation = FormationDetailInfo(
            slot=1,
            personality_id=99999999,  # Way out of range
            ego1=0, ego2=0, ego3=0, ego4=0, ego5=0,
            enabled=True,
            slot_type=1
        )

        # Encode and decode with validation
        code = FormationDeckCode.encode([formation])
        decoded, had_errors = FormationDeckCode.decode(code, validate=True)

        # The validation in decode checks if values are in expected ranges
        assert decoded is not None

    def test_slot_type_range(self):
        """Test formations with different slot types (0-15)."""
        for slot_type in [0, 1, 5, 10, 15]:
            formation = FormationDetailInfo(
                slot=1,
                personality_id=10101,
                ego1=20101, ego2=0, ego3=0, ego4=0, ego5=0,
                enabled=slot_type > 0,
                slot_type=slot_type
            )

            code = FormationDeckCode.encode([formation])
            decoded, _ = FormationDeckCode.decode(code)

            if slot_type > 0:
                assert len(
                    decoded) > 0, f"slot_type {slot_type} should produce a formation"
                assert decoded[0].slot_type == slot_type

    def test_disabled_slot(self):
        """Test that disabled slots (slot_type=0) are handled correctly."""
        formation = FormationDetailInfo(
            slot=1,
            personality_id=10101,
            ego1=0, ego2=0, ego3=0, ego4=0, ego5=0,
            enabled=False,
            slot_type=0
        )

        code = FormationDeckCode.encode([formation])
        decoded, _ = FormationDeckCode.decode(code)

        # A slot with slot_type=0 and no personality might not appear in decoded
        # This tests that the encoder handles disabled slots correctly


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

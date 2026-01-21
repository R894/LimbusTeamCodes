# Limbus Company Formation Deck Code Library

Encoder and decoder libraries for Limbus Company formation deck codes, available in both **Python** and **TypeScript**.

This library replicates the assembly-level logic from Limbus Company's formation deck code encoder/decoder. The code was reverse-engineered from the game's binary to ensure exact compatibility.

## Available Implementations

- **Python** - Located in [py/](py/) directory
- **TypeScript** - Located in [ts/](ts/) directory (full NPM package)

## Quick Start

### Python

```python
from py.formation_deck import FormationDeckCode

# Decode
result = FormationDeckCode.decode("H4sIAAAAAAAACnMMdEx3BAInR2cQ5ejq6AmmqSLsaGsLANDKykhgAAAA")
formations, had_errors = result
print(formations)

# Encode
from py.models import FormationDetailInfo
formations = [
    FormationDetailInfo(
        slot=1,
        personality_id=10101,
        ego1=20101,
        ego2=0, ego3=0, ego4=0, ego5=0,
        enabled=True,
        slot_type=1
    )
]
encoded = FormationDeckCode.encode(formations)
print(encoded)
```

### TypeScript

```bash
npm install limbus-formation-deck
```

```typescript
import { FormationDeckCode } from "limbus-formation-deck";

// Decode
const result = FormationDeckCode.decode(
  "H4sIAAAAAAAACnMMdEx3BAInR2cQ5ejq6AmmqSLsaGsLANDKykhgAAAA",
);
console.log(result.formations);

// Encode
const formations = [
  {
    slot: 1,
    personalityId: 10101,
    ego1: 20101,
    ego2: 0,
    ego3: 0,
    ego4: 0,
    ego5: 0,
    enabled: true,
    slotType: 1,
  },
];
const encoded = FormationDeckCode.encode(formations);
console.log(encoded);
```

## How It Works Under the Hood

### Overview of Encoding Layers

The formation deck code uses a multi-layer encoding scheme:

```text
Original Formation Data
        ↓
   Bit Packing (or Integer List for out-of-rule)
        ↓
   Base64 Encoding
        ↓
   Gzip Compression
        ↓
   Base64 Encoding (outer layer)
        ↓
   Final Deck Code
```

### Data Structure Format

Each formation deck code encodes **exactly 12 slots**, regardless of how many are actually used.

#### Per-Slot Data Layout

For each slot, the following data is encoded:

| Field                | Bits | Range | Description           |
| -------------------- | ---- | ----- | --------------------- |
| Personality Modifier | 7    | 0-127 | Character ID modifier |
| Slot Type            | 4    | 0-15  | Slot activation type  |
| EGO 1 Modifier       | 7    | 0-127 | First EGO modifier    |
| EGO 2 Modifier       | 7    | 0-127 | Second EGO modifier   |
| EGO 3 Modifier       | 7    | 0-127 | Third EGO modifier    |
| EGO 4 Modifier       | 7    | 0-127 | Fourth EGO modifier   |
| EGO 5 Modifier       | 7    | 0-127 | Fifth EGO modifier    |

**Total: 46 bits per slot × 12 slots = 552 bits + 1 header bit = 553 bits (0x229)**

#### ID Encoding Formula

The actual IDs are computed from modifiers using a slot-based offset:

```python
slot_offset = slot_number * 100

# Personality ID
if personality_modifier > 0:
    personality_id = personality_modifier + 10000 + slot_offset
else:
    personality_id = 0

# EGO ID
if ego_modifier > 0:
    ego_id = ego_modifier + 20000 + slot_offset
else:
    ego_id = 0
```

#### Examples

- Slot 1, Personality Modifier 1 → ID: `1 + 10000 + 100 = 10101`
- Slot 3, EGO Modifier 5 → ID: `5 + 20000 + 300 = 20305`
- Slot 12, Personality Modifier 99 → ID: `99 + 10000 + 1200 = 11299`

### Bit Packing Details

The assembly code builds numbers using the pattern `value = (value × 2) | bit`, which reads bits in **MSB-first order**.

#### Example: Packing value `5` into 7 bits

```text
Value 5 in binary: 0000101

Bit order in stream:
[0][0][0][0][1][0][1]
 ↑                 ↑
MSB               LSB

Reading process (assembly):
value = 0
value = (0 × 2) | 0 = 0
value = (0 × 2) | 0 = 0
value = (0 × 2) | 0 = 0
value = (0 × 2) | 0 = 0
value = (0 × 2) | 1 = 1
value = (1 × 2) | 0 = 2
value = (2 × 2) | 1 = 5  ✓
```

#### Bitstream Layout

```text
Bit Index:  0    1-7      8-11    12-18   19-25   26-32   33-39   40-46
           ───  ───────  ──────  ───────────────────────────────────────
Content:   [1]  [Pers1]  [Type1] [EGO1₁] [EGO2₁] [EGO3₁] [EGO4₁] [EGO5₁]

           47-53    54-57   58-64   ... (continues for all 12 slots)
           ───────  ──────  ───────
           [Pers2]  [Type2] [EGO1₂] ...
```

The first bit (index 0) is always `1` (header bit).

### Boolean to Base64 Conversion

The boolean array is packed into bytes:

```python
# Each byte stores 8 bits, MSB-first
byte = 0
for j in range(8):
    if bools[i + j]:
        bit_position = 7 - j
        byte |= (1 << bit_position)
```

#### Example

Booleans `[true, false, false, false, true, false, true, false]`

```text
Bit positions: 7  6  5  4  3  2  1  0
Values:       [1][0][0][0][1][0][1][0]

Binary: 10001010
Hex: 0x8A
Decimal: 138
```

### Text Compression

The Base64-encoded boolean array is then compressed using **gzip** and encoded again with Base64:

```text
boolArray → Base64 → UTF-8 bytes → Gzip → Base64 → Final Code
```

This dual Base64 + gzip approach achieves high compression ratios (typically 70-90% size reduction).

### Out-of-Rule Encoding

When `out_of_rule = True` (Python) or `outOfRule = true` (TypeScript), the encoding uses a simpler integer list format instead of bit packing:

```python
# For each formation:
int_list = [
    personality_id, slot_type,
    ego1, ego2, ego3, ego4, ego5
]

# Then: int_list → Base64 (as int32 LE) → Gzip → Base64
```

This format is less compact but easier to parse and doesn't require the slot offset calculations.

### Assembly References

The implementation is based on reverse-engineering the following game assembly functions:

| Function                    | Address       | Purpose                   |
| --------------------------- | ------------- | ------------------------- |
| `FormationDeckCode::Decode` | `0x1812247b0` | Main decode entry point   |
| `FormationDeckCode::Encode` | `0x18122457f` | Main encode entry point   |
| Bit reading loop            | `0x18122496c` | Reads 7-bit personality   |
| Slot type reading           | `0x1812249a4` | Reads 4-bit slot type     |
| EGO reading loop            | `0x1812249cd` | Reads 5×7-bit EGO values  |
| ID reconstruction           | `0x181224abb` | Converts modifiers to IDs |

### Edge Cases and Validation

The decode function optionally validates:

1. **Personality IDs**: Must be 0 or in range `[10000, 99999]`
2. **EGO IDs**: Must be 0 or in range `[20000, 99999]`
3. **Slot Types**: Must be in range `[0, 15]`

Invalid values are set to 0 and the `had_errors` flag is set to `true`.

### Performance Considerations

- **Encoding**: O(n) where n = 12 slots (constant)
- **Decoding**: O(n) where n = 12 slots (constant)
- **Memory**: ~70 bytes per encoded formation (gzipped)
- **Compression ratio**: ~85% size reduction on average

The constant-time performance is due to the fixed 12-slot format, making it very efficient regardless of how many slots are actually populated.

## Repository Structure

```
LimbusTeamCodes/
├── README.md                    # This file
├── py/                          # Python implementation
│   ├── formation_deck.py
│   ├── models.py
│   └── converters/
│       ├── __init__.py
│       ├── bool_converter.py
│       ├── int_converter.py
│       └── text_converter.py
└── ts/                          # TypeScript implementation
    ├── README.md
    ├── package.json
    ├── tsconfig.json
    ├── example.ts
    └── src/
        ├── index.ts
        ├── formation-deck.ts
        ├── models.ts
        └── converters/
            ├── index.ts
            ├── bool-converter.ts
            ├── int-converter.ts
            └── text-converter.ts
```

## License

MIT

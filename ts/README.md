# Limbus Formation Deck Code Library

TypeScript library for encoding and decoding Limbus Company formation deck codes.

## Installation

```bash
npm install
```

## Usage

### Decoding a formation deck code

```typescript
import { FormationDeckCode } from "limbus-formation-deck";

const encoded = "H4sIAAAAAAAA..."; // Your encoded deck code
const result = FormationDeckCode.decode(encoded);

console.log(result.formations);
console.log(result.hadErrors);
```

### Encoding formations

```typescript
import { FormationDeckCode, FormationDetailInfo } from "limbus-formation-deck";

const formations: FormationDetailInfo[] = [
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
  // ... more formations
];

const encoded = FormationDeckCode.encode(formations);
console.log(encoded);
```

## API

### `FormationDeckCode.decode(encoded: string, validate?: boolean): DecodeResult`

Decodes a formation deck code string into a list of formations.

**Parameters:**

- `encoded` - Base64+gzip encoded deck code
- `validate` - Optional, whether to perform basic validation (default: false)

**Returns:**

- `DecodeResult` object containing:
  - `formations` - Array of `FormationDetailInfo` objects
  - `hadErrors` - Boolean flag indicating if errors were encountered

### `FormationDeckCode.encode(formations: FormationDetailInfo[], outOfRule?: boolean): string`

Encodes formations into a deck code string.

**Parameters:**

- `formations` - Array of formations to encode
- `outOfRule` - Optional, whether to use out-of-rule encoding (default: false)

**Returns:**

- Encoded deck code string

### `FormationDetailInfo` Interface

```typescript
interface FormationDetailInfo {
  slot: number; // Slot number (1-12)
  personalityId: number; // Character ID
  ego1: number; // EGO slot 1
  ego2: number; // EGO slot 2
  ego3: number; // EGO slot 3
  ego4: number; // EGO slot 4
  ego5: number; // EGO slot 5
  enabled: boolean; // Whether slot is active
  slotType: number; // Slot type (0-15)
}
```

## Building

```bash
npm run build
```

This will compile the TypeScript code to JavaScript in the `dist` directory.

## Testing

```bash
npm test
```

## How It Works Under the Hood

This library replicates the assembly-level logic from Limbus Company's formation deck code encoder/decoder. The code was reverse-engineered from the game's binary to ensure exact compatibility.

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

```typescript
slotOffset = slotNumber × 100

// Personality ID
if (personalityModifier > 0) {
  personalityId = personalityModifier + 10000 + slotOffset
} else {
  personalityId = 0
}

// EGO ID
if (egoModifier > 0) {
  egoId = egoModifier + 20000 + slotOffset
} else {
  egoId = 0
}
```

#### Examples:

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

```typescript
// Each byte stores 8 bits, MSB-first
byte = 0;
for (j = 0; j < 8; j++) {
  if (bools[i + j]) {
    bitPosition = 7 - j;
    byte |= 1 << bitPosition;
  }
}
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

```typescript
boolArray → Base64 → UTF-8 bytes → Gzip → Base64 → Final Code
```

This dual Base64 + gzip approach achieves high compression ratios (typically 70-90% size reduction).

### Out-of-Rule Encoding

When `outOfRule = true`, the encoding uses a simpler integer list format instead of bit packing:

```typescript
// For each formation:
intList = [personalityId, slotType, ego1, ego2, ego3, ego4, ego5];

// Then: intList → Base64 (as int32 LE) → Gzip → Base64
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

Invalid values are set to 0 and the `hadErrors` flag is set to `true`.

### Performance Considerations

- **Encoding**: O(n) where n = 12 slots (constant)
- **Decoding**: O(n) where n = 12 slots (constant)
- **Memory**: ~70 bytes per encoded formation (gzipped)
- **Compression ratio**: ~85% size reduction on average

The constant-time performance is due to the fixed 12-slot format, making it very efficient regardless of how many slots are actually populated.

## License

MIT

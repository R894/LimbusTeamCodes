/**
 * Data models for formation deck codes.
 *
 * Contains interface and class definitions for formation-related data structures.
 */

/**
 * Represents one formation slot.
 */
export interface FormationDetailInfo {
  /** Slot number (1-12) */
  slot: number;
  /** Character ID */
  personalityId: number;
  /** EGO slot 1 */
  ego1: number;
  /** EGO slot 2 */
  ego2: number;
  /** EGO slot 3 */
  ego3: number;
  /** EGO slot 4 */
  ego4: number;
  /** EGO slot 5 */
  ego5: number;
  /** Whether slot is active */
  enabled: boolean;
  /** Slot type (0-15) */
  slotType: number;
}

/**
 * Creates a FormationDetailInfo object with default values.
 */
export function createFormationDetailInfo(
  partial: Partial<FormationDetailInfo> & Pick<FormationDetailInfo, "slot">,
): FormationDetailInfo {
  return {
    slot: partial.slot,
    personalityId: partial.personalityId ?? 0,
    ego1: partial.ego1 ?? 0,
    ego2: partial.ego2 ?? 0,
    ego3: partial.ego3 ?? 0,
    ego4: partial.ego4 ?? 0,
    ego5: partial.ego5 ?? 0,
    enabled: partial.enabled ?? false,
    slotType: partial.slotType ?? 0,
  };
}

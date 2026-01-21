"""Data models for formation deck codes.

Contains dataclass definitions for formation-related data structures.
"""

from dataclasses import dataclass


@dataclass
class FormationDetailInfo:
    """Represents one formation slot."""
    slot: int              # Slot number (1-12)
    personality_id: int    # Character ID
    ego1: int             # EGO slot 1
    ego2: int             # EGO slot 2
    ego3: int             # EGO slot 3
    ego4: int             # EGO slot 4
    ego5: int             # EGO slot 5
    enabled: bool         # Whether slot is active
    slot_type: int        # Slot type (0-15)
